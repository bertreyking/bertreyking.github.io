## 安装 dashabord

```shell
[root@controller-node-1 ~]# kubectl apply -f https://raw.githubusercontent.com/kubernetes/dashboard/v2.7.0/aio/deploy/recommended.yaml
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
```

## 检查状态

```shell
[root@controller-node-1 ~]# kubectl get pod -n kubernetes-dashboard 
NAME                                        READY   STATUS              RESTARTS   AGE
dashboard-metrics-scraper-7bc864c59-lwlnf   0/1     ContainerCreating   0          10s
kubernetes-dashboard-6c7ccbcf87-55jln       0/1     ContainerCreating   0          10s

[root@controller-node-1 ~]# kubectl get pod -n kubernetes-dashboard 
NAME                                        READY   STATUS    RESTARTS   AGE
dashboard-metrics-scraper-7bc864c59-lwlnf   1/1     Running   0          76s
kubernetes-dashboard-6c7ccbcf87-55jln       1/1     Running   0          76s
```

## 使用 nodeport 暴露出来

```shell
[root@controller-node-1 ~]# kubectl get svc -n kubernetes-dashboard 
NAME                        TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
dashboard-metrics-scraper   ClusterIP   10.233.52.164   <none>        8000/TCP   2m52s
kubernetes-dashboard        ClusterIP   10.233.18.137   <none>        443/TCP    2m52s

[root@controller-node-1 ~]# kubectl edit svc  -n kubernetes-dashboard kubernetes-dashboard 
apiVersion: v1
kind: Service
metadata:
  annotations:
    kubectl.kubernetes.io/last-applied-configuration: |
      {"apiVersion":"v1","kind":"Service","metadata":{"annotations":{},"labels":{"k8s-app":"kubernetes-dashboard"},"name":"kubernetes-dashboard","namespace":"kubernetes-dashboard"},"spec":{"ports":[{"port":443,"targetPort":8443}],"selector":{"k8s-app":"kubernetes-dashboard"}}}
  creationTimestamp: "2023-12-12T07:58:58Z"
  labels:
    k8s-app: kubernetes-dashboard
  name: kubernetes-dashboard
  namespace: kubernetes-dashboard
  resourceVersion: "18237823"
  uid: 4d121aa7-791e-4f31-98f9-0b33d8b91d09
spec:
  clusterIP: 10.233.18.137
  clusterIPs:
  - 10.233.18.137
  internalTrafficPolicy: Cluster
  ipFamilies:
  - IPv4
  ipFamilyPolicy: SingleStack
  ports:
  - port: 443
    protocol: TCP
    targetPort: 8443
  selector:
    k8s-app: kubernetes-dashboard
  sessionAffinity: None
  type: NodePort
status:
  loadBalancer: {}
```

## 访问

```shell
https://10.29.17.83:32764/#/login
```

![image-20231212160520297](../png/dashboard_login.png)

## 创建 admin 用户

