# ClusterPedia 对接 k8s 集群

### 1. 接入集群中创建 clusterrole/clusterrolebinding/serviceaccout/secret 

```shell
# 创建 cluserpedia-RBAC
[root@master01 clusterpedia]# vi clusterpedia_synchro_rbac.yaml 
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: clusterpedia-synchro
rules:
- apiGroups:
  - '*'
  resources:
  - '*'
  verbs:
  - '*'
- nonResourceURLs:
  - '*'
  verbs:
  - '*'
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: clusterpedia-synchro
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: clusterpedia-synchro
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: clusterpedia-synchro
subjects:
- kind: ServiceAccount
  name: clusterpedia-synchro
  namespace: default
---
[root@master01 clusterpedia]# kubectl apply -f clusterpedia_synchro_rbac.yaml 
clusterrole.rbac.authorization.k8s.io/clusterpedia-synchro created
serviceaccount/clusterpedia-synchro created
clusterrolebinding.rbac.authorization.k8s.io/clusterpedia-synchro created

# 查看 sa/secret
[root@master01 clusterpedia]# kubectl get sa 
NAME                   SECRETS   AGE
clusterpedia-synchro   1         9s
default                1         2d14h
[root@master01 clusterpedia]# kubectl get secret 
NAME                               TYPE                                  DATA   AGE
clusterpedia-synchro-token-bjj5m   kubernetes.io/service-account-token   3      14s
default-token-jxtkh                kubernetes.io/service-account-token   3      2d14h
sh.helm.release.v1.dao-2048.v1     helm.sh/release.v1                    1      43h

# 获取 caData/toeknData
[root@master01 clusterpedia]# kubectl get secret clusterpedia-synchro-token-bjj5m -o yaml
apiVersion: v1
data:
  ca.crt: LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUdNRENDQkJpZ0F3SUJBZ0lKQU1CVkpiU3RXZ0JKTUEwR0NTcUdTSWIzRFFFQkN3VUFNRzB4Q3pBSkJnTlYKQkFZVEFrTk9NUkV3RHdZRFZRUUlFd2hUYUdGdVoyaGhhVEVSTUE4R0ExVUVCeE1JVTJoaGJtZG9ZV2t4RVRBUApCZ05WQkFvVENFUmhiME5zYjNWa01SRXdEd1lEVlFRTEV3aEVZVzlEYkc5MVpERVNNQkFHQTFVRUF4TUpiRzlqCllXeG9iM04wTUI0WERURTNNRFV4TURBMk16UTFPVm9YRFRJM01EVXdPREEyTXpRMU9Wb3diVEVMTUFrR0ExVUUKQmhNQ1EwNHhFVEFQQmdOVkJBZ1RDRk5vWVc1bmFHRnBNUkV3RHdZRFZRUUhFd2hUYUdGdVoyaGhhVEVSTUE4RwpBMVVFQ2hNSVJHRnZRMnh2ZFdReEVUQVBCZ05WQkFzVENFUmhiME5zYjNWa01SSXdFQVlEVlFRREV3bHNiMk5oCmJHaHZjM1F3Z2dJaU1BMEdDU3FHU0liM0RRRUJBUVVBQTRJQ0R3QXdnZ0lLQW9JQ0FRQzFab3laTFdIc2ozVGMKN09PejRxZUlDa1J0NTFOM1lJVkNqc2cxTnA1ZllLQWRzQStNRktWN3VWYnc5djcrbmZpUEwySjFoeGx1MzF2UAo0Zlliamp5ZlAyd0w0RXlOeVBxYjlhNG5nRWZxZmhxOUo1QitCTWd2cTNSMFNCQ05YTTE2Mm1pSzBuUmlSU1pUCmlvSTY0S29wdjFvWXFsaW5mR2RzcnlPdHM1UUpYMFN1TEZKekhIK1hpa3dzQVJSOWNjRkpGajZTazJHODllZkUKZ1FaY2hvZThnd3BqSW9zK2w4S1BEVkxEdDFzeVM4MUVZaFpLZXpSWmZVWmdyb0VhZU5iRVdmNjg5NGpRQUdhNwpsbklpL0RCTWJXYjcwN1FybG9mYkt4ZWorSE9OUHdzai9uZFB5VjM3SFVNOG5iMFM3eTJ5V3A0dFJVdm5QQ2R4CkRWUjlyYzRMUEhGbjB5SUZtTmRrNTU5Q3BTS01meHBoTjNzbkZXdEsxZG1ieis3R2svUlpwRi96VkYvMnpEM2UKRkVTWmVZOU9ucUt0Wk1VZlR4dy9oZW83dC9OZHFNdU50TVJJY294SHREdzZIU0pibHhwTkxIcnh5M0l3Z3lUZApBZVMvR3Rjblg5T3hYRHFWUDJMN1RENlVuK05GRVBSbHhqTi9EVzRRS1gvdGg4T2FNTU9PekVZdlhTUUl2TVg4ClRTb2x5c0pBNGhrR0crM09YVUNENzFwS0N0TTVTU2lPTzNYc0xQdm1YYWt6NXpNd0p3cXBPUyt6M01LM0s4K08KRFBOcld1ZExNcm40VVduRkx2SzJhakx3Q2xTYk5Rdzk0K0I0eVdqVkR5a21hNGpkUm1QSkVvTVBRN3NNTGRISQpHbHdEOWkxMGdpaUpiR3haclp1a0pIUlMvMzFQS3dJREFRQUJvNEhTTUlIUE1CMEdBMVVkRGdRV0JCUlZsajNlCk1mWk1KNGVnSEdGbHRmcVAwSWxBNVRDQm53WURWUjBqQklHWE1JR1VnQlJWbGozZU1mWk1KNGVnSEdGbHRmcVAKMElsQTVhRnhwRzh3YlRFTE1Ba0dBMVVFQmhNQ1EwNHhFVEFQQmdOVkJBZ1RDRk5vWVc1bmFHRnBNUkV3RHdZRApWUVFIRXdoVGFHRnVaMmhoYVRFUk1BOEdBMVVFQ2hNSVJHRnZRMnh2ZFdReEVUQVBCZ05WQkFzVENFUmhiME5zCmIzVmtNUkl3RUFZRFZRUURFd2xzYjJOaGJHaHZjM1NDQ1FEQVZTVzByVm9BU1RBTUJnTlZIUk1FQlRBREFRSC8KTUEwR0NTcUdTSWIzRFFFQkN3VUFBNElDQVFBYjRnenI1dXhLZEdWTjBRck9meWNvS1BiTDltN0hsazlYcDFOYgpiVXQzQ0FnbHhDemc0NkVqOTNZK2dOZHF6SmNoU2o3M3RIYmRMYzY0Zlh1R3Riemp4RU55aUcwTlFVUXlVdEVBCjFKUmhJY2RSaG1uZVpzNGNNdm9OVTVmbU4yRllVZGFFT3JoUkRHd3pzQks1MDgzVXNDRVBaelhxV1FVRUpWNlQKVTVoMmJQbHUxT3ZwdlhpQ0hENG5kOVVSa21pZkdGSWZHWk16enRjay9MQnVEWE4wdUltSW1mSXluM0hkK2FNRQpZaTk1N1NjVFhuSXVkK0dtOVRkZjZSRW14Z0pkQVhwUmZVRm9UOVRBVURIcFhGcTlHcW4xSmlHUlJxRWFVbWZ6Cmp5ek5DMXowQmtMK2JkOG5LTGpseURhMVdaNHRuYU1yMGZ0TFp4dldYeEJ0NjBDcVM2Rk1SekhTUHpPRUNUSjQKb1g4WjlsQnhBYkx3bTBjSUx2K2JHdGxOREwzbGlxK3h1ck5OQjJsOHdFcndNUTdoUEVFeG1wQ0VJRGcxNVBCQgpKb3A0bEpxNTlwVms4dytNbzJzR3psMVVrSE5yOUdRbi9MZ3pCNDFrdTEzcll4dCthWFN0eTYzVUM1dUc5SEtlCldmY2U1RXE4YkcyZmZlME45c2xLdmc3K0FMNFdiNEtFVjk5U2VmY0pqL3JrcitiN2xrbERBZjl5cVJLNzdwMHkKZkZLT3dtSTVadlVSQW9BZDRBN1R4cXMvNjRNUjNWREhlMWZiMzVUU2g5RjZhSm0wVWNkQ2I3MGcwUG01bERoRwpOTTEyNjlKUHUxNVQxRHNHbWxUVGxSOXNHUFR4QnM0QlkvRDVFdDNRdFYvS2tIWTVDSW9RZnk3SXNCdWdyeU1rCjZ1UmZOQT09Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K
  namespace: ZGVmYXVsdA==
  token: ZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNkltUnVibTFSYUVkbVdtTlBUR2hzZHpVd1dEZE9UVWhhZFdKdlJVZHpaMDV2Y1hOcmFqTnNTM1ZVYUhNaWZRLmV5SnBjM01pT2lKcmRXSmxjbTVsZEdWekwzTmxjblpwWTJWaFkyTnZkVzUwSWl3aWEzVmlaWEp1WlhSbGN5NXBieTl6WlhKMmFXTmxZV05qYjNWdWRDOXVZVzFsYzNCaFkyVWlPaUprWldaaGRXeDBJaXdpYTNWaVpYSnVaWFJsY3k1cGJ5OXpaWEoyYVdObFlXTmpiM1Z1ZEM5elpXTnlaWFF1Ym1GdFpTSTZJbU5zZFhOMFpYSndaV1JwWVMxemVXNWphSEp2TFhSdmEyVnVMV0pxYWpWdElpd2lhM1ZpWlhKdVpYUmxjeTVwYnk5elpYSjJhV05sWVdOamIzVnVkQzl6WlhKMmFXTmxMV0ZqWTI5MWJuUXVibUZ0WlNJNkltTnNkWE4wWlhKd1pXUnBZUzF6ZVc1amFISnZJaXdpYTNWaVpYSnVaWFJsY3k1cGJ5OXpaWEoyYVdObFlXTmpiM1Z1ZEM5elpYSjJhV05sTFdGalkyOTFiblF1ZFdsa0lqb2lOakZoWVRZMk16VXRPV1UwWlMwME9UQmpMV0ZtTjJJdFpEUTFaVGs0WkdNME9XRmxJaXdpYzNWaUlqb2ljM2x6ZEdWdE9uTmxjblpwWTJWaFkyTnZkVzUwT21SbFptRjFiSFE2WTJ4MWMzUmxjbkJsWkdsaExYTjVibU5vY204aWZRLkljVnNmcEdRVDFfUC1DM1BZRkZ4TU95dzIzdk10Ykw5Z2NNMVc2bnJRcWt1OE95dl9GaHFBLWxoV2dQXzRZRW83S0o0NU5qeGNlTDZtZkdub1BSX2NnaHoxVjVZSEZhUFhVVTFBZDl4NjA0bnlzTHFYemdCLUVKdEE4MjJZX0tHUWE3RHVuWktDUHJ2Y2NybVZiOS1NcEpoYjFfVmJTVDNpbWpiSDFSRnRHWnM1MllyU1ZNWmZqb0luR3BhemRQTzA3dFFTTmpXc0NUaTdlcW42cFIwV2VTOUZCYV83MXdDX1ZTdkRpYWZsRnRqT3ZNamdYbmc4OXJjVW8zWlNMaXd5aGcwYnhHOXZSWXRxTXp1X0hFa3JxTXJMTV9RaGJSc0lrWTJmTnlaN2hBY2VrRXl4eWJQWkpYVzV0Z3NBZ2Jka0RmOUJQS2NDWnJhWHdhdVdBX0dIZw==
kind: Secret
metadata:
  annotations:
    kubernetes.io/service-account.name: clusterpedia-synchro
    kubernetes.io/service-account.uid: 61aa6635-9e4e-490c-af7b-d45e98dc49ae
  creationTimestamp: "2023-01-11T02:07:32Z"
  name: clusterpedia-synchro-token-bjj5m
  namespace: default
  resourceVersion: "1032452"
  selfLink: /api/v1/namespaces/default/secrets/clusterpedia-synchro-token-bjj5m
  uid: 52f797f6-9c86-4ac4-935e-7d9ce5f87370
type: kubernetes.io/service-account-token
```

