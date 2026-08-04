# Kafka 副本未同步分区问题分析报告

## 一、事件概述

2026 年 8 月 4 日，`uat-cluster01` 集群中的 Kafka 触发“副本未同步分区”告警。

告警基本信息：

| 项目        | 内容                                               |
| --------- | ------------------------------------------------ |
| 集群        | `uat-cluster01`                                  |
| 命名空间      | `dominos-mq`                                     |
| Kafka 集群  | `kafka`                                          |
| Topic     | `dominos-apps`                                   |
| 告警级别      | Warning                                          |
| 告警持续时间    | 超过 10 分钟                                         |
| 异常类型      | Under Replicated Partitions                      |
| 涉及 Broker | Broker 2                                         |
| 涉及分区      | Partition 0、Partition 2；日志显示 Partition 1 此前也曾受影响 |

监控分别在 `kafka-kafka-0` 和 `kafka-kafka-1` 上产生告警，是因为这两个 Broker 分别是异常分区的 Leader，并不表示 Broker 0、Broker 1 自身的 Follower 副本发生了异常。

---

## 二、问题现象

### 2.1 告警信息

监控显示：

```text
kafka-kafka-0：未充分复制分区数量为 1
kafka-kafka-1：未充分复制分区数量为 1
```

对应的告警指标为：

```promql
sum(
  kafka_server_replicamanager_underreplicatedpartitions{
    cluster_name!="kpanda-global-cluster"
  }
) by (
  cluster_name,
  namespace,
  pod,
  cluster
)
```

`UnderReplicatedPartitions` 表示：

```text
ISR 数量 < Replicas 数量
```

即某些分区的一个或多个 Follower 副本没有及时跟上 Leader，已被移出 ISR。

### 2.2 异常分区检查

进入任意正常 Kafka Pod，执行：

```bash
./bin/kafka-topics.sh \
  --bootstrap-server 127.0.0.1:9092 \
  --describe \
  --under-replicated-partitions
```

检查结果：

```text
Topic: dominos-apps  Partition: 0  Leader: 0  Replicas: 0,2,1  Isr: 0,1
Topic: dominos-apps  Partition: 2  Leader: 1  Replicas: 1,0,2  Isr: 0,1
```

异常分区对应关系：

| Topic        | Partition | Leader | Replicas | ISR | 未进入 ISR 的 Broker |
| ------------ | --------: | -----: | -------- | --- | ---------------: |
| dominos-apps |         0 |      0 | 0,2,1    | 0,1 |         Broker 2 |
| dominos-apps |         2 |      1 | 1,0,2    | 0,1 |         Broker 2 |

两个分区中，Broker 2 均存在于 `Replicas` 中，但不在 `ISR` 中，因此可以确定：

> 本次同步落后的副本位于 Broker 2。

---

## 三、告警 Pod 与实际异常 Broker 的关系

本次告警与分区 Leader 的对应关系如下：

| 告警 Pod          | Leader 分区        | 实际未同步 Broker |
| --------------- | ---------------- | ------------ |
| `kafka-kafka-0` | `dominos-apps-0` | Broker 2     |
| `kafka-kafka-1` | `dominos-apps-2` | Broker 2     |

该指标统计的是当前 Broker 作为 Leader 时，其管理的未充分复制分区数量。

因此：

```text
告警 Pod = 异常分区的 Leader Broker
实际异常 Broker = Replicas 中存在、但不在 ISR 中的 Broker
```

告警描述中不应直接将告警 Pod 定义为同步异常 Broker。

---

## 四、日志证据分析

### 4.1 Broker 2 曾同时退出多个分区的 ISR

Broker 2 收到的元数据信息显示，`dominos-apps` 三个分区一度均为：

```text
isr=[0,1]
```

具体状态：

```text
dominos-apps-0：Replicas=[0,2,1]，ISR=[0,1]
dominos-apps-1：Replicas=[2,1,0]，ISR=[0,1]
dominos-apps-2：Replicas=[1,0,2]，ISR=[0,1]
```

