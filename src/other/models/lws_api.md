# LeaderWorkerSet API

## LeaderWorkerSet API 是什么？

- 简称 LWS

-  是一个 API

- 旨在解决 AI/ML 推理工作负载的常见部署模式，尤其是多机多卡的推理工作负载，其中 LLM 将被分片并在多个节点上的多个设备上运行

  ![lws-img](https://github.com/kubernetes-sigs/lws/blob/main/site/static/images/concept.png?raw=true)

## 功能

- 

##  场景

- 用于大模型的服务推理

- 利用多个主机的 GPU 卡完成模型部署和推理

  ![img](https://lh7-rt.googleusercontent.com/docsz/AD_4nXdiwrSFYK_rp07reoazLeW1gl3XZmkYfIC47MBi1Un_pshhXg_1tU77iQ_7Cd5v1HlC1y8DoC1jPhdPvu8EkIMj12p4tKO6IWnZ11sjTA67Uy3rCtt9QSoOTb05RL_RjNtcaEehlQTCCdigA2Xb2Hs2Dght?key=HumZL73ai0vhaoBTLZ-gyw)

## 安装 lws

- [helm chart](https://github.com/kubernetes-sigs/lws/tree/main/charts/lws)
- [manifests](https://github.com/kubernetes-sigs/lws/releases/download/v0.6.0/manifests.yaml)

```shell
## install
[root@tf1-dameile-master01 ~]# VERSION=v0.6.0
[root@tf1-dameile-master01 ~]# kubectl apply --server-side -f https://github.com/kubernetes-sigs/lws/releases/download/$VERSION/manifests.yaml

namespace/lws-system serverside-applied
customresourcedefinition.apiextensions.k8s.io/leaderworkersets.leaderworkerset.x-k8s.io serverside-applied
serviceaccount/lws-controller-manager serverside-applied
role.rbac.authorization.k8s.io/lws-leader-election-role serverside-applied
clusterrole.rbac.authorization.k8s.io/lws-manager-role serverside-applied
clusterrole.rbac.authorization.k8s.io/lws-metrics-reader serverside-applied
clusterrole.rbac.authorization.k8s.io/lws-proxy-role serverside-applied
rolebinding.rbac.authorization.k8s.io/lws-leader-election-rolebinding serverside-applied
clusterrolebinding.rbac.authorization.k8s.io/lws-manager-rolebinding serverside-applied
clusterrolebinding.rbac.authorization.k8s.io/lws-metrics-reader-rolebinding serverside-applied
clusterrolebinding.rbac.authorization.k8s.io/lws-proxy-rolebinding serverside-applied
configmap/lws-manager-config serverside-applied
secret/lws-webhook-server-cert serverside-applied
service/lws-controller-manager-metrics-service serverside-applied
service/lws-webhook-service serverside-applied
deployment.apps/lws-controller-manager serverside-applied
mutatingwebhookconfiguration.admissionregistration.k8s.io/lws-mutating-webhook-configuration serverside-applied
validatingwebhookconfiguration.admissionregistration.k8s.io/lws-validating-webhook-configuration serverside-applied
[root@tf1-dameile-master01 ~]# 

## check
[root@tf1-dameile-master01 ~]# kubectl get deployments.apps -n lws-system 
NAME                     READY   UP-TO-DATE   AVAILABLE   AGE
lws-controller-manager   0/2     2            0           95s
[root@tf1-dameile-master01 ~]# kubectl get deployments.apps -n lws-system lws-controller-manager -o yaml | grep image
        image: registry.k8s.io/lws/lws:v0.6.0
        imagePullPolicy: IfNotPresent
        
## modify
registry.k8s.io/lws/lws:v0.6.0 替换为 k8s.m.daocloud.io/lws/lws:v0.6.0 # k8s.m.daocloud.io 是 daocloud 加速器

```

## lws 滚动更新

### 更新策略

- `MaxUnavailable`：表示在更新过程中允许多少个副本不可用，不可用数量基于 spec.replicas。默认为 1
- `MaxSurge`：表示更新时可以部署多少个额外副本。默认为 0
- maxSurge 和 maxUnavailable 不能同时为零

### 滚动更新 demo

- 示例 yaml

```yaml
spec:
  rolloutStrategy:
    type: RollingUpdate
    rollingUpdateConfiguration:
      maxUnavailable: 2
      maxSurge: 2
  replicas: 4
```

- 更新过程如下：
  - ✅ 副本已更新
  - ❎ 副本尚未更新
  - ⏳ 副本正在滚动更新

|           | 分区 | 副本 | R-0  | R-1  | R-2  | R-3  | R-4  | R-5  | 说明                                                         |
| --------- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ---- | ------------------------------------------------------------ |
| 第一阶段  | 0    | 4    | ✅    | ✅    | ✅    | ✅    |      |      | 滚动更新之前                                                 |
| 第 2 阶段 | 4    | 6    | ❎    | ❎    | ❎    | ❎    | ⏳    | ⏳    | 滚动更新已开始                                               |
| 第 3 阶段 | 2    | 6    | ❎    | ❎    | ⏳    | ⏳    | ⏳    | ⏳    | 分区从 4 变为 2                                              |
| 第四阶段  | 2    | 6    | ❎    | ❎    | ⏳    | ⏳    | ✅    | ⏳    | 由于最后一个 Replica 尚未准备好，因此 Partition 不会发生改变 |
| 第五阶段  | 0    | 6    | ⏳    | ⏳    | ⏳    | ⏳    | ✅    | ✅    | 分区从 2 变为 0                                              |
| 第六阶段  | 0    | 6    | ⏳    | ⏳    | ⏳    | ✅    | ✅    | ✅    |                                                              |
| 第七阶段  | 0    | 5    | ⏳    | ✅    | ⏳    | ✅    | ✅    |      | 回收副本以容纳尚未准备好的副本                               |
| 第八阶段  | 0    | 4    | ✅    | ⏳    | ✅    | ✅    |      |      | 发布另一个副本                                               |
| 第九阶段  | 0    | 4    | ✅    | ✅    | ✅    | ✅    |      |      | 滚动更新已完成                                               |

## lws 标签、注解、环境变量

### Labels

| 键                                                   | 描述                                                    | 例子                   | 适用于                         |
| ---------------------------------------------------- | ------------------------------------------------------- | ---------------------- | ------------------------------ |
| `leaderworkerset.sigs.k8s.io/name`                   | 这些资源所属的 LeaderWorkerSet 对象的名称。             | leaderworkerset-多模板 | Pod、StatefulSet、服务         |
| `leaderworkerset.sigs.k8s.io/template-revision-hash` | 用于跟踪与 LeaderWorkerSet 对象匹配的控制器修订的哈希。 | 5c5fcdfb44             | Pod、StatefulSet               |
| `leaderworkerset.sigs.k8s.io/group-index`            | 它所属的组。                                            | 0                      | Pod、StatefulSet（仅工作线程） |
| `leaderworkerset.sigs.k8s.io/group-key`              | 标识该组的唯一键。                                      | 689ce1b5…b07           | Pod、StatefulSet（仅工作线程） |
| `leaderworkerset.sigs.k8s.io/worker-index`           | 组内 pod 的索引或标识。                                 | 0                      | 荚                             |
| `leaderworkerset.sigs.k8s.io/subgroup-index`         | 跟踪该 pod 所属的子分组。                               | 0                      | Pod（仅当设置了 SubGroup 时）  |
| `leaderworkerset.sigs.k8s.io/subgroup-key`           | 属于同一子组的 Pod 将具有相同的唯一哈希值。             | 92904e74…801           | Pod（仅当设置了 SubGroup 时）  |

### Annotations

| 键                                                        | 描述                              | 例子                          | 适用于                                                       |
| --------------------------------------------------------- | --------------------------------- | ----------------------------- | ------------------------------------------------------------ |
| `leaderworkerset.sigs.k8s.io/size`                        | 每个组中的 pod 总数。             | 4                             | 荚                                                           |
| `leaderworkerset.sigs.k8s.io/replicas`                    | 副本数：领导-工作组的数量。       | 3                             | StatefulSet (唯一领导者)                                     |
| `leaderworkerset.sigs.k8s.io/leader-name`                 | 领导者荚的名称。                  | leaderworkerset-多模板-0      | Pod（仅工作进程）                                            |
| `leaderworkerset.sigs.k8s.io/exclusive-topology`          | 指定独占 1:1 调度的拓扑。         | cloud.google.com/gke-nodepool | LeaderWorkerSet、Pod（仅当使用 exclusive-topology 时）       |
| `leaderworkerset.sigs.k8s.io/subdomainPolicy`             | 确定将注入哪种类型的域。          | 每个副本唯一                  | Pod（仅当 leader 和 subdomainPolicy 设置为 UniquePerReplica 时） |
| `leaderworkerset.sigs.k8s.io/subgroup-size`               | 每个子组的 pod 数量。             | 2                             | Pod（仅当设置了 SubGroup 时）                                |
| `leaderworkerset.sigs.k8s.io/subgroup-exclusive-topology` | 指定子组内的独占 1:1 调度的拓扑。 | 拓扑键                        | LeaderWorkerSet、Pod（仅当设置了 SubGroup 并使用了 subgroup-exclusive-topology 时） |

### Env

| 键                     | 描述                                    | 例子                                                         | 适用于                 |
| ---------------------- | --------------------------------------- | ------------------------------------------------------------ | ---------------------- |
| `LWS_LEADER_ADDRESS`   | 通过无头服务获取领导者的地址。          | leaderworkerset-多模板-0.leaderworkerset-多模板.默认         | 荚                     |
| `LWS_GROUP_SIZE`       | 跟踪 LWS 组的大小。                     | 4                                                            | 荚                     |
| `LWS_WORKER_INDEX`     | 组内 pod 的索引或标识。                 | 2                                                            | 荚                     |
| `TPU_WORKER_HOSTNAMES` | 仅位于同一子组中的 TPU 工作者的主机名。 | 测试样本-1-5.默认,测试样本-1-6.默认,测试样本-1-7.默认,测试样本-1-8.默认 | Pod（仅当启用 TPU 时） |
| `TPU_WORKER_ID`        | TPU 工人的 ID。                         | 0                                                            | Pod（仅当启用 TPU 时） |
| `TPU_NAME`             | TPU 的名称。                            | 测试样本-1                                                   | Pod（仅当启用 TPU 时） |

- 更多环境变量，请参考 [Kubernetes Downward API](https://kubernetes.io/docs/concepts/workloads/pods/downward-api/)

## 更多示例配置

- https://lws.sigs.k8s.io/docs/examples/

  - https://github.com/kubernetes-sigs/lws/blob/main/docs/examples/vllm/GPU/lws.yaml

  - https://github.com/kubernetes-sigs/lws/blob/main/docs/examples/sglang/lws.yaml
    - https://hub.docker.com/r/lmsysorg/sglang/tags

- https://cloud.google.com/kubernetes-engine/docs/tutorials/serve-multihost-gpu?hl=zh-cn
- https://docs.vllm.ai/en/latest/serving/distributed_serving.html#running-vllm-on-multiple-nodes
- https://docs.sglang.ai/references/multi_node.html

## LWS 设计文档

- https://docs.google.com/document/d/1C0wgkOdDov8fEsBNZF3wPwYv1njRuWBs2-BueymXyfM/edit?tab=t.0