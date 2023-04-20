## [Prometheus 查询函数 ](https://prometheus.io/docs/prometheus/latest/querying/functions/)

### label_join

-  新增 label，并将 source_labels 的 values 赋予给 new_label=values

 ```shell
- 格式:
label_join(v instant-vector, dst_label string, separator string, src_label_1, src_label_2)

- 示例:
label_join(up{job="kubelet"},"new_key",",","instance","node_ip")  # 若 "," 不写，会将第二个源标签 valeus 就行赋值，此语句是将 "instance","node_ip" 赋值给 new_key

- 输出:
up{beta_kubernetes_io_arch="amd64",beta_kubernetes_io_os="linux",instance="k8s-master01",job="kubelet",kubernetes_io_arch="amd64",kubernetes_io_hostname="k8s-master01",kubernetes_io_os="linux",new_key="k8s-master01,10.6.203.60",node_ip="10.6.203.60",noderole="master"}
 ```

### label_replace

- 新增 label，并将 source_labels 的 values 赋予给 new_label=values，并且支持 regex 匹配

 ```shell
- 格式:
label_replace(v instant-vector, dst_label string, replacement string, src_label string, regex string) # 如果 regex 匹配不到，则按原数据进行显示

- 示例:
label_replace(up,"new_key","$1","instance","(.*):.*") # 匹配 "instance" 的 values 的第一列数据，并且按 "(.*):.*" 进行过滤 
label_replace(up,"new_key","$1","instance","(.*)")    # 匹配 "instance" 的 values 的第一列数据

- 输出:
up{instance="10.6.179.65:9090",job="prometheus",new_key="10.6.179.65"}
up{instance="10.6.179.65:9090",job="prometheus",new_key="10.6.179.65:9090"}
 ```

