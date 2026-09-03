# Rocky Linux 9.2 单网卡多 VLAN 路由配置

## 1. 需求

当前服务器网络：

```text
eth0
IP：10.1.32.119/24
GW：10.1.32.1

eth0.31
VLAN：31
IP：10.1.31.119/24
GW：10.1.31.1
```

目标：

```text
10.1.32.119 → 默认走 10.1.32.1 / eth0

10.1.31.119 → 回包固定走 10.1.31.1 / eth0.31
```

避免外部访问 `10.1.31.119` 时，回包从 `eth0 → 10.1.32.1` 返回。

---

## 2. 创建 VLAN 31

```bash
nmcli con add type vlan \
  con-name eth0.31 \
  ifname eth0.31 \
  dev eth0 \
  id 31
```

配置 IP：

```bash
nmcli con mod eth0.31 \
  ipv4.method manual \
  ipv4.addresses 10.1.31.119/24 \
  ipv4.never-default yes \
  ipv6.method disabled
```

启用：

```bash
nmcli con up eth0.31
```

检查：

```bash
ip -br addr
ip -d link show eth0.31
```

---

# 3. 方案一：明细静态路由

适用于已知远端网段的情况。

例如：

```text
10.20.0.0/16
10.30.0.0/16
```

都需要通过 VLAN31：

```bash
nmcli con mod eth0.31 \
  +ipv4.routes "10.20.0.0/16 10.1.31.1"

nmcli con mod eth0.31 \
  +ipv4.routes "10.30.0.0/16 10.1.31.1"
```

应用：

```bash
nmcli con up eth0.31
```

验证：

```bash
ip route get 10.20.1.10
```

预期：

```text
10.20.1.10 via 10.1.31.1 dev eth0.31 src 10.1.31.119
```

### 特点

```text
优点：简单、直观
缺点：需要维护所有远端网段
```

---

# 4. 方案二：独立路由表 + Policy Routing

更适合当前需求。

原则：

```text
source = 10.1.31.119
        ↓
     table 131
        ↓
default via 10.1.31.1
        ↓
      eth0.31
```

不需要提前知道远端是什么网段。

---

## 4.1 持久化配置

指定独立路由表：

```bash
nmcli con mod eth0.31 \
  ipv4.route-table 131
```

添加 VLAN31 默认路由：

```bash
nmcli con mod eth0.31 \
  +ipv4.routes "0.0.0.0/0 10.1.31.1 table=131"
```

添加源地址策略：

```bash
nmcli con mod eth0.31 \
  +ipv4.routing-rules \
  "priority 100 from 10.1.31.119/32 table 131"
```

应用：

```bash
nmcli con up eth0.31
```

以上配置通过 NetworkManager 持久化，**服务器重启后不会丢失**。

---

# 5. 检查配置

## 5.1 检查网卡和 Connection 状态

查看所有网卡：

```bash
nmcli device status
```

查看所有 NetworkManager Connection：

```bash
nmcli connection show
```

只查看当前已激活的 Connection：

```bash
nmcli connection show --active
```

查看物理网卡 `eth0` 的详细信息：

```bash
nmcli device show eth0
```

查看 VLAN 子接口：

```bash
nmcli device show eth0.31
```

查看 `eth0` Connection 配置：

```bash
nmcli connection show eth0
```

查看 VLAN31 Connection 完整配置：

```bash
nmcli connection show eth0.31
```

查看接口 IP：

```bash
ip -br addr
```

或者：

```bash
ip addr show eth0
ip addr show eth0.31
```

---

## 5.2 检查 VLAN 配置

查看所有 VLAN 子接口：

```bash
ip -d link show type vlan
```

只查看 VLAN31：

```bash
ip -d link show eth0.31
```

重点应看到：

```text
eth0.31@eth0
vlan protocol 802.1Q id 31
```

通过 NetworkManager 查看 VLAN ID 和父接口：

```bash
nmcli -f connection.id,connection.interface-name,vlan.id,vlan.parent \
  connection show eth0.31
```

预期类似：

