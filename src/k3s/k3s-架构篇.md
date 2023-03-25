# k3s 架构

## 架构

![image-20230323142110363](src/png/image-20230323142110363.png)

## 组件

### 角色

- server
- agent

两者的通信是通过 tunnel proxy 来完成，它们有大量的通信，均会通过 tunnel proxy 设置对应连接和端口

### 组件(所有组件一个进程一起运行，90s一个单节点集群)

- kubelet
- api-server
- controller-manager
- scheduler
- kube-proxy

通过 tunnel proxy 来完成和 api-server 的连接，tunnel 模式创建单向连接跟 api 进行通信，一旦建立链接便会创建双向连接，通过使用单个端口进行通信来确保连接安全(长连接)

- sqlite
  1. 单节点 server，推荐使用
  2. 高可用模式下，推荐使用其它外部存储
- flannel

flannel 与 kubelet 建立连接，而 kubelet 又与 containerd 通信，并最终由 containerd 来跟 集群中的 pod 建立连接

- containerd/runc(支持 docker，部署集群时支持 args 选择)
- traefik
- coredns
- local-path-provisioner
- helm-controller

## 差异

- k3s：k8s 遗留、非默认功能、以及处于 alpha 的功能均被删除(Rancher 表示删除 30 亿行 code)

## 优势

- 体积小、简化安装，一个单节点集群，只需 90s 即可启动完成。多节点集群需要约3条名称来完成集群的创建。(对硬件设备的要求低，适合物联网、边缘计算场景下的客户)
- 支持 helm 和 manifst 清单，只需将 yaml 放入对应目录，k3s 启动时会扫描 helm 介质和 ymal 目录来完成集群/应用的启动(边缘计算硬需求)
- 集群节点的新增和删除用一条命令完成
- 简单的集群配置

## 兼容矩阵

| k3s                               | 系统                                                         | 芯片                               |
| --------------------------------- | :----------------------------------------------------------- | ---------------------------------- |
| k3s-1.26.1-k3s1 、k3s-1.25.1-k3s1 | rhel 8.4～8.7、rocky linux 8.4～8.7Ubuntu 、18.04\20.04\22.04 | x86_64、arm64/aarch64、armv7、s390 |
| k3s-1.24.10-k3s1                  | rhel 8.4～8.7、rocky linux 8.4～8.7、Ubuntu 18.04\20.04\22.04、centos7.9 | x86_64、arm64/aarch64、armv7、s390 |

## 安装参数搜集

### 单节点

- --write-kubeconfig-mode 6444            # 默认 kubeconfig 文件仅 root 可读，其它用户可读需要加上该参数

### 多节点

- K3S_URL=https://127.0.0.1:6443        # 节点接入时需要提供集群的入口地址 
- K3S_TOKEN=$node-toekn                  # 节点接入时需要提供集群的接入 token 信息

## 客户场景

封装小，硬件要求小、在树莓派上都可以轻松运行，而且 k3s 对于制作单个应用程序的集群非常高效

- 边缘计算
- 嵌入式系统
- 物联网

## 参考文档

- [Everything You Need to Know about K3s: Lightweight Kubernetes for IoT, Edge Computing, Embedded Systems & More](https://mattermost.com/blog/intro-to-k3s-lightweight-kubernetes/)



