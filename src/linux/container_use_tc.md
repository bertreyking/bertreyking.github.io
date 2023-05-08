# 使用 TC 模拟容器内网络延迟

## 场景

- 模拟跨地域级别的请求，通过广域网的形式无法满足需求，因此使用 tc 来模拟请求链路上的延迟

## 前提

- 基础镜像需要安装 iproute、nmap-ncat

```shell
sh-4.2# yum install -y iproute nmap-ncat

sh-4.2# tc
Usage: tc [ OPTIONS ] OBJECT { COMMAND | help }
       tc [-force] [-OK] -batch filename
where  OBJECT := { qdisc | class | filter | action | monitor | exec }
       OPTIONS := { -s[tatistics] | -d[etails] | -r[aw] | -p[retty] | -b[atch] [filename] | -n[etns] name |
                    -nm | -nam[es] | { -cf | -conf } path }
sh-4.2# nc 
Ncat: You must specify a host to connect to. QUITTING.

sh-4.2# nc -vz 10.2x.16.2x 22 
Ncat: Version 7.50 ( https://nmap.org/ncat )
Ncat: Connected to 10.2x.16.2x:22.
Ncat: 0 bytes sent, 0 bytes received in 0.01 seconds.

sh-4.2# nc -vz 10.2x.16.2x 22 
Ncat: Version 7.50 ( https://nmap.org/ncat )
Ncat: Connected to 10.2x.16.2x:22.
Ncat: 0 bytes sent, 0 bytes received in 0.01 seconds.
```

## 配置规则

### 临时配置

- 添加规则，为了效果更明显这里我们设置为设置 100ms

```shell
[root@worker02 ~]# docker inspect `docker ps | grep centos | awk '{print $1}'` --format={{.State.Pid}}
299938
[root@worker02 ~]# nsenter -t 299938 -n tc qdisc add dev eth0 root handle 1: prio
[root@worker02 ~]# nsenter -t 299938 -n tc filter add dev eth0 parent 1:0 protocol ip prio 1 u32 match ip dst 10.2x.16.2x/32 match ip dport 22 0xffff flowid 2:1
[root@worker02 ~]# nsenter -t 299938 -n tc filter add dev eth0 parent 1:0 protocol ip prio 1 u32 match ip dst 10.2x.16.2x/32 match ip dport 22 0xffff flowid 2:1
[root@worker02 ~]# nsenter -t 299938 -n tc qdisc add dev eth0 parent 1:1 handle 2: netem delay 100ms
```

- 查看规则是否添加成功

```shell
[root@worker02 ~]# nsenter -t 299938 -n tc -s qdisc show dev eth0
qdisc prio 1: root refcnt 2 bands 3 priomap  1 2 2 2 1 2 0 0 1 1 1 1 1 1 1 1
 Sent 0 bytes 0 pkt (dropped 0, overlimits 0 requeues 0) 
 backlog 0b 0p requeues 0 
qdisc netem 2: parent 1:1 limit 1000 delay 100.0ms
 Sent 0 bytes 0 pkt (dropped 0, overlimits 0 requeues 0) 
 backlog 0b 0p requeues 0 

[root@worker02 ~]# nsenter -t 299938 -n tc -s filter show dev eth0
filter parent 1: protocol ip pref 1 u32 chain 0 
filter parent 1: protocol ip pref 1 u32 chain 0 fh 800: ht divisor 1 
filter parent 1: protocol ip pref 1 u32 chain 0 fh 800::800 order 2048 key ht 800 bkt 0 flowid 2:1 not_in_hw  (rule hit 0 success 0)
  match 0a1d101b/ffffffff at 16 (success 0 ) 
  match 00000016/0000ffff at 20 (success 0 ) 
filter parent 1: protocol ip pref 1 u32 chain 0 fh 800::801 order 2049 key ht 800 bkt 0 flowid 2:1 not_in_hw  (rule hit 0 success 0)
  match 0a1d1021/ffffffff at 16 (success 0 ) 
  match 00000016/0000ffff at 20 (success 0 ) 
```

- 验证规则是否生效

