# podman containers 数据软链

## 停止 podman 容器

```shell
# 暂停容器
podman ps -q | xargs podman pause 
5f375c9d1750

# 检查容器状态
podman ps -a 
CONTAINER ID  IMAGE                                      COMMAND     CREATED      STATUS      PORTS                                                                                                         NAMES
5f375c9d1750  docker.m.daocloud.io/kindest/node:v1.26.2              2 weeks ago  Paused      0.0.0.0:443->30443/tcp, 0.0.0.0:8081->30081/tcp, 0.0.0.0:9000-9001->32000-32001/tcp, 0.0.0.0:16443->6443/tcp  my-cluster-installer-control-plane
```

## 备份数据

```shell
# cp 数据到 /home/kind/podman-containers/ 目录下
mkdir -p /home/kind/podman-containers
cp -rf /var/lib/containers/* /home/kind/podman-containers/

# 备份数据
cd /var/lib/
tar -zcvf /home/kind/podman-containers/containers.tgz containers
```

## 清理数据

```shell
# 检查是否有 container 的 tmp 目录在挂载
df -hT | grep containers 
shm                     tmpfs                 63M     0   63M    0% /var/lib/containers/storage/overlay-containers/5f375c9d1750c5e5705467541ac92c23f6a338998cd1d2881dcdab1485a0be72/userdata/shm
fuse-overlayfs          fuse.fuse-overlayfs  546G  220G  326G   41% /var/lib/containers/storage/overlay/0cec29426340872d7368db0571a3fc26731040f6e7a9ccd92e2442441f44de84/merged

# 有则 umount 掉，否则 rm 时会失败
umount /var/lib/containers/storage/overlay-containers/5f375c9d1750c5e5705467541ac92c23f6a338998cd1d2881dcdab1485a0be72/userdata/shm
umount /var/lib/containers/storage/overlay/0cec29426340872d7368db0571a3fc26731040f6e7a9ccd92e2442441f44de84/merged

# 删除数据
cd /var/lib/
rm -rf containers/*
rm: 无法删除"containers/storage/overlay": 设备或资源忙, # 貌似要多删除几次
```

## 配置软链并恢复容器

```shell
# 软链
ln -vs /home/kind/podman-containers/storage /var/lib/containers/storage
ln -vs /home/kind/podman-containers/docker /var/lib/containers/docker
ln -vs /home/kind/podman-containers/cache /var/lib/containers/cache

# 如何删除 软链
unlink /var/lib/containers/cache

# 查看结果
ls -l 
总用量 0
lrwxrwxrwx. 1 root root 11 1月  24 15:38 cache -> /home/kind/podman-containers/cache
lrwxrwxrwx. 1 root root 12 1月  24 15:38 docker -> /home/kind/podman-containers/docker
lrwxrwxrwx. 1 root root 13 1月  24 15:41 storage -> /home/kind/podman-containers/storage

# 启动容器
podman unpause 5f375c9d1750
5f375c9d1750

# 检查容器状态
podman ps -a 
CONTAINER ID  IMAGE                                      COMMAND     CREATED      STATUS      PORTS                                                                                                         NAMES
5f375c9d1750  docker.m.daocloud.io/kindest/node:v1.26.2              2 weeks ago  Up 2 weeks  0.0.0.0:443->30443/tcp, 0.0.0.0:8081->30081/tcp, 0.0.0.0:9000-9001->32000-32001/tcp, 0.0.0.0:16443->6443/tcp  my-cluster-installer-control-plane
```

## 最后检查

