# helm 使用笔记

- env

  1. 查看本地 helm client 环境变量配置

     ```shell
     # 查看
     helm env
     
     HELM_BIN="helm"
     HELM_BURST_LIMIT="100"
     HELM_CACHE_HOME="/root/.cache/helm"
     HELM_CONFIG_HOME="/root/.config/helm"
     HELM_DATA_HOME="/root/.local/share/helm"
     HELM_DEBUG="false"
     HELM_KUBEAPISERVER=""
     HELM_KUBEASGROUPS=""
     HELM_KUBEASUSER=""
     HELM_KUBECAFILE=""
     HELM_KUBECONTEXT=""
     HELM_KUBEINSECURE_SKIP_TLS_VERIFY="false"
     HELM_KUBETLS_SERVER_NAME=""
     HELM_KUBETOKEN=""
     HELM_MAX_HISTORY="10"
     HELM_NAMESPACE="default"
     HELM_PLUGINS="/root/.local/share/helm/plugins"
     HELM_REGISTRY_CONFIG="/root/.config/helm/registry/config.json"
     HELM_REPOSITORY_CACHE="/root/.cache/helm/repository"
     HELM_REPOSITORY_CONFIG="/root/.config/helm/repositories.yaml" # helm repo add 的 repo 都会保存在这个文件中
     
     # 查看 repositories.yaml 文件
     cat .config/helm/repositories.yaml 
     apiVersion: ""
     generated: "0001-01-01T00:00:00Z"
     repositories:
     - caFile: ""
       certFile: ""
       insecure_skip_tls_verify: false
       keyFile: ""
       name: postgres-operator-ui-charts
       pass_credentials_all: false
       password: ""
       url: https://opensource.zalando.com/postgres-operator/charts/postgres-operator-ui
       username: ""
     - caFile: ""
       certFile: ""
       insecure_skip_tls_verify: false
       keyFile: ""
       name: elastic
       pass_credentials_all: false
       password: ""
       url: https://helm.elastic.co
       username: ""
     ```

- repo

  1. 添加 elastic repo 仓库

     ```shell
     helm repo add elastic https://helm.elastic.co
     ```

   2. 查看 repo 列表

      ```shell
      helm repo list
      ```

  3. 查看 repo 中所有 chart

     ```shell
     # 显示预发布版本
     helm search repo elastic --devel
     
     # 按版本检索
     helm search repo elastic --version ^8
     helm search repo elastic --version ^6
     
     # 显示 repo 中具体项目的版本, --versions 可以简写为 -l
     helm search repo elastic --versions 
     
     ```

- pull

  1. 下在某个版本的 chart

     ```shell
     helm pull elastic/elasticsearch --version 7.16.2 # 默认下载最新版本
     ```

  2. 扩展

     ```shell
     --untar # 下载后解压
     --untardir # 解压到指定路径、默认 ./
     --insecure-skip-tls-verify  # 跳过 tls 证书
     --plain-http # 使用 http
     ```

- package

  1. 打包

     ```shell
     # 重新打包为 tgz，主要是针对自定义 template 的场景
     helm package ./elasticsearch
     ```

- list

  1. 查看已安装的 release

     ```shell
     # 查看所有 namespace 下已经部署的 release，包含 成功/失败、并按 date 排序
     helm list -A -a -d
     ```