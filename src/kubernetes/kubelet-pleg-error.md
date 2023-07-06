# 一次 kubelet PLEG is not healthy 报错事项

## 排查记录

- 现象：

  1. 节点 PLEG is not healthy 报错

     ```shell
     Jul 03 19:59:01 xxx-worker-004 kubelet[1946644]: E0703 19:59:01.292918 1946644 kubelet.go:1879] skipping pod synchronization - PLEG is not healthy: pleg was last seen active 3m36.462980645s ago; threshold is 3m0s
     Jul 03 19:59:06 xxx-worker-004 kubelet[1946644]: E0703 19:59:06.293545 1946644 kubelet.go:1879] skipping pod synchronization - PLEG is not healthy: pleg was last seen active 3m41.463610227s ago; threshold is 3m0s
     Jul 03 19:59:07 xxx-worker-004 kubelet[1946644]: I0703 19:59:07.513240 1946644 setters.go:77] Using node IP: "xxxxxx"
     Jul 03 19:59:11 xxx-worker-004 kubelet[1946644]: E0703 19:59:11.294548 1946644 kubelet.go:1879] skipping pod synchronization - PLEG is not healthy: pleg was last seen active 3m46.464602826s ago; threshold is 3m0s
     Jul 03 19:59:16 xxx-worker-004 kubelet[1946644]: E0703 19:59:16.294861 1946644 kubelet.go:1879] skipping pod synchronization - PLEG is not healthy: pleg was last seen active 3m51.464916622s ago; threshold is 3m0s
     Jul 03 19:59:17 xxx-worker-004 kubelet[1946644]: I0703 19:59:17.585868 1946644 setters.go:77] Using node IP: "xxxxxx"
     ```

  2. 节点短暂性 NotReady、且有获取 / kill container 状态失败的 log

     ```shell
     --- container 状态失败的 log
     Jul 03 19:59:24 xxx-worker-004 kubelet[1946644]: E0703 19:59:24.854445 1946644 remote_runtime.go:295] ContainerStatus "bdf4dc0af526a317e248c994719eabb233a9db337d535351a277b1b324cf5fec" from runtime service failed: rpc error: code = DeadlineExceeded desc = context deadline exceeded
     Jul 03 19:59:24 xxx-worker-004 kubelet[1946644]: E0703 19:59:24.854492 1946644 kuberuntime_manager.go:969] getPodContainerStatuses for pod "dss-controller-pod-658c484975-zq9mh_dss(65f4d584-88df-4fb7-bf04-d2a20a4273e3)" failed: rpc error: code = DeadlineExceeded desc = context deadline exceeded
     Jul 03 19:59:25 xxx-worker-004 kubelet[1946644]: E0703 19:59:25.996630 1946644 kubelet_pods.go:1247] Failed killing the pod "dss-controller-pod-658c484975-zq9mh": failed to "KillContainer" for "dss-controller-pod" with KillContainerError: "rpc error: code = DeadlineExceeded desc = context deadline exceeded"
     
     --- PLEG is not healthy / Node became not ready 的 log
     Jul 03 20:02:24 xxx-worker-004 kubelet[1946644]: I0703 20:02:24.508392 1946644 kubelet.go:1948] SyncLoop (UPDATE, "api"): "dx-insight-stolon-keeper-1_dx-insight(895aded8-7556-4c00-aca5-6c6e7aacf7a2)"
     Jul 03 20:02:25 xxx-worker-004 kubelet[1946644]: E0703 20:02:25.989898 1946644 kubelet.go:1879] skipping pod synchronization - PLEG is not healthy: pleg was last seen active 3m0.135142317s ago; threshold is 3m0s
     Jul 03 20:02:26 xxx-worker-004 kubelet[1946644]: E0703 20:02:26.090013 1946644 kubelet.go:1879] skipping pod synchronization - PLEG is not healthy: pleg was last seen active 3m0.235263643s ago; threshold is 3m0s
     Jul 03 20:02:26 xxx-worker-004 kubelet[1946644]: E0703 20:02:26.290144 1946644 kubelet.go:1879] skipping pod synchronization - PLEG is not healthy: pleg was last seen active 3m0.435377809s ago; threshold is 3m0s
     Jul 03 20:02:26 xxx-worker-004 kubelet[1946644]: E0703 20:02:26.690286 1946644 kubelet.go:1879] skipping pod synchronization - PLEG is not healthy: pleg was last seen active 3m0.835524997s ago; threshold is 3m0s
     Jul 03 20:02:27 xxx-worker-004 kubelet[1946644]: E0703 20:02:27.490434 1946644 kubelet.go:1879] skipping pod synchronization - PLEG is not healthy: pleg was last seen active 3m1.63566563s ago; threshold is 3m0s
     Jul 03 20:02:28 xxx-worker-004 kubelet[1946644]: I0703 20:02:28.903852 1946644 setters.go:77] Using node IP: "xxxxxx"
     Jul 03 20:02:28 xxx-worker-004 kubelet[1946644]: I0703 20:02:28.966272 1946644 kubelet_node_status.go:486] Recording NodeNotReady event message for node xxx-worker-004
     Jul 03 20:02:28 xxx-worker-004 kubelet[1946644]: I0703 20:02:28.966300 1946644 setters.go:559] Node became not ready: {Type:Ready Status:False LastHeartbeatTime:2023-07-03 20:02:28.966255129 +0800 CST m=+7095087.092396567 LastTransitionTime:2023-07-03 20:02:28.966255129 +0800 CST m=+7095087.092396567 Reason:KubeletNotReady Message:PLEG is not healthy: pleg was last seen active 3m3.111515826s ago; threshold is 3m0s}
     
     --- 每次 pleg 都有获取 container 状态失败的 log，也有在 pleg 之前的 log
     Jul 03 20:03:25 xxx-worker-004 kubelet[1946644]: E0703 20:03:25.881543 1946644 remote_runtime.go:295] ContainerStatus "bdf4dc0af526a317e248c994719eabb233a9db337d535351a277b1b324cf5fec" from runtime service failed: rpc error: code = DeadlineExceeded desc = context deadline exceeded
     Jul 03 20:03:25 xxx-worker-004 kubelet[1946644]: E0703 20:03:25.881593 1946644 kuberuntime_manager.go:969] getPodContainerStatuses for pod "dss-controller-pod-658c484975-zq9mh_dss(65f4d584-88df-4fb7-bf04-d2a20a4273e3)" failed: rpc error: code = DeadlineExceeded desc = context deadline exceeded
     
     Jul 03 20:06:26 xxx-worker-004 kubelet[1946644]: I0703 20:06:26.220050 1946644 kubelet.go:1948] SyncLoop (UPDATE, "api"): "dx-insight-stolon-keeper-1_dx-insight(895aded8-7556-4c00-aca5-6c6e7aacf7a2)"
     Jul 03 20:06:26 xxx-worker-004 kubelet[1946644]: E0703 20:06:26.989827 1946644 kubelet.go:1879] skipping pod synchronization - PLEG is not healthy: pleg was last seen active 3m0.108053792s ago; threshold is 3m0s
     Jul 03 20:06:27 xxx-worker-004 kubelet[1946644]: E0703 20:06:27.089940 1946644 kubelet.go:1879] skipping pod synchronization - PLEG is not healthy: pleg was last seen active 3m0.208169468s ago; threshold is 3m0s
     Jul 03 20:06:27 xxx-worker-004 kubelet[1946644]: E0703 20:06:27.290060 1946644 kubelet.go:1879] skipping pod synchronization - PLEG is not healthy: pleg was last seen active 3m0.408291772s ago; threshold is 3m0s
     Jul 03 20:06:27 xxx-worker-004 kubelet[1946644]: E0703 20:06:27.690186 1946644 kubelet.go:1879] skipping pod synchronization - PLEG is not healthy: pleg was last seen active 3m0.808415818s ago; threshold is 3m0s
     Jul 03 20:06:28 xxx-worker-004 kubelet[1946644]: E0703 20:06:28.490307 1946644 kubelet.go:1879] skipping pod synchronization - PLEG is not healthy: pleg was last seen active 3m1.608530704s ago; threshold is 3m0s
     Jul 03 20:06:30 xxx-worker-004 kubelet[1946644]: E0703 20:06:30.090657 1946644 kubelet.go:1879] skipping pod synchronization - PLEG is not healthy: pleg was last seen active 3m3.208885327s ago; threshold is 3m0s
     Jul 03 20:06:30 xxx-worker-004 kubelet[1946644]: I0703 20:06:30.557003 1946644 setters.go:77] Using node IP: "xxxxxx"
     Jul 03 20:06:30 xxx-worker-004 kubelet[1946644]: I0703 20:06:30.616041 1946644 kubelet_node_status.go:486] Recording NodeNotReady event message for node xxx-worker-004
     ```

  3. 当前状态下，节点可以创建 、删除 pod