这说明当时不是单个 Partition 的孤立异常，而是 Broker 2 上多个 Follower 副本同时被移出 ISR，问题范围集中在 Broker 2。

### 4.2 ReplicaFetcher 线程未完全停止

Broker 2 日志中持续存在以下复制线程：

```text
ReplicaFetcherThread-4-0
ReplicaFetcherThread-3-0
ReplicaFetcherThread-2-1
```

这些线程持续执行：

* 更新 Log Start Offset；
* 写入新的日志段；
* 滚动 Log Segment；
* 写入 Producer Snapshot；
* 从 Leader 拉取分区数据。

例如，Broker 2 持续处理 `dominos-apps-0`、`dominos-apps-1` 和 `dominos-apps-2` 的日志段。

后续日志中仍持续出现三个分区的日志段滚动，说明 ReplicaFetcher 并未永久停止。

因此，本次问题不像：

* Broker 2 持续完全失联；
* ReplicaFetcherThread 永久停止；
* Kafka 日志目录永久不可用。

更符合以下过程：

```text
Broker 2 短时发生资源抖动、通信异常或进程停顿
                     ↓
多个 Follower 副本不能持续跟上 Leader
                     ↓
Broker 2 被移出多个分区的 ISR
                     ↓
Broker 2 恢复后持续拉取副本数据
                     ↓
各分区逐步重新加入 ISR
```

### 4.3 分区逐步恢复

日志确认 `dominos-apps-1` 后续恢复为：

```text
isr=[0,1,2]
```

随后，`dominos-apps-0` 也恢复为：

```text
isr=[0,1,2]
```

这说明 Broker 2 恢复后，各 Follower 副本是逐个追平 Leader 并重新加入 ISR，而不是同时恢复。

当前截取日志中尚未看到 `dominos-apps-2` 重新加入 ISR 的明确元数据记录，但其 ReplicaFetcher 仍持续工作。是否最终恢复，应以以下命令的实时结果为准：

```bash
./bin/kafka-topics.sh \
  --bootstrap-server 127.0.0.1:9092 \
  --describe \
  --under-replicated-partitions
```

命令无输出时，表示当前已不存在未充分复制分区。

---

## 五、副本数据目录检查

执行：

```bash
./bin/kafka-log-dirs.sh \
  --bootstrap-server 127.0.0.1:9092 \
  --describe \
  --broker-list 2 \
  --topic-list dominos-apps
```

检查结果：

```json
{
  "broker": 2,
  "logDir": "/var/lib/kafka/data/kafka-log2",
  "error": null,
  "partitions": [
    {
      "partition": "dominos-apps-0",
      "offsetLag": 0,
      "isFuture": false
    },
    {
      "partition": "dominos-apps-1",
      "offsetLag": 0,
      "isFuture": false
    },
    {
      "partition": "dominos-apps-2",
      "offsetLag": 0,
      "isFuture": false
    }
  ]
}
```

该结果说明检查时：

* Broker 2 日志目录未返回错误；
* 分区不是副本迁移过程中的 Future Replica；
* 副本已经追到当前可见的 High Watermark 附近；
* 未发现日志目录被 Kafka 标记为故障。

需要注意：

```text
offsetLag=0 不等于该副本已经重新加入 ISR
```

ISR 恢复还需要 Leader 确认 Follower 持续、稳定地追上最新日志进度，并完成 ISR 状态更新。

---

## 六、日志保留与磁盘负载分析

Kafka 配置为：

```properties
log.retention.hours=24
```

日志中对应的保留时间为：

```text
retention time 86400000ms
```

换算关系：

```text
86400000ms = 24 小时
```

说明 `log.retention.hours=24` 已正常生效。

Kafka 日志显示正在正常删除超过 24 小时的 Segment，并同步更新 Log Start Offset。

`dominos-apps` 单个日志段约为 1 GiB，且日志段滚动和删除较频繁。Kafka Broker 同时需要处理：

