#  VictoriaMetrics

- [helm-install](https://docs.victoriametrics.com/helm/)
- [operator-install](https://docs.victoriametrics.com/operator/)

## 通过 operator 安装 VictoriaMetrics

### 安装 operator
1. 下载最新版本 operator 相关的 crd
```shell
export VM_OPERATOR_VERSION=$(basename $(curl -fs -o /dev/null -w %{redirect_url} https://github.com/VictoriaMetrics/operator/releases/latest));
echo "VM_OPERATOR_VERSION=$VM_OPERATOR_VERSION";

wget -O operator-and-crds.yaml \
  "https://github.com/VictoriaMetrics/operator/releases/download/$VM_OPERATOR_VERSION/install-no-webhook.yaml";

# Output:
# VM_OPERATOR_VERSION=v0.56.0
```
2. 安装 crd 和 operator
```shell
[root@mwb-k8s-master-test01 vm]# kubectl apply -f operator-and-crds.yaml 
namespace/vm created
customresourcedefinition.apiextensions.k8s.io/vlagents.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vlclusters.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vlogs.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vlsingles.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vmagents.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vmalertmanagerconfigs.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vmalertmanagers.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vmalerts.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vmanomalies.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vmauths.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vmclusters.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vmnodescrapes.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vmpodscrapes.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vmprobes.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vmrules.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vmscrapeconfigs.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vmservicescrapes.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vmsingles.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vmstaticscrapes.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vmusers.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vtclusters.operator.victoriametrics.com created
customresourcedefinition.apiextensions.k8s.io/vtsingles.operator.victoriametrics.com created
serviceaccount/vm-operator created
role.rbac.authorization.k8s.io/vm-leader-election-role created
clusterrole.rbac.authorization.k8s.io/vm-operator created
rolebinding.rbac.authorization.k8s.io/vm-leader-election-rolebinding created
clusterrolebinding.rbac.authorization.k8s.io/vm-operator created
service/vm-operator-metrics-service created
deployment.apps/vm-operator created
networkpolicy.networking.k8s.io/vm-allow-metrics-traffic created
networkpolicy.networking.k8s.io/vm-allow-webhook-traffic created
```
3. 查看 operator 状态
```shell
[root@mwb-k8s-master-test01 vm]# kubectl get deployments.apps -n mv 
No resources found in mv namespace.
[root@mwb-k8s-master-test01 vm]# kubectl get deployments.apps -n vm 
NAME          READY   UP-TO-DATE   AVAILABLE   AGE
vm-operator   1/1     1            1           83s
[root@mwb-k8s-master-test01 vm]# kubectl get pod -n vm 
NAME                           READY   STATUS    RESTARTS   AGE
vm-operator-674c6cc4fd-kdb4p   1/1     Running   0          88s
[root@mwb-k8s-master-test01 vm]# kubectl get svc -n vm 
NAME                          TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
vm-operator-metrics-service   ClusterIP   10.233.57.253   <none>        8080/TCP   102s
[root@mwb-k8s-master-test01 vm]# kubectl api-resources --api-group=operator.victoriametrics.com
NAME                    SHORTNAMES   APIVERSION                             NAMESPACED   KIND
vlagents                             operator.victoriametrics.com/v1        true         VLAgent
vlclusters                           operator.victoriametrics.com/v1        true         VLCluster
vlogs                                operator.victoriametrics.com/v1beta1   true         VLogs
vlsingles                            operator.victoriametrics.com/v1        true         VLSingle
vmagents                             operator.victoriametrics.com/v1beta1   true         VMAgent
vmalertmanagerconfigs                operator.victoriametrics.com/v1beta1   true         VMAlertmanagerConfig
vmalertmanagers         vma          operator.victoriametrics.com/v1beta1   true         VMAlertmanager
vmalerts                             operator.victoriametrics.com/v1beta1   true         VMAlert
vmanomalies                          operator.victoriametrics.com/v1        true         VMAnomaly
vmauths                              operator.victoriametrics.com/v1beta1   true         VMAuth
vmclusters                           operator.victoriametrics.com/v1beta1   true         VMCluster
vmnodescrapes                        operator.victoriametrics.com/v1beta1   true         VMNodeScrape
vmpodscrapes                         operator.victoriametrics.com/v1beta1   true         VMPodScrape
vmprobes                             operator.victoriametrics.com/v1beta1   true         VMProbe
vmrules                              operator.victoriametrics.com/v1beta1   true         VMRule
vmscrapeconfigs                      operator.victoriametrics.com/v1beta1   true         VMScrapeConfig
vmservicescrapes                     operator.victoriametrics.com/v1beta1   true         VMServiceScrape
vmsingles                            operator.victoriametrics.com/v1beta1   true         VMSingle
vmstaticscrapes                      operator.victoriametrics.com/v1beta1   true         VMStaticScrape
vmusers                              operator.victoriametrics.com/v1beta1   true         VMUser
vtclusters                           operator.victoriametrics.com/v1        true         VTCluster
vtsingles                            operator.victoriametrics.com/v1        true         VTSingle
```
### 部署 VictoriaMetrics 集群 single node

1. 创建 single node yaml 文件 vm-single.yaml
```yaml
cat <<'EOF' > vmsingle-demo.yaml
apiVersion: operator.victoriametrics.com/v1beta1
kind: VMSingle
metadata:
  name: vmsingle
  namespace: vm
spec:
  retentionPeriod: "7d"
  replicaCount: 1
  image:
    repository: docker.m.daocloud.io/victoriametrics/victoria-metrics
    tag: v1.131.0
    pullPolicy: IfNotPresent
  storage:
    accessModes:
      - ReadWriteOnce
    resources:
      requests:
        storage: 50Gi
    storageClassName: nfs-provisioner
  serviceSpec:
    spec:
      type: NodePort
      ports:
        - name: http
          port: 8429
          targetPort: 8429
        - name: grpc
          port: 8428
          targetPort: 8428
EOF
```

2. 检查状体，并更新 svc 类型为 NodePort
```shell
[root@mwb-k8s-master-test01 vm]# kubectl get pod -n vm
NAME                                 READY   STATUS              RESTARTS   AGE
vm-operator-674c6cc4fd-kdb4p         1/1     Running             0          12m
vmsingle-vmsingle-749798d5b8-ktkgp   0/1     ContainerCreating   0          33s
[root@mwb-k8s-master-test01 vm]# kubectl get svc -n vm vmsingle-vmsing
Error from server (NotFound): services "vmsingle-vmsing" not found
[root@mwb-k8s-master-test01 vm]# kubectl get svc -n vm vmsingle-vmsingle 
NAME                TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)             AGE
vmsingle-vmsingle   ClusterIP   10.233.23.190   <none>        8429/TCP,8428/TCP   5m26s
[root@mwb-k8s-master-test01 vm]# kubectl edit svc -n vm vmsingle-vmsingle 
service/vmsingle-vmsingle edited
[root@mwb-k8s-master-test01 ~]# kubectl get svc -n vm 
NAME                                   TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                         AGE
vm-operator-metrics-service            NodePort    10.233.57.253   <none>        8080:32131/TCP                  46m
vmsingle-vmsingle                      ClusterIP   10.233.1.186    <none>        8429/TCP,8428/TCP               10m
vmsingle-vmsingle-additional-service   NodePort    10.233.48.164   <none>        8429:31950/TCP,8428:30380/TCP   9s
```
3. 访问 VictoriaMetrics 单节点实例
- 8429: http 端口（这里会返回 vm 的一些 api 接口，比如 vmui、targets、metrics 等）
- 8428: grpc 端口 (数据的写入和查询都是通过它)，vmui 还是 8428 暴露出来的

```shell
http://10.1.32.175:31950/
Single-node VictoriaMetrics

See docs at https://docs.victoriametrics.com/
Useful endpoints:
vmui - Web UI
targets - status for discovered active targets
service-discovery - labels before and after relabeling for discovered targets
metric-relabel-debug - debug metric relabeling
expand-with-exprs - WITH expressions' tutorial
api/v1/targets - advanced information about discovered targets in JSON format
config - -promscrape.config contents
metrics - available service metrics
flags - command-line flags
api/v1/status/tsdb - tsdb status page
api/v1/status/top_queries - top queries
api/v1/status/active_queries - active queries
-/reload - reload configuration

http://10.1.32.175:31950/vmui/

```
4. 为啥 rancher 中没有 cr 的封装
5. 知识补充
```shell
- 写入数据
curl -i -X POST \
  --url http://127.0.0.1:8428/api/v1/import/prometheus \
  --header 'Content-Type: text/plain' \
  --data 'a_metric{foo="fooVal"} 123'

- 查询数据
curl -i --url http://127.0.0.1:8428/api/v1/query --url-query query=a_metric
```
6. vmsingle 相当于 allinone 的模式，数据通过 8428 写入后，会落到 vmstorage 中
```shell
VMSINGLE_POD_NAME=$(kubectl get pod -l "app.kubernetes.io/name=vmsingle"  -n vm -o jsonpath="{.items[0].metadata.name}");

kubectl exec -n vm "$VMSINGLE_POD_NAME" -- ls -l  /victoria-metrics-data;

[root@mwb-k8s-master-test01 ~]# kubectl exec -n vm "$VMSINGLE_POD_NAME" -- ps 
PID   USER     TIME  COMMAND
    1 root      0:01 /victoria-metrics-prod -httpListenAddr=:8429 -retentionPeriod=7d -storageDataPath=/victoria-metrics-data
   19 root      0:00 ps
```

### 部署 vmagent 来搜集 exporter 的数据到 vmsingle
1. 创建 vmagent.yaml
```yaml
cat <<'EOF' > vmagent.yaml
apiVersion: operator.victoriametrics.com/v1beta1
kind: VMAgent
metadata:
  name: vmagent
  namespace: vm
spec:
  containers:
    - name: vmagent
      image: docker.m.daocloud.io/victoriametrics/vmagent:v1.131.0
    - name: config-reloader
      image: docker.m.daocloud.io/victoriametrics/operator:config-reloader-v0.66.1
  initContainers:
    - name: config-init
      image: docker.m.daocloud.io/victoriametrics/operator:config-reloader-v0.66.1
  selectAllByDefault: true
  remoteWrite:
    - url: "http://vmsingle-vmsingle.vm.svc:8428/api/v1/write"
  replicaCount: 1
  image:
    repository: docker.m.daocloud.io/victoriametrics/vmagent
    tag: v1.131.0
    pullPolicy: IfNotPresent
  serviceSpec:
    spec:
      type: NodePort
      ports:
        - name: http
          port: 8429
          targetPort: 8429
        - name: grpc
          port: 8435
          targetPort: 8435
EOF
```
2. 检查
```shell
[root@mwb-k8s-master-test01 vm]# kubectl apply -f vmagent.yaml  
vmagent.operator.victoriametrics.com/vmagent created
[root@mwb-k8s-master-test01 vm]# kubectl get pod -n vm 
NAME                                 READY   STATUS     RESTARTS   AGE
vm-operator-674c6cc4fd-kdb4p         1/1     Running    0          64m
vmagent-vmagent-567bf6879-4l9kj       0/2     Init:0/1   0          8s
vmsingle-vmsingle-76b88c76d5-jq8wd   1/1     Running    0          29m
[root@mwb-k8s-master-test01 vm]# kubectl get svc -n vm 
NAME                                   TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                         AGE
vm-operator-metrics-service            NodePort    10.233.57.253   <none>        8080:32131/TCP                  64m
vmagent-vmagent                         ClusterIP   10.233.44.106   <none>        8429/TCP                        14s
vmagent-vmagent-additional-service      NodePort    10.233.52.118   <none>        8429:31663/TCP,8428:30734/TCP   14s
vmsingle-vmsingle                      ClusterIP   10.233.1.186    <none>        8429/TCP,8428/TCP               28m
vmsingle-vmsingle-additional-service   NodePort    10.233.48.164   <none>        8429:31950/TCP,8428:30380/TCP   18m
[root@mwb-k8s-master-test01 vm]# kubectl get pod -n vm 
NAME                                 READY   STATUS    RESTARTS   AGE
vm-operator-78f68b8b5-5clqr          1/1     Running   0          42m
vmagent-vmagent-686cd5dbd9-5dz79      2/2     Running   0          32s
vmsingle-vmsingle-76b88c76d5-jq8wd   1/1     Running   0          83m

- http://10.1.32.177:31663/ # 8429
- http://10.1.32.177:31663/targets
```
3. 部署 demo 应用
```shell
cat <<'EOF' > demo-app.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: demo-app
  namespace: default
  labels:
    app.kubernetes.io/name: demo-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app.kubernetes.io/name: demo-app
  template:
    metadata:
      labels:
        app.kubernetes.io/name: demo-app
    spec:
      containers:
        - name: main
          image: docker.m.daocloud.io/victoriametrics/demo-app:1.2
---
apiVersion: v1
kind: Service
metadata:
  name: demo-app
  namespace: default
  labels:
    app.kubernetes.io/name: demo-app
spec:
  selector:
    app.kubernetes.io/name: demo-app
  ports:
    - port: 8080
      name: http
EOF
```
4. 创建 scrape 配置,它会告知 vmagent 去 scrape 这个服务的 metrics 数据

```shell
cat <<'EOF' > demo-app-scrape.yaml
apiVersion: operator.victoriametrics.com/v1beta1
kind: VMServiceScrape
metadata:
  name: demo-app-service-scrape
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: demo-app
  endpoints:
  - port: http
EOF

[root@mwb-k8s-master-test01 vm]# kubectl apply -f demo-app-scrape.yaml 
vmservicescrape.operator.victoriametrics.com/demo-app-service-scrape created

[root@mwb-k8s-master-test01 vm]# kubectl get vmservicescrapes.operator.victoriametrics.com 
NAME                      AGE    STATUS        SYNC ERROR
demo-app-service-scrape   106s   operational  
```
### 部署 vmalertmananger、vmalert、vmrule 来告警
1. 安装 vmalertmanager
```shell
cat <<'EOF' > vmalertmanager.yaml
apiVersion: operator.victoriametrics.com/v1beta1
kind: VMAlertmanager
metadata:
  name: vmalertmanager
  namespace: vm
spec:
  configRawYaml: |
    route:
      receiver: 'demo-app'
    receivers:
    - name: 'demo-app'
      webhook_configs:
      - url: 'http://demo-app.default.svc:8080/alerting/webhook'
  replicaCount: 1
  containers:
    - name: config-reloader
      image: docker.m.daocloud.io/victoriametrics/operator:config-reloader-v0.66.1
  image:
    repository: docker.m.daocloud.io/prom/alertmanager
    tag: v0.29.0
    pullPolicy: IfNotPresent
  serviceSpec:
    spec:
      type: NodePort
      ports:
        - name: http
          port: 9093
          targetPort: 9093
EOF

[root@mwb-k8s-master-test01 vm]# kubectl apply -f vmalertmanager.yaml 
vmalertmanager.operator.victoriametrics.com/vmalertmanager created

[root@mwb-k8s-master-test01 vm]# kubectl get svc -n vm 
NAME                                               TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                         AGE
vm-operator-metrics-service                        NodePort    10.233.57.253   <none>        8080:32131/TCP                  11h
vmagent-vmagent                                     ClusterIP   10.233.44.106   <none>        8429/TCP                        10h
vmagent-vmagent-additional-service                  NodePort    10.233.52.118   <none>        8429:31663/TCP,8428:30734/TCP   10h
vmalertmanager-vmalertmanager                      ClusterIP   None            <none>        9093/TCP,9094/TCP,9094/UDP      3m58s
vmalertmanager-vmalertmanager-additional-service   NodePort    10.233.36.98    <none>        9093:31668/TCP                  3m58s
vmsingle-vmsingle                                  ClusterIP   10.233.1.186    <none>        8429/TCP,8428/TCP               10h
vmsingle-vmsingle-additional-service               NodePort    10.233.48.164   <none>        8429:31950/TCP,8428:30380/TCP   10h
[root@mwb-k8s-master-test01 vm]# kubectl get pod -n vm 
NAME                                 READY   STATUS    RESTARTS   AGE
vm-operator-78f68b8b5-5clqr          1/1     Running   0          9h
vmagent-vmagent-686cd5dbd9-5dz79      2/2     Running   0          9h
vmalertmanager-vmalertmanager-0      2/2     Running   0          39s
vmsingle-vmsingle-76b88c76d5-jq8wd   1/1     Running   0          10h

- http://10.1.32.177:31668/#/status # 9093 是 alertmanager 的 http 端口
```
2. 创建 vmalert
```shell
cat <<'EOF' > vmalert.yaml
apiVersion: operator.victoriametrics.com/v1beta1
kind: VMAlert
metadata:
  name: vmalert
  namespace: vm
spec:
  containers:
    - name: config-reloader
      image: docker.m.daocloud.io/victoriametrics/operator:config-reloader-v0.66.1
  image:
    repository: docker.m.daocloud.io/victoriametrics/vmalert
    tag: v1.131.0
  # Metrics source (VMCluster/VMSingle)
  datasource:
    url: "http://vmsingle-vmsingle.vm.svc:8428"
  # Where alert state and recording rules are stored
  remoteWrite:
    url: "http://vmsingle-vmsingle.vm.svc:8428"
  # Where the previous alert state is loaded from. Optional
  remoteRead:
    url: "http://vmsingle-vmsingle.vm.svc:8428"
  # Alertmanager URL for sending alerts
  notifier:
    url: "http://vmalertmanager-vmalertmanager.vm.svc:9093"
  # How often the rules are evaluated
  evaluationInterval: "10s"
  # Watch VMRule resources in all namespaces
  selectAllByDefault: true
  serviceSpec:
    spec:
      type: NodePort
      ports:
        - name: http
          port: 8080
          targetPort: 8080
EOF

[root@mwb-k8s-master-test01 vm]# kubectl apply -f vmalert.yaml 
vmalert.operator.victoriametrics.com/vmalert created

[root@mwb-k8s-master-test01 ~]# kubectl get svc -n vm 
NAME                                               TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                         AGE
vm-operator-metrics-service                        NodePort    10.233.57.253   <none>        8080:32131/TCP                  12h
vmagent-vmagent                                     ClusterIP   10.233.44.106   <none>        8429/TCP                        10h
vmagent-vmagent-additional-service                  NodePort    10.233.52.118   <none>        8429:31663/TCP,8428:30734/TCP   10h
vmalert-vmalert                                    ClusterIP   10.233.36.230   <none>        8080/TCP                        44m
vmalert-vmalert-additional-service                 NodePort    10.233.41.234   <none>        8080:31166/TCP                  7s
vmalertmanager-vmalertmanager                      ClusterIP   None            <none>        9093/TCP,9094/TCP,9094/UDP      55m
vmalertmanager-vmalertmanager-additional-service   NodePort    10.233.36.98    <none>        9093:31668/TCP                  55m
vmsingle-vmsingle                                  ClusterIP   10.233.1.186    <none>        8429/TCP,8428/TCP               11h
vmsingle-vmsingle-additional-service               NodePort    10.233.48.164   <none>        8429:31950/TCP,8428:30380/TCP   11h
[root@mwb-k8s-master-test01 ~]# kubectl get pod -n vm 
NAME                                 READY   STATUS    RESTARTS   AGE
vm-operator-78f68b8b5-5clqr          1/1     Running   0          10h
vmagent-vmagent-686cd5dbd9-5dz79      2/2     Running   0          10h
vmalert-vmalert-cf767bc5b-npvwl      2/2     Running   0          39m
vmalertmanager-vmalertmanager-0      2/2     Running   0          52m
vmsingle-vmsingle-76b88c76d5-jq8wd   1/1     Running   0          11h

- http://10.1.32.177:31166/ # 8080  VMAlert UI

API:
api/v1/rules - list all loaded groups and rules
api/v1/alerts - list all active alerts
api/v1/notifiers - list all notifiers
api/v1/alert?group_id=<int>&alert_id=<int> - get alert status by group and alert ID
api/v1/rule?group_id=<int>&rule_id=<int> - get rule status by group and rule ID
api/v1/group?group_id=<int> - get group status by group ID
System:
vmalert/groups - UI
flags - command-line flags
metrics - list of application metrics
-/reload - reload configuration

demo-app (every 10s) #
1
/etc/vmalert/config/vm-vmalert-rulefiles-0/default-demo.yaml

```
3. 创建 vmrule 告警规则
```shell
cat <<'EOF' > demo-app-rule.yaml
apiVersion: operator.victoriametrics.com/v1beta1
kind: VMRule
metadata:
  name: demo
  namespace: default
spec:
  groups:
    - name: demo-app
      rules:
        - alert: DemoAlertFiring
          expr: 'sum(demo_alert_firing{job="demo-app",namespace="default"}) by (job,pod,namespace) > 0'
          for: 30s
          labels:
            job: '{{ $labels.job }}'
            pod: '{{ $labels.pod }}'
          annotations:
            description: 'demo-app pod {{ $labels.pod }} is firing demo alert'
EOF

kubectl apply -f demo-app-rule.yaml
kubectl wait --for=jsonpath='{.status.updateStatus}'=operational vmrule/demo

[root@mwb-k8s-master-test01 vm]# kubectl get vmrules.operator.victoriametrics.com 
NAME   AGE   STATUS        SYNC ERROR
demo   17s   operational   

http://10.1.32.177:31166/vmalert/groups?search= # 8080  VMAlert UI

demo-app (every 10s) #
1
/etc/vmalert/config/vm-vmalert-rulefiles-0/default-demo.yaml
```
### 开启认证
1. 部署  vmauth
```shell
cat <<'EOF' > vmauth.yaml
apiVersion: operator.victoriametrics.com/v1beta1
kind: VMAuth
metadata:
  name: vmauth
spec:
  initContainers:
    - name: config-init
      image: docker.m.daocloud.io/victoriametrics/operator:config-reloader-v0.66.1
  containers:
    - name: config-reloader
      image: docker.m.daocloud.io/victoriametrics/operator:config-reloader-v0.66.1
  image:
    repository: docker.m.daocloud.io/victoriametrics/vmauth
    tag: v1.131.0
  selectAllByDefault: true
  ingress:
    class_name: 'nginx'                
    host: victoriametrics.dominos.com.cn
  serviceSpec:
    spec:
      type: NodePort
      ports:
        - name: http
          port: 8427
          targetPort: 8427
EOF

[root@mwb-k8s-master-test01 vm]# kubectl apply -f vmauth.yaml 
vmauth.operator.victoriametrics.com/vmauth created

[root@mwb-k8s-master-test01 vm]# kubectl get pod -n vm 
NAME                                 READY   STATUS    RESTARTS   AGE
vm-operator-78f68b8b5-5clqr          1/1     Running   0          11h
vmagent-vmagent-686cd5dbd9-5dz79      2/2     Running   0          10h
vmalert-vmalert-cf767bc5b-npvwl      2/2     Running   0          76m
vmalertmanager-vmalertmanager-0      2/2     Running   0          88m
vmauth-vmauth-8467c998cf-ghs52       2/2     Running   0          29s
vmsingle-vmsingle-76b88c76d5-jq8wd   1/1     Running   0          12h
[root@mwb-k8s-master-test01 vm]# kubectl get svc -n vm 
NAME                                               TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)                         AGE
vm-operator-metrics-service                        NodePort    10.233.57.253   <none>        8080:32131/TCP                  12h
vmagent-vmagent                                     ClusterIP   10.233.44.106   <none>        8429/TCP                        11h
vmagent-vmagent-additional-service                  NodePort    10.233.52.118   <none>        8429:31663/TCP,8428:30734/TCP   11h
vmalert-vmalert                                    ClusterIP   10.233.36.230   <none>        8080/TCP                        81m
vmalert-vmalert-additional-service                 NodePort    10.233.41.234   <none>        8080:31166/TCP                  36m
vmalertmanager-vmalertmanager                      ClusterIP   None            <none>        9093/TCP,9094/TCP,9094/UDP      92m
vmalertmanager-vmalertmanager-additional-service   NodePort    10.233.36.98    <none>        9093:31668/TCP                  92m
vmauth-vmauth                                      ClusterIP   10.233.9.104    <none>        8427/TCP                        39s
vmauth-vmauth-additional-service                   NodePort    10.233.41.18    <none>        8427:30599/TCP                  39s
vmsingle-vmsingle                                  ClusterIP   10.233.1.186    <none>        8429/TCP,8428/TCP               12h
vmsingle-vmsingle-additional-service               NodePort    10.233.48.164   <none>        8429:31950/TCP,8428:30380/TCP   11h
[root@mwb-k8s-master-test01 vm]# kubectl get ingress -n vm 
NAME            CLASS   HOSTS                            ADDRESS         PORTS   AGE
vmauth-vmauth   nginx   victoriametrics.dominos.com.cn   10.233.29.142   80      2m25s

- http://10.1.32.177:30599/ # 8427  vmauth-UI,上来就让输入用户名和密码
```
2. 创建 vmuser 认证信息
```shell
cat <<'EOF' > vmuser.yaml
apiVersion: operator.victoriametrics.com/v1beta1
kind: VMUser
metadata:
  name: vmuser
  namespace: vm
spec:
  name: vmuser-demo
  username: weibing.ma
  generatePassword: true
  targetRefs:
    # vmsingle
    - crd:
        kind: VMSingle
        name: vmsingle
        namespace: vm
      paths:
        - "/vmui.*"
        - "/prometheus/.*"
    # vmalert
    - crd:
        kind: VMAlert
        name: vmalert
        namespace: vm
      paths:
        - "/vmalert.*"
        - "/api/v1/groups"
        - "/api/v1/alert"
        - "/api/v1/alerts"
    # vmagent
    - crd:
        kind: VMAgent
        name: vmagent
        namespace: vm
      paths:
        - "/api/v1/write"
        - "/api/v1/read"
        - "/targets.*"
    # vmalertmanager
    - crd:
        kind: VMAlertmanager
        name: vmalertmanager
        namespace: vm
      paths:
        - "/api/v2/alerts"
        - "/api/v2/status"
EOF

[root@mwb-k8s-master-test01 vm]# kubectl apply -f vmuser.yaml 
vmuser.operator.victoriametrics.com/vmuser created
[root@mwb-k8s-master-test01 vm]# kubectl get vmagents.operator.victoriametrics.com -n vm 
NAME     SHARDS COUNT   REPLICA COUNT   STATUS        AGE
vmagent                  1               operational   11h

[root@mwb-k8s-master-test01 vm]# kubectl get secret -n vm 
NAME                                   TYPE     DATA   AGE
tls-assets-vmagent-vmaget              Opaque   0      11h
tls-assets-vmalert-vmalert             Opaque   0      93m
vmagent-vmaget                         Opaque   1      11h
vmalert-vmalert                        Opaque   0      93m
vmalertmanager-vmalertmanager-config   Opaque   1      104m
vmauth-config-vmauth                   Opaque   1      12m
vmuser-vmuser                          Opaque   3      2m40s
[root@mwb-k8s-master-test01 vm]# kubectl get secret -n vm vmuser-vmuser -o yaml 
apiVersion: v1
data:
  name: dmFjdGlvci12bXVzZXItZGVtby==
  password: <PASSWORD>==
  username: d2VpYmluZy5tYQ==

export DEMO_USERNAME="$(kubectl get secret -n vm vmuser-vmuser -o jsonpath="{.data.username}" | base64 --decode)";
export DEMO_PASSWORD="$(kubectl get secret -n vm vmuser-vmuser -o jsonpath="{.data.password}" | base64 --decode)";
echo "Username: $DEMO_USERNAME; Password: $DEMO_PASSWORD";

- http://victoriametrics.dominos.com.cn/vmui/  # vmsingle
- http://victoriametrics.dominos.com.cn/targets # vmagent
- http://victoriametrics.dominos.com.cn/vmalert # vmalert
- http://victoriametrics.dominos.com.cn/api/v2/status # vmalertmanager
```