- 排查方向

  1. 节点负载不高

     - cpu/memory 正常范围内

     - dockerd 文件句柄 1.9+

       ```shell
       lsof -p $(cat /var/run/docker.pid) |wc -l 
       ```

  2. 容器数量对比其他节点也没有很多

  3. docker ps / info 正常输出

     - 发现有残留的 container 和 pasue 容器，手动 ***docker rm -f*** 无法删除

     - 后续再遇到可以看下 containerd 的日志

       ```shell
       journalctl -f -u containerd
       docker stats # 看是有大量的残留容器
       ```

  4. dockerd 开启 debug 模式 - 已搜集

  5. kubelet 在 调整为 v4 重启后报错

  ```shell
  Jul 03 20:10:48 xxx-worker-004 kubelet[465378]: I0703 20:10:48.289216  465378 status_manager.go:158] Starting to sync pod status with apiserver
  Jul 03 20:10:48 xxx-worker-004 kubelet[465378]: I0703 20:10:48.289245  465378 kubelet.go:1855] Starting kubelet main sync loop.
  Jul 03 20:10:48 xxx-worker-004 kubelet[465378]: E0703 20:10:48.289303  465378 kubelet.go:1879] skipping pod synchronization - [container runtime status check may not have completed yet, PLEG is not healthy: pleg has yet to be successful]
  ```

  6. 查看是否由于 apiserver 限流导致的 worker 节点短暂性 NotReady 
     -  重启后拿的数据，没有参考意义，3*master 数据最大的 18