* 生产者消息写入；
* Follower 副本写入；
* 消费者读取；
* 日志段滚动；
* Offset Index 和 Time Index 更新；
* Producer Snapshot 写入；
* 过期日志段删除；
* Page Cache 回写。

这些操作会增加磁盘 I/O 压力。

但现有日志中未发现：

* 日志目录损坏；
* 磁盘读写错误；
* Segment 删除失败；
* LogDirFailure；
* I/O Exception。

因此：

> `log.retention.hours=24` 属于正常配置，并不是本次副本退出 ISR 的直接根因，但高吞吐下频繁的日志段滚动和清理，可能放大节点短时磁盘抖动的影响。

---

## 七、Replication Bytes In/Out 分析

### 7.1 指标含义

`Replication Bytes In`：

```text
Broker 作为 Follower，从 Leader Broker 接收的副本数据速率
```

`Replication Bytes Out`：

```text
Broker 作为 Leader，向其他 Follower Broker发送的副本数据速率
```

### 7.2 本次查询结果

Replication Bytes In：

```text
kafka-kafka-0：47,631 B/s
kafka-kafka-1：82,331 B/s
kafka-kafka-2：129,884 B/s
```

Replication Bytes Out：

```text
kafka-kafka-0：161,462 B/s
kafka-kafka-1：96,062 B/s
kafka-kafka-2：307 B/s
```

该分布与分区角色基本一致：

* Broker 0 承担多个 Leader 分区，因此 Replication Out 较高；
* Broker 1 也承担 Leader 分区，因此存在较高 Replication Out；
* Broker 2 在相关分区中主要作为 Follower，因此 Replication In 最高；
* Broker 2 没有承担相关分区的 Leader，因此 Replication Out 接近 0。

Broker 2 的 Replication Out 接近 0 并不表示复制异常，而是由其 Leader/Follower 角色决定。

### 7.3 集群复制流量总量

```text
Replication IN  ≈ 259,847 B/s
Replication OUT ≈ 257,833 B/s
```

两者相差约：

```text
2,014 B/s
```

差异约为：

```text
0.78%
```

Replication In 和 Replication Out 总体接近，说明检查时 Broker 间复制链路已经基本恢复，没有发现持续性的全局复制流量丢失。

因此，目前不能认定：

```text
Broker 2 长期存在复制速度低于写入速度的问题
```

### 7.4 Replication Bytes In 查询命令

在 Prometheus 或 Grafana Explore 中执行：

```promql
sum by (
  cluster_name,
  namespace,
  cluster,
  pod
) (
  rate(
    kafka_server_brokertopicmetrics_replicationbytesin_total{
      cluster_name="uat-cluster01",
      namespace="dominos-mq"
    }[5m]
  )
)
```

如果指标中确认存在 `cluster="kafka"` 标签，也可以增加：

```promql
sum by (
  cluster_name,
  namespace,
  cluster,
  pod
) (
  rate(
    kafka_server_brokertopicmetrics_replicationbytesin_total{
      cluster_name="uat-cluster01",
      namespace="dominos-mq",
      cluster="kafka"
    }[5m]
  )
)
```

### 7.5 Replication Bytes Out 查询命令

```promql
sum by (
  cluster_name,
  namespace,
  cluster,
  pod
) (
  rate(
    kafka_server_brokertopicmetrics_replicationbytesout_total{
      cluster_name="uat-cluster01",
      namespace="dominos-mq"
    }[5m]
  )
)
```

带 Kafka 集群标签的查询：

```promql
sum by (
  cluster_name,
  namespace,
  cluster,
  pod
) (
  rate(
    kafka_server_brokertopicmetrics_replicationbytesout_total{
      cluster_name="uat-cluster01",
      namespace="dominos-mq",
      cluster="kafka"
    }[5m]
  )
)
```

### 7.6 查询集群复制流量总量

Replication In 总量：

