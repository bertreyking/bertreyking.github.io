1. 处理json文件
```
cat allip | jq -r '[select(any(.;.state=="acquired"))|.tenant_name,.cidr,.pod_name] | @tsv' | grep -v ^$ | awk '/monitoring/'
monitoring	10.6.	grafana-6468c88748-xgc68
monitoring	10.6.	kube-state-metrics-6d98cc688f-drc5r
monitoring	10.6. prometheus-operator-7f7b8b587b-76bf6
monitoring	10.6.	kube-metrics-exporter-789954cdf9-gq8g5


注释：
    select(): 查询json数据中符合要求的， == ,!= , >= , <= 等其它
    any(condition): 布尔值数组作为输入，即 true/false，数据为真，则返回true
    any(generator; condition): generator-json数据按层级划分 ，condition 条件
```
2. 取最大值
```
cat /tmp/i_cpu_data.json | jq -r '[.values[][1]]|@json' | jq max -r  #列表元素少于10个可以使用
cat /tmp/i_cpu_data.json | awk 'BEGIN {max = 0} {if ($1+0 > max+0) max=$1} END {print max}'
```

# 参考链接：
- [查询集群启动失败的pod](https://stackoverflow.com/questions/57222210/how-can-i-view-pods-with-kubectl-and-filter-based-on-having-a-status-of-imagepul?answertab=active#tab-top)
- [jq](https://stedolan.github.io/jq/manual/#Invokingjq)
- [jq输出格式](https://gist.github.com/sloanlance/6b648e51c3c2a69ae200c93c6a310cb6)
- [jq_select](https://stackoverflow.com/questions/46530167/jq-select-filter-with-multiple-arguments)
