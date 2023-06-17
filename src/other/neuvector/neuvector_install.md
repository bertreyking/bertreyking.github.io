# NeuVector 安装

## 添加 [NeuVector][1] 的 repo 及检索版本

```shell
[root@master01 ~]# helm repo add neuvector https://neuvector.github.io/neuvector-helm/
"neuvector" has been added to your repositories
[root@master01 ~]# helm search repo neuvector/core
NAME            CHART VERSION   APP VERSION     DESCRIPTION                             
neuvector/core  2.4.5           5.1.3           Helm chart for NeuVector's core services
[root@master01 ~]# helm search repo neuvector/core -l
NAME            CHART VERSION   APP VERSION     DESCRIPTION                                       
neuvector/core  2.4.5           5.1.3           Helm chart for NeuVector's core services          
neuvector/core  2.4.4           5.1.3           Helm chart for NeuVector's core services          
neuvector/core  2.4.3           5.1.2           Helm chart for NeuVector's core services          
neuvector/core  2.4.2           5.1.1           Helm chart for NeuVector's core services          
neuvector/core  2.4.1           5.1.0           Helm chart for NeuVector's core services          
neuvector/core  2.4.0           5.1.0           Helm chart for NeuVector's core services          
neuvector/core  2.2.5           5.0.5           Helm chart for NeuVector's core services          
neuvector/core  2.2.4           5.0.4           Helm chart for NeuVector's core services          
neuvector/core  2.2.3           5.0.3           Helm chart for NeuVector's core services          
neuvector/core  2.2.2           5.0.2           Helm chart for NeuVector's core services          
neuvector/core  2.2.1           5.0.1           Helm chart for NeuVector's core services          
neuvector/core  2.2.0           5.0.0           Helm chart for NeuVector's core services          
neuvector/core  1.9.2           4.4.4-s2        Helm chart for NeuVector's core services          
neuvector/core  1.9.1           4.4.4           Helm chart for NeuVector's core services          
neuvector/core  1.9.0           4.4.4           Helm chart for NeuVector's core services          
neuvector/core  1.8.9           4.4.3           Helm chart for NeuVector's core services          
neuvector/core  1.8.8           4.4.2           Helm chart for NeuVector's core services          
neuvector/core  1.8.7           4.4.1           Helm chart for NeuVector's core services          
neuvector/core  1.8.6           4.4.0           Helm chart for NeuVector's core services          
neuvector/core  1.8.5           4.3.2           Helm chart for NeuVector's core services          
neuvector/core  1.8.4           4.3.2           Helm chart for NeuVector's core services          
neuvector/core  1.8.3           4.3.2           Helm chart for NeuVector's core services          
neuvector/core  1.8.2           4.3.1           Helm chart for NeuVector's core services          
neuvector/core  1.8.0           4.3.0           Helm chart for NeuVector's core services          
neuvector/core  1.7.7           4.2.2           Helm chart for NeuVector's core services          
neuvector/core  1.7.6           4.2.2           Helm chart for NeuVector's core services          
neuvector/core  1.7.5           4.2.0           Helm chart for NeuVector's core services          
neuvector/core  1.7.2           4.2.0           Helm chart for NeuVector's core services          
neuvector/core  1.7.1           4.2.0           Helm chart for NeuVector's core services          
neuvector/core  1.7.0           4.0.0           Helm chart for NeuVector's core services          
neuvector/core  1.6.9           4.0.0           Helm chart for NeuVector's core services          
neuvector/core  1.6.8           4.0.0           Helm chart for NeuVector's core services          
neuvector/core  1.6.7           4.0.0           Helm chart for NeuVector's core services          
neuvector/core  1.6.6           4.0.0           Helm chart for NeuVector's core services          
neuvector/core  1.6.5           4.0.0           Helm chart for NeuVector's core services          
neuvector/core  1.6.4           4.0.0           Helm chart for NeuVector's core services          
neuvector/core  1.6.1           4.0.0           NeuVector Full Lifecycle Container Security Pla...
```

## 创建 namespace 及安装

```shell
[root@master01 ~]# kubectl create namespace neuvector
namespace/neuvector created
[root@master01 ~]# kubectl label  namespace neuvector "pod-security.kubernetes.io/enforce=privileged"
namespace/neuvector labeled
[root@master01 ~]# helm install neuvector --namespace neuvector --create-namespace neuvector/core
NAME: neuvector
LAST DEPLOYED: Sat Jun 17 17:40:43 2023
NAMESPACE: neuvector
STATUS: deployed
REVISION: 1
TEST SUITE: None
NOTES:
Get the NeuVector URL by running these commands:
  NODE_PORT=$(kubectl get --namespace neuvector -o jsonpath="{.spec.ports[0].nodePort}" services neuvector-service-webui)
  NODE_IP=$(kubectl get nodes --namespace neuvector -o jsonpath="{.items[0].status.addresses[0].address}")
  echo https://$NODE_IP:$NODE_PORT
 
[root@master01 ~]# NODE_PORT=$(kubectl get --namespace neuvector -o jsonpath="{.spec.ports[0].nodePort}" services neuvector-service-webui)
[root@master01 ~]# NODE_IP=$(kubectl get nodes --namespace neuvector -o jsonpath="{.items[0].status.addresses[0].address}")
[root@master01 ~]#  echo https://$NODE_IP:$NODE_PORT
https://10.2x.16.x:30196
```

## 依赖镜像

```yaml
docker.io/neuvector/controller:5.1.3
docker.io/neuvector/enforcer:5.1.3
docker.io/neuvector/manager:5.1.3
docker.io/neuvector/scanner:latest
```

## 登录UI

- 默认：admin/admin

![NeuVector](/png/neuvector_ui.jpg)

[1]:https://github.com/neuvector/neuvector-helm
