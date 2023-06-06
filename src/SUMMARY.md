# Summary

[前言](README.md)
---

# 开源组件

- [Kubernetes (k8s)]()
  - [Cronjob 使用](kubernetes/cronjob.md)
  - [Probe 使用](kubernetes/liveness_readiness_startup.md)
  - [ConfigMap 使用](kubernetes/Configmap.md)
- [K3s (轻量型 k8s)](k3s/k3s-架构篇.md)
  - [安装](k3s/k3s-安装篇.md)

- [ClusterPedia](clusterpedia/ClusterPedia-概念介绍.md)
  - [ClusterPedia 安装步骤](clusterpedia/ClusterPedia-安装步骤-v0.6.3.md)
  - [ClusterPedia 对接 k8s 集群](clusterpedia/ClusterPedia-对接-k8s.md)

- [Prometheus](other/prometheus/prometheus.md)
  - [安装]()
  - [配置]()
  - [使用](other/prometheus/prometheus_usege.md)
    - [常用函数](other/prometheus/prometheus-query.md)
    - [标签自定义配置](other/prometheus/relabel_configs.md)
    - [Grafana 模版变量](other/prometheus/grafana.md)
  - [故障排查](other/prometheus/troubleshooting.md)
    - [kubelet Job 丢失](other/prometheus/kubelet-job-missing.md)

- [Skywalking](/other/skywalking/what_is_skywalking.md)
  - [安装](other/skywalking/skywalking_install.md)

- [Image-syncer 使用](other/imagesyncer/image-syncer.md)
---

# [自动化运维工具]()

- [Ansible]()
  - [Ansible 使用](ansible/ansible.md)
---

# 操作系统

- [Linux]()
  - [性能分析]()
    - [上下文切换](linux/cpu_上下文切换.md)
    - [负载分析](linux/cpu_Load_Average分析.md)

  - [DNS](linux/dns.md)
  - [命令手册]()
    - [Echo 自定义输出](linux/echo定制脚本输出颜色.md)
    - [Json 文本处理](linux/json_jq.md)
    - [查找大文件](linux/linux_find_du_mv_delete.md)
    - [Iptables 使用](linux/iptables.md)
    - [Tcpdump 使用](linux/tcpdump.md)
  - [Shell](linux/shell.md)
    - [条件判断](linux/shell_condition.md)
    - [特殊变量](linux/shell_variable.md)
  - [窥探容器]()
    - [自定义容器路由](linux/container_addroutes.md)
    - [通过 Pid 查找 ContainerID](linux/pidstat_vs_ps.md)
    - [tc 模拟网络延迟](linux/container_use_tc.md)
  - [故障排查](linux/troubleshooting.md)
    - [断电导致系统启动失败](linux/startupFailed.md)
---

# 语言
 
- [Python]()
  - [控制语句](python/流程控制语句.md)
  - [读写文件](python/python读写文件.md)
  - [包使用]()
    - [DockerSDK 使用](python/docker_sdk_used.md)
    - [Request 使用](python/requests.md)
---

