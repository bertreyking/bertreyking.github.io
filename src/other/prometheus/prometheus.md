# Prometheus

## Prometheus 是什么？

[Prometheus](https://github.com/prometheus) 是一个开源系统监控和告警工具，目前是一个独立开源的项目，2016年之后加入 CNCF。其通过指标搜集性能数并存为时间序列数据。

## 特点

- 具有指标、标签键值对、时间序列数据的多维数据模型
- 具有 PromQl 灵活的查询语言
- 单节点部署数据落盘、也可使用远端存储存放监控数据
- 通过 HTTP 的 pull 搜集监控数据(默认)
- 通过 pushgateway 中间 push 数据到 Prometheus Server
- 多种服务发现模式(动态/静态)
- 内嵌图形和支持 Grafana 对性能数据进行展示

## Metrics 是什么？

- web 服务器下，你的指标可能是请求时间、成功/失败率.等
- db 服务器，你的指标可能是读/写io、延迟.等

## 架构

![Prometheus](.../png/prometheus-architecture.png)

## 组件

- Prometheus Server 负责搜集和存储 pull/push 模式的数据
  - PromQL
  - Rule
  - ServiceDiscovery
    - 动态
    - 静态
- Exporter 负责通过 metrics 采集应用/主机上的性能数据
- Pushgateway 负责将短时间/间歇性运行的 exporter 的数据 push 给 Prometheus Server
- Alertmanager 负责将触发的告警条目通过 mail、企业微信等多种方式发送给组织进行警示
- Grafana 负责对接Prometheus 数据源，通过各种模型数据和 Query 将数据以友好形式展示出来

## 场景

- Docker、Kubernetes
- Linux 
- 应用系统 (需要具备开发能力，可根据应用自定义 metrics)
- Windows (不太友好)
