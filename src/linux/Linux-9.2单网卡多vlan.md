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

查看 NetworkManager 配置：

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

# 7. 推荐

当前场景推荐使用：

```text
VLAN 子接口
+
独立路由表
+
Source-Based Policy Routing
```

相比明细路由，不需要维护大量远端子网，更适合后续继续增加 VLAN。