## 2. cluserpedia 组件节点中创建 pediacluser 实例

```shell
# 创建 pediacluser 配置文件
[root@master01 ~]# cat clusterpedia/examples/pediacluster-dce4010.yaml 
apiVersion: cluster.clusterpedia.io/v1alpha2
kind: PediaCluster
metadata:
  name: cluster2-dce4010
spec:
  apiserver: "https://10.29.16.27:16443"
  caData: "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSUdNRENDQkJpZ0F3SUJBZ0lKQU1CVkpiU3RXZ0JKTUEwR0NTcUdTSWIzRFFFQkN3VUFNRzB4Q3pBSkJnTlYKQkFZVEFrTk9NUkV3RHdZRFZRUUlFd2hUYUdGdVoyaGhhVEVSTUE4R0ExVUVCeE1JVTJoaGJtZG9ZV2t4RVRBUApCZ05WQkFvVENFUmhiME5zYjNWa01SRXdEd1lEVlFRTEV3aEVZVzlEYkc5MVpERVNNQkFHQTFVRUF4TUpiRzlqCllXeG9iM04wTUI0WERURTNNRFV4TURBMk16UTFPVm9YRFRJM01EVXdPREEyTXpRMU9Wb3diVEVMTUFrR0ExVUUKQmhNQ1EwNHhFVEFQQmdOVkJBZ1RDRk5vWVc1bmFHRnBNUkV3RHdZRFZRUUhFd2hUYUdGdVoyaGhhVEVSTUE4RwpBMVVFQ2hNSVJHRnZRMnh2ZFdReEVUQVBCZ05WQkFzVENFUmhiME5zYjNWa01SSXdFQVlEVlFRREV3bHNiMk5oCmJHaHZjM1F3Z2dJaU1BMEdDU3FHU0liM0RRRUJBUVVBQTRJQ0R3QXdnZ0lLQW9JQ0FRQzFab3laTFdIc2ozVGMKN09PejRxZUlDa1J0NTFOM1lJVkNqc2cxTnA1ZllLQWRzQStNRktWN3VWYnc5djcrbmZpUEwySjFoeGx1MzF2UAo0Zlliamp5ZlAyd0w0RXlOeVBxYjlhNG5nRWZxZmhxOUo1QitCTWd2cTNSMFNCQ05YTTE2Mm1pSzBuUmlSU1pUCmlvSTY0S29wdjFvWXFsaW5mR2RzcnlPdHM1UUpYMFN1TEZKekhIK1hpa3dzQVJSOWNjRkpGajZTazJHODllZkUKZ1FaY2hvZThnd3BqSW9zK2w4S1BEVkxEdDFzeVM4MUVZaFpLZXpSWmZVWmdyb0VhZU5iRVdmNjg5NGpRQUdhNwpsbklpL0RCTWJXYjcwN1FybG9mYkt4ZWorSE9OUHdzai9uZFB5VjM3SFVNOG5iMFM3eTJ5V3A0dFJVdm5QQ2R4CkRWUjlyYzRMUEhGbjB5SUZtTmRrNTU5Q3BTS01meHBoTjNzbkZXdEsxZG1ieis3R2svUlpwRi96VkYvMnpEM2UKRkVTWmVZOU9ucUt0Wk1VZlR4dy9oZW83dC9OZHFNdU50TVJJY294SHREdzZIU0pibHhwTkxIcnh5M0l3Z3lUZApBZVMvR3Rjblg5T3hYRHFWUDJMN1RENlVuK05GRVBSbHhqTi9EVzRRS1gvdGg4T2FNTU9PekVZdlhTUUl2TVg4ClRTb2x5c0pBNGhrR0crM09YVUNENzFwS0N0TTVTU2lPTzNYc0xQdm1YYWt6NXpNd0p3cXBPUyt6M01LM0s4K08KRFBOcld1ZExNcm40VVduRkx2SzJhakx3Q2xTYk5Rdzk0K0I0eVdqVkR5a21hNGpkUm1QSkVvTVBRN3NNTGRISQpHbHdEOWkxMGdpaUpiR3haclp1a0pIUlMvMzFQS3dJREFRQUJvNEhTTUlIUE1CMEdBMVVkRGdRV0JCUlZsajNlCk1mWk1KNGVnSEdGbHRmcVAwSWxBNVRDQm53WURWUjBqQklHWE1JR1VnQlJWbGozZU1mWk1KNGVnSEdGbHRmcVAKMElsQTVhRnhwRzh3YlRFTE1Ba0dBMVVFQmhNQ1EwNHhFVEFQQmdOVkJBZ1RDRk5vWVc1bmFHRnBNUkV3RHdZRApWUVFIRXdoVGFHRnVaMmhoYVRFUk1BOEdBMVVFQ2hNSVJHRnZRMnh2ZFdReEVUQVBCZ05WQkFzVENFUmhiME5zCmIzVmtNUkl3RUFZRFZRUURFd2xzYjJOaGJHaHZjM1NDQ1FEQVZTVzByVm9BU1RBTUJnTlZIUk1FQlRBREFRSC8KTUEwR0NTcUdTSWIzRFFFQkN3VUFBNElDQVFBYjRnenI1dXhLZEdWTjBRck9meWNvS1BiTDltN0hsazlYcDFOYgpiVXQzQ0FnbHhDemc0NkVqOTNZK2dOZHF6SmNoU2o3M3RIYmRMYzY0Zlh1R3Riemp4RU55aUcwTlFVUXlVdEVBCjFKUmhJY2RSaG1uZVpzNGNNdm9OVTVmbU4yRllVZGFFT3JoUkRHd3pzQks1MDgzVXNDRVBaelhxV1FVRUpWNlQKVTVoMmJQbHUxT3ZwdlhpQ0hENG5kOVVSa21pZkdGSWZHWk16enRjay9MQnVEWE4wdUltSW1mSXluM0hkK2FNRQpZaTk1N1NjVFhuSXVkK0dtOVRkZjZSRW14Z0pkQVhwUmZVRm9UOVRBVURIcFhGcTlHcW4xSmlHUlJxRWFVbWZ6Cmp5ek5DMXowQmtMK2JkOG5LTGpseURhMVdaNHRuYU1yMGZ0TFp4dldYeEJ0NjBDcVM2Rk1SekhTUHpPRUNUSjQKb1g4WjlsQnhBYkx3bTBjSUx2K2JHdGxOREwzbGlxK3h1ck5OQjJsOHdFcndNUTdoUEVFeG1wQ0VJRGcxNVBCQgpKb3A0bEpxNTlwVms4dytNbzJzR3psMVVrSE5yOUdRbi9MZ3pCNDFrdTEzcll4dCthWFN0eTYzVUM1dUc5SEtlCldmY2U1RXE4YkcyZmZlME45c2xLdmc3K0FMNFdiNEtFVjk5U2VmY0pqL3JrcitiN2xrbERBZjl5cVJLNzdwMHkKZkZLT3dtSTVadlVSQW9BZDRBN1R4cXMvNjRNUjNWREhlMWZiMzVUU2g5RjZhSm0wVWNkQ2I3MGcwUG01bERoRwpOTTEyNjlKUHUxNVQxRHNHbWxUVGxSOXNHUFR4QnM0QlkvRDVFdDNRdFYvS2tIWTVDSW9RZnk3SXNCdWdyeU1rCjZ1UmZOQT09Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K"
  tokenData: "ZXlKaGJHY2lPaUpTVXpJMU5pSXNJbXRwWkNJNkltUnVibTFSYUVkbVdtTlBUR2hzZHpVd1dEZE9UVWhhZFdKdlJVZHpaMDV2Y1hOcmFqTnNTM1ZVYUhNaWZRLmV5SnBjM01pT2lKcmRXSmxjbTVsZEdWekwzTmxjblpwWTJWaFkyTnZkVzUwSWl3aWEzVmlaWEp1WlhSbGN5NXBieTl6WlhKMmFXTmxZV05qYjNWdWRDOXVZVzFsYzNCaFkyVWlPaUprWldaaGRXeDBJaXdpYTNWaVpYSnVaWFJsY3k1cGJ5OXpaWEoyYVdObFlXTmpiM1Z1ZEM5elpXTnlaWFF1Ym1GdFpTSTZJbU5zZFhOMFpYSndaV1JwWVMxemVXNWphSEp2TFhSdmEyVnVMV0pxYWpWdElpd2lhM1ZpWlhKdVpYUmxjeTVwYnk5elpYSjJhV05sWVdOamIzVnVkQzl6WlhKMmFXTmxMV0ZqWTI5MWJuUXVibUZ0WlNJNkltTnNkWE4wWlhKd1pXUnBZUzF6ZVc1amFISnZJaXdpYTNWaVpYSnVaWFJsY3k1cGJ5OXpaWEoyYVdObFlXTmpiM1Z1ZEM5elpYSjJhV05sTFdGalkyOTFiblF1ZFdsa0lqb2lOakZoWVRZMk16VXRPV1UwWlMwME9UQmpMV0ZtTjJJdFpEUTFaVGs0WkdNME9XRmxJaXdpYzNWaUlqb2ljM2x6ZEdWdE9uTmxjblpwWTJWaFkyTnZkVzUwT21SbFptRjFiSFE2WTJ4MWMzUmxjbkJsWkdsaExYTjVibU5vY204aWZRLkljVnNmcEdRVDFfUC1DM1BZRkZ4TU95dzIzdk10Ykw5Z2NNMVc2bnJRcWt1OE95dl9GaHFBLWxoV2dQXzRZRW83S0o0NU5qeGNlTDZtZkdub1BSX2NnaHoxVjVZSEZhUFhVVTFBZDl4NjA0bnlzTHFYemdCLUVKdEE4MjJZX0tHUWE3RHVuWktDUHJ2Y2NybVZiOS1NcEpoYjFfVmJTVDNpbWpiSDFSRnRHWnM1MllyU1ZNWmZqb0luR3BhemRQTzA3dFFTTmpXc0NUaTdlcW42cFIwV2VTOUZCYV83MXdDX1ZTdkRpYWZsRnRqT3ZNamdYbmc4OXJjVW8zWlNMaXd5aGcwYnhHOXZSWXRxTXp1X0hFa3JxTXJMTV9RaGJSc0lrWTJmTnlaN2hBY2VrRXl4eWJQWkpYVzV0Z3NBZ2Jka0RmOUJQS2NDWnJhWHdhdVdBX0dIZw=="
  syncResources:
  - group: apps
    resources:
     - deployments
  - group: ""
    resources:
     - pods
     - configmaps
  - group: cert-manager.io
    versions:
      - v1
    resources:
      - certificates

# caData / tokenData 均来自接入集群中 clusterpedia-synchro-token-bjj5m Secret。另外 1.24 以后版本的 k8s，在创建 sa 后不会自动创建对应的 secret

# 查看 pediacluser 列表
[root@master01 ~]# kubectl get pediacluster
NAME                 READY   VERSION    APISERVER
cluster1-maweibing   True    v1.24.7    https://10.29.15.79:6443
cluster2-dce4010     True    v1.18.20   https://10.29.16.27:16443

# 通过 -o yaml 可以查看资源的同步状态
```

