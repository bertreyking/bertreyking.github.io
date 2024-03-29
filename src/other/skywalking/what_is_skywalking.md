# 什么是 skywalking (数据来源 OpenAI) ？

## 介绍

- SkyWalking 是一个开源的应用性能监控系统
- 由 Apache 软件基金会孵化，并成为 Apache 孵化器的顶级项目
- SkyWalking 的目标是帮助开发人员监控、诊断和优化分布式系统的性能和健康状况

## 特性

- SkyWalking 提供了一种分布式追踪解决方案
  1. 可以追踪和监控分布式应用程序中的各个组件之间的调用和交互
  2. 通过插入特定的代理或 SDK 到应用程序中，来收集关于请求流经系统的详细信息，
     - 包括服务间调用、
     - 数据库访问
     - 消息队列等
  3. 这些信息可以用于分析应用程序性能、识别瓶颈和故障，并提供可视化的监控仪表板和警报系统。
  4. SkyWalking 还提供了一些附加功能
     - 应用程序拓扑图
     - 性能指标收集
     - 分布式日志跟踪等
- 它支持多种编程语言和框架，包括 Java、.NET、Node.js、Go、Python 等，可以适用于各种分布式系统和微服务架构。总之 SkyWalking 是一个用于监控和诊断分布式应用程序性能的开源工具，它可以帮助开发人员更好地理解和优化复杂的分布式系统。

## 核心组件

- Collector：Collector 是 SkyWalking 的数据收集器
  1. 负责接收和处理来自应用程序的跟踪数据
  2. 可以通过配置多个实例以实现高可用性和负载均衡

- Storage：Storage 组件用于接收和存储从 Collector 收集到的跟踪数据和指标数据
  1. 支持多种存储后端
     - Elasticsearch、
     - MySQL、
     - H2 等

- UI：UI 组件提供了一个用户界面，用于展示和查询监控数据。可以通过 UI 组件查看应用程序的拓扑图、性能指标、调用链追踪等信息。

- Probe：Probe 组件是用于与应用程序集成的代理或 SDK。它负责在应用程序中收集跟踪数据，并将其发送给 Collector 进行处理和存储。

- 除了这些核心组件之外，SkyWalking 还提供了一些可选的扩展组件和插件，用于增强功能和支持特定的场景

  例如：

  1. Alarm：Alarm 组件提供了警报功能，可以基于自定义的规则和阈值触发警报，帮助用户及时发现和解决潜在的问题。
  2. Analysis：Analysis 组件提供了数据分析功能，可以对跟踪数据和指标数据进行统计和分析，帮助用户理解应用程序的性能状况和趋势。
  3. Plugin：Plugin 组件是一种可扩展机制，允许用户根据需要添加自定义的插件，以支持特定的框架、中间件或协议。

  需要注意的是，SkyWalking 的组件可以根据版本和配置的不同而有所变化。以上列出的是一些常见的组件，具体的组件列表和功能可以在官方文档或项目的 GitHub 页面中找到。