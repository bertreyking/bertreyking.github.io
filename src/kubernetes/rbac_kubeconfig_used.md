# rbac 和 kubeconfig 汇总篇

## 配置 rbac

1. 定义 clusterrole & clusterrolebinding

   ```yaml
   apiVersion: rbac.authorization.k8s.io/v1
   kind: ClusterRole
   metadata:
     name: common-node-clusterrole
   rules:
   - apiGroups:
     - ""
     resources:
     - nodes
     verbs:
     - get
     - list
     - watch
   ---
   apiVersion: rbac.authorization.k8s.io/v1
   kind: ClusterRoleBinding
   metadata:
     name: common-node-clusterrolebinding
   roleRef:
     apiGroup: rbac.authorization.k8s.io
     kind: ClusterRole
     name: common-node-clusterrole
   subjects:
   - kind: ServiceAccount
     name: test
     namespace: test
   ```

2. shell 脚本交互式生成 kubeconfig 文件

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
   - apiGroups: ["*"]
     resources: ["*"] # 根据需要修改资源类型
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
   
   # 创建 ClusterRole # 仅第一执行脚本时需要，clusterrole 不需要多次创建
   #cat <<EOF | kubectl apply -f -
   #apiVersion: rbac.authorization.k8s.io/v1
   #kind: ClusterRole
   #metadata:
   #  name: common-node-clusterrole
   #rules:
   #- apiGroups:
   #  - ""
   #  resources:
   #  - nodes
   #  verbs:
   #  - get
   #  - list
   #  - watch
   #EOF
   
   # 创建Clusterrolebinding，使 ns 有查看 node 权限
   cat <<EOF | kubectl apply -f -
   apiVersion: rbac.authorization.k8s.io/v1
   kind: ClusterRoleBinding
   metadata:
     name: common-node-clusterrolebinding-$namespace
   roleRef:
     apiGroup: rbac.authorization.k8s.io
     kind: ClusterRole
     name: common-node-clusterrole
   subjects:
   - kind: ServiceAccount
     name: $sa_name
     namespace: $namespace
   EOF
   
   # 获取 ServiceAccount 的 Token
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
   
   echo "RBAC 和 Config 文件创建成功！"
   
   # 这部分按需原则即可，要求免密
   ssh 192.168.0.110 "mkdir -p /home/$namespace/.kube/"
   
   scp $config_file_name 192.168.0.110:/home/$namespace/.kube/
   
   ssh 192.168.0.110 "chmod 755 /home/$namespace/.kube/$config_file_name && cp /home/$namespace/.kube/$config_file_name /home/$namespace/.kube/config"
   
   ssh 192.168.0.110 "cp /opt/scripts/.bashrc /home/$namespace/"
   
   echo "KubeConfig 远程 copy 完成，请用普通用户登录 centos 执行: kubectl get pod "
   
   ```

## 合并多个 kubeconfig 文件

1. kubeconfig

   ```yaml
   # first kubeconfig file
   apiVersion: v1
   clusters:
   - cluster:
       certificate-authority-data: ""
       server: https://192.168.0.196:6443
     name: 196cluster
   contexts:
   - context:
       cluster: 196cluster
       user: 196cluster
     name: 196cluster
   current-context: 196cluster
   kind: Config
   preferences: {}
   users:
   - name: 196global
     user:
       client-certificate-data: ""
       client-key-data: ""
   
   # second kubeconfig file
   apiVersion: v1
   clusters:
   - cluster:
       certificate-authority-data: ""
       server: https://192.168.0.255:6443
     name: 255cluster
   contexts:
   - context:
       cluster: 255cluster
       user: 255cluster
     name: 255cluster
   current-context: 255cluster
   kind: Config
   preferences: {}
   users:
   - name: 255cluster
     user:
       client-certificate-data: ""
       client-key-data: ""
   ```

2. 合并

   - 定义 KUBECONFIG 变量，该变量值是 config 文件的路径列表，这里过滤掉了 config.swp 文件

   ```shell
   # export KUBECONFIG=$HOME/.kube/config:$(find $HOME/.kube -type f -maxdepth 1 | grep config | grep -v '\.config\.swp' | tr '\n' ':')
   export KUBECONFIG=$HOME/.kube/config:$(find $HOME/.kube -maxdepth 1 -type f | grep config | grep -v '\.config\.swp' | tr '\n' ':')
   kubectl config view --flatten > .kube/config
   
   echo $KUBECONFIG
   /Users/kingskye/.kube/config:/Users/kingskye/.kube/255-config:/Users/kingskye/.kube/196-config:
   ```

   - 合并

   ```shell
   
   ```

   - 结果

   ```shell
   mawb:~ kingskye$ kubectl config get-clusters
   NAME
   196cluster
   255cluster
   mawb:~ kingskye$ kubectl config get-contexts
   CURRENT   NAME         CLUSTER      AUTHINFO     NAMESPACE
   *         196cluster   196cluster   196cluster    
             255cluster   255cluster   255cluster   
   ```

   
