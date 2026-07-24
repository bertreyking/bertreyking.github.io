# SkyWalking Metrics 索引异常排查报告

## 一、问题概述

2026 年 7 月 24 日，Java 应用重启后，SkyWalking UI 中无法正常看到原有服务及实例信息。

同时，SkyWalking OAP 持续出现以下告警：

```text
Metric: service_cpm values size is not equal to duration points size,
metrics values size: 0, duration points size: 31

Metric: service_instance_cpm values size is not equal to duration points size,
metrics values size: 0, duration points size: 31
```

涉及的主要指标包括：

```text
service_cpm
service_sla
service_apdex
service_resp_time
service_instance_cpm
service_instance_sla
service_instance_resp_time
```

从界面现象看，问题一度表现为 Java 应用重启后未成功注册到 SkyWalking。

---

## 二、问题发生前的变更

2026 年 7 月 23 日，为释放 Elasticsearch 存储空间，人工删除了部分 SkyWalking 历史索引。

删除的 Trace 索引包括：

```text
sw_segment-20260721
sw_segment-20260722
```

删除的 Metrics 索引包括：

```text
sw_metrics-all-20260717
sw_metrics-all-20260718
sw_metrics-all-20260719
sw_metrics-all-20260720
sw_metrics-all-20260721
sw_metrics-all-20260722
```

删除后，部分历史 Metrics 索引再次被创建，但索引内文档数为 0：

```text
sw_metrics-all-20260720    docs.count=0
sw_metrics-all-20260721    docs.count=0
sw_metrics-all-20260722    docs.count=0
```

当前日期的 Metrics 索引仍在正常写入：

```text
sw_metrics-all-20260723    docs.count=12438965    size=4.6GB
sw_metrics-all-20260724    docs.count=2524054     size=1GB
```

---

## 三、排查过程

### 3.1 Java Agent 加载正常

Java Agent 日志中可见：

```text
SkyWalking agent version:
8.16.0-dominos-1.0.0-SNAPSHOT
```

Agent 启动后虽然短暂处于：

```text
DISCONNECT
```

但随后正常选择 OAP Collector，并建立 gRPC 通道。

由此可以确认：

- Java Agent 已正常加载；
- Java 启动参数中的 `-javaagent` 已生效；
- Agent 插件初始化正常。

---

### 3.2 Agent 到 OAP 的通信链路正常

Agent 已成功连接 OAP：

```text
skywalking-skywalking-helm-oap.skywalking.svc.cluster.local:11800
```

Agent 向 OAP 上报 Event 数据时，返回：

```text
HTTP status: 200
grpc-status: 0
```

Agent 上报 JVM Metrics 时，同样返回：

```text
HTTP status: 200
grpc-status: 0
```

其中：

```text
grpc-status: 0
```

表示 gRPC 请求处理成功。

因此可以排除：

- Java Agent 未加载；
- OAP 地址配置错误；
- Kubernetes DNS 异常；
- Java Pod 到 OAP 11800 端口不通；
- OAP gRPC 服务不可用；
- Agent 上报被 OAP 拒绝。

结论：

```text
Java Agent → OAP
```

链路正常。

---

### 3.3 当前 Metrics 写入正常

`sw_metrics-all-20260724` 已持续写入数据，说明以下链路正常：

```text
Java Agent
    ↓
OAP 11800
    ↓
Metrics 聚合
    ↓
Elasticsearch
```

因此可以确认：

- 当前 Metrics 数据仍在持续写入；
- OAP 到 Elasticsearch 的存储链路正常；
- 问题不是 Metrics 全局停止写入；
- 问题不是 Java 应用真正无法上报。

---

### 3.4 当前时间查询仍返回空指标

本次在 SkyWalking UI 中查看的是当前时间范围，并未主动查询已删除日期的历史数据。

但 OAP 仍持续出现：

```text
metrics values size: 0
duration points size: 31
```

这里的：

```text
duration points size: 31
```

