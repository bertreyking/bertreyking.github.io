NFS-CSI 组件部署

# 创建 nfs-server 

```shell
yum install -y nfs-utils
systemctl start nfs-server.service 
systemctl enable nfs-server.service 
echo "/data/ 10.29.26.0/16(rw,sync,no_subtree_check,no_root_squash)" >> /etc/exports
exportfs
```

# helm 部署 nfs-subdir

```shell
helm install nfs-provisioner ./nfs-subdir-external-provisioner \
    --set nfs.server=10.29.26.x \ # 这里需要替换为自己的 nfs-server 实例
    --set nfs.path=/data/ \ # 这里需要替换为自己的 nfs-server 实例
    --set storageClass.name=nfs-provisioner \
    --set storageClass.provisionerName=k8s-sigs.io/nfs-provisioner

cat test-claim.yaml 
kind: PersistentVolumeClaim
apiVersion: v1
metadata:
  name: test-claim
spec:
  storageClassName: nfs-provisioner
  accessModes:
    - ReadWriteMany
  resources:
    requests:
      storage: 1Mi

kubectl apply -f test-claim.yaml 
kubectl get pvc  #会立即 bound，如果遇到bound 失败，请检查 node、rpc-statd 服务是否启动

## 报错
 Events:
  Type     Reason                Age               From                                                               Message
  ----     ------                ----              ----                                                               -------
  Normal   ExternalProvisioning  8s (x3 over 29s)  persistentvolume-controller                                        waiting for a volume to be created, either by external provisioner "nfs.csi.k8s.io" or manually created by system administrator
  Warning  ProvisioningFailed    8s (x2 over 19s)  nfs.csi.k8s.io_worker-node-1_52792836-2ebf-421f-97ce-ce1fbfdb1e44  failed to provision volume with StorageClass "nfs-csi": rpc error: code = Internal desc = failed to mount nfs server: rpc error: code = Internal desc = mount failed: exit status 32
Mounting command: mount
Mounting arguments: -t nfs -o nfsvers=3 10.29.26.199:/data /tmp/pvc-70557e32-5d98-4fd6-8cd4-e285a7c4a279
Output: /usr/sbin/start-statd: 10: cannot create /run/rpc.statd.lock: Read-only file system
mount.nfs: rpc.statd is not running but is required for remote locking.
mount.nfs: Either use '-o nolock' to keep locks local, or start statd.
  Normal  Provisioning  6s (x3 over 29s)  nfs.csi.k8s.io_worker-node-1_52792836-2ebf-421f-97ce-ce1fbfdb1e44  External provisioner is provisioning volume for claim "default/test-claim-csi"

[root@controller-node-1 ~]# systemctl start rpc-statd && systemctl enable rpc-statd 
[root@controller-node-1 ~]# systemctl status rpc-statd 
● rpc-statd.service - NFS status monitor for NFSv2/3 locking.
   Loaded: loaded (/usr/lib/systemd/system/rpc-statd.service; static; vendor preset: disabled)
   Active: active (running) since Thu 2024-05-09 14:41:35 CST; 2h 15min ago
 Main PID: 1110879 (rpc.statd)
    Tasks: 1
   Memory: 852.0K
   CGroup: /system.slice/rpc-statd.service
           └─1110879 /usr/sbin/rpc.statd

May 09 14:41:35 controller-node-1 systemd[1]: Starting NFS status monitor for NFSv2/3 locking....
May 09 14:41:35 controller-node-1 rpc.statd[1110879]: Version 1.3.0 starting
May 09 14:41:35 controller-node-1 rpc.statd[1110879]: Flags: TI-RPC
May 09 14:41:35 controller-node-1 rpc.statd[1110879]: Initializing NSM state
May 09 14:41:35 controller-node-1 systemd[1]: Started NFS status monitor for NFSv2/3 locking..
[root@controller-node-1 ~]#   
```

# helm 部署 nfs-csi

