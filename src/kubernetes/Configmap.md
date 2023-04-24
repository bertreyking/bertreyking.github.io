# ConfigMaps

## [ConfigMap][ConfigMaps] 是什么？

- 非 🔐 数据以 `key:value` 的形式保存
-  [Pods](https://kubernetes.io/zh-cn/docs/concepts/workloads/pods/) 可以将其用作环境变量、命令行参数或者存储卷中的配置文件
- 将你的环境配置信息和 [容器镜像](https://kubernetes.io/zh-cn/docs/reference/glossary/?all=true#term-image) 进行解耦，便于应用配置的修改及多云场景下应用的部署
- 与 ConfigMap 所对应的就是 [Secret](https://kubernetes.io/zh-cn/docs/concepts/configuration/secret/) (加密数据)

## ConfigMap 的特性

- 名字必须是一个合法的 [DNS 子域名](https://kubernetes.io/zh-cn/docs/concepts/overview/working-with-objects/names#dns-subdomain-names)
- `data` 或 `binaryData` 字段下面的键名称必须由字母数字字符或者 `-`、`_` 或 `.` 组成、键名不可有重叠
-  v1.19 开始，可以添加`immutable`字段到 ConfigMap 定义中，来创建[不可变更的 ConfigMap](https://kubernetes.io/zh-cn/docs/concepts/configuration/configmap/#configmap-immutable)
- ConfigMap 需要跟引用它的资源在同一命名空间下
- ConfigMap 更新新，应用会自动更新，kubelet 会定期检索配置是否最新
- [SubPath](https://kubernetes.io/zh-cn/docs/concepts/storage/volumes#using-subpath) 卷挂载的容器将不会收到 ConfigMap 的更新，需要重启应用

## 如何使用 ConfigMap

- 创建一个 ConfigMap 资源或者使用现有的 ConfigMap，多个 Pod 可以引用同一个 ConfigMap 资源

- 修改 Pod 定义，在 `spec.volumes[]` 下添加一个卷。 为该卷设置任意名称，之后将

- 为每个需要该 ConfigMap 的容器添加一个 volumeMount

  1. 设置`.spec.containers[].volumeMounts[].name`定义卷挂载点的名称

  2. 设置 `.spec.containers[].volumeMounts[].readOnly=true` 
  3. 设置 `.spec.containers[].volumeMounts[].mountPath` 定义一个未使用的目录

- 更改你的 Yaml 或者命令行，以便程序能够从该目录中查找文件。ConfigMap 中的每个 `data` 键会变成 `mountPath` 下面的一个文件名

## 场景

### 基于文件创建 ConfigMap

使用 `kubectl create configmap` 基于单个文件或多个文件创建 ConfigMap

``` shell
# 文件如下：
[root@master01 ~]# cat /etc/resolv.conf
nameserveer 1.1.1.1

# 创建 ConfigMap
[root@master01 ~]# kubectl create configmap dnsconfig --from-file=resolve.conf
[root@master01 ~]# kubectl get configmap dnsconfig -o yaml 
apiVersion: v1
data:
  resolve.conf: |
    nameserveer 1.1.1.1
kind: ConfigMap
metadata:
  name: dnsconfig
  namespace: default
```

Deployment 使用所创建的 ConfigMap 资源 [Configure a Pod to Use a ConfigMap][Configure a Pod to Use a ConfigMap]

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    app: dao-2048-2-test
  name: dao-2048-2-test-dao-2048
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      component: dao-2048-2-test-dao-2048
  strategy:
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 25%
    type: RollingUpdate
  template:
    metadata:
      labels:
        app: dao-2048-2-test
      name: dao-2048-2-test-dao-2048
    spec:
      affinity:
        nodeAffinity:
          requiredDuringSchedulingIgnoredDuringExecution:
            nodeSelectorTerms:
            - matchExpressions:
              - key: kubernetes.io/os
                operator: In
                values:
                - linux
              - key: kubernetes.io/arch
                operator: In
                values:
                - amd64
      containers:
      - image: x.x.x.x/dao-2048/dao-2048:latest
        imagePullPolicy: Always
        name: dao-2048-2-test-dao-2048
        resources:
          limits:
            cpu: 100m
            memory: "104857600"
          requests:
            cpu: 100m
            memory: "104857600"
        terminationMessagePath: /dev/termination-log
        terminationMessagePolicy: File
        volumeMounts:
        - mountPath: /etc/resolv.conf
          name: configmap-dns
          subPath: resolv.conf
      dnsConfig:
        nameservers:
        - 192.0.2.1
      dnsPolicy: None
      imagePullSecrets:
      - name: dao-2048-2-test-dao-2048-10.29.140.12
      restartPolicy: Always
      schedulerName: default-scheduler
      securityContext: {}
      terminationGracePeriodSeconds: 30
      volumes:
      - configMap:
          defaultMode: 420
          items:
          - key: resolve.conf
            path: resolv.conf
          name: dnsconfig
        name: configmap-dns
```

配置说明

```yaml
# volumeMounts
volumeMounts:
- mountPath: /etc/resolv.conf     # 定义容器内挂载路径
  name: configmap-dns             # 定义卷挂载点名称，以便 volumes 使用该名称挂载 configmap 资源
  subPath: resolv.conf            # 指定所引用的卷内的子文件/子路径，而不是其根路径
  
# volumes
volumes:
- name: configmap-dns
  configMap:
    name: dnsconfig               # 引用所创建的 configmap 资源 dnsconfig
    defaultMode: 420
    items:                        # 引用对应的 key，将其创建问文件
    - key: resolve.conf           # .data.resolve.conf
      path: resolv.conf           # 将 resolve.conf `key` 创建成 resolv.conf 文件
```

疑问 (为什么使用了 dnsConfig 的前提下，又将 resolv.conf 以 configmap 的形式注入容器中呢)

1. 做测试，看 k8s 下以哪个配置生效，结果是 configmap 的形 会覆盖 yaml 定义的 dnsConfig 配置
2. 在多云场景中，需要区分出应用配置的差异化，所以才考虑使用 configmap 的形式实现，在单一环境中推荐在 yaml 中直接定义 dnsCofnig

```yaml
dnsPolicy: None
dnsConfig:
  nameservers:
  - 192.0.2.1
dnsPolicy: None
```

[ConfigMaps]: https://kubernetes.io/docs/concepts/configuration/configmap/
[Configure a Pod to Use a ConfigMap]: https://kubernetes.io/docs/tasks/configure-pod-container/configure-pod-configmap/