```promql
sum(
  rate(
    kafka_server_brokertopicmetrics_replicationbytesin_total{
      cluster_name="uat-cluster01",
      namespace="dominos-mq"
    }[5m]
  )
)
```

Replication Out 总量：

```promql
sum(
  rate(
    kafka_server_brokertopicmetrics_replicationbytesout_total{
      cluster_name="uat-cluster01",
      namespace="dominos-mq"
    }[5m]
  )
)
```

在稳定状态下：

```text
集群 Replication In 总量应与 Replication Out 总量趋势基本一致
```

由于 Prometheus 抓取时间、计算窗口和瞬时流量不同，两者不要求绝对相等。

### 7.7 检查告警时段的复制流量

建议将 Grafana 时间范围调整到告警前后，例如：

```text
2026-08-04 13:30:00 至 2026-08-04 14:20:00
```

查看 Broker 2 的一分钟复制接收流量：

```promql
sum by (pod) (
  rate(
    kafka_server_brokertopicmetrics_replicationbytesin_total{
      cluster_name="uat-cluster01",
      namespace="dominos-mq",
      pod="kafka-kafka-2"
    }[1m]
  )
)
```

查看 Broker 0、1 的一分钟复制发送流量：

```promql
sum by (pod) (
  rate(
    kafka_server_brokertopicmetrics_replicationbytesout_total{
      cluster_name="uat-cluster01",
      namespace="dominos-mq",
      pod=~"kafka-kafka-[01]"
    }[1m]
  )
)
```

重点观察：

1. Broker 2 的 Replication In 是否突然下降或归零；
2. Broker 2 的复制流量下降时间是否与 ISR Shrink 时间一致；
3. Broker 2 恢复后 Replication In 是否明显升高；
4. Broker 0、1 的 Replication Out 是否同期下降；
5. Replication In/Out 异常是否与磁盘延迟、CPU Throttling 或 GC Pause 同时发生。

如果 Broker 2 的 Replication In 曾短时归零，随后恢复并升高，说明 Broker 2 曾经无法正常从 Leader 拉取副本，恢复后进入追赶状态。

如果 Replication In 始终正常，则需要重点排查：

* 磁盘写入延迟；
* CPU Throttling；
* JVM GC Pause；
* Kafka 进程调度停顿；
* 节点资源竞争；
* ISR 更新或控制面通信异常。

### 7.8 检查指标是否重复采集

查看原始指标：

```promql
kafka_server_brokertopicmetrics_replicationbytesin_total{
  cluster_name="uat-cluster01",
  namespace="dominos-mq"
}
```

```promql
kafka_server_brokertopicmetrics_replicationbytesout_total{
  cluster_name="uat-cluster01",
  namespace="dominos-mq"
}
```

检查每个 Pod 的时序数量：

```promql
count by (
  cluster_name,
  namespace,
  cluster,
  pod
) (
  kafka_server_brokertopicmetrics_replicationbytesin_total{
    cluster_name="uat-cluster01",
    namespace="dominos-mq"
  }
)
```

```promql
count by (
  cluster_name,
  namespace,
  cluster,
  pod
) (
  kafka_server_brokertopicmetrics_replicationbytesout_total{
    cluster_name="uat-cluster01",
    namespace="dominos-mq"
  }
)
```

如果同一个 Pod 存在多个不同 `instance`、`job`、`service` 或 `endpoint` 的重复时序，直接 `sum by(pod)` 可能造成数值重复累计，需要先排除重复采集。

---

## 八、磁盘吞吐差异判断

现场观察到：

```text
Broker 0、1 磁盘读写约 30 MB/s
Broker 2 磁盘读写约 20 MB/s
```

IOPS 也存在类似差异。

该现象值得关注，但不能单独证明 Broker 2 的磁盘性能不足，因为三个 Broker 当前承担的角色不同：

* Leader Broker 需要接收生产写入；
* Leader Broker 需要处理消费者读取；
* Leader Broker 需要从日志文件读取数据并发送给 Follower；
* Follower Broker 主要接收副本数据并写入本地日志。

