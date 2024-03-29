# Grafana Dashboard 

## Dashboard 中定义 Query Variable 从而获取对应 Job 中的 label 信息

常用查询变量 [Prometheus template variables][Prometheus template variables]

```shell
Name                          Description
label_names()                 Returns a list of label names.
label_values(label)           Returns a list of label values for the label in every metric.
label_values(metric, label)   Returns a list of label values for the label in the specified metric.
metrics(metric)               Returns a list of metrics matching the specified metric regex.
query_result(query)           Returns a list of Prometheus query result for the query.
```

前后数据对比(Prometheus Graph)

```shell
# 源数据

node_filesystem_size_bytes{device="/dev/mapper/centos-root",fstype="xfs",instance="10.6.203.60:9100",job="node_exporter-metrics",mountpoint="/"}	50432839680
node_filesystem_size_bytes{device="/dev/mapper/centos-root",fstype="xfs",instance="10.6.203.62:9100",job="node_exporter-metrics",mountpoint="/"}

# 目标数据
label_values(node_filesystem_size_bytes,instance)

Preview of values
All 10.6.203.60:9100 10.6.203.62:9100 10.6.203.63:9100 10.6.203.64:9100
```

[Prometheus template variables]: https://grafana.com/docs/grafana/latest/datasources/prometheus/template-variables/
