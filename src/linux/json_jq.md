# jq 进阶

## 格式化 json 文件

```
命令：
cat allip | jq -r .
cat allip | jq -r '[select(any(.;.state=="acquired"))|.tenant_name,.cidr,.pod_name] | @tsv' | grep -v ^$ | awk '/monitoring/'

输出：
monitoring	10.6.	grafana-6468c88748-xgc68
monitoring	10.6.	kube-state-metrics-6d98cc688f-drc5r
monitoring	10.6.   prometheus-operator-7f7b8b587b-76bf6
monitoring	10.6.	kube-metrics-exporter-789954cdf9-gq8g5

说明：
- select(): 查询 json 数据中符合要求的， == ,!= , >= , <= 等其它
- any(condition): 布尔值数组作为输入，即 true/false，数据为真，则返回 true
- any(generator; condition): generator-json 数据按层级划分 ，condition 条件
```

## 取最大值、列表元素 <=10 个
```
cat /tmp/i_cpu_data.json | jq -r '[.values[][1]]|@json' | jq max -r
```

## 取最大值
```
cat /tmp/i_cpu_data.json | awk 'BEGIN {max = 0} {if ($1+0 > max+0) max=$1} END {print max}'
```

## 格式化数据，按 csv 格式输出
```
bash getadminrole_userlist.sh | jq -r '["User","Type","ID"],(.items[] | [.name,.type,.id]) | @csv'
"User","Type","ID"
"admin","user","b5ec0e22-bfbc-414c-83b3-260c0dca21d2"

说明：
["User","Type","ID"]：定义 title
(.items[] | [.name,.type,.id])：按 dict/list 对数据检索
｜ @csv：导出为 csv 格式
输出示例如下：
curl http://10.233.10.18:9090/api/v1/targets?state=active | jq -r '["targets","endpoint","health"],(.data.activeTargets[] | [.scrapePool,.scrapeUrl,.health]) | @tsv'
targets endpoint        health
serviceMonitor/ingress-nginx-lb01/ingress-nginx-lb01-controller/0       http://10.233.74.103:10254/metrics      up
serviceMonitor/insight-system/insight-agent-etcd-exporter/0     http://10.233.74.110:2381/metrics       up
serviceMonitor/insight-system/insight-agent-fluent-bit/0        http://10.233.74.119:2020/api/v1/metrics/prometheus     up
serviceMonitor/insight-system/insight-agent-fluent-bit/0        http://10.233.84.205:2020/api/v1/metrics/prometheus     up
serviceMonitor/insight-system/insight-agent-kube-prometh-apiserver/0    https://10.29.26.199:6443/metrics       up
serviceMonitor/insight-system/insight-agent-kube-prometh-coredns/0      http://10.233.74.127:9153/metrics       up
serviceMonitor/insight-system/insight-agent-kube-prometh-coredns/0      http://10.233.84.219:9153/metrics       up
```


## 参考链接

- [集群启动失败的pod](https://stackoverflow.com/questions/57222210/how-can-i-view-pods-with-kubectl-and-filter-based-on-having-a-status-of-imagepul?answertab=active#tab-top)
- [jq 官方手册](https://stedolan.github.io/jq/manual/#Invokingjq)
- [jq 输出格式](https://gist.github.com/sloanlance/6b648e51c3c2a69ae200c93c6a310cb6)
- [jq select用法](https://stackoverflow.com/questions/46530167/jq-select-filter-with-multiple-arguments)
