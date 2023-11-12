# bonding 配置

## bond 模式

| Mode                      | Switch配置                                      |
| ------------------------- | ----------------------------------------------- |
| **0** - **balance-rr**    | 需要启用静态的 Etherchannel（未启用 LACP 协商） |
| **1** - **active-backup** | 需要可自主端口                                  |
| **2** - **balance-xor**   | 需要启用静态的 Etherchannel（未启用 LACP 协商） |
| **3** - **broadcast**     | 需要启用静态的 Etherchannel（未启用 LACP 协商） |
| **4** - **802.3ad**       | 需要启用 LACP 协商的 Etherchannel               |
| **5** - **balance-tlb**   | 需要可自主端口                                  |
| **6** - **balance-alb**   | 需要可自主端口                                  |

## 配置

### 检查网卡是否支持 mii 检查机制

```shell
# 判断网卡是否支持 mii、以及网卡是否连线
ethtool interface_name | grep "Link detected:"
Link detected: yes
```

### 检查网卡对应关系，避免 bonding 时搞错网卡

```shell
# ethtool -p p5p1 # 此时网卡会拼命像你招手
```

### 手动配置 bonding

```shell
# nmcli con add type bond ifname bond0 bond.options "mode=802.3ad,miimon=100,lacp_rate=1”  # 802.3ad or 4、lacp_rate=fast/1
Connection 'bond-mybond0' (5f739690-47e8-444b-9620-1895316a28ba) successfully added.

# nmcli con add type ethernet ifname ens3 master bond0
Connection 'bond-slave-ens3' (220f99c6-ee0a-42a1-820e-454cbabc2618) successfully added.

#nmcli con add type ethernet ifname ens7 master bond0
Connection 'bond-slave-ens7' (ecc24c75-1c89-401f-90c8-9706531e0231) successfully added.
```

### 脚本配置 bonding

```shell
#!/bin/bash

echo '配置 bond'
nmcli con add type bond ifname bond0 bond.options "mode=802.3ad,miimon=100,lacp_rate=1"
nmcli con add type ethernet ifname $1 master bond0
nmcli con add type ethernet ifname $2 master bond0
sed -i 's/BOOTPROTO=dhcp/BOOTPROTO=none/g' /etc/sysconfig/network-scripts/ifcfg-bond-bond0
sed -i 's/ONBOOT=no/ONBOOT=yes/g' /etc/sysconfig/network-scripts/ifcfg-bond-bond0
echo IPADDR=$3 >> /etc/sysconfig/network-scripts/ifcfg-bond-bond0
echo PREFIX=24 >> /etc/sysconfig/network-scripts/ifcfg-bond-bond0
echo GATEWAY=$4 >> /etc/sysconfig/network-scripts/ifcfg-bond-bond0
echo DNS1=10.29.19.254 >> /etc/sysconfig/network-scripts/ifcfg-bond-bond0
cat /etc/sysconfig/network-scripts/ifcfg-bond-bond0

echo ' '
echo '检查 bond 信息'
cat /sys/class/net/bond0/bonding/miimon
cat /sys/class/net/bond0/bonding/lacp_rate
cat /sys/class/net/bond0/bonding/mode

echo '重启网络服务'
systemctl restart network
ip ro ls

echo ' '
echo '禁用 selinx、firewalld'
systemctl stop firewalld && systemctl disable firewalld
sed -i 's/SELINUX=enforcing/SELINUX=disabled/g' /etc/selinux/config
```

### lcap_rate 含义

```shell
**lacp_rate=\*value\***

指定链接合作伙伴应在 802.3ad 模式下传输 LACPDU 数据包的速率。可能的值有：

slow 或 0  # 默认设置。这规定合作伙伴应每 30 秒传输一次 LACPDU。
fast 或 1  # 指定合作伙伴应每 1 秒传输一次 LACPDU 
```

## 禁止 NetworkManger 管理网卡设备

```shell
# vi /etc/NetworkManager/conf.d/99-unmanaged-devices.conf
[keyfile]
# 单个设备 
unmanaged-devices=interface-name:enp1s0  
# 多个设备 
unmanaged-devices=interface-name:interface_1;interface-name:interface_2;

# systemctl reload NetworkManager

# nmcli device status
DEVICE  TYPE      STATE      CONNECTION
enp1s0  ethernet  unmanaged  --
```

## 多网卡场景禁用非默认网关网卡中网关的配置

```shell
# vi ifcfg-enps10
DEFROUTE=no
```

## 参考文档

[7.3. 使用 NetworkManager 命令行工具 nmcli 进行网络绑定][https://access.redhat.com/documentation/zh-cn/red_hat_enterprise_linux/7/html/networking_guide/sec-network_bonding_using_the_networkmanager_command_line_tool_nmcli]