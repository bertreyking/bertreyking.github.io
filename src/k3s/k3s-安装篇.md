# k3s 离线安装篇

## 1. [containerd runc cni](https://github.com/containerd/containerd/blob/main/docs/getting-started.md) 安装(该章节忽略，k3s 自带 containerd)

### 1.1 containerd

```shell
- 解压并将二进制文件放入 /usr/local/bin/ 目录下
tar Cxzvf /usr/local containerd-1.7.0-linux-arm64.tar.gz
bin/
bin/containerd-shim-runc-v2
bin/containerd-shim
bin/ctr
bin/containerd-shim-runc-v1
bin/containerd
bin/containerd-stress

- 配置systemd
vi /usr/lib/systemd/system/containerd.service
[Unit]
Description=containerd container runtime
Documentation=https://containerd.io
After=network.target local-fs.target

[Service]
#uncomment to enable the experimental sbservice (sandboxed) version of containerd/cri integration
#Environment="ENABLE_CRI_SANDBOXES=sandboxed"
ExecStartPre=-/sbin/modprobe overlay
ExecStart=/usr/local/bin/containerd

Type=notify
Delegate=yes
KillMode=process
Restart=always
RestartSec=5
# Having non-zero Limit*s causes performance problems due to accounting overhead
# in the kernel. We recommend using cgroups to do container-local accounting.
LimitNPROC=infinity
LimitCORE=infinity
LimitNOFILE=infinity
# Comment TasksMax if your systemd version does not supports it.
# Only systemd 226 and above support this version.
TasksMax=infinity
OOMScoreAdjust=-999

[Install]
WantedBy=multi-user.target

- 启动
systemctl daemon-reload
systemctl enable --now containerd

- 生成默认配置文件
mkdir -p /etc/containerd/
containerd config default >> /etc/containerd/config.toml
```

### 1.2 runc

```shell
install -m 755 runc.arm64 /usr/local/sbin/runc
```

### 1.3 cni

```shell
mkdir -p /opt/cni/bin
tar Cxzvf /opt/cni/bin cni-plugins-linux-arm64-v1.2.0.tgz
./
./macvlan
./static
./vlan
./portmap
./host-local
./vrf
./bridge
./tuning
./firewall
./host-device
./sbr
./loopback
./dhcp
./ptp
./ipvlan
./bandwidth
```

## 2. k3s 安装

### 2.1 准备[介质](https://github.com/k3s-io/k3s/releases)

```shell
- 手动部署镜像(如果是用私有仓库，cri 调整默认仓库地址即可)
mkdir -p /var/lib/rancher/k3s/agent/images/
cp /root/k3s/k3s-airgap-images-arm64.tar /var/lib/rancher/k3s/agent/images/

- k3s 二进制文件
chmod +x k3s-arm64
cp k3s-arm64 /usr/local/bin/k3s 

[root@k3s-master k3s]# k3s --version 
k3s version v1.26.2+k3s1 (ea094d1d)
go version go1.19.6
```

### 2.2 安装 master 节点

