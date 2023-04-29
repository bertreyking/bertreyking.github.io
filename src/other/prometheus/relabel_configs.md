# [Prometheus 配置文件 relabel_configs 实操](https://prometheus.io/docs/prometheus/latest/configuration/configuration/#relabel_config)
- source_labels: 源标签
- separator: 分隔符，默认为；
- [regex](https://github.com/google/re2/wiki/Syntax): 按正则进行匹配，默认为 .*
- target_label: 指定一个 label 的 key
- replacement: 通过regex 检索出来的进行替换，默认为 $1 也就是 regex 匹配出来的 value
- action: <relabel_action>  基于 regex 进行的操作，默认是 replace
# relabel_action
- replace: 按 regex 进行匹配，并配合 replacement 的 $x，将 target_labels 的 key 与 replacement 的 $x 进行组合，另外如果没有 regex 则不会就行替换
- keep: 删除 regex 不匹配的 source_lables
- drop: 删除 regex 匹配的 source_lables
- labelmap: 将所有 regex 匹配到的lables，配合 replacement 进行替换操作
- labelkeep：删除 regex 不匹配的 source_lables
- labeldrop：删除 regex 不匹配的 source_lables

# 示例
- prometheus-job_configs
```
- job_name: kubelet-cadvisor
  honor_timestamps: true
  scrape_interval: 15s
  scrape_timeout: 10s
  metrics_path: /metrics/cadvisor
  scheme: https
  kubernetes_sd_configs:
  - api_server: https://10.6.203.60:6443
    role: node
    bearer_token_file: /opt/caas/prometh/prometh_server/k8s.token
    tls_config:
      insecure_skip_verify: true
  bearer_token_file: /opt/caas/prometh/prometh_server/k8s.token
  tls_config:
    insecure_skip_verify: true
  relabel_configs:
  - separator: ;
    regex: __meta_kubernetes_node_label_(.+)
    replacement: $1
    action: labelmap
 ```
 - prometheus-job_configs_jpg
 ![kubelet-job](https://raw.githubusercontent.com/bertreyking/monitor/master/prometheus/exporter/blackbox_exporter/labels.jpg)
 
 # relabel_config场景
 ```
 1. 标签新增(在后期制作dashboard以及使用metrics进行高级及自定义的筛选时会用到)
 2. 标签重构

- 示例文件如下：
    relabel_configs:
    
    - regex: __meta_kubernetes_node_label_(.+) #标签重构而非元数据信息
      replacement: $1
      action: labelmap
  
    - source_labels: [__meta_kubernetes_node_address_InternalIP] #标签新增
      target_label: node_ip
      replacement: $1
      action: replace
 ```
