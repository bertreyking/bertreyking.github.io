# 通过 kubernetes API 配置 rbac 策略

## 创建 clusterrole

- 接口 __POST__

  `https://apiserver_ip:6443/apis/rbac.authorization.k8s.io/v1/clusterrole`

- body

  ```json
  {
      "apiVersion": "rbac.authorization.k8s.io/v1",
      "kind": "ClusterRole",
      "metadata": {
          "name": "namespace-admin-writer1"
      },
      "rules": [
          {
              "apiGroups": [
                  ""
              ],
              "resources": [
                  "pods",
                  "services",
                  "configmaps",
                  "secrets",
                  "persistentvolumeclaims",
                  "replicationcontrollers",
                  "serviceaccounts",
                  "endpoints"
              ],
              "verbs": [
                  "get",
                  "list",
                  "watch",
                  "create",
                  "update",
                  "patch",
                  "delete"
              ]
          },
          {
              "apiGroups": [
                  "apps"
              ],
              "resources": [
                  "deployments",
                  "statefulsets",
                  "daemonsets",
                  "replicasets"
              ],
              "verbs": [
                  "get",
                  "list",
                  "watch",
                  "create",
                  "update",
                  "patch",
                  "delete"
              ]
          },
          {
              "apiGroups": [
                  "batch"
              ],
              "resources": [
                  "jobs",
                  "cronjobs"
              ],
              "verbs": [
                  "get",
                  "list",
                  "watch",
                  "create",
                  "update",
                  "patch",
                  "delete"
              ]
          },
          {
              "apiGroups": [
                  "autoscaling"
              ],
              "resources": [
                  "horizontalpodautoscalers"
              ],
              "verbs": [
                  "get",
                  "list",
                  "watch",
                  "create",
                  "update",
                  "patch",
                  "delete"
              ]
          },
          {
              "apiGroups": [
                  "networking.k8s.io"
              ],
              "resources": [
                  "ingresses",
                  "networkpolicies"
              ],
              "verbs": [
                  "get",
                  "list",
                  "watch",
                  "create",
                  "update",
                  "patch",
                  "delete"
              ]
          }
      ]
  }
  ```

- response 

  ```json
  {
      "kind": "ClusterRole",
      "apiVersion": "rbac.authorization.k8s.io/v1",
      "metadata": {
          "name": "namespace-admin-writer1",
          "uid": "f7cc8507-f93a-4c0f-b24f-9c37744efd18",
          "resourceVersion": "613595193",
          "creationTimestamp": "2025-04-16T13:03:41Z",
          "managedFields": [
              {
                  "manager": "PostmanRuntime",
                  "operation": "Update",
                  "apiVersion": "rbac.authorization.k8s.io/v1",
                  "time": "2025-04-16T13:03:41Z",
                  "fieldsType": "FieldsV1",
                  "fieldsV1": {
                      "f:rules": {}
                  }
              }
          ]
      },
      "rules": [
          {
              "verbs": [
                  "get",
                  "list",
                  "watch",
                  "create",
                  "update",
                  "patch",
                  "delete"
              ],
              "apiGroups": [
                  ""
              ],
              "resources": [
                  "pods",
                  "services",
                  "configmaps",
                  "secrets",
                  "persistentvolumeclaims",
                  "replicationcontrollers",
                  "serviceaccounts",
                  "endpoints"
              ]
          },
          {
              "verbs": [
                  "get",
                  "list",
                  "watch",
                  "create",
                  "update",
                  "patch",
                  "delete"
              ],
              "apiGroups": [
                  "apps"
              ],
              "resources": [
                  "deployments",
                  "statefulsets",
                  "daemonsets",
                  "replicasets"
              ]
          },
          {
              "verbs": [
                  "get",
                  "list",
                  "watch",
                  "create",
                  "update",
                  "patch",
                  "delete"
              ],
              "apiGroups": [
                  "batch"
              ],
              "resources": [
                  "jobs",
                  "cronjobs"
              ]
          },
          {
              "verbs": [
                  "get",
                  "list",
                  "watch",
                  "create",
                  "update",
                  "patch",
                  "delete"
              ],
              "apiGroups": [
                  "autoscaling"
              ],
              "resources": [
                  "horizontalpodautoscalers"
              ]
          },
          {
              "verbs": [
                  "get",
                  "list",
                  "watch",
                  "create",
                  "update",
                  "patch",
                  "delete"
              ],
              "apiGroups": [
                  "networking.k8s.io"
              ],
              "resources": [
                  "ingresses",
                  "networkpolicies"
              ]
          }
      ]
  }
  ```

  

