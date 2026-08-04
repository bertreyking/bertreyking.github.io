# RabbitMQ 无法路由消息问题根因报告

## 1. 问题现象

RabbitMQ 管理页面出现以下指标：

```text
Unroutable (drop) 66/s
```

该指标表示当时平均每秒约有 66 条消息因无法匹配到有效路由而被 RabbitMQ 直接丢弃。

原有 Prometheus 告警只能统计无法路由消息总量，无法定位具体的：

* VHost
* Exchange
* 消息处理结果

同时，RabbitMQ 已经暴露 Exchange 级详细指标，但 Prometheus 中无法查询到，导致 Exchange 级告警无法正常触发。

---

## 2. 环境信息

RabbitMQ 版本：

```text
RabbitMQ 4.1.0
```

Prometheus 插件版本：

```text
rabbitmq_prometheus 4.1.0
```

RabbitMQ 详细指标接口：

```text
/metrics/detailed
```

Exchange 指标组：

```text
family=exchange_metrics
```

---

## 3. 排查过程

### 3.1 确认 RabbitMQ 支持 Exchange 详细指标

通过以下命令直接访问 RabbitMQ Prometheus 接口：

```bash
curl -sS \
  'http://<RabbitMQ-Pod-IP>:15692/metrics/detailed?family=exchange_metrics'
```

接口正常返回以下指标：

```text
rabbitmq_detailed_exchange_messages_published_total
rabbitmq_detailed_exchange_messages_confirmed_total
rabbitmq_detailed_exchange_messages_unroutable_returned_total
rabbitmq_detailed_exchange_messages_unroutable_dropped_total
```

说明 RabbitMQ 端已经正常暴露 Exchange 级详细指标。

---

### 3.2 定位异常 Exchange

在 `dominos-uat` VHost 下发现：

```text
rabbitmq_detailed_exchange_messages_published_total{
  vhost="dominos-uat",
  exchange="DELAY_EXCHANGE"
} 5776545
```

同时：

```text
rabbitmq_detailed_exchange_messages_unroutable_dropped_total{
  vhost="dominos-uat",
  exchange="DELAY_EXCHANGE"
} 5776545
```

该节点历史累计数据表明：

* 发布到 `DELAY_EXCHANGE` 的消息数量：`5,776,545`
* 无法路由并被丢弃的消息数量：`5,776,545`

即该统计周期内，发布到 `DELAY_EXCHANGE` 的消息全部未成功路由到队列。

默认 Exchange 也存在少量历史无法路由消息：

```text
rabbitmq_detailed_exchange_messages_unroutable_dropped_total{
  vhost="dominos-uat",
  exchange=""
} 167
```

其中：

```text
exchange=""
```

表示 RabbitMQ 默认 Exchange。

---

### 3.3 检查 Prometheus ServiceMonitor

ServiceMonitor 已配置详细指标接口：

```yaml
path: /metrics/detailed
```

同时配置了 Exchange 指标组：

```yaml
params:
  family:
    - queue_consumer_count
    - queue_coarse_metrics
    - exchange_metrics
```

但 ServiceMonitor 中还配置了以下指标过滤规则：

```yaml
metricRelabelings:
  - action: keep
    sourceLabels:
      - __name__
    regex: rabbitmq_detailed_queue_consumers|rabbitmq_detailed_queue_messages|queue_consumer_count|queue_coarse_metrics
```

该规则使用：

```yaml
action: keep
```

表示只保留符合正则表达式的指标，其余指标全部在写入 Prometheus 前被过滤。

由于正则中未包含：

```text
rabbitmq_detailed_exchange_messages_unroutable_dropped_total
rabbitmq_detailed_exchange_messages_unroutable_returned_total
```

因此 RabbitMQ 虽然正常返回了指标，但 Prometheus 将这些指标过滤掉了。

---

## 4. 根因分析

### 4.1 监控告警无法触发的根因

ServiceMonitor 的 `metricRelabelings` 过滤规则未包含 Exchange 级详细指标。

因此导致：

* Prometheus 查询不到 Exchange 无法路由指标；
* Exchange 级无法路由告警无法触发；
* 告警中无法显示具体 VHost 和 Exchange；
* 无法快速定位异常消息发生在哪个交换机。

这是本次监控告警失效的直接根因。

---

### 4.2 RabbitMQ 消息无法路由的可能根因

无法路由消息主要集中在：

```text
VHost：dominos-uat
Exchange：DELAY_EXCHANGE
```

最可能的原因包括：

1. 生产者使用的 `routing key` 与 Exchange 的 `binding key` 不匹配；
2. 消息发送时 Exchange 未绑定有效队列；
3. 目标队列当时不存在或已被自动删除。

由于生产者未设置：

```text
mandatory=true
```

RabbitMQ 在没有找到匹配队列时，直接将消息丢弃，而没有退回给生产者。

---

## 5. 处理措施

### 5.1 修复 Prometheus 指标过滤规则

已调整 ServiceMonitor，允许以下指标进入 Prometheus：

