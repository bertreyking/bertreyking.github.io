# Prometheus Job 丢失事件

## Prometheus 的监控项 是什么 ？

众所周知，Prometheus 中的监控项是在 Targets 中的，而 Targets 中定义了具体的监控项，也就是所谓的 Job，详情见 [CONFIGURATION][CONFIGURATION] 和 [SampleConfig][SampleConfig]		



## 记一次 Job 丢失后如何恢复

- 一次巡检中发现监控项 kubelet 丢失

## 排查思路

1. 查看 Prometheus 的配置文件，确认是否真的有配置其 kubelet 的 job
   - 存在

2. 查看 Prometheus Pod 的 log，提示 open /etc/ssl/private/kubelet/tls.crt: no such file or directory"
   - 说明是 Prometheus Server 去访问 kubelet job 的实例时认证错误导致(提示：找不到对应的证书文件)

3. 查看 Promethues StatefulSets，发现之前添加 volumes 和 volumeMounts 丢失了
   - volume 和 volumeMounts 就是声明了将 tls.crt 证书放在哪个目录下
4. 由于 Prometheus 时采用 operator 部署的，因此怀疑 operator 相关的 pod 重启导致 Promethues StatefulSets 的配置被还原，从而导致后续自定义的监控项 (Job) 被丢失
5. 建议自定义监控项 (Job) 全部更改为永久生效

## 更改为永久生效

- 将 kubelet-tls 密钥添加至 Prometheus CRD 下 k8s 资源中

```shell
kubectl get prometheus k8s -n monitoring -o yaml 
  secrets:         #增加 kubelet-tls
  - kubelet-tls
```
-  上述执行后，Prometheus 的 sts 会自动重建 pod，Prometheus 下会新增一个  volumeMounts 、volumes 的声明

```yaml
   volumeMounts:
   - mountPath: /etc/prometheus/secrets/kubelet-tls
     name: secret-kubelet-tls
     readOnly: true

  volumes:
  - name: secret-kubelet-tls
    secret:
      defaultMode: 420
      secretName: kubelet-tls
```
- 查看发现 Tartgets 下依然没有 kubelet 的 job，查看 Prometheus 的 log 发现证书路径与 volumeMounts 不一致

```shell
kubectl logs -f prometheus-k8s-0 -n monitoring -c prometheus
level=error ts=2021-01-06T10:09:02.392Z caller=manager.go:188 component="scrape manager" msg="error creating new scrape pool" err="error creating HTTP client: unable to use specified client cert (/etc/ssl/private/kubelet/tls.crt) & key (/etc/ssl/private/kubelet/tls.key): open /etc/ssl/private/kubelet/tls.crt: no such file or directory" scrape_pool=monitoring/kubelet/0
level=error ts=2021-01-06T10:09:02.392Z caller=manager.go:188 component="scrape manager" msg="error creating new scrape pool" err="error creating HTTP client: unable to use specified client cert (/etc/ssl/private/kubelet/tls.crt) & key (/etc/ssl/private/kubelet/tls.key): open /etc/ssl/private/kubelet/tls.crt: no such file or directory" scrape_pool=monitoring/kubelet/1
```
- 编辑 Servicemonitor 下 kubelet 监控项

```shell
kubectl edit servicemonitor kubelet -n monitoring
%s#/etc/ssl/private/kubelet#/etc/prometheus/secrets/kubelet-tls#g   #:(冒号)，全局替换保存退出
```
- 再次查看 kubelet 监控项 (Job) 已恢复

## 结论

- 追述之前是变更步骤时 kubectl patch 的方式添加的 volumes 和 volumeMounts 字段，所以在编辑 monitoring  下 crd 的 k8s 资源后，重建了 Prometheus 的 pod，所以之前自定义的配置丢失了

- 查看 operator 相关知识，说是可以在 crd prometheus下的 k8s 资源中自定义 volumes 和 volumemounts，但是尝试了几次不行，于是参照了 etcd-certs 的方式，并修改 Servermointor 下 kubelet 后使其永久生效

  

[CONFIGURATION]:https://prometheus.io/docs/prometheus/latest/configuration/configuration/
[SampleConfig]: https://github.com/prometheus/prometheus/tree/release-2.43/documentation/examples