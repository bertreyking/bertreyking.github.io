# SpiderPool 学习笔记

## 什么是 SpiderPool 

```shell
Spiderpool 是一个 IP 地址管理 (IPAM) 插件，可为容器云平台分配 IP 地址。 大部分的 Overlay CNI 都具备符合功能特性的 IPAM 组件，SpiderPool 的主要设计目标是搭配 Underlay CNI （例如 MacVLAN CNI、 VLAN CNI、 IPVLAN CNI等）进行 IP 的精细化管理。

Spiderpool 适用于任何能够对接第三方 IPAM 的 CNI 插件，尤其适合于一些缺失 IPAM 的 CNI， 包括 SRI-OV、 MacVLAN、 IPVLAN、 OVS-CNI 等。 而一些 overlay CNI 自带了 IPAM 组件，对 Spiderpool 需求相对较低。

Spiderpool 具备以下特点：
- CRD 设计，全面的状态和事件展示
- 应用绑定 ippool 具备多种渠道，包括 annotation 静态指定、annotation 智能分配、租户默认池、集群默认池、CNI 配置文件等
- ippool 的节点亲和性设置，帮助同一应用解决跨子网分配 IP 地址等特殊需求
- “应用固定 IP 地址范围” 场景的智能管理，包括智能创建 ippool、弹性扩缩容 IP 数量、智能回收 ippool 等
- 防止 IP 地址泄露的回收机制，避免 IP 浪费
- ipv4-only、ipv6-only 和 dual-stack 集群的支持
- statefulset 支持
- 配合 multus，在对多网卡场景下，支持不同网卡的进行独立指定 ippool
- 预留集群外部的 IP 地址，使得 IPAM 永不分配给 Pod 使用
- 路由定制
- 丰富的 metrics 度量指
```

## 组件部署([ui 安装](https://docs.daocloud.io/network/modules/spiderpool/install/)、[helm 安装](https://github.com/spidernet-io/spiderpool/blob/main/docs/usage/install.md))

```shell
- helm 启动 job 控制器来完成
[root@master01 ~]# kubectl get pod -n kube-system | grep -i spider 
helm-operation-install-spiderpoll-maweibing-wfr9m-kk42c      0/1     Completed   0             45h
helm-operation-install-spiderpool-maweibing-bn6k9-m75ml      0/1     Completed   0             44h
helm-operation-install-spiderpool-maweibing-qqlbk-sb6dr      0/1     Completed   0             44h
helm-operation-uninstall-spiderpoll-maweibing-47gxt-fk2nx    0/1     Completed   0             44h
helm-operation-uninstall-spiderpool-maweibing-8bw6m-gd7zs    0/1     Completed   0             44h

- spiderpool-agent 的 pod 由 daemonsets 控制器来完成 
spiderpool-agent-5r8kg                                       1/1     Running     1 (10h ago)   44h
spiderpool-agent-c2jgh                                       1/1     Running     1 (10h ago)   44h

- controller 由 deployment 控制器来完成
spiderpool-controller-5cc8487f48-mmrq9                       1/1     Running     0             44h
spiderpool-init                                              0/1     Completed   0             44h
```

## 配置文件(configmap 、secret )

```shell
- 这里是 spiderpool-controller 启动时依赖的一个 config 文件
[root@master01 ~]# kubectl get cm -n kube-system | grep -i spider 
spiderpool-conf                              1      44h
[root@master01 ~]# kubectl get cm -n kube-system spiderpool-conf -o yaml 
apiVersion: v1
data:
  conf.yml: |
    ipamUnixSocketPath: /var/run/spidernet/spiderpool.sock
    networkMode: legacy
    enableIPv4: true
    enableIPv6: false
    enableStatefulSet: true
    enableSpiderSubnet: true
    clusterDefaultIPv4IPPool: [default-v4-ippool]
    clusterDefaultIPv6IPPool: []
kind: ConfigMap
metadata:
  annotations:
    meta.helm.sh/release-name: spiderpool-maweibing
    meta.helm.sh/release-namespace: kube-system
  creationTimestamp: "2022-10-29T09:46:08Z"
  labels:
    app.kubernetes.io/component: spiderpool-controller
    app.kubernetes.io/instance: spiderpool-maweibing
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/name: spiderpool
    app.kubernetes.io/version: 0.3.0
    helm.sh/chart: spiderpool-0.3.0
  name: spiderpool-conf
  namespace: kube-system
  resourceVersion: "16777"
  uid: 4be2b8f2-12b9-464c-9ae0-fc51fd373a30
  
- 相关的证书文件
[root@master01 ~]# kubectl get secret -n kube-system | grep -i spider 
sh.helm.release.v1.spiderpool-maweibing.v1   helm.sh/release.v1   1      45h
spiderpool-controller-server-certs           kubernetes.io/tls    3      45h
```

