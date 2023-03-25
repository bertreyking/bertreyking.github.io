# 自定义容器内路由

## 通过容器查找其 PID

```shell
docker inspect --format '{{ .State.Pid }}' $container_id
```

## 制作软链接

```shell
ln -s /proc/$pid/ns/net /var/run/netns/$pid
```

## 增删改查容器内明细路由

```
- ip netns 方法
cd /var/run/netns
ip netns exec $pid
ip netns exec $pid route -n 
ip netns exec $pid ip route add 10.114.0.0/24 via 10.142.2.1
ip netns exec $pid route -n 
ip netns exec $pid ip route delete 10.114.0.0/24 via 10.142.2.1
ip netns exec $pid route -n 

- nsenter 方法
nsenter -t $pid -n ip route add 10.114.0.0/24 via 10.142.2.1
nsenter -t $pid -n routne -n
```

## [ip-netns](https://man7.org/linux/man-pages/man8/ip-netns.8.html) vs [nsenter](https://man7.org/linux/man-pages/man1/nsenter.1.html)

```shell
ip netns：进程网络命名空间管理工具

- ip netns list         # 显示所有 netns 列表
- ip netns monitor      # 监控 netns 的创建和删除事件
- ip netns add xxx      # 创建
- ip netns delete xxx   # 删除
- ip netns pids xxx.    # 查找所有跟此 netns 有关联的进程 pid (思考：如果有残留的容器netns，是不是也可用这个方法查找)

nsenter：不同 namespace 下运行程序

-t  # 进程 pid
-n, --net[=file]
    Enter the network namespace. If no file is specified, enter
    the network namespace of the target process. If file is
    specified, enter the network namespace specified by file.
```