```text
rabbitmq_detailed_exchange_messages_unroutable_dropped_total
rabbitmq_detailed_exchange_messages_unroutable_returned_total
```

推荐直接删除不必要的 `metricRelabelings`，通过 `family` 参数控制采集范围：

```yaml
spec:
  endpoints:
    - interval: 30s
      path: /metrics/detailed
      port: prometheus
      scheme: http
      scrapeTimeout: 30s
      params:
        family:
          - queue_consumer_count
          - queue_coarse_metrics
          - exchange_metrics
```

如果必须保留过滤规则，可使用：

```yaml
metricRelabelings:
  - action: keep
    sourceLabels:
      - __name__
    regex: 'rabbitmq_detailed_(queue_.*|exchange_messages_.*)'
```

---

### 5.2 新增 Exchange 级无法路由告警

告警规则通过以下指标进行判断：

```text
rabbitmq_detailed_exchange_messages_unroutable_dropped_total
rabbitmq_detailed_exchange_messages_unroutable_returned_total
```

告警可展示以下标签：

```text
cluster_name
namespace
pod
vhost
exchange
unroutable_type
```

其中：

| 标签                         | 含义            |
| -------------------------- | ------------- |
| `vhost`                    | RabbitMQ 虚拟主机 |
| `exchange`                 | 发生无法路由消息的交换机  |
| `unroutable_type=dropped`  | 消息无法路由并被直接丢弃  |
| `unroutable_type=returned` | 消息无法路由并退回生产者  |

---

## 6. 当前状态判断

RabbitMQ 的以下指标属于 Counter：

```text
rabbitmq_detailed_exchange_messages_unroutable_dropped_total
```

历史累计值不会因为问题恢复而自动归零。

因此，不能仅根据当前累计值判断问题是否仍然存在。

应通过以下 PromQL 判断最近 5 分钟是否有新增无法路由消息：

```promql
increase(
  rabbitmq_detailed_exchange_messages_unroutable_dropped_total[5m]
)
```

如果查询结果为：

```text
0
```

表示最近 5 分钟没有新增无法路由并被丢弃的消息。

当前该指标已无新增，说明无法路由问题已经停止。

---

## 7. 关于 DELAY_EXCHANGE Binding 数量较多

指标：

```text
rabbitmq_cluster_exchange_bindings
```

表示 Exchange 当前的 Binding 数量，不是解绑次数，也不是无法路由消息数量。

`DELAY_EXCHANGE` Binding 较多，通常是因为：

* 多个延迟队列共用同一个 Exchange；
* 不同业务使用不同 routing key；
* 同一个队列配置了多个 Binding；
* 多个应用共用统一延迟消息交换机。

只要 Binding 数量稳定，且无法路由消息增量为 0，一般不属于异常。

判断逻辑如下：

```text
无法路由消息 > 0，Binding = 0
```

说明 Exchange 没有绑定有效队列。

```text
无法路由消息 > 0，Binding > 0
```

说明更可能是 `routing key` 与 `binding key` 不匹配。

```text
无法路由消息 = 0，Binding 较多且稳定
```

说明当前路由关系正常。

---

## 8. 存在的监控限制

当前 Exchange 级指标只能定位到：

* RabbitMQ 集群
* Pod
* VHost
* Exchange
* 消息是被丢弃还是退回

无法直接获取：

* 具体生产者应用；
* 客户端 IP；
* routing key；
* 消息内容；
* message ID；
* 生产者连接名称。

Binding 指标也只能说明 Exchange 与 Queue 的绑定关系，不能直接定位具体生产者。

---

## 9. 后续优化建议

1. 保留 Exchange 级无法路由告警，持续监控 `dropped` 和 `returned`；
2. 生产者统一设置 `mandatory=true`；
3. 在生产者中实现 Return Callback；
4. Return Callback 日志中记录：

   * Exchange
   * routing key
   * message ID
   * reply code
   * reply text
5. RabbitMQ 客户端设置明确的 Connection Name；
6. 不同应用尽量使用独立 RabbitMQ 用户；
7. 必要时采集 `channel_exchange_metrics`，辅助定位产生无法路由消息的 Channel；
8. 修改 Insight 或 Operator 的配置源，避免手工修改 ServiceMonitor 后被控制器覆盖；
9. 定期检查 `DELAY_EXCHANGE` 的 Binding 数量变化，避免应用持续创建无效 Binding。

---

## 10. 最终结论

本次问题包含两个层面。

### 监控层面

ServiceMonitor 的 `metricRelabelings` 使用了 `action: keep`，但正则表达式未包含 Exchange 级详细指标，导致 RabbitMQ 已暴露的 Exchange 指标被 Prometheus 过滤，告警无法触发。

### 业务层面

`DELAY_EXCHANGE` 历史上存在大量消息无法匹配有效路由，并因生产者未设置 `mandatory=true` 被直接丢弃。

最可能的原因是：

* `routing key` 与 `binding key` 不匹配；
* 或消息产生时 Exchange 没有绑定有效队列。

目前 Exchange 详细指标已经正常进入 Prometheus，且最近未再出现新增无法路由消息，当前问题已恢复。

