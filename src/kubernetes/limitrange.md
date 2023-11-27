# LimitRange

## pod [资源限额](https://kubernetes.io/zh-cn/docs/concepts/policy/limit-range/)

[Pod](https://kubernetes.io/zh-cn/docs/concepts/workloads/pods/) 最多能够使用命名空间的资源配额所定义的 CPU 和内存用量

## namespace - resourceQuotas资源配额

```yaml
[root@g-master1 ~]# kubectl get resourcequotas -n mawb -o yaml  quota-mawb 
apiVersion: v1
kind: ResourceQuota
metadata:
  creationTimestamp: "2023-11-27T05:16:16Z"
  name: quota-mawb
  namespace: mawb
  resourceVersion: "14278163"
  uid: 60ae6d65-5ce6-4f8f-bee2-ec0db19a9785
spec:
  hard:  # 限制改 ns 下可以使用的资源、cpu、memory 哪个先到就先限制哪个资源
    limits.cpu: "1"
    limits.memory: "1073741824"
    requests.cpu: "1"
    requests.memory: "1073741824"
status:
  hard:
    limits.cpu: "1"
    limits.memory: "1073741824"
    requests.cpu: "1"
    requests.memory: "1073741824"
  used:  # 当前 ns 下已经使用的资源、这里看 memory 已经到配额，再起新的 pod，会导致启动失败
    limits.cpu: 500m
    limits.memory: 1Gi
    requests.cpu: 500m
    requests.memory: 1Gi
```

## pod - rangeLimit 资源限额

```yaml
[root@g-master1 ~]# kubectl get limitranges -n mawb -o yaml limits-mawb 
apiVersion: v1
kind: LimitRange
metadata:
  creationTimestamp: "2023-11-27T05:16:16Z"
  name: limits-mawb
  namespace: mawb
  resourceVersion: "14265593"
  uid: 233b6dc7-e12a-4f2d-88f2-7c923a5cac7b
spec:
  limits:
  - default:  # 定制默认限制
      cpu: "1"
      memory: "1073741824"
    defaultRequest:  # 定义默认请求  
      cpu: 500m
      memory: 524288k
    type: Container
```

## 示例应用

```shell
# deployment 副本数
[root@g-master1 ~]# kubectl get deployments.apps -n mawb 
NAME            READY   UP-TO-DATE   AVAILABLE   AGE
resources-pod   2/4     0            2           33m

      resources:
        limits:
          cpu: 250m
          memory: 512Mi
        requests:
          cpu: 250m
          memory: 512Mi

# pod 列表数
[root@g-master1 ~]# kubectl get pod -n mawb 
NAME                             READY   STATUS    RESTARTS   AGE
resources-pod-6b678fdc9f-957ft   1/1     Running   0          29m
resources-pod-6b678fdc9f-vngq7   1/1     Running   0          29m

# 新的 pod 启动报错、提示新的副本没有内存可用
kubectl describe rs -n mawb resources-pod-5b67cf49cf 
Warning  FailedCreate 15m replicaset-controller  Error creating: pods "resources-pod-5b67cf49cf-6k6r5" is forbidden: exceeded quota: quota-mawb
requested: limits.cpu=1,limits.memory=1073741824,requests.memory=524288k # 需要在请求 512m 内存
used: limits.cpu=500m,limits.memory=1Gi,requests.memory=1Gi  # 已用 cpu 500m、memory 1g
limited: limits.cpu=1,limits.memory=1073741824,requests.memory=1073741824  # 限制 cpu 1c、memory 1g
```



