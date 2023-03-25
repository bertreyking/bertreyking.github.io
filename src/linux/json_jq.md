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


## 参考链接

- [集群启动失败的pod](https://stackoverflow.com/questions/57222210/how-can-i-view-pods-with-kubectl-and-filter-based-on-having-a-status-of-imagepul?answertab=active#tab-top)
- [jq 官方手册](https://stedolan.github.io/jq/manual/#Invokingjq)
- [jq 输出格式](https://gist.github.com/sloanlance/6b648e51c3c2a69ae200c93c6a310cb6)
- [jq select用法](https://stackoverflow.com/questions/46530167/jq-select-filter-with-multiple-arguments)
