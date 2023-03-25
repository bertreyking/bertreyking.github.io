# ClusterPedia-安装-v0.6.3

## 1. 下载 [clusterpedia](https://clusterpedia.io/zh-cn/docs/) 项目到本地

```shell
[root@master01 ~]# git clone https://github.com/clusterpedia-io/clusterpedia.git
[root@master01 ~]# cd clusterpedia
```

## 2.  部署 mysql 组件

### 2.1. 安装 mysql

```shell
cd ./deploy/internalstorage/mysql

# 重新定义 mysql pv 和 job yaml 文件 ( pv 需要更改 hostpath 路径也在这里更改)
[root@master01 ~/clusterpedia/deploy/internalstorage/mysql]# export STORAGE_NODE_NAME=worker01

[root@master01 ~/clusterpedia/deploy/internalstorage/mysql]# sed "s|__NODE_NAME__|$STORAGE_NODE_NAME|g" `grep __NODE_NAME__ -rl ./templates` > clusterpedia_internalstorage_pv.yaml

[root@master01 ~/clusterpedia/deploy/internalstorage/mysql]# cat clusterpedia_internalstorage_pv.yaml
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: clusterpedia-internalstorage-mysql
  labels:
    app: clusterpedia-internalstorage
    internalstorage.clusterpedia.io/type: mysql
spec:
  capacity:
    storage: 20Gi
  volumeMode: Filesystem
  accessModes:
  - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  local:
    path: /var/local/clusterpedia/internalstorage/mysql
  nodeAffinity:
    required:
      nodeSelectorTerms:
      - matchExpressions:
        - key: kubernetes.io/hostname
          operator: In
          values:
          - worker01
---
apiVersion: batch/v1
kind: Job
metadata:
  name: check-worker01-mysql-local-pv-dir
  namespace: clusterpedia-system
  labels:
    app: clusterpedia-internalstorage
    internalstorage.clusterpedia.io/type: mysql
spec:
  ttlSecondsAfterFinished: 600
  template:
    metadata:
      labels:
        app: clusterpedia-internalstorage
        internalstorage.clusterpedia.io/type: mysql
        job: check-node-local-pv-dir
    spec:
      restartPolicy: Never
      nodeName: worker01
      containers:
      - name: check-dir
        image: mysql:8
        command: ['sh', '-c', 'stat /var/lib/mysql']
        volumeMounts:
        - name: pv-dir
          mountPath: /var/lib/mysql
      volumes:
      - name: pv-dir
        hostPath:
          path: /var/local/clusterpedia/internalstorage/mysql
      tolerations:
      - key: "node-role.kubernetes.io/master"
        operator: "Exists"
        effect: "NoSchedule"

# 部署 mysql 
[root@master01 ~/clusterpedia/deploy/internalstorage/mysql]# kubectl apply -f .
namespace/clusterpedia-system created
configmap/clusterpedia-internalstorage created
service/clusterpedia-internalstorage-mysql created
persistentvolumeclaim/internalstorage-mysql created
deployment.apps/clusterpedia-internalstorage-mysql created
persistentvolume/clusterpedia-internalstorage-mysql created
job.batch/check-worker01-mysql-local-pv-dir created
secret/internalstorage-password created

```

### 2.2 检查 mysql 状态

```shell
# 查看组件资源
[root@master01 ~/clusterpedia/deploy/internalstorage/mysql]# kubectl get all -n clusterpedia-system
NAME                                                      READY   STATUS      RESTARTS   AGE
pod/check-worker01-mysql-local-pv-dir-gqrpc               0/1     Completed   0          2m43s
pod/clusterpedia-internalstorage-mysql-6c4778f66b-7shcd   1/1     Running     0          2m43s

NAME                                         TYPE        CLUSTER-IP     EXTERNAL-IP   PORT(S)    AGE
service/clusterpedia-internalstorage-mysql   ClusterIP   10.233.28.80   <none>        3306/TCP   2m43s

NAME                                                 READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/clusterpedia-internalstorage-mysql   1/1     1            1           2m43s

NAME                                                            DESIRED   CURRENT   READY   AGE
replicaset.apps/clusterpedia-internalstorage-mysql-6c4778f66b   1         1         1       2m43s

NAME                                          COMPLETIONS   DURATION   AGE
job.batch/check-worker01-mysql-local-pv-dir   1/1           4s         2m43s

[root@master01 ~/clusterpedia/deploy/internalstorage/mysql]# kubectl get pvc -n clusterpedia-system
NAME                    STATUS   VOLUME                               CAPACITY   ACCESS MODES   STORAGECLASS   AGE
internalstorage-mysql   Bound    clusterpedia-internalstorage-mysql   20Gi       RWO                           3m14s

# 查看 mysql 密码
echo `kubectl get secret -n clusterpedia-system internalstorage-password  -o jsonpath='{.data.password}'` | base64 -d 
dangerous0
```

## 3. 安装 clusterpedia

### 3.1 clusterpedia

