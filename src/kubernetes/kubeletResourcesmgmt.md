## kubelet 资源预留及限制

### systemReserved

- `system-reserved` 用于为诸如 `sshd`、`udev` 等系统守护进程记述其资源预留值
- `system-reserved` 也应该为 `kernel` 预留 `内存`，因为目前 `kernel` 使用的内存并不记在 Kubernetes 的 Pod 上，也推荐为用户登录会话预留资源（systemd 体系中的 `user.slice`）

### kubeReserved

- `kube-reserved` 用来给诸如 `kubelet`、containerd、节点问题监测器等 Kubernetes 系统守护进程记述其资源预留值

### podPidsLimit

- `podPidsLimit` 用来给每个 Pod 中可使用的 PID 个数上限

### kubelet-config.yaml

```yaml
[root@worker-node-1 ~]# cat /etc/kubernetes/kubelet-config.yaml 
apiVersion: kubelet.config.k8s.io/v1beta1
kind: KubeletConfiguration
nodeStatusUpdateFrequency: "10s"
failSwapOn: True
authentication:
  anonymous:
    enabled: false
  webhook:
    enabled: True
  x509:
    clientCAFile: /etc/kubernetes/ssl/ca.crt
systemReserved:         # 给系统组件预留、生产计划 4c、8g
  cpu: 1000m
  memory: 2048Mi
kubeReserved:           # 给 kube 组件预留、生产计划 12c、24g
  cpu: 1000m
  memory: 2048Mi
authorization:
  mode: Webhook
staticPodPath: /etc/kubernetes/manifests
cgroupDriver: systemd
containerLogMaxFiles: 5
containerLogMaxSize: 10Mi
maxPods: 115
podPidsLimit: 12000        # 灵雀默认值 10000、为了保证组件及业务的稳定将其 +2000
address: 10.29.26.200
readOnlyPort: 0
healthzPort: 10248
healthzBindAddress: 127.0.0.1
kubeletCgroups: /system.slice/kubelet.service
clusterDomain: cluster.local
protectKernelDefaults: true
rotateCertificates: true
clusterDNS:
- 10.233.0.3
resolvConf: "/etc/resolv.conf"
eventRecordQPS: 5
shutdownGracePeriod: 60s
shutdownGracePeriodCriticalPods: 20s
```

```shell
# 默认值
Capacity:
  cpu:                14
  ephemeral-storage:  151094724Ki
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             28632864Ki
  pods:               115
Allocatable:
  cpu:                14
  ephemeral-storage:  139248897408
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             28530464Ki
  pods:               115

# 更改后
Capacity:
  cpu:                14
  ephemeral-storage:  151094724Ki
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             28632864Ki
  pods:               115
Allocatable:
  cpu:                12
  ephemeral-storage:  139248897408
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             24336160Ki
  pods:               115
```