```text
connection.id:                 eth0.31
connection.interface-name:     eth0.31
vlan.id:                       31
vlan.parent:                   eth0
```

---

## 5.3 检查 IP 和策略路由配置

查看关键配置：

```bash
nmcli -f \
ipv4.addresses,ipv4.gateway,ipv4.routes,ipv4.route-table,ipv4.routing-rules \
con show eth0.31
```

预期：

```text
ipv4.addresses:       10.1.31.119/24
ipv4.gateway:         --
ipv4.route-table:     131
ipv4.routing-rules:   priority 100 from 10.1.31.119/32 table 131
```

查看主路由：

```bash
ip route
```

查看策略：

```bash
ip rule
```

预期包含：

```text
100: from 10.1.31.119 lookup 131
```

查看表 131：

```bash
ip route show table 131
```

预期：

```text
default via 10.1.31.1 dev eth0.31
10.1.31.0/24 dev eth0.31 scope link src 10.1.31.119
```

---

## 5.4 检查 NetworkManager 网卡配置文件

Rocky Linux 9 默认使用 NetworkManager Keyfile，配置文件通常位于：

```bash
ls -l /etc/NetworkManager/system-connections/
```

可以查找 `eth0` 和 `eth0.31`：

```bash
ls -l /etc/NetworkManager/system-connections/ | grep -E 'eth0|eth0.31'
```

查看 VLAN31 配置文件：

```bash
cat /etc/NetworkManager/system-connections/eth0.31.nmconnection
```

如果不确定实际文件名：

```bash
grep -ril 'id=eth0.31' /etc/NetworkManager/system-connections/
```

查看配置文件中的关键内容：

```bash
grep -Ev '^$|^#' /etc/NetworkManager/system-connections/eth0.31.nmconnection
```

配置文件中通常可以看到：

```ini
[connection]
id=eth0.31
type=vlan
interface-name=eth0.31

[ipv4]
address1=10.1.31.119/24
method=manual
never-default=true
route-table=131

[vlan]
id=31
parent=eth0
```

> 建议通过 `nmcli` 修改配置，不建议直接手工编辑 `.nmconnection` 文件。

如果确实手工修改了配置文件，需要重新加载：

```bash
nmcli connection reload
```

然后重新激活：

```bash
nmcli connection up eth0.31
```

---

# 6. 最终验证

验证 VLAN31 地址：

```bash
ip route get 8.8.8.8 from 10.1.31.119
```

预期：

```text
8.8.8.8 via 10.1.31.1 dev eth0.31 src 10.1.31.119
```

验证原有地址：

```bash
ip route get 8.8.8.8 from 10.1.32.119
```

预期：

```text
8.8.8.8 via 10.1.32.1 dev eth0 src 10.1.32.119
```

最终效果：

```text
10.1.31.119 → table 131 → 10.1.31.1 → eth0.31

10.1.32.119 → main table → 10.1.32.1 → eth0
```

---

# 7. 推荐检查命令汇总

```bash
# 网卡状态
nmcli device status

# Connection
nmcli connection show
nmcli connection show --active

# 接口详细配置
nmcli device show eth0
nmcli device show eth0.31
nmcli connection show eth0.31

# IP
ip -br addr

# VLAN
ip -d link show type vlan
ip -d link show eth0.31

# VLAN ID / Parent
nmcli -f connection.id,connection.interface-name,vlan.id,vlan.parent \
  con show eth0.31

# 主路由
ip route

# 策略路由
ip rule
ip route show table 131

# NetworkManager 持久化配置
nmcli -f \
ipv4.addresses,ipv4.gateway,ipv4.routes,ipv4.route-table,ipv4.routing-rules \
con show eth0.31

# 配置文件
ls -l /etc/NetworkManager/system-connections/
cat /etc/NetworkManager/system-connections/eth0.31.nmconnection

# 验证实际选路
ip route get 8.8.8.8 from 10.1.31.119
```

---

# 8. 推荐

当前场景推荐：

```text
VLAN 子接口
+
独立路由表
+
Source-Based Policy Routing
```

相比明细路由，不需要维护大量远端子网，更适合后续继续增加 VLAN。