```shell
# 查看项目文件
[root@master01 ~/clusterpedia]# ll
total 216
-rw-r--r--.  1 root root   344 Feb 28 20:57 builder.dockerfile
-rw-r--r--.  1 root root     0 Feb 28 16:56 builder.dockerfile.dockerignore
drwxr-xr-x.  3 root root    86 Feb 28 16:56 charts
drwxr-xr-x.  6 root root   104 Feb 28 16:56 cmd
-rw-r--r--.  1 root root   144 Feb 28 16:56 CODE_OF_CONDUCT.md
-rw-r--r--.  1 root root  4192 Feb 28 16:56 CONTRIBUTING.md
drwxr-xr-x.  6 root root  4096 Feb 28 16:56 deploy
-rw-r--r--.  1 root root   319 Feb 28 20:57 Dockerfile
drwxr-xr-x.  3 root root    20 Feb 28 16:56 docs
drwxr-xr-x.  2 root root   134 Feb 28 16:56 examples
-rw-r--r--.  1 root root  8466 Feb 28 20:57 go.mod
-rw-r--r--.  1 root root 98838 Feb 28 20:57 go.sum
-rw-r--r--.  1 root root  6605 Feb 28 16:56 GOVERNANCE.md
drwxr-xr-x.  2 root root  4096 Feb 28 20:57 hack
-rw-r--r--.  1 root root  2270 Feb 28 16:56 ldflags.sh
-rw-r--r--.  1 root root 11357 Feb 28 16:56 LICENSE
-rw-r--r--.  1 root root   374 Feb 28 20:57 MAINTAINERS.md
-rw-r--r--.  1 root root  9063 Feb 28 16:56 Makefile
-rw-r--r--.  1 root root    70 Feb 28 16:56 OWNERS
drwxr-xr-x. 13 root root   196 Feb 28 16:56 pkg
-rw-r--r--.  1 root root 25220 Feb 28 20:57 README.md
-rw-r--r--.  1 root root  2253 Feb 28 16:56 ROADMAP.md
drwxr-xr-x.  3 root root    17 Feb 28 16:56 staging
drwxr-xr-x.  4 root root    85 Feb 28 20:57 test
drwxr-xr-x. 12 root root   214 Feb 28 20:57 vendor

# 下发 deploy 目录下所有资源
[root@master01 ~/clusterpedia]# kubectl apply -f deploy/
customresourcedefinition.apiextensions.k8s.io/clustersyncresources.cluster.clusterpedia.io created
Warning: Detected changes to resource pediaclusters.cluster.clusterpedia.io which is currently being deleted.
customresourcedefinition.apiextensions.k8s.io/pediaclusters.cluster.clusterpedia.io configured
apiservice.apiregistration.k8s.io/v1beta1.clusterpedia.io created
serviceaccount/clusterpedia-apiserver created
service/clusterpedia-apiserver created
deployment.apps/clusterpedia-apiserver created
clusterrole.rbac.authorization.k8s.io/clusterpedia created
clusterrolebinding.rbac.authorization.k8s.io/clusterpedia created
serviceaccount/clusterpedia-clustersynchro-manager created
deployment.apps/clusterpedia-clustersynchro-manager created
serviceaccount/clusterpedia-controller-manager created
deployment.apps/clusterpedia-controller-manager created
namespace/clusterpedia-system unchanged
Warning: Detected changes to resource clusterimportpolicies.policy.clusterpedia.io which is currently being deleted.
customresourcedefinition.apiextensions.k8s.io/clusterimportpolicies.policy.clusterpedia.io configured
customresourcedefinition.apiextensions.k8s.io/pediaclusterlifecycles.policy.clusterpedia.io created

# 2 个 warning 时因为前期没有删除干净导致，通过创建时间可以看出
[root@master01 ~/clusterpedia]# kubectl get crd  | grep clusterpedia
clusterimportpolicies.policy.clusterpedia.io          2022-12-08T08:26:47Z
clustersyncresources.cluster.clusterpedia.io          2023-02-28T13:15:35Z
pediaclusterlifecycles.policy.clusterpedia.io         2023-02-28T13:15:35Z
pediaclusters.cluster.clusterpedia.io                 2022-12-08T08:26:47Z

# 4 个 无状态资源类型
deployment.apps/clusterpedia-apiserver created （svc、sa、secret）  ------> mysql、-----> pediacluster 来兼容 k8 api 做一下复杂的资源检索
deployment.apps/clusterpedia-clustersynchro-manager created （sa） -----> mysql、-----> pediacluster 进行资源同步
deployment.apps/clusterpedia-controller-manager created （sa）     
deployment.apps/clusterpedia-internalstorage-mysql # 步骤 2 已安装

# 4 个 crd （后期接入集群是，如果报错，可以到 crds 目录再执行下）
customresourcedefinition.apiextensions.k8s.io/clustersyncresources.cluster.clusterpedia.io created
customresourcedefinition.apiextensions.k8s.io/pediaclusters.cluster.clusterpedia.io configured
customresourcedefinition.apiextensions.k8s.io/clusterimportpolicies.policy.clusterpedia.io configured
customresourcedefinition.apiextensions.k8s.io/pediaclusterlifecycles.policy.clusterpedia.io created

# clusterrole、clusterrolebinding （apiserver、clustersynchro-manager、controller-manager）
clusterrole.rbac.authorization.k8s.io/clusterpedia created
clusterrolebinding.rbac.authorization.k8s.io/clusterpedia created

```

### 3.2 检查各组件状态

```shell
[root@master01 ~/clusterpedia]# kubectl get deployments.apps -n clusterpedia-system 
NAME                                  READY   UP-TO-DATE   AVAILABLE   AGE
clusterpedia-apiserver                1/1     1            1           12h
clusterpedia-clustersynchro-manager   1/1     1            1           12h
clusterpedia-controller-manager       1/1     1            1           12h
clusterpedia-internalstorage-mysql    1/1     1            1           13h

[root@master01 ~/clusterpedia]# kubectl get pod -n clusterpedia-system 
NAME                                                   READY   STATUS    RESTARTS   AGE
clusterpedia-apiserver-b7d9ddd86-hlq8k                 1/1     Running   0          12h
clusterpedia-clustersynchro-manager-84fbdf5758-x948t   1/1     Running   0          12h
clusterpedia-controller-manager-6fc45659dd-sxmsd       1/1     Running   0          12h
clusterpedia-internalstorage-mysql-6c4778f66b-7shcd    1/1     Running   0          13h
```