```shell
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin
  namespace: kubernetes-dashboard
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: admin
  namespace: kubernetes-dashboard
  
---- 创建 token
[root@controller-node-1 ~]# kubectl -n kubernetes-dashboard create token admin
eyJhbGciOiJSUzI1NiIsImtpZCI6IndhQTNza3VaX0dtTmpOQU84TVNyaDRCaGlRNUVIbmVIXzNzVVc3VnVDaWsifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiXSwiZXhwIjoxNzAyMzcyMTQ5LCJpYXQiOjE3MDIzNjg1NDksImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsInNlcnZpY2VhY2NvdW50Ijp7Im5hbWUiOiJhZG1pbiIsInVpZCI6ImIyNGMyZDc0LTkyMTMtNGMyZi04YmQyLWRiMWY3NzdjMzgzMSJ9fSwibmJmIjoxNzAyMzY4NTQ5LCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZXJuZXRlcy1kYXNoYm9hcmQ6YWRtaW4ifQ.onk5Pu6dieQUvi57mQ18_T942eUHZnE7viqUAklE_Ol3n8dv3uCoP6ieUal98NMEEtjfMinU4Kgn2d9iKnBB0wH8dwLSqawM114Y7GzhndX2XlCQKp55umb3v9wVyfYguqC3Q3F2nV23VjvLzuLoUXLeVU7jrkLEj1wPc7uRk1jMAoCqP5sSZBPFhcO2SduJBWZSEvkq3xJDK_nFYW37wNI3Zs3dglCzAN2RYC_cDjL6u6Mmzys3mFV9vCD41EkOkcAOcvXIkkVEFM52yDBG44LPSCZrYtJLFMwCEsmAisn8UZxBhDKOGebewyyh-cU1bCd8-QYaJWoY5GPQI1y9kQ

---- 创建带时间戳的 token
[root@controller-node-1 ~]# kubectl -n kubernetes-dashboard create token admin --duration 3600m
eyJhbGciOiJSUzI1NiIsImtpZCI6IndhQTNza3VaX0dtTmpOQU84TVNyaDRCaGlRNUVIbmVIXzNzVVc3VnVDaWsifQ.eyJhdWQiOlsiaHR0cHM6Ly9rdWJlcm5ldGVzLmRlZmF1bHQuc3ZjLmNsdXN0ZXIubG9jYWwiXSwiZXhwIjoxNzAyNjQ2OTc5LCJpYXQiOjE3MDI0MzA5NzksImlzcyI6Imh0dHBzOi8va3ViZXJuZXRlcy5kZWZhdWx0LnN2Yy5jbHVzdGVyLmxvY2FsIiwia3ViZXJuZXRlcy5pbyI6eyJuYW1lc3BhY2UiOiJrdWJlcm5ldGVzLWRhc2hib2FyZCIsInNlcnZpY2VhY2NvdW50Ijp7Im5hbWUiOiJhZG1pbiIsInVpZCI6ImIyNGMyZDc0LTkyMTMtNGMyZi04YmQyLWRiMWY3NzdjMzgzMSJ9fSwibmJmIjoxNzAyNDMwOTc5LCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZXJuZXRlcy1kYXNoYm9hcmQ6YWRtaW4ifQ.XzEqLRNDq2lHE1M_3wRhQTt0V1JgsoKE_iSFASyfDqEkuMa7V8l4YXKWoD-7TAevfObVHavGR19nTqQ8DPQ2jD3MfJGxpEZMkJ3A8HdQ1KLEwf-A_9kbh5gBviNdukhFspLtx7n9P1T9a3otztVwQTf6RqP-VAdBB-6iZfKXzf-zK7jUAbS7eAR--LJ1Wx5lukcUSguyHnZ0kHS1hRH6rUfxeaNLF3Tuk5W4clfPmufOnRT2ocWmfkvyEE5SSJQJd_odludGjx6Yu-ZB5t5OM1AsQDCNNQ7fNxYRdrDWRJCDkBg5UILMjSULCZ2k--VZXTmtxZAPm51j3y4pmt3Yqw
```

## 再次登录 UI

![image-20231212161148424](../png/dashboard.png)

## 开源 UI 调研

- [kubeapps](https://kubeapps.dev/docs/latest/tutorials/getting-started/)：看起来是管理 helm-chart 的一个页面工具，来方便应用的部署和升级，调研下是否有中文界面，使用上需要用户学习 helm 打包，难度中级、页面风格有点类似 vmware 的登录首页
- [octant](https://github.com/vmware-tanzu/octant)：vmware 开源的 dashboard 页面，和原生提供的页面类似，界面简洁、资源配置丰富，重点调研下

## 安装神器

- kubean：daocloud 公司开源的一个集群生命周期管理工具
- [kubeesz](https://github.com/easzlab/kubeasz)：github 社区挺活跃的
- kubespary：k8s 维护的一个工具，国内大多都是套壳这个

## 参考文件

- [install_kubernetes_dashboard](https://kubernetes.io/zh-cn/docs/tasks/access-application-cluster/web-ui-dashboard/)

- [create_admin_user](https://github.com/kubernetes/dashboard/blob/master/docs/user/access-control/creating-sample-user.md)