因此，总磁盘吞吐不具备完全等值的横向可比性。

要确认磁盘是否为瓶颈，应对比：

```text
rMB/s
wMB/s
r/s
w/s
r_await
w_await
aqu-sz
%util
```

节点侧检查：

```bash
iostat -x 1 60
```

判断方式：

* Broker 2 吞吐较低，同时 `%util` 接近 100%、`await` 明显升高：高度怀疑存储瓶颈；
* Broker 2 吞吐较低，但 `%util` 和 `await` 正常：应优先检查网络、CPU、GC 和 ReplicaFetcher；
* Broker 2 网络接收流量正常，但磁盘写入下降：重点检查存储路径；
* Broker 2 Replication In 同时下降：重点检查 Broker 间网络或 Kafka 进程状态。

---

## 九、根因判断

### 9.1 直接原因

Broker 2 上的多个 Follower 副本在一段时间内未能持续跟上 Leader 最新日志进度，导致 Broker 2 被移出 `dominos-apps` 多个分区的 ISR，从而触发 `UnderReplicatedPartitions` 告警。

### 9.2 已确认事实

当前已确认：

1. Broker 2 同时退出过多个分区的 ISR；
2. 分区 Leader 始终存在；
3. Broker 0、Broker 1 仍处于 ISR；
4. Broker 2 的 ReplicaFetcherThread 没有永久停止；
5. Broker 2 后续持续执行副本拉取；
6. `dominos-apps-1` 和 `dominos-apps-0` 已确认重新加入 ISR；
7. Kafka 日志目录未返回错误；
8. 检查时 `offsetLag=0`；
9. 复制流量 In/Out 总量基本匹配；
10. 未发现明确的 Kafka ERROR、日志目录损坏或 Segment 删除失败。

### 9.3 初步根因

综合现有证据，初步判断：

> Broker 2 曾发生短时资源抖动、进程停顿或 Broker 间通信异常，导致多个 Follower 副本未能持续跟上 Leader，并被移出 ISR。异常恢复后，ReplicaFetcher 继续拉取数据，各分区逐步追平并重新加入 ISR。

### 9.4 尚未确认的触发因素

目前还不能唯一确定最初触发 Broker 2 掉出 ISR 的具体因素，需继续排查：

1. Broker 2 Pod 或 Kafka 进程短时重启；
2. Broker 2 容器 CPU Throttling；
3. JVM Full GC 或长时间 Stop-The-World；
4. Broker 2 所在节点磁盘延迟短时升高；
5. Broker 2 与 Broker 0、1 之间网络抖动；
6. 节点资源竞争或系统调度停顿；
7. 高吞吐及频繁日志段滚动、清理放大短时资源抖动。

因此，当前根因结论应定义为“初步判断”，不能直接认定为磁盘性能不足或复制带宽不足。

---

## 十、影响评估

问题发生期间：

* Partition Leader 正常；
* ISR 中仍保留 Broker 0、1；
* 未发现 Offline Partition；
* 分区仍可正常提供读写；
* 未发现数据丢失证据；
* Kafka 集群后续能够自行恢复。

但同步副本数由 3 个下降为 2 个，集群容错能力降低。

如果 Topic 配置：

```properties
min.insync.replicas=2
```

则当时 ISR 数量已经处于最低允许值。

此时如果 Broker 0 或 Broker 1 再次异常，配置 `acks=all` 的生产请求可能失败。

因此，该告警虽然最终自行恢复，但仍属于有效告警，不建议直接屏蔽。

---

## 十一、处置及优化建议

### 11.1 保留现有 Warning 告警

建议继续保留：

```yaml
for: 10m
severity: warning
```

本次异常持续时间已经超过 10 分钟，属于有效异常，不建议通过简单延长 `for` 时间进行屏蔽。

### 11.2 增加 UnderMinIsr 严重告警

建议增加：

