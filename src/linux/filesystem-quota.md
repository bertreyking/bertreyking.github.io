# 按 user 对文件系统及子目录进行限额

## 修改 fstab 在 os 启动 mount 文件系统时开启 fs_quota 

```shell
[root@controller-node-1 ~]# cat /etc/fstab 

#
# /etc/fstab
# Created by anaconda on Fri Jul  2 13:57:38 2021
#
# Accessible filesystems, by reference, are maintained under '/dev/disk'
# See man pages fstab(5), findfs(8), mount(8) and/or blkid(8) for more info
#
/dev/mapper/centos-root /                       xfs     defaults        0 0
/dev/mapper/fs--quota-lv /data/                 xfs     defaults,usrquota,grpquota,prjquota        0 0
UUID=3ed67e9f-ad87-41ae-88c5-b38d000ca3f4 /boot                   xfs     defaults        0 0

[root@controller-node-1 ~]# mount | grep data 
/dev/mapper/fs--quota-lv on /data type xfs (rw,relatime,seclabel,attr2,inode64,usrquota,prjquota,grpquota)
```

## 查看 data 挂载点是否开启 user、group、project 限制

```shell
[root@controller-node-1 ~]# xfs_quota -x -c "state" /data 
User quota state on /data (/dev/mapper/fs--quota-lv)
  Accounting: ON
  Enforcement: ON
  Inode: #67 (1 blocks, 1 extents)
Group quota state on /data (/dev/mapper/fs--quota-lv)
  Accounting: ON
  Enforcement: ON
  Inode: #68 (1 blocks, 1 extents)
Project quota state on /data (/dev/mapper/fs--quota-lv)
  Accounting: ON
  Enforcement: ON
  Inode: #68 (1 blocks, 1 extents)
Blocks grace time: [7 days]
Inodes grace time: [7 days]
Realtime Blocks grace time: [7 days]

```

## 限制用户所使用的子目录空间大小

- xfs_quota：可以对文件系统进行限制
- 如果对子目录进行限制，需要创建识别码、对应目录、名称，让 xfs_quota 知道关系图

### 创建、目录/项目识别码、对应目录、及名称

```shell
[root@controller-node-1 ~]# echo "30:/data/mawb/dir1" >> /etc/projects
[root@controller-node-1 ~]# echo "dir1quota:30" >> /etc/projid
```

### 配置限制
```shell
[root@controller-node-1 ~]# xfs_quota -x -c "project -s dir1quota"
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).
Setting up project dir1quota (path /data/mawb/dir1)...
Processed 1 (/etc/projects and cmdline) paths for project dir1quota with recursion depth infinite (-1).

[root@controller-node-1 ~]# xfs_quota -x -c "print" /data
Filesystem          Pathname
/data               /dev/mapper/fs--quota-lv (uquota, gquota, pquota)
/data/mawb/dir1     /dev/mapper/fs--quota-lv (project 30, dir1quota)

[root@controller-node-1 ~]# xfs_quota -x -c "report -pbih" /data
Project quota on /data (/dev/mapper/fs--quota-lv)
                        Blocks                            Inodes              
Project ID   Used   Soft   Hard Warn/Grace     Used   Soft   Hard Warn/Grace  
---------- --------------------------------- --------------------------------- 
#0              0      0      0  00 [------]      4      0      0  00 [------]
dir1quota       0      0      0  00 [------]      1      0      0  00 [------]

[root@controller-node-1 ~]# xfs_quota -x -c "limit -p bsoft=400M bhard=500M dir1quota" /data
[root@controller-node-1 ~]# xfs_quota -x -c "report -pbih" /data
Project quota on /data (/dev/mapper/fs--quota-lv)
                        Blocks                            Inodes              
Project ID   Used   Soft   Hard Warn/Grace     Used   Soft   Hard Warn/Grace  
---------- --------------------------------- --------------------------------- 
#0              0      0      0  00 [------]      4      0      0  00 [------]
dir1quota       0   400M   500M  00 [------]      1      0      0  00 [------]
```