- 结论

  1. 节点中有残留的容器且 dokcer cli 无法正常删除、及 kubelet 获取容器状态时有 rpc failed 报错

  2. 在 kubelet 调整为 v4 level 的 log 日志后，重启 kubelet 也报 dockerd 检查异常

  3. 通过 kubelet 的监控来看，整个响应时间是在正常范围内的，因此 k8s 层面应该没有问题

     

  通过以上结论，怀疑是 kubelet 调用 docker 去获取容器状态信息时异常导致的节点短暂性 NotReady，重启节点后恢复状态恢复正常

  

- 后续措施
  1. 监控 apiserver 性能数据，看是否有限流和响应慢的现象
  2. 优化集群中应用，发现应用使用了不存在 secret 来 pull 镜像，导致 pull 失败错误 1d 有 5w+条，增加了 kubelet 与 apiserver 通信的开销

- 做的不足的地方
  1. 没有拿 dockerd 堆栈的信息
  2. apiserver  kubelet 的监控
     - 在重启后看了 apiserver 是否有限流现象 (虽然嫌疑不大，worker 节点重启后 3*master 都不高)
     - kubelet 的 relist 函数监控没有查看

## 环境信息搜集步骤

1. 在不重启 dockerd 的情况下搜集 ***debug*** 日志和 ***堆栈*** 信息

   ```shell
   - 开启 dockerd debug 模式
   [root@worker03 ~]# vi /etc/docker/daemon.json 
   {
       "storage-driver": "overlay2", 
       "log-opts": {
           "max-size": "100m", 
           "max-file": "3"
       }, 
       "storage-opts": [
           "overlay2.size=10G"
       ], 
       "insecure-registries": [
           "0.0.0.0/0"
       ], 
       "debug": true, # 新增
       "log-driver": "json-file"
   }
   
   kill -SIGHUP $(pidof dockerd)
   journalctl -f -u docker > docker-devbug.info
   
   - 打印堆栈信息
   kill -SIGUSR1 $(pidof dockerd)
   cat docker-devbug.info | grep goroutine  # 检索堆栈日志文件在哪个路径下
   cat docker-devbug.info | grep datastructure # 这个我的环境没有
   ```