```shell
# add repo
helm repo add csi-driver-nfs https://raw.githubusercontent.com/kubernetes-csi/csi-driver-nfs/master/charts

# install
helm install csi-driver-nfs csi-driver-nfs/csi-driver-nfs --version v4.7.0 --set image.nfs.repository=k8s.m.daocloud.io/sig-storage/nfsplugin --set image.csiProvisioner.repository=k8s.m.daocloud.io/sig-storage/csi-provisioner --set image.livenessProbe.repository=k8s.m.daocloud.io/sig-storage/livenessprobe --set image.nodeDriverRegistrar.repository=k8s.m.daocloud.io/sig-storage/csi-node-driver-registrar --set image.csiSnapshotter.repository=k8s.m.daocloud.io/sig-storage/csi-snapshotter --set image.externalSnapshotter.repository=k8s.m.daocloud.io/sig-storage/snapshot-controller --set externalSnapshotter.enabled=true

# create storageclass for nfs-server
[root@controller-node-1 ~]# cat sc.yaml  # 当有多个 nfs-server 时，创建新的 sc 并指定ip:path 即可，这点比 nfs-subdir 方便不少
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: nfs-csi
provisioner: nfs.csi.k8s.io
parameters:
  server: 10.29.26.199
  share: /data
  # csi.storage.k8s.io/provisioner-secret is only needed for providing mountOptions in DeleteVolume
  csi.storage.k8s.io/provisioner-secret-name: "mount-options"
  csi.storage.k8s.io/provisioner-secret-namespace: "default"
reclaimPolicy: Delete
volumeBindingMode: Immediate
mountOptions:
  - nfsvers=3
```

## 检查及验证快照功能

```shell
# get sc
[root@controller-node-1 ~]# kubectl get csidrivers.storage.k8s.io 
NAME             ATTACHREQUIRED   PODINFOONMOUNT   STORAGECAPACITY   TOKENREQUESTS   REQUIRESREPUBLISH   MODES        AGE
nfs.csi.k8s.io   false            false            false             <unset>         false               Persistent   25m

# create snapshotclass
[root@controller-node-1 ~]# cat nfs-csi-snapshot.yaml 
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshotClass
metadata:
  name: csi-nfs-snapclass
driver: nfs.csi.k8s.io
deletionPolicy: Delete

# create snapshot
apiVersion: snapshot.storage.k8s.io/v1
kind: VolumeSnapshot
metadata:
  name: test-nfs-snapshot
spec:
  volumeSnapshotClassName: csi-nfs-snapclass
  source:
    persistentVolumeClaimName: test-claim-csi

[root@controller-node-1 ~]# kubectl apply -f nfs-csi-snapshot-pvc-test-claim-csi.yaml 
volumesnapshot.snapshot.storage.k8s.io/test-nfs-snapshot created

# check snapshot status
[root@controller-node-1 ~]# kubectl get volumesnapshot
NAME                READYTOUSE   SOURCEPVC        SOURCESNAPSHOTCONTENT   RESTORESIZE   SNAPSHOTCLASS       SNAPSHOTCONTENT                                    CREATIONTIME   AGE
test-nfs-snapshot   true         test-claim-csi                           105           csi-nfs-snapclass   snapcontent-462e5866-3c10-4201-8c5b-c3e5fd68af3b   13s            13s

# check nfs-server data
[root@controller-node-1 ~]# cd /data/
[root@controller-node-1 data]# ll
total 0
drwxrwxrwx. 2 root root 21 May  9 15:30 default-test-claim-pvc-372c6ee4-c2fa-41e5-9e7d-a7b18e7c6efc
drwxrwxrwx. 2 root root  6 May  9 15:34 default-test-claim2-pvc-88fe2a10-60b6-47c6-b77a-b07cbe7e001e
drwxr-xr-x. 2 root root  6 May  9 17:01 pvc-8ceef78d-bdaa-4503-9012-4844b9ce3739
drwxr-xr-x. 2 root root 61 May  9 17:09 snapshot-462e5866-3c10-4201-8c5b-c3e5fd68af3b
[root@controller-node-1 data]# ls pvc-8ceef78d-bdaa-4503-9012-4844b9ce3739/
[root@controller-node-1 data]# ls snapshot-462e5866-3c10-4201-8c5b-c3e5fd68af3b/
pvc-8ceef78d-bdaa-4503-9012-4844b9ce3739.tar.gz
```

# 对比及建议 

- k8 版本较老建议使用 nfs-subdir(使用 deployment 来对接 nfs-server)
- 新建的 k8-cluster 可以尝试使用 nfs-csi(使用 sc 对接 nfs-server，灵活不少)组件，功能相对来说丰富不少 

# 参考文档

- [nfs-subdir](https://github.com/kubernetes-sigs/nfs-subdir-external-provisioner) 
- [nfs-csi](https://github.com/kubernetes-csi/csi-driver-nfs?tab=readme-ov-file) 
- - [nfs-csi-snapshotter](https://github.com/kubernetes-csi/external-snapshotter)