```shell
- 下载安装脚本
curl https://get.k3s.io/ -o install.sh 
chmod +x install.sh

- 跳过下载镜像
INSTALL_K3S_SKIP_DOWNLOAD=true

- 安装
[root@k3s-master k3s]# INSTALL_K3S_SKIP_DOWNLOAD=true ./install.sh
[INFO]  Skipping k3s download and verify
[INFO]  Skipping installation of SELinux RPM
[INFO]  Creating /usr/local/bin/kubectl symlink to k3s
[INFO]  Creating /usr/local/bin/crictl symlink to k3s
[INFO]  Skipping /usr/local/bin/ctr symlink to k3s, already exists
[INFO]  Creating killall script /usr/local/bin/k3s-killall.sh
[INFO]  Creating uninstall script /usr/local/bin/k3s-uninstall.sh
[INFO]  env: Creating environment file /etc/systemd/system/k3s.service.env
[INFO]  systemd: Creating service file /etc/systemd/system/k3s.service
[INFO]  systemd: Enabling k3s unit
Created symlink /etc/systemd/system/multi-user.target.wants/k3s.service → /etc/systemd/system/k3s.service.
[INFO]  systemd: Starting k3s

- 检查节点/组件状态
[root@k3s-master k3s]# kubectl get node
NAME         STATUS   ROLES                  AGE   VERSION
k3s-master   Ready    control-plane,master   55s   v1.26.2+k3s1
[root@k3s-master k3s]# kubectl get pod -A -o wide 
NAMESPACE     NAME                                      READY   STATUS      RESTARTS   AGE   IP          NODE         NOMINATED NODE   READINESS GATES
kube-system   coredns-5c6b6c5476-tz8jn                  1/1     Running     0          48s   10.42.0.4   k3s-master   <none>           <none>
kube-system   local-path-provisioner-5d56847996-n27l6   1/1     Running     0          48s   10.42.0.5   k3s-master   <none>           <none>
kube-system   helm-install-traefik-crd-cnjhj            0/1     Completed   0          49s   10.42.0.3   k3s-master   <none>           <none>
kube-system   metrics-server-7b67f64457-bzgdt           1/1     Running     0          48s   10.42.0.6   k3s-master   <none>           <none>
kube-system   svclb-traefik-569139e2-rgdqr              2/2     Running     0          28s   10.42.0.7   k3s-master   <none>           <none>
kube-system   traefik-56b8c5fb5c-g5ggl                  1/1     Running     0          28s   10.42.0.8   k3s-master   <none>           <none>
kube-system   helm-install-traefik-sqfzx                0/1     Completed   2          49s   10.42.0.2   k3s-master   <none>           <none>
```

### 2.3 接入 agent 节点

```shell
- 参考前面步骤
1. containerd runc cni 安装
2.1 准备介质
2.2 安装 master 节点
    -下载脚本 
    - 安装

- 查看 master 节点 token
来自服务器的令牌通常位于/var/lib/rancher/k3s/server/token
[root@k3s-master k3s]# cat /var/lib/rancher/k3s/server/token 
K108226e8e6a76a0b1f8586b2f191ad16e496d190854d08310b07168c2cfa5f0bca::server:0c8280fe93b598d279470bf8648b2344

- 接入命令
INSTALL_K3S_SKIP_DOWNLOAD=true \
K3S_URL=https://10.29.33.52:6443 \
K3S_TOKEN=K108226e8e6a76a0b1f8586b2f191ad16e496d190854d08310b07168c2cfa5f0bca::server:0c8280fe93b598d279470bf8648b2344 \
./install.sh
[INFO]  Skipping k3s download and verify
[INFO]  Skipping installation of SELinux RPM
[INFO]  Creating /usr/local/bin/kubectl symlink to k3s
[INFO]  Creating /usr/local/bin/crictl symlink to k3s
[INFO]  Skipping /usr/local/bin/ctr symlink to k3s, already exists
[INFO]  Creating killall script /usr/local/bin/k3s-killall.sh
[INFO]  Creating uninstall script /usr/local/bin/k3s-agent-uninstall.sh
[INFO]  env: Creating environment file /etc/systemd/system/k3s-agent.service.env
[INFO]  systemd: Creating service file /etc/systemd/system/k3s-agent.service
[INFO]  systemd: Enabling k3s-agent unit
Created symlink /etc/systemd/system/multi-user.target.wants/k3s-agent.service → /etc/systemd/system/k3s-agent.service.
[INFO]  systemd: Starting k3s-agent

- 检查
[root@k3s-master k3s]# kubectl get node -o wide 
NAME         STATUS   ROLES                  AGE     VERSION        INTERNAL-IP   EXTERNAL-IP   OS-IMAGE                                  KERNEL-VERSION                     CONTAINER-RUNTIME
k3s-master   Ready    control-plane,master   9m56s   v1.26.2+k3s1   10.29.33.52   <none>        Kylin Linux Advanced Server V10 (Sword)   4.19.90-25.24.v2101.ky10.aarch64   containerd://1.6.15-k3s1
k3s-agent    Ready    <none>                 42s     v1.26.2+k3s1   10.29.33.54   <none>        Kylin Linux Advanced Server V10 (Sword)   4.19.90-25.24.v2101.ky10.aarch64   containerd://1.6.15-k3s1
[root@k3s-master k3s]# kubectl get pod -A -o wide
NAMESPACE     NAME                                      READY   STATUS      RESTARTS   AGE     IP          NODE         NOMINATED NODE   READINESS GATES
kube-system   coredns-5c6b6c5476-tz8jn                  1/1     Running     0          9m46s   10.42.0.4   k3s-master   <none>           <none>
kube-system   local-path-provisioner-5d56847996-n27l6   1/1     Running     0          9m46s   10.42.0.5   k3s-master   <none>           <none>
kube-system   helm-install-traefik-crd-cnjhj            0/1     Completed   0          9m47s   10.42.0.3   k3s-master   <none>           <none>
kube-system   metrics-server-7b67f64457-bzgdt           1/1     Running     0          9m46s   10.42.0.6   k3s-master   <none>           <none>
kube-system   svclb-traefik-569139e2-rgdqr              2/2     Running     0          9m26s   10.42.0.7   k3s-master   <none>           <none>
kube-system   traefik-56b8c5fb5c-g5ggl                  1/1     Running     0          9m26s   10.42.0.8   k3s-master   <none>           <none>
kube-system   helm-install-traefik-sqfzx                0/1     Completed   2          9m47s   10.42.0.2   k3s-master   <none>           <none>
kube-system   svclb-traefik-569139e2-4tsz4              2/2     Running     0          44s     10.42.1.2   k3s-agent    <none>           <none>
```

