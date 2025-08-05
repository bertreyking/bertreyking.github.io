# 使用 operator 部署 gitlab

## operator 安装

```shell
kubectl create namespace gitlab-system
```

- gitlab-operator 地址

```shell
https://gitlab.com/gitlab-org/cloud-native/gitlab-operator/-/releases?after=eyJyZWxlYXNlZF9hdCI6IjIwMjUtMDEtMTYgMTQ6Mjc6MjAuMTM5NTk0MDAwICswMDAwIiwiaWQiOiIxNTU1NjE4OSJ9
```

- Install-operator

```shell
[root@controller-node-1 ~]# kubectl apply -f gitlab-operator.yaml 
customresourcedefinition.apiextensions.k8s.io/gitlabs.apps.gitlab.com created
serviceaccount/gitlab-app-nonroot created
serviceaccount/gitlab-manager created
serviceaccount/gitlab-nginx-ingress created
serviceaccount/gitlab-prometheus-server created
clusterrole.rbac.authorization.k8s.io/gitlab-app-role-nonroot created
clusterrole.rbac.authorization.k8s.io/gitlab-metrics-auth-role created
clusterrole.rbac.authorization.k8s.io/gitlab-metrics-reader created
clusterrole.rbac.authorization.k8s.io/gitlab-manager-role created
clusterrole.rbac.authorization.k8s.io/gitlab-nginx-ingress created
clusterrole.rbac.authorization.k8s.io/gitlab-prometheus-server created
clusterrolebinding.rbac.authorization.k8s.io/gitlab-app-rolebinding-nonroot created
clusterrolebinding.rbac.authorization.k8s.io/gitlab-metrics-auth-rolebinding created
clusterrolebinding.rbac.authorization.k8s.io/gitlab-manager-rolebinding created
clusterrolebinding.rbac.authorization.k8s.io/gitlab-nginx-ingress created
clusterrolebinding.rbac.authorization.k8s.io/gitlab-prometheus-server created
role.rbac.authorization.k8s.io/gitlab-leader-election-role created
role.rbac.authorization.k8s.io/gitlab-nginx-ingress created
rolebinding.rbac.authorization.k8s.io/gitlab-leader-election-rolebinding created
rolebinding.rbac.authorization.k8s.io/gitlab-nginx-ingress created
service/gitlab-controller-manager-metrics-service created
service/gitlab-webhook-service created
deployment.apps/gitlab-controller-manager created
ingressclass.networking.k8s.io/gitlab-nginx created
validatingwebhookconfiguration.admissionregistration.k8s.io/gitlab-validating-webhook-configuration created
resource mapping not found for name: "gitlab-serving-cert" namespace: "gitlab-system" from "gitlab-operator.yaml": no matches for kind "Certificate" in version "cert-manager.io/v1"
ensure CRDs are installed first
resource mapping not found for name: "gitlab-selfsigned-issuer" namespace: "gitlab-system" from "gitlab-operator.yaml": no matches for kind "Issuer" in version "cert-manager.io/v1"
ensure CRDs are installed first

# 安装报错，它依赖 cert-manager 组件，估计是跟 https 有关系 

# 再次安装过了
[root@controller-node-1 ~]# kubectl apply -f gitlab-operator.yaml 
customresourcedefinition.apiextensions.k8s.io/gitlabs.apps.gitlab.com configured
serviceaccount/gitlab-app-nonroot unchanged
serviceaccount/gitlab-manager unchanged
serviceaccount/gitlab-nginx-ingress unchanged
serviceaccount/gitlab-prometheus-server unchanged
clusterrole.rbac.authorization.k8s.io/gitlab-app-role-nonroot unchanged
clusterrole.rbac.authorization.k8s.io/gitlab-metrics-auth-role unchanged
clusterrole.rbac.authorization.k8s.io/gitlab-metrics-reader unchanged
clusterrole.rbac.authorization.k8s.io/gitlab-manager-role unchanged
clusterrole.rbac.authorization.k8s.io/gitlab-nginx-ingress unchanged
clusterrole.rbac.authorization.k8s.io/gitlab-prometheus-server unchanged
clusterrolebinding.rbac.authorization.k8s.io/gitlab-app-rolebinding-nonroot unchanged
clusterrolebinding.rbac.authorization.k8s.io/gitlab-metrics-auth-rolebinding unchanged
clusterrolebinding.rbac.authorization.k8s.io/gitlab-manager-rolebinding unchanged
clusterrolebinding.rbac.authorization.k8s.io/gitlab-nginx-ingress unchanged
clusterrolebinding.rbac.authorization.k8s.io/gitlab-prometheus-server unchanged
role.rbac.authorization.k8s.io/gitlab-leader-election-role unchanged
role.rbac.authorization.k8s.io/gitlab-nginx-ingress unchanged
rolebinding.rbac.authorization.k8s.io/gitlab-leader-election-rolebinding unchanged
rolebinding.rbac.authorization.k8s.io/gitlab-nginx-ingress unchanged
service/gitlab-controller-manager-metrics-service unchanged
service/gitlab-webhook-service unchanged
deployment.apps/gitlab-controller-manager unchanged
ingressclass.networking.k8s.io/gitlab-nginx unchanged
certificate.cert-manager.io/gitlab-serving-cert created
issuer.cert-manager.io/gitlab-selfsigned-issuer created
validatingwebhookconfiguration.admissionregistration.k8s.io/gitlab-validating-webhook-configuration configured
```

## install-gitlab

```shell
apiVersion: apps.gitlab.com/v1beta1
kind: GitLab
metadata:
  name: gitlab
spec:
  chart:
    version: "1.6.0"
    values:
      global:
        hosts:
          domain: mawb.gitlab.com
        ingress:
          configureCertmanager: true
      certmanager-issuer:
        email: weibing.ma@daocloud.io
```

