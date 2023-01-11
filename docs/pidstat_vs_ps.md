# 通过 pid 查找 container_ID

## 场景

我的问题是，节点负载很高(cpu/mem)，一时半会定位不到问题所在，且监控层面看到文件句柄数很高18w+，因此通过 pidstat 查看下进程利用率(内存相关)，因为之前出现过主机内存 90+% 的利用率居高不下

## 命令

```shell
# 查找占用 40g 以上的虚拟内存的 pid
# pidstat -rsl 1 3 | awk 'NR>1{if($7>40000000) print}'

# pidstat -rsl 1 3 | awk 'NR>1{if($7>10000) print}'
# output
11时42分28秒   UID       PID  minflt/s  majflt/s     VSZ    RSS   %MEM StkSize  StkRef  Command
11时42分30秒     0   2738052      1.54      0.00 1254560 484040   3.99    136      24  kube-apiserver --advertise-address=10.29.15.79 --allow-privileged=true --anonymous-auth=True --apiserver-count=1 --audit-log-ma
平均时间:   UID       PID  minflt/s  majflt/s     VSZ    RSS   %MEM StkSize  StkRef  Command
平均时间:     0   2738052      1.54      0.00 1254560 484040   3.99    136      24  kube-apiserver --advertise-address=10.29.15.79 --allow-privileged=true --anonymous-auth=True --apiserver-count=1 --audit-log-ma

# lsof -p $PID | wc -l  # 可以使用 lsof 来统计该 pid 的文件句柄数集信息，我的环境是打开了 8w+，kill 掉其主进程后内存和 cpu利用有所降低，之所以有 8w+，是因为其中一部分文件删除后没有自动释放掉导致

# 通过 pid 查找其是否有 ppid
# ps -elF | grep 2738052 | grep -v grep 
# output
4 S root     2738052 2737683 18  80   0 - 313640 futex_ 451296 5 1月02 ?       15:09:26 kube-apiserver --advertise-address=10.29.15.79 --allow-privileged=true --anonymous-auth=True --apiserver-count=1 --audit-log-maxage=30 --audit-log-maxbackup=1 --audit-log-maxsize=100 --audit-log-path=/var/log/audit/kube-apiserver-audit.log --audit-policy-file=/etc/kubernetes/audit-policy/apiserver-audit-policy.yaml --authorization-mode=Node,RBAC --bind-address=0.0.0.0 --client-ca-file=/etc/kubernetes/ssl/ca.crt --default-not-ready-toleration-seconds=300 --default-unreachable-toleration-seconds=300 --enable-admission-plugins=NodeRestriction --enable-aggregator-routing=False --enable-bootstrap-token-auth=true --endpoint-reconciler-type=lease --etcd-cafile=/etc/kubernetes/ssl/etcd/ca.crt --etcd-certfile=/etc/kubernetes/ssl/apiserver-etcd-client.crt --etcd-keyfile=/etc/kubernetes/ssl/apiserver-etcd-client.key --etcd-servers=https://127.0.0.1:2379 --event-ttl=1h0m0s --kubelet-client-certificate=/etc/kubernetes/ssl/apiserver-kubelet-client.crt --kubelet-client-key=/etc/kubernetes/ssl/apiserver-kubelet-client.key --kubelet-preferred-address-types=InternalDNS,InternalIP,Hostname,ExternalDNS,ExternalIP --profiling=False --proxy-client-cert-file=/etc/kubernetes/ssl/front-proxy-client.crt --proxy-client-key-file=/etc/kubernetes/ssl/front-proxy-client.key --request-timeout=1m0s --requestheader-allowed-names=front-proxy-client --requestheader-client-ca-file=/etc/kubernetes/ssl/front-proxy-ca.crt --requestheader-extra-headers-prefix=X-Remote-Extra- --requestheader-group-headers=X-Remote-Group --requestheader-username-headers=X-Remote-User --secure-port=6443 --service-account-issuer=https://kubernetes.default.svc.cluster.local --service-account-key-file=/etc/kubernetes/ssl/sa.pub --service-account-lookup=True --service-account-signing-key-file=/etc/kubernetes/ssl/sa.key --service-cluster-ip-range=10.233.0.0/18 --service-node-port-range=30000-32767 --storage-backend=etcd3 --tls-cert-file=/etc/kubernetes/ssl/apiserver.crt --tls-private-key-file=/etc/kubernetes/ssl/apiserver.key

# ps -elF | grep 2737683 | grep -v grep 
# output
0 S root     2737683       1  0  80   0 - 178160 futex_ 13124  5 1月02 ?       00:03:22 /usr/local/bin/containerd-shim-runc-v2 -namespace k8s.io -id fd272ecbe1bf56fb5fbff41130437e5c4b5b444dab2e315a19ed846dc1eacd42 -address /run/containerd/containerd.sock
4 S 65535    2737744 2737683  0  80   0 -   245 sys_pa     4   2 1月02 ?       00:00:00 /pause
4 S root     2738052 2737683 18  80   0 - 313640 futex_ 487444 5 1月02 ?       15:09:52 kube-apiserver --advertise-address=10.29.15.79 --allow-privileged=true --anonymous-auth=True --apiserver-count=1 --audit-log-maxage=30 --audit-log-maxbackup=1 --audit-log-maxsize=100 --audit-log-path=/var/log/audit/kube-apiserver-audit.log --audit-policy-file=/etc/kubernetes/audit-policy/apiserver-audit-policy.yaml --authorization-mode=Node,RBAC --bind-address=0.0.0.0 --client-ca-file=/etc/kubernetes/ssl/ca.crt --default-not-ready-toleration-seconds=300 --default-unreachable-toleration-seconds=300 --enable-admission-plugins=NodeRestriction --enable-aggregator-routing=False --enable-bootstrap-token-auth=true --endpoint-reconciler-type=lease --etcd-cafile=/etc/kubernetes/ssl/etcd/ca.crt --etcd-certfile=/etc/kubernetes/ssl/apiserver-etcd-client.crt --etcd-keyfile=/etc/kubernetes/ssl/apiserver-etcd-client.key --etcd-servers=https://127.0.0.1:2379 --event-ttl=1h0m0s --kubelet-client-certificate=/etc/kubernetes/ssl/apiserver-kubelet-client.crt --kubelet-client-key=/etc/kubernetes/ssl/apiserver-kubelet-client.key --kubelet-preferred-address-types=InternalDNS,InternalIP,Hostname,ExternalDNS,ExternalIP --profiling=False --proxy-client-cert-file=/etc/kubernetes/ssl/front-proxy-client.crt --proxy-client-key-file=/etc/kubernetes/ssl/front-proxy-client.key --request-timeout=1m0s --requestheader-allowed-names=front-proxy-client --requestheader-client-ca-file=/etc/kubernetes/ssl/front-proxy-ca.crt --requestheader-extra-headers-prefix=X-Remote-Extra- --requestheader-group-headers=X-Remote-Group --requestheader-username-headers=X-Remote-User --secure-port=6443 --service-account-issuer=https://kubernetes.default.svc.cluster.local --service-account-key-file=/etc/kubernetes/ssl/sa.pub --service-account-lookup=True --service-account-signing-key-file=/etc/kubernetes/ssl/sa.key --service-cluster-ip-range=10.233.0.0/18 --service-node-port-range=30000-32767 --storage-backend=etcd3 --tls-cert-file=/etc/kubernetes/ssl/apiserver.crt --tls-private-key-file=/etc/kubernetes/ssl/apiserver.key

# ps -ejH | grep -B 10 2738052  # 打印进程树
# output
2737683 2737683    1163 ?        00:03:24   containerd-shim
2737744 2737744 2737744 ?        00:00:00     pause
2738052 2738052 2738052 ?        15:17:02     kube-apiserver

# 结论
pid 2738052 是由 ppid 2737683 启动，而 2737683 是 containerd-shim 的 pid，因此 2738052 是 containerd-shim 的线程，也就是由它启动的 container
```