## 3. k8s-dashboard 安装

```
- 安装
[root@k3s-master ~]# GITHUB_URL=https://github.com/kubernetes/dashboard/releases
[root@k3s-master ~]# VERSION_KUBE_DASHBOARD=$(curl -w '%{url_effective}' -I -L -s -S ${GITHUB_URL}/latest -o /dev/null | sed -e 's|.*/||')
[root@k3s-master ~]# sudo k3s kubectl create -f https://raw.githubusercontent.com/kubernetes/dashboard/${VERSION_KUBE_DASHBOARD}/aio/deploy/recommended.yaml
namespace/kubernetes-dashboard created
serviceaccount/kubernetes-dashboard created
service/kubernetes-dashboard created
secret/kubernetes-dashboard-certs created
secret/kubernetes-dashboard-csrf created
secret/kubernetes-dashboard-key-holder created
configmap/kubernetes-dashboard-settings created
role.rbac.authorization.k8s.io/kubernetes-dashboard created
clusterrole.rbac.authorization.k8s.io/kubernetes-dashboard created
rolebinding.rbac.authorization.k8s.io/kubernetes-dashboard created
clusterrolebinding.rbac.authorization.k8s.io/kubernetes-dashboard created
deployment.apps/kubernetes-dashboard created
service/dashboard-metrics-scraper created
deployment.apps/dashboard-metrics-scraper created

- 创建 admin-user 的 serviceaccount
[root@k3s-master k8s-dashboard]# kubectl apply -f admin-user.yaml 
serviceaccount/admin-user created

- 创建 clusterrolebinding
vi admin-user-clusterrolebinding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-user
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin-user
  namespace: kubernetes-dashboard
  
[root@k3s-master k8s-dashboard]# kubectl apply -f admin-user-clusterrolebinding.yaml 
clusterrolebinding.rbac.authorization.k8s.io/admin-user created

- 创建 token
[root@k3s-master k8s-dashboard]# k3s kubectl create token admin-user -n kubernetes-dashboard
eyJhbGciOiJSUzI1NiIsImtpZCI6IkZQY0NuTGh5Vy1FMEdWb3hlQk4tWmpJZ2E3WW9CM2ZKNURQejRoX1hFalkifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiLCJrM3MiXSwiZXhwIjoxNjc5MDY2MTkzLCJpYXQiOjE2NzkwNjI1OTMsImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsInNlcnZpY2VhY2NvdW50Ijp7Im5hbWUiOiJhZG1pbi11c2VyIiwidWlkIjoiMjAyZDdlZTUtNjg3MC00YjgxLTljYzktM2FlNWNhNTkyYjBjIn19LCJuYmYiOjE2NzkwNjI1OTMsInN1YiI6InN5c3RlbTpzZXJ2aWNlYWNjb3VudDprdWJlcm5ldGVzLWRhc2hib2FyZDphZG1pbi11c2VyIn0.tH_jW4FbuWzu9qcPsBUaUjTNOIaaahY5uV0svTiV_9V0BnzrYgFFe7czhIOkoluLmWnbBwxv1xCp4rwR42Vkpd99gHd8nfQAHhCzk2pypomF9gyr2UeKF1SvcbY4PXbOYaqJ3G-CX9l8uHQCvG3Uev70Xzy6eouDegeEsjfo_h7l1M3xfMf9KQ0x-1ErLt9sm5nL0dO0B9nagcgRZObk-RlwP7kT4MwJ4EF6anjxlfJ7GX-HWwrdodNCHqxX-zkM-K1v0Slzvn0jMif01G6d7uu8CyW18xsP65XwW2hwSpcvpe9VoZYKkhRDhQVz83UtPqPZF9BdqmOVBKp6-Ucxxw

- 检查发现 imagepullfailed，手动 pull 即可(dockerhub 国内直通)
ctr images pull docker.io/kubernetesui/dashboard:v.2.7.0
ctr images pull docker.io/kubernetesui/metrics-scraper:v1.0.8
```