```promql
sum by (
  cluster_name,
  namespace,
  cluster
) (
  kafka_server_replicamanager_underminisrpartitioncount{
    cluster_name!="kpanda-global-cluster"
  }
) > 0
```

建议配置：

```yaml
for: 2m
severity: critical
```

### 11.3 检查 Broker 2 是否重启

```bash
kubectl get pod -n dominos-mq kafka-kafka-2 \
  -o jsonpath='{range .status.containerStatuses[*]}{.name}{" restartCount="}{.restartCount}{" lastReason="}{.lastState.terminated.reason}{" lastExitCode="}{.lastState.terminated.exitCode}{" finishedAt="}{.lastState.terminated.finishedAt}{"\n"}{end}'
```

查看前一个容器日志：

```bash
kubectl logs -n dominos-mq kafka-kafka-2 \
  -c kafka \
  --previous \
  --timestamps
```

### 11.4 检查 Broker 日志

Broker 2：

```bash
kubectl logs -n dominos-mq kafka-kafka-2 \
  -c kafka \
  --since=1h \
  | grep -Ei \
  'ReplicaFetcher|Fetcher|dominos-apps|ISR|AlterPartition|timeout|disconnect|network|error|exception|failed'
```

Leader Broker 0：

```bash
kubectl logs -n dominos-mq kafka-kafka-0 \
  -c kafka \
  --since=1h \
  | grep -Ei \
  'dominos-apps-0|Shrinking ISR|Expanding ISR|ISR|broker 2|AlterPartition|error|timeout'
```

Leader Broker 1：

```bash
kubectl logs -n dominos-mq kafka-kafka-1 \
  -c kafka \
  --since=1h \
  | grep -Ei \
  'dominos-apps-2|Shrinking ISR|Expanding ISR|ISR|broker 2|AlterPartition|error|timeout'
```

### 11.5 检查节点资源

```bash
iostat -x 1 60
vmstat 1 60
dmesg -T | grep -Ei \
  'I/O error|timeout|reset|nvme|scsi|ext4|xfs'
```

重点对比：

```text
CPU Throttling
JVM GC Pause
磁盘 await
磁盘 %util
磁盘 aqu-sz
网络丢包
TCP 重传
Pod 重启次数
节点内存压力
```

### 11.6 完善监控指标

建议补充：

```text
UnderReplicatedPartitions
UnderMinIsrPartitionCount
ReplicationBytesInPerSec
ReplicationBytesOutPerSec
ReplicaFetcherManager MaxLag
IsrShrinksPerSec
IsrExpandsPerSec
OfflinePartitionsCount
ActiveControllerCount
JVM GC Pause
CPU Throttling
磁盘 await
磁盘队列长度
网络丢包和 TCP 重传
```

---

## 十二、最终结论

本次 Kafka 副本未同步告警的直接原因是：

> Broker 2 上的多个 Follower 副本在一段时间内未能持续跟上 Leader，导致 Broker 2 被移出 `dominos-apps` 多个分区的 ISR。

Broker 2 后续 ReplicaFetcher 线程持续工作，部分分区已确认逐步追平 Leader 并重新加入 ISR。

检查时 Kafka 日志目录正常，副本 `offsetLag=0`，Replication Bytes In/Out 总量基本匹配，未发现持续性复制带宽不足、日志目录损坏、Partition Offline 或数据丢失证据。

当前可以确定的是 Broker 2 曾发生短时同步异常，但最初触发因素尚未完全确认。后续应重点结合告警时段的以下数据继续定位：

```text
Broker 2 Pod 重启记录
CPU Throttling
JVM GC Pause
磁盘 await、%util 和 aqu-sz
Replication Bytes In 瞬时变化
节点网络丢包和 TCP 重传
```

现阶段建议将根因定性为：

> Broker 2 短时资源抖动、进程停顿或 Broker 间通信异常，导致多个 Follower 副本退出 ISR；具体触发因素仍需结合节点及 JVM 历史监控进一步确认。