```Markdown
# exec 进容器异常，需要手动重启下容器
podman exec -it 5f37 /bin/bash 
Error: runc: exec failed: unable to start container process: exec: "/bin/bash": stat /bin/bash: no such file or directory: OCI runtime attempted to invoke a command that was not found

# 重启容器
podman restart 5f37  
WARN[0010] StopSignal (37) failed to stop container my-cluster-installer-control-plane in 10 seconds, resorting to SIGKILL 
ERRO[0013] Cleaning up container 5f375c9d1750c5e5705467541ac92c23f6a338998cd1d2881dcdab1485a0be72: unmounting container 5f375c9d1750c5e5705467541ac92c23f6a338998cd1d2881dcdab1485a0be72 storage: cleaning up container 5f375c9d1750c5e5705467541ac92c23f6a338998cd1d2881dcdab1485a0be72 storage: unmounting container 5f375c9d1750c5e5705467541ac92c23f6a338998cd1d2881dcdab1485a0be72 root filesystem: removing mount point "/var/lib/containers/storage/overlay/0cec29426340872d7368db0571a3fc26731040f6e7a9ccd92e2442441f44de84/merged": directory not empty 
Error: OCI runtime error: runc: runc create failed: invalid rootfs: not an absolute path, or a symlink

# 重启后检查，容器运行正常
podman ps -a 
CONTAINER ID  IMAGE                                      COMMAND     CREATED      STATUS         PORTS                                                                                                         NAMES
5f375c9d1750  docker.m.daocloud.io/kindest/node:v1.26.2              2 weeks ago  Up 22 seconds  0.0.0.0:443->30443/tcp, 0.0.0.0:8081->30081/tcp, 0.0.0.0:9000-9001->32000-32001/tcp, 0.0.0.0:16443->6443/tcp  my-cluster-installer-control-plane

# 再次进容器，检查点火各组件pod 状态，均恢复正常
podman exec -it 5f37 /bin/bash 
root@my-cluster-installer-control-plane:/# kubectl get node 
NAME                                 STATUS   ROLES           AGE   VERSION
my-cluster-installer-control-plane   Ready    control-plane   17d   v1.26.2
root@my-cluster-installer-control-plane:/# kubectl get pod -A 
NAMESPACE            NAME                                                         READY   STATUS      RESTARTS      AGE
kube-system          coredns-787d4945fb-fs7b6                                     1/1     Running     1 (31s ago)   17d
kube-system          coredns-787d4945fb-hscmx                                     1/1     Running     1 (31s ago)   17d
kube-system          etcd-my-cluster-installer-control-plane                      1/1     Running     0             20s
kube-system          kindnet-hmhfb                                                1/1     Running     2 (31s ago)   17d
kube-system          kube-apiserver-my-cluster-installer-control-plane            1/1     Running     0             20s
kube-system          kube-controller-manager-my-cluster-installer-control-plane   1/1     Running     1 (31s ago)   17d
kube-system          kube-proxy-2lz72                                             1/1     Running     1 (31s ago)   16d
kube-system          kube-scheduler-my-cluster-installer-control-plane            1/1     Running     1 (31s ago)   17d
kubean-system        kubean-admission-5d4768f9cf-7tqqq                            1/1     Running     1 (31s ago)   17d
kubean-system        kubean-c6b8c997-zchfh                                        1/1     Running     1 (31s ago)   17d
kubean-system        kubean-my-cluster-ops-job-w68tm                              0/1     Completed   0             17d
local-path-storage   local-path-provisioner-84f55fc489-m9hbf                      1/1     Running     1 (31s ago)   17d
minio-system         minio-5888c499dd-vxrpk                                       1/1     Running     1 (31s ago)   17d
museum-system        chartmuseum-5db46b89f4-dv7tj                                 1/1     Running     1 (31s ago)   17d
registry-system      registry-docker-registry-55666698c5-jkn7p                    1/1     Running     1 (31s ago)   17d
```

## 执行 push/pull 验证

```shell
push 镜像
[root@g-master-all ~]# podman tag docker.m.daocloud.io/nginx:latest 10.29.14.27/docker.m.daocloud.io/nginx:latest
[root@g-master-all ~]# podman push 10.29.14.27/docker.m.daocloud.io/nginx:latest
Getting image source signatures
Copying blob 943132143199 done   | 
Copying blob 88ebb510d2fb done   | 
Copying blob 58045dd06e5b done   | 
Copying blob 32c977818204 done   | 
Copying blob f5fe472da253 done   | 
Copying blob 541cf9cf006d done   | 
Copying blob b57b5eac2941 done   | 
Copying config 9bea9f2796 done   | 
Writing manifest to image destination
[root@g-master-all ~]# podman push 10.29.14.27/docker.m.daocloud.io/nginx:latest

# 换节点 pull 镜像
[root@g-m-10-29-14-196 containers]# podman pull 10.29.14.27/docker.m.daocloud.io/nginx:latest --tls-verify=false 
Trying to pull 10.29.14.27/docker.m.daocloud.io/nginx:latest...
Getting image source signatures
Copying blob b24790593a5b done   | 
Copying blob 0569eaf32db2 done   | 
Copying blob 0aaac86b6acc done   | 
Copying blob ab698a6d27cf done   | 
Copying blob ba27271778c3 done   | 
Copying blob 3bc4473eb8b1 done   | 
Copying blob 96cab5c185c1 done   | 
Copying config 9bea9f2796 done   | 
Writing manifest to image destination
9bea9f2796e236cb18c2b3ad561ff29f655d1001f9ec7247a0bc5e08d25652a1
```