## 确认容器

```shell
# nerdctl ps | awk 'NR>1{print $1}' | while read line;do echo -n "ContainerID: " $line;  echo " Pid: " `nerdctl inspect $line --format="{{.State.Pid}}"`;done

# output
ContainerID:  001c06d37aa3 Pid:  3894654
ContainerID:  10948947ffe2 Pid:  3190
ContainerID:  12e473bf2092 Pid:  2738736
ContainerID:  2036c51b2eb1 Pid:  2638619
ContainerID:  31f6916a4d19 Pid:  2144173
ContainerID:  3e7aaa92e14d Pid:  946163
ContainerID:  40290d1314b0 Pid:  2737814
ContainerID:  41ef80123273 Pid:  2738052
ContainerID:  422a631fa706 Pid:  4151
ContainerID:  4bf701e368e1 Pid:  2737820
ContainerID:  535448e5cdd0 Pid:  2638612
ContainerID:  5ea9dbdedc25 Pid:  4711
ContainerID:  5f17a1c82e2a Pid:  2565
ContainerID:  68ddb09e71ba Pid:  4962
ContainerID:  69cf228ae17d Pid:  4054
ContainerID:  74d39157ea3c Pid:  2738680
ContainerID:  77cf2b283806 Pid:  5056
ContainerID:  7acb0441a3ad Pid:  2737689
ContainerID:  821dcae2eaca Pid:  1023468
ContainerID:  88060b9b98da Pid:  2448
ContainerID:  9179c60702c4 Pid:  2647586
ContainerID:  91ea0bcd6c1f Pid:  2737993
ContainerID:  95b54dbb14d0 Pid:  2286
ContainerID:  9cc402cb9ca2 Pid:  2716
ContainerID:  9dab08f90039 Pid:  946124
ContainerID:  ade4806bb944 Pid:  2518
ContainerID:  aee2b96ee5d9 Pid:  2544
ContainerID:  b3519e63725c Pid:  2737695
ContainerID:  b5bd53932069 Pid:  2295
ContainerID:  b816d668b027 Pid:  3962
ContainerID:  c8198ad4cc28 Pid:  2543
ContainerID:  d27c2a0c9a22 Pid:  1021592
ContainerID:  e9bdb4ad0fd6 Pid:  2350
ContainerID:  f41fa9aee395 Pid:  2737656
ContainerID:  f56f55af0af3 Pid:  4065
ContainerID:  fd272ecbe1bf Pid:  2737744

# grep 2738052 
# outout
ContainerID:  41ef80123273 Pid:  2738052

# nerdctl ps | grep 41ef80123273
# output
41ef80123273    k8s-gcr.m.daocloud.io/kube-apiserver:v1.24.7                             "kube-apiserver --ad…"    3 days ago      Up                 k8s://kube-system/kube-apiserver-master01/kube-apiserver

# kubectl get pod -o wide --all-namespaces  | grep kube-apiserver-master01
# output
kube-system           kube-apiserver-master01                                      1/1     Running            11 (3d9h ago)    67d   10.29.15.79      master01   <none>           <none>
```

## 总结

- pidstat -rsl 1 3 | awk 'NR>1{if($7>40000000) print}'

  ```shell

  -r 查看 pid 占用的内存信息，虚拟内存/实际使用内存/占总内存的百分比
  -s 查看 pid 占用的内存堆栈
  -l 显示详细的 command
  ```

- ps -elF ｜ grep $PID 

  ```shell

  -e 所有进程
  -L 显示线程，带有 LWP 和 NLWP 列，结合 -f 使用
  -l 通常是输出格式的控制
  -F 按指定格式打印进程/线程，信息更完整,结合 -el
  
  -elF 可以找到其线程的 ppid，我的环境中一次就定位到 pid，说明 pod 没有其它的主进程或者更多的线程，而像业务 pod，一般都是用 shell 脚本拉起主进程，而主进程再启动更多的线程，如果要定为就是多次使用 ps -elF 进行 ppid 的查询，并最后通过 ppid 来找到该线程/进程是哪个容器和 pod 产生的 
  
  -efL 可以精确的统计每个进程的线程数
  
  -ejH # 打印进程树、更直观
  ```  