## 以 CRD 形式定义 ipPool

```shell
- 查看
[root@master01 ~]# kubectl get crd | grep -i spider 
spiderendpoints.spiderpool.spidernet.io               2022-10-29T08:48:07Z
spiderippools.spiderpool.spidernet.io                 2022-10-29T08:48:07Z
spiderreservedips.spiderpool.spidernet.io             2022-10-29T08:48:07Z
spidersubnets.spiderpool.spidernet.io                 2022-10-29T08:48:07Z

- 查看IP子网、IP访问、IP使用信息
[root@master01 ~]# kubectl get spiderippools.spiderpool.spidernet.io -o yaml 
apiVersion: v1
items:
- apiVersion: spiderpool.spidernet.io/v1
  kind: SpiderIPPool
  metadata:
    creationTimestamp: "2022-10-29T09:46:19Z"
    finalizers:
    - spiderpool.spidernet.io
    generation: 1
    labels:
      ipam.spidernet.io/owner-spider-subnet: default-v4-subnet
    name: default-v4-ippool
    ownerReferences:
    - apiVersion: spiderpool.spidernet.io/v1
      blockOwnerDeletion: true
      controller: true
      kind: SpiderSubnet
      name: default-v4-subnet
      uid: daa8e1e6-5ebd-4785-a96d-fb585b84a803
    resourceVersion: "28021"
    uid: 9756bbb1-134c-4f5c-97aa-01fb7673350e
  spec:
    disable: false
    gateway: 10.29.0.1
    ipVersion: 4
    ips:
    - 10.29.140.50-10.29.140.100
    subnet: 10.29.0.0/16
    vlan: 0
  status:
    allocatedIPCount: 2
    allocatedIPs:
      10.29.140.56:
        containerID: 4cb556c5ac62a134e37b441341da9a546f6dbfbb594902727345f65b3eafea06
        interface: net1
        namespace: maweibing
        node: worker01
        ownerControllerName: macvlan-pod-5b7ccffd6c
        ownerControllerType: ReplicaSet
        pod: macvlan-pod-5b7ccffd6c-z62sp
      10.29.140.90:
        containerID: e1582da9b1d65ac6ee5b0b3a2f7e6709cb98113ffde684c7b78ca66bba722414
        interface: eth0
        namespace: default
        node: worker01
        ownerControllerName: nginx-macvlan-7dcbd9797b
        ownerControllerType: ReplicaSet
        pod: nginx-macvlan-7dcbd9797b-wq9gx
    totalIPCount: 51
kind: List
metadata:
  resourceVersion: ""
 
[root@master01 ~]# kubectl get svc -n kube-system | grep -i spider 
spiderpool-controller                                  ClusterIP      10.233.3.11     <none>        5722/TCP,5720/TCP            45h
[root@master01 ~]# kubectl get svc -n kube-system spiderpool-controller  -o yaml 
apiVersion: v1
kind: Service
metadata:
  annotations:
    meta.helm.sh/release-name: spiderpool-maweibing
    meta.helm.sh/release-namespace: kube-system
  creationTimestamp: "2022-10-29T09:46:08Z"
  labels:
    app.kubernetes.io/component: spiderpool-controller
    app.kubernetes.io/instance: spiderpool-maweibing
    app.kubernetes.io/managed-by: Helm
    app.kubernetes.io/name: spiderpool
    app.kubernetes.io/version: 0.3.0
    helm.sh/chart: spiderpool-0.3.0
  name: spiderpool-controller
  namespace: kube-system
  resourceVersion: "16781"
  uid: 5914c1af-b0c3-4eaa-87ad-262679263ee4
spec:
  clusterIP: 10.233.3.11
  clusterIPs:
  - 10.233.3.11
  internalTrafficPolicy: Cluster
  ipFamilies:
  - IPv4
  ipFamilyPolicy: SingleStack
  ports:
  - name: webhook
    port: 5722
    protocol: TCP
    targetPort: webhook
  - name: http
    port: 5720
    protocol: TCP
    targetPort: http
  selector:
    app.kubernetes.io/component: spiderpool-controller
    app.kubernetes.io/instance: spiderpool-maweibing
    app.kubernetes.io/name: spiderpool
  sessionAffinity: None
  type: ClusterIP
status:
  loadBalancer: {}
```

