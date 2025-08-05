# Summary

[前言](README.md)
---

# 开源组件

- [Kubernetes (k8s)]()
  - [安装]()
    - [Kubeadm 安装 k8s1.28.1](kubernetes/k8s-install-doc.md)
    - [Dashboard](kubernetes/kubernetes-dashabord.md)
  - [资源]()
    - [Cronjob 使用](kubernetes/cronjob.md)
    - [Probe 使用](kubernetes/liveness_readiness_startup.md)
    - [ConfigMap 使用](kubernetes/Configmap.md)
  - [故障排查]()
    - [Kubelet PLEG](kubernetes/kubelet-pleg-error.md)
    - [podman 容器数据软链](kubernetes/podman_containers_data_ln.md)
  - [优化]()
    - [Kubelet 资源限制](kubernetes/kubeletResourcesmgmt.md)
    - [LimitRange](kubernetes/limitrange.md)
    - [RBAC 汇总]()
      - [交互式生成 kubeconfig 文件](kubernetes/gen_rbac.md)
      - [合并多个 kubeconfig 文件](kubernetes/rbac_kubeconfig_used.md)
      - [API 接口创建](kubernetes/api_rbac_create.md)
  - [存储]()
    - [nfs](kubernetes/nfs-csi.md)
  - [API](kubernetes/api-doc.md)
  - [LeaderWorkSet]()
    - [lws](other/models/lws_api.md)
- [K3s (轻量型 k8s)](k3s/k3s-架构篇.md)
  - [安装](k3s/k3s-安装篇.md)

- [ClusterPedia](clusterpedia/ClusterPedia-概念介绍.md)
  - [ClusterPedia 安装步骤](clusterpedia/ClusterPedia-安装步骤-v0.6.3.md)
  - [ClusterPedia 对接 k8s](clusterpedia/ClusterPedia-对接-k8s.md)

- [Prometheus](other/prometheus/prometheus.md)
  - [vmetrics+prometheus 安装](other/prometheus/victoriametrics_install.md)
  - [配置]()
  - [使用](other/prometheus/prometheus_usege.md)
    - [常用函数](other/prometheus/prometheus-query.md)
    - [标签自定义配置](other/prometheus/relabel_configs.md)
    - [Grafana 模版变量](other/prometheus/grafana.md)
    - [Grafana 自定义配置](other/prometheus/grafana_subpath.md)
  - [故障排查](other/prometheus/troubleshooting.md)
    - [kubelet Job 丢失](other/prometheus/kubelet-job-missing.md)
  - [AI 生成]()
    - [deepseek-r1](other/prometheus/deepseek-metrics-data-storage.md)
    - [chatgpt](other/prometheus/openai-metrics-data-storage.md)

- [Elastic](other/elastic/elastic.md)

- [Skywalking](other/skywalking/what_is_skywalking.md)
  - [安装](other/skywalking/skywalking_install.md)

- [NeuVector](other/neuvector/what_is_neuvector.md)
  - [安装](other/neuvector/neuvector_install.md)

- [Gitlab]()
  - [安装](other/gitlab/gitlab_install.md)
    - [operator_install_gitlab](other/gitlab/operator_install_gitlab.md)
    - [gitlab_subpath](other/gitlab/gitlab_subpath.md)
  - [Git 克隆 master 分支后将修改推送 dev 分支](other/gitlab/gitmaster-todev.md)

- [Helm]()
  - [helm 使用](kubernetes/helm_use.md)

- [Harbor]()
  - [docker 安装](other/harbor/harbor-install-doc.md)
  - [k8s 安装](other/harbor/harbor-install.md)
  - [docker 融合镜像](other/harbor/docker-multi-arch.md)
- [Image-syncer 使用](other/imagesyncer/image-syncer.md)
---

# [CICD]()

- [Jenkins 学习]()
  - [通过 Github 自动构建镜像(CI)](other/jenkins/autobuildimg.md)
  - [Nexus](other/jenkins/nexus-used.md)
# [自动化运维工具]()

- [Ansible]()
  - [Ansible 使用](ansible/ansible.md)
---

# 操作系统

- [Linux]()
  - [性能分析]()
    - [上下文切换](linux/cpu_上下文切换.md)
    - [负载分析](linux/cpu_Load_Average分析.md)
  - [系统配置]()
    - [bonding](linux/bonding.md)
    - [fs_quota](linux/filesystem-quota.md)
  - [Chrony 时钟同步]()
    - [chrony](linux/chronyd_sync.md)
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
    - [统计文件数及目录大小](linux/countfile_size.md)
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
  - [配置管理](python/python_configmgmt.md)
    - [获取环境变量](python/python_getenv.md)
    - [读取配置文件](python/python_getconfig.md)
  - [Flask](python/restful_api_doc.md)
    - [镜像同步]()
      - [设计文档]()
      - [流程图]()
      - [接口文档]()
      - [测试文档]()
      - [构建部署文档]()
---

