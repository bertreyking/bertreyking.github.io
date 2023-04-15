# ClusterPedia-介绍

## ClusterPedia  概念

### 1. [PediaCluster](https://clusterpedia.io/zh-cn/docs/concepts/pediacluster/)

```shell
# PediaCluster 是什么？
个人理解：我称它为实例，一个集群一个实例，这个实例包含了认证信息和需要同步给 clusterpedia 的资源信息

# PediaCluster 怎么用？
- 包含集群集群的认证信息
  - kubeconfig      # 集群的 kubeconfig 文件，使用它 pediacluster 的 apiserver 列显示为空
  - caData          # namesapce 下 serviceaccoint 的 secret ca (推荐)
  - tokenData       # namesapce 下 serviceaccoint 的 secret ca (推荐)
  - certData        # 证书
  - keyData         # 证书
  
- 包含集群需要同步的资源信息
  - syncResources: []              # 自定义需要同步的资源，deploy、pod、configmap、secret、......
  - syncAllCustomResources: false  # 同步所有自定义资源
  - syncResourcesRefName: ""       # 引用公共的集群同步配置
```

### 2. [ClusterSyncResources](https://clusterpedia.io/zh-cn/docs/concepts/cluster-sync-resources/)

```shell
# ClusterSyncResources 是什么？
一个公共/通用的集群资源同步配置，有了它在创建 PediaCluster 实例时就不用配置 syncResources，使用 syncResourcesRefName 引用即可，如果两者并存，那么取两者并集

# ClusterSyncResources 示例：
root@master01 ~]# kubectl get clustersyncresources.cluster.clusterpedia.io  cluster-sync-resources-example -o yaml 
apiVersion: cluster.clusterpedia.io/v1alpha2
kind: ClusterSyncResources
metadata:
  name: cluster-sync-resources-example
spec:
  syncResources:
  - group: ""
    resources:
    - pods
    versions:
    - v1
  - group: ""
    resources:
    - nodes
    - services
    - ingress
    - secrets
    - configmaps
        
# PediaCluster 示例：
[root@master01 ~]# kubectl get pediacluster dce4-010 -o yaml 
apiVersion: cluster.clusterpedia.io/v1alpha2
kind: PediaCluster
metadata:
  name: dce4-010
spec:
  apiserver: https://10.29.16.27:16443
  caData: ""
  tokenData: ""
  syncResources:
  - group: apps
    resources:
    - deployments
  - group: ""
    resources:
    - pods
    - configmaps
  - group: cert-manager.io
    resources:
    - certificates
    versions:
    - v1
  syncResourcesRefName: cluster-sync-resources-example

```

### 3. [Collection Resource](https://clusterpedia.io/zh-cn/docs/concepts/collection-resource/)

```shell
# Collection Resource(聚合资源) 是什么?
- 一次获取多个类型的资源
- 不同类型资源组合而成
- 多种资源进行统一的检索和分页
- 只能检索 pediacluster 都同步了的资源类型，比如，两个资源都同步了 sts ，如果一个没有同步就会聚合资源时就不会显示 sts 资源

# 目前支持的聚合资源(建议：kubectl get --raw="$API" api 的形式对资源进行检索和分页)
- any                # 所有资源，不能使用 kubectl 工具获取, 使用 url 时需要定义 grops / resources
- workloads          # deployment\daemonsets\statefulsets
- kuberesources      # kubernetes 所有内置资源

# kubectl get collectionresources any
# kubectl get collectionresources workloads
# kubectl get deploy,cm,secrets --cluster clusterpedia -A
# kubectl get collectionresources.clusterpedia.io kuberesources
# kubectl get --raw="/apis/clusterpedia.io/v1beta1/collectionresources/workloads?limit=2" | jq
# kubectl get --raw "/apis/clusterpedia.io/v1beta1/collectionresources/any?onlyMetadata=true&resources=apps/deployments&limit=2" | jq

# 暂不支持自定义
```

### 4. [ClusterImportPolicy](https://clusterpedia.io/zh-cn/docs/concepts/cluster-import-policy/)

```shell
# ClusterImportPolicy(自动接入)
- 定义某种资源，并根据前期约定的模板、条件来自动创建、更新、删除 pediacluster
- 对于已经存在的 pediacluster 不会创建和删除，只会对其更新/手动删除
```

