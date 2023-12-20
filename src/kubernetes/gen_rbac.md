# 用户可通过 RBAC 进行权限控制，让不同 os 用户管理各自 namespace 下的资源

## 生成 configfile

```shell
#!/bin/bash

# 获取用户输入
read -p "请输入要创建的Namespace名称: " namespace
read -p "请输入要创建的ServiceAccount名称: " sa_name
read -p "请输入要创建的SecretName名称: " secret_name
read -p "请输入要生成的Config文件名称: " config_file_name
read -p "请输入Kubernetes集群API服务器地址: " api_server

# 创建Namespace
kubectl create namespace $namespace

# 创建ServiceAccount
kubectl create serviceaccount $sa_name -n $namespace

# 创建Secret
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Secret
type: kubernetes.io/service-account-token
metadata:
  name: $secret_name
  namespace: $namespace
  annotations:
    kubernetes.io/service-account.name: $sa_name
EOF

# 创建Role
cat <<EOF | kubectl apply -f -
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  namespace: $namespace
  name: $sa_name-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps"] # 根据需要修改资源类型
  verbs: ["get", "list", "watch", "create", "update", "delete"]
EOF

# 创建RoleBinding
cat <<EOF | kubectl apply -f -
kind: RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: $sa_name-binding
  namespace: $namespace
subjects:
- kind: ServiceAccount
  name: $sa_name
  namespace: $namespace
roleRef:
  kind: Role
  name: $sa_name-role
  apiGroup: rbac.authorization.k8s.io
EOF

# 获取ServiceAccount的Token
#secret_name=$(kubectl get serviceaccount $sa_name -n $namespace -o jsonpath='{.secrets[0].name}')
token=$(kubectl get secret $secret_name -n $namespace -o jsonpath='{.data.token}' | base64 --decode)

# 生成Config文件
cat <<EOF > $config_file_name
apiVersion: v1
kind: Config
clusters:
- name: $namespace-cluster
  cluster:
    server: "https://$api_server:6443"
    certificate-authority-data: "$(kubectl config view --raw -o jsonpath='{.clusters[0].cluster.certificate-authority-data}')"
contexts:
- name: $namespace-context
  context:
    cluster: $namespace-cluster
    namespace: $namespace
    user: $sa_name
current-context: $namespace-context
users:
- name: $sa_name
  user:
    token: $token
EOF

echo "RBAC和Config文件创建成功！"

ssh 192.168.1.110 "mkdir -p /home/$namespace/.kube/"
scp $config_file_name root@192.168.1.110:/home/$namespace/.kube/
ssh 192.168.1.110 "chmod 755 /home/$namespace/.kube/$config_file_name && cp /home/$namespace/.kube/$config_file_name /home/$config_file_name/.kube/config"

echo "Configfile远程copy完成，请用普通用户登录centos执行: alias k='kubectl --kubeconfig=.kube/config' 或将其追加到 .bashrc 并 source .bashrc"
```

## 使用

```shell
root@g-m-10-8-162-12 rbac]# bash gen_rbac.sh
请输入要创建的Namespace名称: mawb
请输入要创建的ServiceAccount名称: mawb
请输入要创建的SecretName名称: mawb
请输入要生成的Config文件名称: mawb
请输入Kubernetes集群API服务器地址: 192.168.1.110
Error from server (AlreadyExists): namespaces "mawb" already exists
error: failed to create serviceaccount: serviceaccounts "mawb" already exists
secret/mawb unchanged
role.rbac.authorization.k8s.io/mawb-role unchanged
rolebinding.rbac.authorization.k8s.io/mawb-binding unchanged
RBAC和Config文件创建成功！
mawb                                                                              100% 2629     7.9MB/s   00:00
Configfile远程copy完成，请用普通用户登录centos执行: alias k='kubectl --kubeconfig=.kube/config' 或将其追加到 .bashrc 并 source .bashrc
```