## 4. 接入集群

### 4.1 创建 rbac 资源并获取 token

```shell
# 创建 clusterrole、clusterrolebinding、sa、secretn(1.22 之后默认创建的 sa，不带 secret)
[root@master01 ~/clusterpedia/examples]# pwd
/root/clusterpedia/examples
[root@master01 ~/clusterpedia/examples]# cat clusterpedia_synchro_rbac.yaml 
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: clusterpedia-synchro
rules:
- apiGroups:
  - '*'
  resources:
  - '*'
  verbs:
  - '*'
- nonResourceURLs:
  - '*'
  verbs:
  - '*'
---
apiVersion: v1
kind: ServiceAccount  # 1.24 之后的版本 sa 不带 secret 密钥，需要自行创建
metadata:
  name: clusterpedia-synchro
  namespace: default
---
apiVersion: v1
kind: Secret
metadata:
  name: clusterpedia-synchro
  namespace: default
  annotations:
    kubernetes.io/service-account.name: clusterpedia-synchro
type: kubernetes.io/service-account-token
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: clusterpedia-synchro
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: clusterpedia-synchro
subjects:
- kind: ServiceAccount
  name: clusterpedia-synchro
  namespace: default
---
root@master01 ~/clusterpedia/examples]# kubectl apply -f clusterpedia_synchro_rbac.yaml 
clusterrole.rbac.authorization.k8s.io/clusterpedia-synchro unchanged
serviceaccount/clusterpedia-synchro unchanged
secret/clusterpedia-synchro created
clusterrolebinding.rbac.authorization.k8s.io/clusterpedia-synchro unchanged

# 查看 secret 种 的 ca 、 token
[root@master01 ~/clusterpedia/examples]# kubectl get sa  clusterpedia-synchro -o yaml 
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"ServiceAccount","metadata":{"annotations":{},"name":"clusterpedia-synchro","namespace":"default"}}
  creationTimestamp: "2023-03-20T02:29:28Z"
  name: clusterpedia-synchro
  namespace: default
  resourceVersion: "62487008"
  uid: a34d7e2a-1ad5-488d-b9aa-8f9682fa2206
[root@master01 ~/clusterpedia/examples]# kubectl get  secret  clusterpedia-synchro -o yaml 
apiVersion: v1
data:
  ca.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUMvakNDQWVhZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJeU1UQXlPVEEzTXpFME1Wb1hEVE15TVRBeU5qQTNNekUwTVZvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBTlpMCjhvVitVemo4Ky9CYTZ1MkVyV2tVQ3IxRitUeEZXSlRRZmMrWE44UGtOMDRUa1V4VzdnTVo4SHUzeFFoZHY1eGsKSmRwNCtRNFFyM1B1U1Z4MGMvNlBOVUFwOVRCY3EyVTRZK09hZjJhR3pXRWxaNXIzVnBRUDF5akx2UURtbUpxRwowVHNnYU1UTnVBQ3ZPRW56eFRzNkZzdkFFTmZ6djhZWDlDeUs4azlTam5qSy9xaS9pSUlLSm45NG1yUUQ5SUtnCkFyYUw2MDMvRzhFMzJGVUFwc3FvVUh1V3pGclRQY2ZNd0xpbWVXeS9PU2lkRTU5aGR2Q2lHWHNvWGxMTURKSXAKT1dsT1FHL2Y3VHNZMFdLMXNvQ3drTjZYdkY0c1J4T1JCK1pQRS9qSFdLbVhhSm5jQ1hMNStocnh1MXg1Z1lJcgpManZ1YUR0NmdYWm5qSXBNYzdrQ0F3RUFBYU5aTUZjd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi93UUZNQU1CQWY4d0hRWURWUjBPQkJZRUZHem5rbkZ0ajFkNzRhN2pNRUd2TWdFQXIzcGpNQlVHQTFVZEVRUU8KTUF5Q0NtdDFZbVZ5Ym1WMFpYTXdEUVlKS29aSWh2Y05BUUVMQlFBRGdnRUJBQmtJZG4xWW93YllGWTdyeHltawo1VWdmRkFwRzBDcUVjSmY1Unk1QU9mYWNxRldaZTF0Yk9kSy9nSEtDT2JRdTQ0Zi94Mnh0K1VqYnllRzYrYmRkCk52THhrOXg1REtjM29ZU1l0bWtqTkxoM2lpYzRNRHZDcmwwWGZzd2R5bDVQbDdqaHBLVE5XMHIyNEt4NDlZdWcKVDNBcURJcFROL3ppTURwMHk5SXFhMkFRcEkyQ0c2cUZOakxlcmxqclFISVZubDZwbjl3WndIVnluL1RsT1hhRgpKRjVLRHg4S3R4ck1zamhTY2pwZzZ4cUJLam8wWDlTenV2UGhUL3dUejQrekhQb1JodzBSMnJlbUNpR1llUFB1Ck9CT2l0WUJwdkYyYVhKcUxpcVFWWG5GdGRyaE81dEVYcW14YmV4amRqUlFBWUQ3UXVRaG9ONlk1Tlc1TzNGcGEKeGFzPQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==
  namespace: ZGVmYXVsdA==
  token: ZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNklqVTFaRUZKVTJ4UWVURktXamxYZW1GemF6TXpPV2swVm1aaFJWazNkbEJUY1hOc01XeG1SMkoxTlhjaWZRLmV5SnBjM01pT2lKcmRXSmxjbTVsZEdWekwzTmxjblpwWTJWaFkyTnZkVzUwSWl3aWEzVmlaWEp1WlhSbGN5NXBieTl6WlhKMmFXTmxZV05qYjNWdWRDOXVZVzFsYzNCaFkyVWlPaUprWldaaGRXeDBJaXdpYTNWaVpYSnVaWFJsY3k1cGJ5OXpaWEoyYVdObFlXTmpiM1Z1ZEM5elpXTnlaWFF1Ym1GdFpTSTZJbU5zZFhOMFpYSndaV1JwWVMxemVXNWphSEp2SWl3aWEzVmlaWEp1WlhSbGN5NXBieTl6WlhKMmFXTmxZV05qYjNWdWRDOXpaWEoyYVdObExXRmpZMjkxYm5RdWJtRnRaU0k2SW1Oc2RYTjBaWEp3WldScFlTMXplVzVqYUhKdklpd2lhM1ZpWlhKdVpYUmxjeTVwYnk5elpYSjJhV05sWVdOamIzVnVkQzl6WlhKMmFXTmxMV0ZqWTI5MWJuUXVkV2xrSWpvaVlUTTBaRGRsTW1FdE1XRmtOUzAwT0Roa0xXSTVZV0V0T0dZNU5qZ3labUV5TWpBMklpd2ljM1ZpSWpvaWMzbHpkR1Z0T25ObGNuWnBZMlZoWTJOdmRXNTBPbVJsWm1GMWJIUTZZMngxYzNSbGNuQmxaR2xoTFhONWJtTm9jbThpZlEuR2pBb1MxZ0RUdUdmSkd5UEJqWHpxcDRwa0ljMWpOX0dvUXZway1VeFE0OEdKUk9lSHFaZFdwZi1CeEZCMHdFUjd2ME9ub19EMGtndHRjRHJzZUluaGx2RVdHa3dwZHEyMVVUeHFhQ293aE1mMWsxdFk4ZVZCQzVBWTJqTVhPN0pMM05KM2xpU25LNFZWbjYtVlpEcXg3dTlxMXFFSE8tb3hubjNleklRSGtLSmFFei03SUlNSlJ5ZGN5R1lPZk9pUTFhbnZqa0ZpUm93VkRZSG1pM1Q0ZVBEbEtqTW9kU0VxTWxUYU9FcmF6YVl0TXJKdmdpYmRrZl9LQzFrVTdYYldaMGhIZHMtTFJCOHoyenV0QWFfZTcxbDNmTmxEWWdvMEdzYjA1d1B3anE1Mm1jc2hxWkEwbG1MdnI2bnkzVEJ6OTVsT3FSdmgxYWZpTmZyU1lHekpR
kind: Secret
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"Secret","metadata":{"annotations":{"kubernetes.io/service-account.name":"clusterpedia-synchro"},"name":"clusterpedia-synchro","namespace":"default"},"type":"kubernetes.io/service-account-token"}
    kubernetes.io/service-account.name: clusterpedia-synchro
    kubernetes.io/service-account.uid: a34d7e2a-1ad5-488d-b9aa-8f9682fa2206
  creationTimestamp: "2023-03-20T02:51:13Z"
  name: clusterpedia-synchro
  namespace: default
  resourceVersion: "62496452"
  uid: b20e8ebc-2c54-4a30-a39d-ed1dec5a42bd
type: kubernetes.io/service-account-token
```