```shell
# 验证 dst+port 的响应时长
[root@worker02 ~]# nsenter -t 299938 -n nc -vz 10.2x.16.2x 22 
Ncat: Version 7.50 ( https://nmap.org/ncat )
Ncat: Connected to 10.2x.16.2x:22.
Ncat: 0 bytes sent, 0 bytes received in 0.11 seconds.
[root@worker02 ~]# nsenter -t 299938 -n nc -vz 10.2x.16.2x 22 
Ncat: Version 7.50 ( https://nmap.org/ncat )
Ncat: Connected to 10.2x.16.2x:22.
Ncat: 0 bytes sent, 0 bytes received in 0.12 seconds.

# 验证非 dst+port 的响应时长
[root@worker02 ~]# nsenter -t 299938 -n nc -vz 10.2x.16.2x 22 
Ncat: Version 7.50 ( https://nmap.org/ncat )
Ncat: Connected to 10.2x.16.2x:22.
Ncat: 0 bytes sent, 0 bytes received in 0.01 seconds.

# 再次查看匹配 tc filter 规则，发现已经匹配成功
[root@worker02 ~]# nsenter -t 299938 -n tc -s filter show dev eth0
filter parent 1: protocol ip pref 1 u32 chain 0 
filter parent 1: protocol ip pref 1 u32 chain 0 fh 800: ht divisor 1 
filter parent 1: protocol ip pref 1 u32 chain 0 fh 800::800 order 2048 key ht 800 bkt 0 flowid 2:1 not_in_hw  (rule hit 15 success 5)
  match 0a1d101b/ffffffff at 16 (success 5 ) 
  match 00000016/0000ffff at 20 (success 5 ) 
filter parent 1: protocol ip pref 1 u32 chain 0 fh 800::801 order 2049 key ht 800 bkt 0 flowid 2:1 not_in_hw  (rule hit 10 success 5)
  match 0a1d1021/ffffffff at 16 (success 5 ) 
  match 00000016/0000ffff at 20 (success 5 ) 
```

- 删除策略

```shell
tc -s qdisc del dev eth0 root
```

### 持久化配置

在 k8s 环境中，推荐使用 initContaiers 的 sidecar 模式来实现，yaml 如下：

``` yaml
kind: Deployment
apiVersion: apps/v1
metadata:
  name: centos-centos
  namespace: default
  labels:
    dce.daocloud.io/app: centos
spec:
  replicas: 1
  selector:
    matchLabels:
      dce.daocloud.io/component: centos-centos
  template:
    metadata:
      name: centos-centos
      creationTimestamp: null
      labels:
        dce.daocloud.io/app: centos
        dce.daocloud.io/component: centos-centos
      annotations:
        dce.daocloud.io/parcel.egress.burst: '0'
        dce.daocloud.io/parcel.egress.rate: '0'
        dce.daocloud.io/parcel.ingress.burst: '0'
        dce.daocloud.io/parcel.ingress.rate: '0'
        dce.daocloud.io/parcel.net.type: calico
        dce.daocloud.io/parcel.net.value: 'default-ipv4-ippool,default-ipv6-ippool'
    spec:
      initContainers:
        - name: init-centos-tc
          image: '10.2x.14x.1x/base/centos:7.9.2009'
          command:
            - /bin/sh
          args:
            - '-c'
            - >-
              yum install -y iproute nmap-ncat && tc qdisc add dev eth0 root
              handle 1: prio && tc filter add dev eth0 parent 1:0 protocol ip
              prio 1 u32 match ip dst 10.2x.16.2x/32 match ip dport 22 0xffff
              flowid 2:1 && tc filter add dev eth0 parent 1:0 protocol ip prio 1
              u32 match ip dst 10.2x.16.3x/32 match ip dport 22 0xffff flowid
              2:1 && tc qdisc add dev eth0 parent 1:1 handle 2: netem delay
              100ms
          resources: {}
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
          imagePullPolicy: IfNotPresent
          securityContext:
            privileged: true
      containers:
        - name: centos-centos
          image: '10.2x.14x.1x/base/centos:7.9.2009'
          command:
            - sleep
          args:
            - '3600'
          resources:
            requests:
              cpu: '0'
              memory: '0'
          lifecycle: {}
          terminationMessagePath: /dev/termination-log
          terminationMessagePolicy: File
          imagePullPolicy: Always
      restartPolicy: Always
      terminationGracePeriodSeconds: 30
      dnsPolicy: ClusterFirst
      securityContext: {}
      imagePullSecrets:
        - name: centos-centos-10.2x.14x.1x
      schedulerName: default-scheduler
      dnsConfig:
        options:
          - name: single-request-reopen
            value: ''
          - name: ndots
            value: '2'
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 25%
      maxSurge: 25%
  revisionHistoryLimit: 10
  progressDeadlineSeconds: 600
```

## 参考文档

- [tc_adv_qdisc_and_filter](https://tldp.org/HOWTO/Adv-Routing-HOWTO/lartc.qdisc.filters.html)  
- [github_doc](https://gist.github.com/digilist/d4b8ecd92b9af7aa0492)
- [tc_adv_use](https://tldp.org/HOWTO/Adv-Routing-HOWTO/index.html)