## 创建 serviceacconut

- 接口 __POST__

  `https://apiserver_ip:6443/api/v1/namespaces/default/serviceaccounts`

  - API 接口中，需要指定 namespace

- body

  ```json
  {
    "apiVersion": "v1",
    "kind": "ServiceAccount",
    "metadata": {
      "name": "namespace-role-admin"
    }
  }
  ```

- response 

  ```json
  {
      "kind": "ServiceAccount",
      "apiVersion": "v1",
      "metadata": {
          "name": "namespace-role-admin",
          "namespace": "default",
          "uid": "e08d4691-2cb1-41f7-9cd9-bbbf5638302d",
          "resourceVersion": "607496346",
          "creationTimestamp": "2025-04-13T14:20:26Z"
      }
  }
  ```

## 创建 secret

- 接口 __POST__

  `https://apiserver_ip:6443/api/v1/namespaces/default/secrets`

  - API 接口中，需要指定 namespace

- body

  ```json
  {
    "apiVersion": "v1",
    "kind": "Secret",
    "metadata": {
      "generateName": "namespace-role-admin-token-",
      "annotations": {
        "kubernetes.io/service-account.name": "namespace-role-admin"
      }
    },
    "type": "kubernetes.io/service-account-token"
  }
  ```

- response 

  ```json
  {
      "kind": "Secret",
      "apiVersion": "v1",
      "metadata": {
          "name": "namespace-role-admin-token-kkfsf",
          "generateName": "namespace-role-admin-token-",
          "namespace": "default",
          "uid": "3a47b9f7-2e83-445a-ab01-f951d26d4e8b",
          "resourceVersion": "607497767",
          "creationTimestamp": "2025-04-13T14:21:23Z",
          "annotations": {
              "kubernetes.io/service-account.name": "namespace-role-admin"
          },
          "managedFields": [
              {
                  "manager": "PostmanRuntime",
                  "operation": "Update",
                  "apiVersion": "v1",
                  "time": "2025-04-13T14:21:23Z",
                  "fieldsType": "FieldsV1",
                  "fieldsV1": {
                      "f:metadata": {
                          "f:annotations": {
                              ".": {},
                              "f:kubernetes.io/service-account.name": {}
                          },
                          "f:generateName": {}
                      },
                      "f:type": {}
                  }
              }
          ]
      },
      "type": "kubernetes.io/service-account-token"
  }
  ```

## 创建 rolebinding

- 接口 __POST__

  `https://apiserver_ip:6443/apis/rbac.authorization.k8s.io/v1/namespaces/default/rolebindings`

  - API 接口中，需要指定 namespace

- body

  ```json
  {
    "apiVersion": "rbac.authorization.k8s.io/v1",
    "kind": "RoleBinding",
    "metadata": {
      "name": "namespace-admin-writer-binding1"
    },
    "subjects": [
      {
        "kind": "ServiceAccount",
        "name": "namespace-role-admin",
        "namespace": "default"
      }
    ],
    "roleRef": {
      "kind": "ClusterRole",
      "name": "namespace-admin-writer1",
      "apiGroup": "rbac.authorization.k8s.io"
    }
  ```

- response 

  ```json
  {
      "kind": "RoleBinding",
      "apiVersion": "rbac.authorization.k8s.io/v1",
      "metadata": {
          "name": "namespace-admin-writer-binding1",
          "namespace": "default",
          "uid": "e43f498e-d1e3-4bcd-9be2-be660766fc43",
          "resourceVersion": "613604237",
          "creationTimestamp": "2025-04-16T13:10:01Z",
          "managedFields": [
              {
                  "manager": "PostmanRuntime",
                  "operation": "Update",
                  "apiVersion": "rbac.authorization.k8s.io/v1",
                  "time": "2025-04-16T13:10:01Z",
                  "fieldsType": "FieldsV1",
                  "fieldsV1": {
                      "f:roleRef": {},
                      "f:subjects": {}
                  }
              }
          ]
      },
      "subjects": [
          {
              "kind": "ServiceAccount",
              "name": "namespace-role-admin",
              "namespace": "default"
          }
      ],
      "roleRef": {
          "apiGroup": "rbac.authorization.k8s.io",
          "kind": "ClusterRole",
          "name": "namespace-admin-writer1"
      }
  }
  ```