### 4.2 生成 pediacluster 实例 并接入集群

```shell
# pediacluster 配置文件
[root@master01 ~/clusterpedia/examples]# kubectl get secret clusterpedia-synchro -o jsonpath='{.data.ca\.crt}'  
[root@master01 ~/clusterpedia/examples]# kubectl get secret clusterpedia-synchro -o jsonpath='{.data.toekn}'  

# 配置文件如下
root@master01 ~]# cat clusterpedia/examples/dce5-mmber-pediacluster.yaml 
apiVersion: cluster.clusterpedia.io/v1alpha2
kind: PediaCluster
metadata:
  name: dce5-member
spec:
  apiserver: "https://10.29.15.79:6443"
  caData: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUMvakNDQWVhZ0F3SUJBZ0lCQURBTkJna3Foa2lHOXcwQkFRc0ZBREFWTVJNd0VRWURWUVFERXdwcmRXSmwKY201bGRHVnpNQjRYRFRJeU1UQXlPVEEzTXpFME1Wb1hEVE15TVRBeU5qQTNNekUwTVZvd0ZURVRNQkVHQTFVRQpBeE1LYTNWaVpYSnVaWFJsY3pDQ0FTSXdEUVlKS29aSWh2Y05BUUVCQlFBRGdnRVBBRENDQVFvQ2dnRUJBTlpMCjhvVitVemo4Ky9CYTZ1MkVyV2tVQ3IxRitUeEZXSlRRZmMrWE44UGtOMDRUa1V4VzdnTVo4SHUzeFFoZHY1eGsKSmRwNCtRNFFyM1B1U1Z4MGMvNlBOVUFwOVRCY3EyVTRZK09hZjJhR3pXRWxaNXIzVnBRUDF5akx2UURtbUpxRwowVHNnYU1UTnVBQ3ZPRW56eFRzNkZzdkFFTmZ6djhZWDlDeUs4azlTam5qSy9xaS9pSUlLSm45NG1yUUQ5SUtnCkFyYUw2MDMvRzhFMzJGVUFwc3FvVUh1V3pGclRQY2ZNd0xpbWVXeS9PU2lkRTU5aGR2Q2lHWHNvWGxMTURKSXAKT1dsT1FHL2Y3VHNZMFdLMXNvQ3drTjZYdkY0c1J4T1JCK1pQRS9qSFdLbVhhSm5jQ1hMNStocnh1MXg1Z1lJcgpManZ1YUR0NmdYWm5qSXBNYzdrQ0F3RUFBYU5aTUZjd0RnWURWUjBQQVFIL0JBUURBZ0trTUE4R0ExVWRFd0VCCi93UUZNQU1CQWY4d0hRWURWUjBPQkJZRUZHem5rbkZ0ajFkNzRhN2pNRUd2TWdFQXIzcGpNQlVHQTFVZEVRUU8KTUF5Q0NtdDFZbVZ5Ym1WMFpYTXdEUVlKS29aSWh2Y05BUUVMQlFBRGdnRUJBQmtJZG4xWW93YllGWTdyeHltawo1VWdmRkFwRzBDcUVjSmY1Unk1QU9mYWNxRldaZTF0Yk9kSy9nSEtDT2JRdTQ0Zi94Mnh0K1VqYnllRzYrYmRkCk52THhrOXg1REtjM29ZU1l0bWtqTkxoM2lpYzRNRHZDcmwwWGZzd2R5bDVQbDdqaHBLVE5XMHIyNEt4NDlZdWcKVDNBcURJcFROL3ppTURwMHk5SXFhMkFRcEkyQ0c2cUZOakxlcmxqclFISVZubDZwbjl3WndIVnluL1RsT1hhRgpKRjVLRHg4S3R4ck1zamhTY2pwZzZ4cUJLam8wWDlTenV2UGhUL3dUejQrekhQb1JodzBSMnJlbUNpR1llUFB1Ck9CT2l0WUJwdkYyYVhKcUxpcVFWWG5GdGRyaE81dEVYcW14YmV4amRqUlFBWUQ3UXVRaG9ONlk1Tlc1TzNGcGEKeGFzPQotLS0tLUVORCBDRVJUSUZJQ0FURS0tLS0tCg==
  tokenData: "ZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNklqVTFaRUZKVTJ4UWVURktXamxYZW1GemF6TXpPV2swVm1aaFJWazNkbEJUY1hOc01XeG1SMkoxTlhjaWZRLmV5SnBjM01pT2lKcmRXSmxjbTVsZEdWekwzTmxjblpwWTJWaFkyTnZkVzUwSWl3aWEzVmlaWEp1WlhSbGN5NXBieTl6WlhKMmFXTmxZV05qYjNWdWRDOXVZVzFsYzNCaFkyVWlPaUprWldaaGRXeDBJaXdpYTNWaVpYSnVaWFJsY3k1cGJ5OXpaWEoyYVdObFlXTmpiM1Z1ZEM5elpXTnlaWFF1Ym1GdFpTSTZJbU5zZFhOMFpYSndaV1JwWVMxemVXNWphSEp2SWl3aWEzVmlaWEp1WlhSbGN5NXBieTl6WlhKMmFXTmxZV05qYjNWdWRDOXpaWEoyYVdObExXRmpZMjkxYm5RdWJtRnRaU0k2SW1Oc2RYTjBaWEp3WldScFlTMXplVzVqYUhKdklpd2lhM1ZpWlhKdVpYUmxjeTVwYnk5elpYSjJhV05sWVdOamIzVnVkQzl6WlhKMmFXTmxMV0ZqWTI5MWJuUXVkV2xrSWpvaVlUTTBaRGRsTW1FdE1XRmtOUzAwT0Roa0xXSTVZV0V0T0dZNU5qZ3labUV5TWpBMklpd2ljM1ZpSWpvaWMzbHpkR1Z0T25ObGNuWnBZMlZoWTJOdmRXNTBPbVJsWm1GMWJIUTZZMngxYzNSbGNuQmxaR2xoTFhONWJtTm9jbThpZlEuR2pBb1MxZ0RUdUdmSkd5UEJqWHpxcDRwa0ljMWpOX0dvUXZway1VeFE0OEdKUk9lSHFaZFdwZi1CeEZCMHdFUjd2ME9ub19EMGtndHRjRHJzZUluaGx2RVdHa3dwZHEyMVVUeHFhQ293aE1mMWsxdFk4ZVZCQzVBWTJqTVhPN0pMM05KM2xpU25LNFZWbjYtVlpEcXg3dTlxMXFFSE8tb3hubjNleklRSGtLSmFFei03SUlNSlJ5ZGN5R1lPZk9pUTFhbnZqa0ZpUm93VkRZSG1pM1Q0ZVBEbEtqTW9kU0VxTWxUYU9FcmF6YVl0TXJKdmdpYmRrZl9LQzFrVTdYYldaMGhIZHMtTFJCOHoyenV0QWFfZTcxbDNmTmxEWWdvMEdzYjA1d1B3anE1Mm1jc2hxWkEwbG1MdnI2bnkzVEJ6OTVsT3FSdmgxYWZpTmZyU1lHekpR"
  syncResources:
    - group: apps
      resources:
        - deployments
    - group: ""
      resources:
        - pods

# 过程报错(提示 crd 没有创建)
[root@master01 ~/clusterpedia/examples]# kubectl apply -f dce5-mmber-pediacluster.yaml 
error: resource mapping not found for name: "dce5-member" namespace: "" from "dce5-mmber-pediacluster.yaml": no matches for kind "PediaCluster" in version "cluster.clusterpedia.io/v1alpha2"
ensure CRDs are installed first

[root@master01 ~/clusterpedia/examples]# cd ..
[root@master01 ~/clusterpedia]# kubectl apply -f deploy/crds/cluster.clusterpedia.io_pediaclusters.yaml 
customresourcedefinition.apiextensions.k8s.io/pediaclusters.cluster.clusterpedia.io created

# 对接 dce5 成员集群
[root@master01 ~/clusterpedia/examples]# kubectl apply -f dce5-mmber-pediacluster.yaml 
pediacluster.cluster.clusterpedia.io/dce5-member created

# 对接 dce4.0.10 集群
[root@master01 ~/clusterpedia/examples]# kubectl apply -f  /root/clusterpedia-v0.5.0/examples/pediacluster-dce4010.yaml 
pediacluster.cluster.clusterpedia.io/dce4-010 created

```

