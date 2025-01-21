# API 接口文档

- [x] [k8s_api_1.23](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.23/#-strong-status-operations-deployment-v1-apps-strong-) 
- [x] [k8s_api_1.29](https://kubernetes.io/docs/reference/generated/kubernetes-api/v1.29/#api-overview)

# 请求

- [patch](https://github.com/kubernetes/kubernetes/issues/68861)
  
  - [op](https://jsonpatch.com/): 支持 add、replace、remove 多种场景
  
    - 使用操作列表（op、path、value）来精确定义需要修改的 JSON 文档部分
  
    ```shell
    curl -X PATCH -H 'Content-Type: application/json-patch+json' --data '[{"op": "replace","path": "/spec/template/spec/containers/0/args","value": ["-c", "./nginx.conf", "-g", "daemon off;"]}]'
    ```
  
  - merge：以原对象为基础，提供一个结构化的 JSON 数据片段进行合并更新、无法删除字段，除非更改 value 为 null
  
  - strategic-merge-patch：merge 基础上支持更复杂的操作，特别适用于更新 array 类型字段（如 containers 列表）k8s 特有
  
    ```shell
    curl -X PATCH -H 'Content-Type: application/strategic-merge-patch+json' --data '
    {"spec":{"template":{"spec":{"containers":[{"name":"nginx","image":"nginx:1.16"}]}}}}' \
    	'http://127.0.0.1:8001/apis/apps/v1/namespaces/default/deployments/deployment-example'
    ```
  
  - kubectl patch 示例
  
    ```shell
    kubectl patch deployment deployment-example --type strategic -p \
    	'{"spec":{"template":{"spec":{"containers":[{"name":"nginx","image":"nginx:1.16"}]}}}}'
    ```
  
  - 区别
    1. op："path": "/spec/template/spec/containers/0/args" 需要定位到 containers 列表中的字典，然后对其 key:value 键值对进行更新
    2. merge：{"spec":{"template":{"spec":{"containers":[{"name":"nginx","image":"nginx:1.16"}]}}}} 需要也是类似，但是需要加上 name么，否则会报错，在我的环境 name 是这个 dict 中的第一个键值对，后续留意下这点