2. 查看 apiserver  是否有限流的现象

   ```shell
   - 获取具有集群 admin 权限的 clusterrolebinding 配置、或者自行创建对应的 clusterrole、clusterrolebinding、serviceaccount
   kubectl get clusterrolebindings.rbac.authorization.k8s.io | grep admin
   
   - 查看 clusterrolebinding 所使用的 serviceaccount 和 secret
   kubectl get clusterrolebindings.rbac.authorization.k8s.io xxx-admin -o yaml 
   kubectl get sa -n kube-system xxx-admin -o yaml 
   kubectl get secrets -n kube-system xxx-admin-token-rgqxl -o yaml 
   echo "$token" | base64 -d > xxx-admin.token
   
   - 查看 apiserver 所有的 api 接口 、也可获取 kubelet 等其他组件的堆栈信息
   curl --cacert /etc/daocloud/xxx/cert/apiserver.crt -H "Authorization: Bearer $(cat /root/xxx-admin.token)" https://$ip:16443 -k 
   
   - 通过 metrics 接口查看监控数据
   curl --cacert /etc/daocloud/xxx/cert/apiserver.crt -H "Authorization: Bearer $(cat /root/xxx-admin.token)" https://$ip:16443/metrics -k > apiserver_metrics.info
   
   - 查看这三个指标来看 apiserver 是否触发了限流
   cat apiserver_metrics.info ｜ grep -E "apiserver_request_terminations_total|apiserver_dropped_requests_total|apiserver_current_inflight_requests"
   
   - 通过 kubelet metrics 查看当时更新状态时卡在什么位置
   curl --cacert /etc/daocloud/xxx/cert/apiserver.crt -H "Authorization: Bearer $(cat /root/xxx-admin.token)" https://127.0.0.1:10250/debug/pprof/goroutine?debug=1 -k
   curl --cacert /etc/daocloud/xxx/cert/apiserver.crt -H "Authorization: Bearer $(cat /root/xxx-admin.token)" https://127.0.0.1:10250/debug/pprof/goroutine?debug=2 -k
   
   # curl --cacert /etc/daocloud/xxx/cert/apiserver.crt -H "Authorization: Bearer $(cat /root/xxx-admin.token)" https://127.0.0.1:10250/debug/pprof/profile -k
   # curl --cacert /etc/daocloud/xxx/cert/apiserver.crt -H "Authorization: Bearer $(cat /root/xxx-admin.token)" https://127.0.0.1:10250/debug/pprof/heap -k 
   ```