表示当前查询时间窗口被划分为 31 个采样点，并不代表查询了 31 天，也不能据此判断查询范围包含历史日期。

因此，本次告警不能简单解释为：

> UI 查询了已经被删除的历史数据。

结合实际现象，更符合情况的解释是：

- 人工删除 `sw_metrics-all-*` 索引后，OAP 对 Metrics 索引集合的识别或查询出现异常；
- 即使查询的是当前时间，OAP 仍无法正常获得服务、实例及对应指标；
- 最终表现为服务列表消失、实例不可见以及当前指标查询为空。

---

### 3.5 OAP 出现 Alias 获取失败

OAP 日志中发现：

```text
AliasClient - Failed to get indices by alias sw_metrics-all
```

该日志说明 OAP 在通过：

```text
sw_metrics-all
```

获取关联 Metrics 索引时发生失败。

虽然没有单独删除 Alias，但删除 Elasticsearch Index 时，该 Index 与 Alias 的关联关系也会同步移除。

结合以下现象：

- 人工删除了多个 `sw_metrics-all-*` Index；
- OAP 出现 `Failed to get indices by alias sw_metrics-all`；
- 原有服务和实例在 SkyWalking UI 中消失；
- 部分历史 Index 后续被重新创建为空索引；
- 当前日期 Index 仍可正常写入；

可以判断，人工删除操作造成了 SkyWalking Metrics 索引集合及 Alias 查询状态的阶段性异常。

现有日志能够确认 Alias 获取曾失败，但不足以证明 Alias 被永久损坏。

---

## 四、根因分析

### 4.1 已确认事实

本次排查已确认：

1. Java Agent 正常加载；
2. Agent 到 OAP 的 gRPC 链路正常；
3. Event 和 JVM Metrics 上报成功；
4. OAP 返回 `grpc-status: 0`；
5. 当前日期 Metrics Index 持续写入；
6. 异常发生前人工删除了多个 `sw_metrics-all-*` Index；
7. 删除后 OAP 出现：

```text
Failed to get indices by alias sw_metrics-all
```

8. 删除后原有服务和实例无法在 UI 中正常显示；
9. 部分被删除的历史 Metrics Index 被重新创建为空索引。

---

### 4.2 根因判断

本次问题的直接诱因是：

> 人工删除 SkyWalking 自主管理的 `sw_metrics-all-*` 历史 Index。

删除操作一方面造成历史 Metrics 数据永久丢失，另一方面影响了 OAP 对 `sw_metrics-all` 索引集合的识别和查询。

在此期间，OAP 曾无法通过 `sw_metrics-all` Alias 正常获取关联索引，导致 SkyWalking UI 无法正常加载原有服务、实例及当前指标信息。

因此，即使查询的是当前时间范围，也会出现：

```text
metrics values size: 0
duration points size: 31
```

并表现为：

- 原有服务列表消失；
- Java 应用重启后看不到新实例；
- 当前服务指标为空；
- 界面上类似应用未注册。

---

### 4.3 更准确的故障描述

本次问题不应描述为：

> Java 应用重启后无法注册 SkyWalking。

更准确的描述是：

> Java Agent 已正常连接 OAP 并持续上报数据，但人工删除 `sw_metrics-all-*` Index 后，OAP 对 Metrics 索引集合及 Alias 的查询出现阶段性异常，导致 SkyWalking UI 无法正常展示原有服务、实例及当前指标，从界面表现上类似应用未注册。

---

### 4.4 故障链路

```text
人工删除 sw_metrics-all-* Index
        ↓
历史 Metrics 数据丢失
        ↓
Index 与 Alias 的关联关系发生变化
        ↓
OAP 获取 sw_metrics-all 关联索引失败
        ↓
服务、实例及当前 Metrics 查询异常
        ↓
SkyWalking UI 中原有服务和实例消失
        ↓
当前时间查询返回 values size=0
        ↓
表现为 Java 应用未注册或无数据
```

---

## 五、处理方案