### 4.3 状态检查

```shell
# 检查同步状态
[root@master01 ~/clusterpedia/examples]# kubectl get pediacluster -o wide 
NAME          READY   VERSION   APISERVER                  VALIDATED   SYNCHRORUNNING   CLUSTERHEALTHY
dce5-member   True    v1.24.7   https://10.29.15.79:6443   Validated   Running          Healthy

# 检查 mysql 数据
mysql> show databases;
+--------------------+
| Database           |
+--------------------+
| clusterpedia       |
| information_schema |
| mysql              |
| performance_schema |
| sys                |
+--------------------+
5 rows in set (0.03 sec)

mysql> use clusterpedia
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
mysql> SELECT * FROM clusterpedia.resources where resource = 'deployments' limit 2 \G
*************************** 1. row ***************************
              id: 1
           group: apps
         version: v1
        resource: deployments
            kind: Deployment
         cluster: dce5-member
       namespace: kube-system
            name: calico-kube-controllers
       owner_uid: 
             uid: ddc79a37-8d8f-4960-a187-c9d68a430f02
resource_version: 13743249
          object: {"kind": "Deployment", "spec": {"replicas": 1, "selector": {"matchLabels": {"k8s-app": "calico-kube-controllers"}}, "strategy": {"type": "Recreate"}, "template": {"spec": {"dnsPolicy": "ClusterFirst", "containers": [{"env": [{"name": "ENABLED_CONTROLLERS", "value": "node"}, {"name": "DATASTORE_TYPE", "value": "kubernetes"}], "name": "calico-kube-controllers", "image": "quay.m.daocloud.io/calico/kube-controllers:v3.23.3", "resources": {"limits": {"cpu": "1", "memory": "256M"}, "requests": {"cpu": "30m", "memory": "64M"}}, "livenessProbe": {"exec": {"command": ["/usr/bin/check-status", "-l"]}, "periodSeconds": 10, "timeoutSeconds": 1, "failureThreshold": 6, "successThreshold": 1, "initialDelaySeconds": 10}, "readinessProbe": {"exec": {"command": ["/usr/bin/check-status", "-r"]}, "periodSeconds": 10, "timeoutSeconds": 1, "failureThreshold": 3, "successThreshold": 1}, "imagePullPolicy": "IfNotPresent", "terminationMessagePath": "/dev/termination-log", "terminationMessagePolicy": "File"}], "hostNetwork": true, "tolerations": [{"key": "node-role.kubernetes.io/master", "effect": "NoSchedule"}, {"key": "node-role.kubernetes.io/control-plane", "effect": "NoSchedule"}], "nodeSelector": {"kubernetes.io/os": "linux"}, "restartPolicy": "Always", "schedulerName": "default-scheduler", "serviceAccount": "calico-kube-controllers", "securityContext": {}, "priorityClassName": "system-cluster-critical", "serviceAccountName": "calico-kube-controllers", "terminationGracePeriodSeconds": 30}, "metadata": {"name": "calico-kube-controllers", "labels": {"k8s-app": "calico-kube-controllers"}, "namespace": "kube-system", "creationTimestamp": null}}, "revisionHistoryLimit": 10, "progressDeadlineSeconds": 600}, "status": {"replicas": 1, "conditions": [{"type": "Progressing", "reason": "NewReplicaSetAvailable", "status": "True", "message": "ReplicaSet \"calico-kube-controllers-7cd4576599\" has successfully progressed.", "lastUpdateTime": "2022-10-29T07:37:57Z", "lastTransitionTime": "2022-10-29T07:36:30Z"}, {"type": "Available", "reason": "MinimumReplicasAvailable", "status": "True", "message": "Deployment has minimum availability.", "lastUpdateTime": "2023-01-06T03:37:48Z", "lastTransitionTime": "2023-01-06T03:37:48Z"}], "readyReplicas": 1, "updatedReplicas": 1, "availableReplicas": 1, "observedGeneration": 1}, "metadata": {"uid": "ddc79a37-8d8f-4960-a187-c9d68a430f02", "name": "calico-kube-controllers", "labels": {"k8s-app": "calico-kube-controllers"}, "namespace": "kube-system", "generation": 1, "annotations": {"deployment.kubernetes.io/revision": "1", "shadow.clusterpedia.io/cluster-name": "dce5-member"}, "resourceVersion": "13743249", "creationTimestamp": "2022-10-29T07:36:30Z"}, "apiVersion": "apps/v1"}
      created_at: 2022-10-29 07:36:30.000
       synced_at: 2023-03-20 06:06:44.674
      deleted_at: NULL
*************************** 2. row ***************************
              id: 2
           group: apps
         version: v1
        resource: deployments
            kind: Deployment
         cluster: dce5-member
       namespace: kube-system
            name: coredns
       owner_uid: 
             uid: 4fab46a9-5cc2-469a-b01d-f62f2ac6e586
resource_version: 39760205
          object: {"kind": "Deployment", "spec": {"replicas": 2, "selector": {"matchLabels": {"k8s-app": "kube-dns"}}, "strategy": {"type": "RollingUpdate", "rollingUpdate": {"maxSurge": "10%", "maxUnavailable": 0}}, "template": {"spec": {"volumes": [{"name": "config-volume", "configMap": {"name": "coredns", "items": [{"key": "Corefile", "path": "Corefile"}], "defaultMode": 420}}], "affinity": {"nodeAffinity": {"preferredDuringSchedulingIgnoredDuringExecution": [{"weight": 100, "preference": {"matchExpressions": [{"key": "node-role.kubernetes.io/control-plane", "values": [""], "operator": "In"}]}}]}, "podAntiAffinity": {"requiredDuringSchedulingIgnoredDuringExecution": [{"topologyKey": "kubernetes.io/hostname", "labelSelector": {"matchLabels": {"k8s-app": "kube-dns"}}}]}}, "dnsPolicy": "Default", "containers": [{"args": ["-conf", "/etc/coredns/Corefile"], "name": "coredns", "image": "k8s-gcr.m.daocloud.io/coredns/coredns:v1.8.6", "ports": [{"name": "dns", "protocol": "UDP", "containerPort": 53}, {"name": "dns-tcp", "protocol": "TCP", "containerPort": 53}, {"name": "metrics", "protocol": "TCP", "containerPort": 9153}], "resources": {"limits": {"memory": "300Mi"}, "requests": {"cpu": "100m", "memory": "70Mi"}}, "volumeMounts": [{"name": "config-volume", "mountPath": "/etc/coredns"}], "livenessProbe": {"httpGet": {"path": "/health", "port": 8080, "scheme": "HTTP"}, "periodSeconds": 10, "timeoutSeconds": 5, "failureThreshold": 10, "successThreshold": 1}, "readinessProbe": {"httpGet": {"path": "/ready", "port": 8181, "scheme": "HTTP"}, "periodSeconds": 10, "timeoutSeconds": 5, "failureThreshold": 10, "successThreshold": 1}, "imagePullPolicy": "IfNotPresent", "securityContext": {"capabilities": {"add": ["NET_BIND_SERVICE"], "drop": ["all"]}, "readOnlyRootFilesystem": true, "allowPrivilegeEscalation": false}, "terminationMessagePath": "/dev/termination-log", "terminationMessagePolicy": "File"}], "tolerations": [{"key": "node-role.kubernetes.io/master", "effect": "NoSchedule"}, {"key": "node-role.kubernetes.io/control-plane", "effect": "NoSchedule"}], "nodeSelector": {"kubernetes.io/os": "linux"}, "restartPolicy": "Always", "schedulerName": "default-scheduler", "serviceAccount": "coredns", "securityContext": {}, "priorityClassName": "system-cluster-critical", "serviceAccountName": "coredns", "terminationGracePeriodSeconds": 30}, "metadata": {"labels": {"k8s-app": "kube-dns"}, "annotations": {"createdby": "kubespray", "seccomp.security.alpha.kubernetes.io/pod": "runtime/default"}, "creationTimestamp": null}}, "revisionHistoryLimit": 10, "progressDeadlineSeconds": 600}, "status": {"replicas": 2, "conditions": [{"type": "Progressing", "reason": "NewReplicaSetAvailable", "status": "True", "message": "ReplicaSet \"coredns-58795d59cc\" has successfully progressed.", "lastUpdateTime": "2022-10-29T07:37:23Z", "lastTransitionTime": "2022-10-29T07:37:03Z"}, {"type": "Available", "reason": "MinimumReplicasAvailable", "status": "True", "message": "Deployment has minimum availability.", "lastUpdateTime": "2023-02-17T02:33:47Z", "lastTransitionTime": "2023-02-17T02:33:47Z"}], "readyReplicas": 2, "updatedReplicas": 2, "availableReplicas": 2, "observedGeneration": 2}, "metadata": {"uid": "4fab46a9-5cc2-469a-b01d-f62f2ac6e586", "name": "coredns", "labels": {"k8s-app": "kube-dns", "kubernetes.io/name": "coredns", "addonmanager.kubernetes.io/mode": "Reconcile"}, "namespace": "kube-system", "generation": 2, "annotations": {"deployment.kubernetes.io/revision": "1", "shadow.clusterpedia.io/cluster-name": "dce5-member"}, "resourceVersion": "39760205", "creationTimestamp": "2022-10-29T07:37:02Z"}, "apiVersion": "apps/v1"}
      created_at: 2022-10-29 07:37:02.000
       synced_at: 2023-03-20 06:06:44.698
      deleted_at: NULL
2 rows in set (0.00 sec)


[root@master01 ~/clusterpedia/examples]# kubectl get pediacluster -o wide 
NAME          READY   VERSION    APISERVER                   VALIDATED   SYNCHRORUNNING   CLUSTERHEALTHY
dce4-010      True    v1.18.20   https://10.29.16.27:16443   Validated   Running          Healthy
dce5-member   True    v1.24.7    https://10.29.15.79:6443    Validated   Running          Healthy


# 检查 mysql 数据
mysql> SELECT * FROM clusterpedia.resources where cluster = 'dce4-010' limit 1 \G
*************************** 1. row ***************************
              id: 54
           group: apps
         version: v1
        resource: deployments
            kind: Deployment
         cluster: dce4-010
       namespace: kube-system
            name: dce-prometheus
       owner_uid: 
             uid: cf53ad44-856d-4e3f-8129-113fa42af534
resource_version: 17190
          object: {"kind": "Deployment", "spec": {"replicas": 1, "selector": {"matchLabels": {"k8s-app": "dce-prometheus"}}, "strategy": {"type": "RollingUpdate", "rollingUpdate": {"maxSurge": 1, "maxUnavailable": 2}}, "template": {"spec": {"volumes": [{"name": "dce-metrics-server-secrets", "secret": {"secretName": "dce-prometheus", "defaultMode": 420}}, {"name": "config", "configMap": {"name": "dce-prometheus", "defaultMode": 420}}, {"name": "dce-certs", "hostPath": {"path": "/etc/daocloud/dce/certs", "type": ""}}], "affinity": {"nodeAffinity": {"requiredDuringSchedulingIgnoredDuringExecution": {"nodeSelectorTerms": [{"matchExpressions": [{"key": "node-role.kubernetes.io/master", "operator": "Exists"}]}]}}, "podAntiAffinity": {"requiredDuringSchedulingIgnoredDuringExecution": [{"topologyKey": "kubernetes.io/hostname", "labelSelector": {"matchExpressions": [{"key": "k8s-app", "values": ["dce-prometheus"], "operator": "In"}]}}]}}, "dnsPolicy": "ClusterFirst", "containers": [{"name": "dce-metrics-server", "image": "10.29.140.12/kube-system/dce-metrics-server:0.3.0", "ports": [{"name": "https", "protocol": "TCP", "containerPort": 6443}, {"name": "http", "protocol": "TCP", "containerPort": 8080}, {"name": "metrics", "protocol": "TCP", "containerPort": 9091}], "command": ["/usr/bin/server", "--hpa-version=v2beta1", "--secure-port=6443", "--tls-cert-file=/srv/kubernetes/server.cert", "--tls-private-key-file=/srv/kubernetes/server.key", "--prometheus-url=http://127.0.0.1:9090"], "resources": {"limits": {"cpu": "50m", "memory": "50Mi"}, "requests": {"cpu": "25m", "memory": "25Mi"}}, "volumeMounts": [{"name": "dce-metrics-server-secrets", "readOnly": true, "mountPath": "/srv/kubernetes/"}], "imagePullPolicy": "IfNotPresent", "terminationMessagePath": "/dev/termination-log", "terminationMessagePolicy": "File"}, {"args": ["--config.file=/prometheus/config/config.yml", "--storage.tsdb.path=/prometheus/data", "--web.listen-address=0.0.0.0:9090", "--storage.tsdb.retention.time=7d", "--web.enable-lifecycle"], "name": "dce-prometheus", "image": "10.29.140.12/kube-system/dce-prometheus:4.0.10-35699", "ports": [{"name": "web", "protocol": "TCP", "containerPort": 9090}], "command": ["/usr/local/bin/prometheus"], "resources": {"limits": {"cpu": "400m", "memory": "500Mi"}, "requests": {"cpu": "100m", "memory": "250Mi"}}, "volumeMounts": [{"name": "config", "mountPath": "/prometheus/config/"}, {"name": "dce-certs", "readOnly": true, "mountPath": "/etc/daocloud/dce/certs"}], "imagePullPolicy": "IfNotPresent", "terminationMessagePath": "/dev/termination-log", "terminationMessagePolicy": "File"}], "tolerations": [{"key": "node-role.kubernetes.io/master", "effect": "NoSchedule"}], "restartPolicy": "Always", "schedulerName": "default-scheduler", "serviceAccount": "dce-prometheus", "securityContext": {}, "priorityClassName": "system-cluster-critical", "serviceAccountName": "dce-prometheus", "terminationGracePeriodSeconds": 30}, "metadata": {"name": "dce-prometheus", "labels": {"k8s-app": "dce-prometheus"}, "namespace": "kube-system", "creationTimestamp": null}}, "revisionHistoryLimit": 10, "progressDeadlineSeconds": 600}, "status": {"replicas": 1, "conditions": [{"type": "Available", "reason": "MinimumReplicasAvailable", "status": "True", "message": "Deployment has minimum availability.", "lastUpdateTime": "2023-01-08T11:51:58Z", "lastTransitionTime": "2023-01-08T11:51:58Z"}, {"type": "Progressing", "reason": "NewReplicaSetAvailable", "status": "True", "message": "ReplicaSet \"dce-prometheus-59b9468478\" has successfully progressed.", "lastUpdateTime": "2023-01-08T13:11:43Z", "lastTransitionTime": "2023-01-08T13:11:43Z"}], "readyReplicas": 1, "updatedReplicas": 1, "availableReplicas": 1, "observedGeneration": 2}, "metadata": {"uid": "cf53ad44-856d-4e3f-8129-113fa42af534", "name": "dce-prometheus", "labels": {"k8s-app": "dce-prometheus", "app.kubernetes.io/managed-by": "Helm"}, "selfLink": "/apis/apps/v1/namespaces/kube-system/deployments/dce-prometheus", "namespace": "kube-system", "generation": 2, "annotations": {"meta.helm.sh/release-name": "dce-components", "meta.helm.sh/release-namespace": "kube-system", "deployment.kubernetes.io/revision": "1", "shadow.clusterpedia.io/cluster-name": "dce4-010", "dce-metrics-server.daocloud.io/collector-config": "{\"kind\": \"DCE-Metrics-Server\", \"parameters\": {\"address\": \"\"}}"}, "resourceVersion": "17190", "creationTimestamp": "2023-01-08T11:51:58Z"}, "apiVersion": "apps/v1"}
      created_at: 2023-01-08 11:51:58.000
       synced_at: 2023-03-20 06:23:59.262
      deleted_at: NULL
1 row in set (0.00 sec)
```