### 验证是否生效

```shell
[root@controller-node-1 ~]# dd if=/dev/zero of=/data/mawb/project.img bs=1M count=520 
记录了520+0 的读入
记录了520+0 的写出
545259520字节(545 MB)已复制，0.298309 秒，1.8 GB/秒

[root@controller-node-1 ~]# dd if=/dev/zero of=/data/project.img bs=1M count=520 
记录了520+0 的读入
记录了520+0 的写出
545259520字节(545 MB)已复制，0.425858 秒，1.3 GB/秒
[root@controller-node-1 ~]# dd if=/dev/zero of=/data/mawb/dir1/project.img bs=1M count=520 
dd: 写入"/data/mawb/dir1/project.img" 出错: 设备上没有空间
记录了501+0 的读入
记录了500+0 的写出
524288000字节(524 MB)已复制，4.45889 秒，118 MB/秒

[root@controller-node-1 ~]# xfs_quota -x -c "report -pbih" /data
Project quota on /data (/dev/mapper/fs--quota-lv)
                        Blocks                            Inodes              
Project ID   Used   Soft   Hard Warn/Grace     Used   Soft   Hard Warn/Grace  
---------- --------------------------------- --------------------------------- 
#0           1.0G      0      0  00 [------]      6      0      0  00 [------]
dir1quota    500M   400M   500M  00 [7 days]      2      0      0  00 [------]
```

### 进阶用法

```shell
[root@controller-node-1 ~]# xfs_quota -x -c "limit -u bsoft=200M bhard=300M maweibing" /data
[root@controller-node-1 ~]# xfs_quota -x -c 'report -h' /data
User quota on /data (/dev/mapper/fs--quota-lv)
                        Blocks              
User ID      Used   Soft   Hard Warn/Grace   
---------- --------------------------------- 
root         1.0G      0      0  00 [0 days]
maweibing       0   200M   300M  00 [------]

Group quota on /data (/dev/mapper/fs--quota-lv)
                        Blocks              
Group ID     Used   Soft   Hard Warn/Grace   
---------- --------------------------------- 
root         1.0G      0      0  00 [------]

Project quota on /data (/dev/mapper/fs--quota-lv)
                        Blocks              
Project ID   Used   Soft   Hard Warn/Grace   
---------- --------------------------------- 
#0           1.0G      0      0  00 [------]
dir1quota       0   400M   500M  00 [------]

[maweibing@controller-node-1 ~]$ dd if=/dev/zero of=/data/mawb/dir1/project.img bs=1M count=520
dd: 写入"/data/mawb/dir1/project.img" 出错: 超出磁盘限额
记录了301+0 的读入
记录了300+0 的写出
314572800字节(315 MB)已复制，0.201772 秒，1.6 GB/秒
[maweibing@controller-node-1 ~]$ dd if=/dev/zero of=/data/mawb/dir1/project.img bs=1M count=100
记录了100+0 的读入
记录了100+0 的写出
104857600字节(105 MB)已复制，0.314926 秒，333 MB/秒

[maweibing@controller-node-1 root]$ dd if=/dev/zero of=/data/mawb/project.img bs=1M count=500
dd: 写入"/data/mawb/project.img" 出错: 超出磁盘限额
记录了201+0 的读入
记录了200+0 的写出
209715200字节(210 MB)已复制，0.758228 秒，277 MB/秒
[maweibing@controller-node-1 root]$ dd if=/dev/zero of=/data/mawb/project.img bs=1M count=100
记录了100+0 的读入
记录了100+0 的写出
104857600字节(105 MB)已复制，0.399685 秒，262 MB/秒
```

## 结论

0. 目录权限还是在 root 用户下设置
1. 按用户/组限制的话，只能对文件系统，不能对某个子目录
2. 按文件系统限制的话，/data/目录下的所有目录都不能大于 hard 的限制
3. 按项目限制的话，可以对子目录限制，但无法对用户限制