### 5.1 调整 Metrics TTL

SkyWalking OAP 配置文件中：

```yaml
metricsDataTTL: ${SW_CORE_METRICS_DATA_TTL:7}
```

其中：

```text
7
```

只是默认值。

OAP Deployment 已增加：

```yaml
- name: SW_CORE_METRICS_DATA_TTL
  value: "3"
```

因此实际生效配置为：

```text
metricsDataTTL=3 天
```

增加该环境变量并完成 OAP Pod 滚动更新后，SkyWalking 已能够自动删除超过 3 天保留周期的 Metrics Index。

处理流程如下：

```text
修改 OAP Deployment
    ↓
增加 SW_CORE_METRICS_DATA_TTL=3
    ↓
滚动更新 OAP Pod
    ↓
OAP 加载 metricsDataTTL=3
    ↓
SkyWalking TTL 任务执行
    ↓
自动删除超过保留周期的 Metrics Index
```

---

### 5.2 停止人工删除 SkyWalking Index

后续不再人工执行：

```bash
DELETE sw_metrics-all-*
```

也不建议使用：

```bash
DELETE sw*
```

SkyWalking 对 Elasticsearch Index 有自身的：

- Alias 管理；
- 时间分片管理；
- TTL 管理；
- Mapping 管理；
- 索引初始化和维护逻辑。

人工删除可能造成：

- 历史 Metrics 数据丢失；
- Alias 查询异常；
- 服务和实例列表异常；
- 空 Index 被重新创建；
- OAP 持续出现 MQE WARN。

---

### 5.3 历史数据缺失期间的查询建议

历史 Metrics 数据已经被人工删除，无法通过重新创建空 Index 恢复。

在历史数据缺失期间，SkyWalking UI 建议优先查看：

```text
最近 15 分钟
最近 1 小时
最近 24 小时
```

用于确认当前服务、实例和指标是否恢复正常。

---

## 六、处理结果

当前状态如下：

```text
Java Agent                  正常
Agent → OAP 11800           正常
OAP gRPC 接收               正常
OAP → ES 当前 Metrics 写入  正常
当前 Metrics Index          正常增长
历史 Metrics 数据           部分已人工删除，无法直接恢复
Alias 获取                  删除后曾出现阶段性失败
Metrics TTL                 已调整为 3 天
历史 Index 清理             已由 SkyWalking 自动执行
Java 应用是否需要重启       不需要
```

---

## 七、后续措施

1. SkyWalking Metrics Index 统一通过 `SW_CORE_METRICS_DATA_TTL` 管理，不再人工删除。

2. 如需调整数据保留周期，统一修改 OAP Deployment 中的 TTL 环境变量。

3. 索引清理前必须确认：

   - Index 类型；
   - Index 日期；
   - 是否仍处于 SkyWalking TTL 管理范围；
   - Alias 关联关系；
   - 删除后对服务、实例、Metrics 和 Trace 查询的影响。

4. 增加以下监控项：

   - Metrics Index 每日增长量；
   - 当前日期 Index 文档增长速率；
   - OAP Alias 查询失败；
   - OAP MQEVisitor WARN；
   - Elasticsearch Bulk 写入失败；
   - TTL 清理执行结果。

---

## 八、最终结论

> 本次异常不是 Java Agent 注册失败。Java Agent 到 OAP 的 gRPC 链路以及当前 Metrics 写入均正常。根因是人工删除 SkyWalking 管理的 `sw_metrics-all-*` Index 后，历史数据丢失，并造成 OAP 对 `sw_metrics-all` 索引集合及 Alias 的获取出现阶段性异常，最终导致 SkyWalking UI 无法正常展示原有服务、实例和当前指标。现已通过 `SW_CORE_METRICS_DATA_TTL=3` 将 Metrics 保留周期调整为 3 天，并验证 SkyWalking 能够自动清理超过保留周期的历史 Index。后续统一使用 SkyWalking TTL 机制管理索引生命周期。