## 4. traefik 使用

### 4.1 ui 调试 ([ingressRoute](https://doc.traefik.io/traefik/getting-started/install-traefik/#exposing-the-traefik-dashboard)、[dashboard](https://doc.traefik.io/traefik/getting-started/install-traefik/#exposing-the-traefik-dashboard))

```shell
- 修改 traefik 的 ingressRoute 规则 （ entryPoints: - web，默认是 trarfik 导致无法访问）
[root@k3s-master manifests]# kubectl get ingressroute -n kube-system -o yaml 
apiVersion: v1
items:
- apiVersion: traefik.containo.us/v1alpha1
  kind: IngressRoute
  metadata:
    annotations:
      helm.sh/hook: post-install,post-upgrade
      meta.helm.sh/release-name: traefik
      meta.helm.sh/release-namespace: kube-system
    creationTimestamp: "2023-03-17T06:43:38Z"
    generation: 8
    labels:
      app.kubernetes.io/instance: traefik-kube-system
      app.kubernetes.io/managed-by: Helm
      app.kubernetes.io/name: traefik
      helm.sh/chart: traefik-20.3.1_up20.3.0
    name: traefik-dashboard
    namespace: kube-system
    resourceVersion: "2722"
    uid: 7360d929-ab7a-45a8-ba8d-7ca60e586fb5
  spec:
    entryPoints:
    - web # 默认是 traefik 会导致无法访问 UI
    routes:
    - kind: Rule
      # 默认不带 Host，用 IP 访问即可  PathPrefix(`/dashboard`) || PathPrefix(`/api`)
      match: Host(`mwb.k3straefik.com`) && (PathPrefix(`/dashboard`) || PathPrefix(`/api`))
      services:
      - kind: TraefikService
        name: api@internal
kind: List
metadata:
  resourceVersion: ""
```

### 4.2 UI 页面

- 域名访问 http://mwb.k3straefik.com/dashboard/

![image-20230317161150720](/Users/kingskye/Library/Application Support/typora-user-images/image-20230317161150720.png)

## 附录

### - 说明

```shell
- 默认配置文件目录
/var/lib/rancher/k3s/server/

- manifests
各组件的 yaml 文件，k3s dameon 服务重启后会覆盖此文件

- token
节点接入使用

- static 
traefik 的 helm 模版文件

- 组件
coredns、traefik、local-storage和metrics-server、servicelbLoadBalancer

- 禁用组件的部署
--disable

- .skip 的神奇支持
前面说过，重启会导致 manifests 下面的资源全部还原(如果有修改)，那么可以用过创建某个资源的 skip 文件，来规避这种问题
traefik.yaml.skip # 表示跳过对该资源的覆盖

```

### - kubectl 自动补全

```shell
yum install bash-completion -y
source /usr/share/bash-completion/bash_completion
echo 'source <(kubectl completion bash)' >>~/.bashrc
echo 'source <(kubectl completion bash)' >>~/.bashrc
source ~/.bashrc
kubectl completion bash >/etc/bash_completion.d/kubectl
```