## 3. cluserpedia 组件节点中为 kubectl 生成集群快捷访问配置

```shell
# 备份 kubeconfig 文件
[root@master01 ~]# cp .kube/config .kube/config_bak

# 追加 pediacluser 配置信息到 kubeconfig
[root@master01 ~]# bash gen_clusterconfig.sh 
Current Context: kubernetes-admin@cluster.local
Current Cluster: cluster.local
        Server: https://127.0.0.1:6443
        TLS Server Name: 
        Insecure Skip TLS Verify: 
        Certificate Authority: 
        Certificate Authority Data: ***

Cluster "clusterpedia" set.
Cluster "dce4-010" set.
Cluster "dce5-member" set.

# 执行后 .kube/config 新增 3 个 cluster 配置，分别是 get pediacluster 集群信息、和 1 个 clusterpedia <这个是属于一个多集群的概念，通过它可以检索所有集群的资源信息>
```

## 4. cluserpedia 组件节点中使用 kubectl 检查集群资源 [更多检索技巧](https://clusterpedia.io/zh-cn/docs/usage/search/)

```shell
# 检索所有 pediacluster 所同步的资源信息
[root@master01 ~]# kubectl --cluster clusterpedia api-resources
NAME          SHORTNAMES   APIVERSION   NAMESPACED   KIND
configmaps    cm           v1           true         ConfigMap
pods          po           v1           true         Pod
deployments   deploy       apps/v1      true         Deployment

# 检索所有 pediacluster 资源
[root@master01 ~]# kubectl --cluster clusterpedia get deployments.apps -A 
NAMESPACE             CLUSTER              NAME                                                 READY   UP-TO-DATE   AVAILABLE   AGE
calico-apiserver      cluster1-maweibing   calico-apiserver                                     1/1     1            1           73d
clusterpedia-system   cluster1-maweibing   clusterpedia-apiserver                               1/1     1            1           33d
clusterpedia-system   cluster1-maweibing   clusterpedia-clustersynchro-manager                  1/1     1            1           33d
dce-system            cluster2-dce4010     dce-system-dnsservice                                1/1     1            1           47h
dce-system            cluster2-dce4010     dce-system-loadbalancermanager                       1/1     1            1           44h
dce-system            cluster2-dce4010     dce-system-uds                                       1/1     1            1           2d14h
default               cluster2-dce4010     dao-2048                                             1/1     1            1           43h
kube-system           cluster2-dce4010     calico-kube-controllers                              1/1     1            1           2d14h
kube-system           cluster2-dce4010     coredns-coredns                                      2/2     2            2           47h
kube-system           cluster2-dce4010     dce-chart-manager                                    1/1     1            1           2d14h
kube-system           cluster2-dce4010     dce-clair                                            1/1     1            1           2d14h

# 检索指定集群和租户信息
[root@master01 ~]# kubectl --cluster cluster2-dce4010 get deployments.apps -n kube-system 
CLUSTER            NAME                                                 READY   UP-TO-DATE   AVAILABLE   AGE
cluster2-dce4010   calico-kube-controllers                              1/1     1            1           2d14h
cluster2-dce4010   coredns-coredns                                      2/2     2            2           47h
cluster2-dce4010   dce-chart-manager                                    1/1     1            1           2d14h
cluster2-dce4010   dce-clair                                            1/1     1            1           2d14h
cluster2-dce4010   dce-controller                                       1/1     1            1           2d14h
cluster2-dce4010   dce-core-keepalived                                  1/1     1            1           2d14h
cluster2-dce4010   dce-prometheus                                       1/1     1            1           2d14h
cluster2-dce4010   dce-registry                                         1/1     1            1           2d14h
cluster2-dce4010   dce-uds-daocloud-dlocal-local-1-0-0-csi-controller   1/1     1            1           37h
cluster2-dce4010   dce-uds-failover-assistant                           1/1     1            1           2d14h
cluster2-dce4010   dce-uds-policy-controller                            1/1     1            1           2d14h
cluster2-dce4010   dce-uds-snapshot-controller                          1/1     1            1           2d14h
cluster2-dce4010   dce-uds-storage-server                               1/1     1            1           2d14h
cluster2-dce4010   lb01-ingress1                                        1/1     1            1           44h
cluster2-dce4010   lb01-ingress2                                        1/1     1            1           44h
cluster2-dce4010   lb01-keepalived                                      2/2     2            2           44h
cluster2-dce4010   metrics-server                                       1/1     1            1           2d14h

[root@master01 ~]# kubectl --cluster cluster2-dce4010 get pod -o wide -n kube-system 
CLUSTER            NAME                                                              READY   STATUS    RESTARTS        AGE     IP               NODE       NOMINATED NODE   READINESS GATES
cluster2-dce4010   calico-kube-controllers-789ff96b77-lwvb6                          1/1     Running   0               2d14h   10.29.16.27      master01   <none>           <none>
cluster2-dce4010   calico-node-28xtc                                                 1/1     Running   0               2d13h   10.29.16.33      worker02   <none>           <none>
cluster2-dce4010   calico-node-bc8b7                                                 1/1     Running   0               2d14h   10.29.16.27      master01   <none>           <none>
cluster2-dce4010   calico-node-bs9fh                                                 1/1     Running   0               2d13h   10.29.16.30      worker01   <none>           <none>
cluster2-dce4010   calico-node-dbz46                                                 1/1     Running   0               37h     10.29.16.39      worker03   <none>           <none>
cluster2-dce4010   coredns-coredns-5b879856b7-lnj4g                                  1/1     Running   0               47h     172.28.2.130     worker01   <none>           <none>
cluster2-dce4010   coredns-coredns-5b879856b7-mjjcl                                  1/1     Running   0               47h     172.28.48.1      worker02   <none>           <none>
cluster2-dce4010   dce-chart-manager-795cdfd86b-6dhnv                                1/1     Running   0               2d14h   172.28.213.70    master01   <none>           <none>
```