3. 通过 prometheus 监控查看 kubelet 性能数据

   ```shell
   - pleg 中relist 函数负责遍历节点容器来更新 pod 状态(relist	周期 1s，relist 完成时间 + 1s = kubelet_pleg_relist_interval_microseconds)
   kubelet_pleg_relist_interval_microseconds
   kubelet_pleg_relist_interval_microseconds_count
   kubelet_pleg_relist_latency_microseconds
   kubelet_pleg_relist_latency_microseconds_count
   
   - kubelet 遍历节点中容器信息
   kubelet_runtime_operations{operation_type="container_status"} 472
   kubelet_runtime_operations{operation_type="create_container"} 93
   kubelet_runtime_operations{operation_type="exec"} 1
   kubelet_runtime_operations{operation_type="exec_sync"} 533
   kubelet_runtime_operations{operation_type="image_status"} 579
   kubelet_runtime_operations{operation_type="list_containers"} 10249
   kubelet_runtime_operations{operation_type="list_images"} 782
   kubelet_runtime_operations{operation_type="list_podsandbox"} 10154
   kubelet_runtime_operations{operation_type="podsandbox_status"} 315
   kubelet_runtime_operations{operation_type="pull_image"} 57
   kubelet_runtime_operations{operation_type="remove_container"} 49
   kubelet_runtime_operations{operation_type="run_podsandbox"} 28
   kubelet_runtime_operations{operation_type="start_container"} 93
   kubelet_runtime_operations{operation_type="status"} 1116
   kubelet_runtime_operations{operation_type="stop_container"} 9
   kubelet_runtime_operations{operation_type="stop_podsandbox"} 33
   kubelet_runtime_operations{operation_type="version"} 564
   
   - kubelet 遍历节点中容器的耗时
   kubelet_runtime_operations_latency_microseconds{operation_type="container_status",quantile="0.5"} 12117
   kubelet_runtime_operations_latency_microseconds{operation_type="container_status",quantile="0.9"} 26607
   kubelet_runtime_operations_latency_microseconds{operation_type="container_status",quantile="0.99"} 27598
   kubelet_runtime_operations_latency_microseconds_count{operation_type="container_status"} 486
   kubelet_runtime_operations_latency_microseconds{operation_type="list_containers",quantile="0.5"} 29972
   kubelet_runtime_operations_latency_microseconds{operation_type="list_containers",quantile="0.9"} 47907
   kubelet_runtime_operations_latency_microseconds{operation_type="list_containers",quantile="0.99"} 80982
   kubelet_runtime_operations_latency_microseconds_count{operation_type="list_containers"} 10812
   kubelet_runtime_operations_latency_microseconds{operation_type="list_podsandbox",quantile="0.5"} 18053
   kubelet_runtime_operations_latency_microseconds{operation_type="list_podsandbox",quantile="0.9"} 28116
   kubelet_runtime_operations_latency_microseconds{operation_type="list_podsandbox",quantile="0.99"} 68748
   kubelet_runtime_operations_latency_microseconds_count{operation_type="list_podsandbox"} 10712
   kubelet_runtime_operations_latency_microseconds{operation_type="podsandbox_status",quantile="0.5"} 4918
   kubelet_runtime_operations_latency_microseconds{operation_type="podsandbox_status",quantile="0.9"} 15671
   kubelet_runtime_operations_latency_microseconds{operation_type="podsandbox_status",quantile="0.99"} 18398
   kubelet_runtime_operations_latency_microseconds_count{operation_type="podsandbox_status"} 323
   ```

4. 如何通过 prometheus 监控 kube_apiserver

   ```shell
   - 待补充
   ```

5. 快速搜集节点当前性能数据信息

   ```shell
   mkdir -p /tmp/pleg-log
   cd /tmp/pleg-log
   journalctl -f -u docker > dockerd.log
   journalctl -f -u containerd  > dockerd.log
   ps -elF > ps.log
   top -n 1 > top.log
   pstree > pstree.log
   netstat -anltp > netsat.log
   sar -u > sar.cpu.log
   iostat > iostat.log
   iotop -n 2 > iotop.log
   top -n 1 >> top.log
   df -h > df.log
   kill -SIGUSR1 $(pidof dockerd) # dump 堆栈信息到 /var/run/docker/
   timeout 5 docker ps -a > docker.ps.log
   timeout 5 docker stats --no-stream > docker.ps.log
   free -lm > free.log
   service kubelet status > kubelet.status
   service docker status > docker.status
   ```

   