## 查看 serviceaccount 对应的 token

- 接口 __GET__

  `https://apiserver_ip:6443/api/v1/namespaces/default/secrets/namespace-role-admin-token-kkfsf`

  - API 接口中，需要指定 namespace 和 secret 

- response 

  ```json
  {
      "kind": "Secret",
      "apiVersion": "v1",
      "metadata": {
          "name": "namespace-role-admin-token-kkfsf",
          "generateName": "namespace-role-admin-token-",
          "namespace": "default",
          "uid": "3a47b9f7-2e83-445a-ab01-f951d26d4e8b",
          "resourceVersion": "612650164",
          "creationTimestamp": "2025-04-13T14:21:23Z",
          "labels": {
              "kubernetes.io/legacy-token-last-used": "2025-04-16"
          },
          "annotations": {
              "kubernetes.io/service-account.name": "namespace-role-admin",
              "kubernetes.io/service-account.uid": "e08d4691-2cb1-41f7-9cd9-bbbf5638302d"
          },
          "managedFields": [
              {
                  "manager": "PostmanRuntime",
                  "operation": "Update",
                  "apiVersion": "v1",
                  "time": "2025-04-13T14:21:23Z",
                  "fieldsType": "FieldsV1",
                  "fieldsV1": {
                      "f:metadata": {
                          "f:annotations": {
                              ".": {},
                              "f:kubernetes.io/service-account.name": {}
                          },
                          "f:generateName": {}
                      },
                      "f:type": {}
                  }
              },
              {
                  "manager": "kube-controller-manager",
                  "operation": "Update",
                  "apiVersion": "v1",
                  "time": "2025-04-13T14:21:23Z",
                  "fieldsType": "FieldsV1",
                  "fieldsV1": {
                      "f:data": {
                          ".": {},
                          "f:ca.crt": {},
                          "f:namespace": {},
                          "f:token": {}
                      },
                      "f:metadata": {
                          "f:annotations": {
                              "f:kubernetes.io/service-account.uid": {}
                          }
                      }
                  }
              },
              {
                  "manager": "kube-apiserver",
                  "operation": "Update",
                  "apiVersion": "v1",
                  "time": "2025-04-16T01:58:16Z",
                  "fieldsType": "FieldsV1",
                  "fieldsV1": {
                      "f:metadata": {
                          "f:labels": {
                              ".": {},
                              "f:kubernetes.io/legacy-token-last-used": {}
                          }
                      }
                  }
              }
          ]
      },
      "data": {
          "ca.crt": "",
          "namespace": "ZGVmYXVsdA==",
          "token": ""
      },
      "type": "kubernetes.io/service-account-token"
  }
  ```

## 最后使用 token

- 生成 kubeconfig 参考上文

- tokne 直接裸奔

  ```shell
  # 由于 secret 是密文的形式，不能直接拿来使用，需要 base64 -d 解码
  token=$(kubectl get secret namespace-role-admin-token-kkfsf -o=jsonpath="{.data.token}" | base64 -d)
  
  # 检查是否生效
  echo $token
  
  # 检查 pod 状态
  kubectl get pod --token=$token --server=https://apiserver_ip:6443 --insecure-skip-tls-verify -n kube-system 
  Error from server (Forbidden): pods is forbidden: User "system:serviceaccount:default:namespace-role-admin" cannot list resource "pods" in API group "" in the namespace "kube-system"
  
  kubectl get pod --token=$token --server=https://apiserver_ip:6443 --insecure-skip-tls-verify                
  NAME                           READY   STATUS    RESTARTS      AGE
  log-cleanup-daemonset-4f4xq    1/1     Running   3 (54d ago)   254d
  test-ulimit-55d976b7f9-qn4tl   1/1     Running   3 (54d ago)   275d
  test-ulimit-6c476d88f8-nmxqs   0/1     Pending   0             107d
  ```

- 如果有一个 token 管理多个 namespace 的需求，
  - 直接新建 rolebinding，
  - roleRef 使用前面创建的 clusterrole
  - subjects 使用前面创建的 serviceaccount 和 secret 

## 以上接口都是使用 postman 验证

- postman 历史版本下载，新版本必须要登录才能获取大部分功能，离线环境肯本没法用，请自行下载 10 以下的版本

  <https://www.filehorse.com/download-postman/old-versions/page-5/>