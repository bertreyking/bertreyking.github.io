# Zabbix 4 Dashboard 接口 Item 匹配异常问题说明及解决方案

## 1. 问题现象

在 Zabbix 4 中创建 Dashboard，并指定设备及以下 Item：

```text
Interfaces: Incoming traffic on interface tunnel.101
Interfaces: Outgoing traffic on interface tunnel.101
```

对应 Key：

```text
ifInOctets[tunnel.101]
ifOutOctets[tunnel.101]
```

预期 Dashboard 中只显示 `tunnel.101` 的入流量和出流量。

但实际 Dashboard Graph 中却关联出了大量其他接口，例如：

```text
tunnel.18
tunnel.101
tunnel.102
dedicated-ha1
dedicated-ha2
ha1
ha2
ethernet1/1
ethernet1/2
...
```

甚至出现：

```text
Displaying 20 of 50 found
```

说明 Dashboard Graph 实际匹配到了几十个 Interface Item。

与此同时，在 Zabbix 的传统 Graph 中手工指定相同的：

```text
ifInOctets[tunnel.101]
ifOutOctets[tunnel.101]
```

却可以正常、准确地只显示 `tunnel.101` 的流量趋势。

---

## 2. 根因

进一步检查自动发现生成的 Item 后发现，Item Prototype 的 Name 使用的是：

```text
Interfaces: Incoming traffic on interface $1
Interfaces: Outgoing traffic on interface $1
```

Key 类似：

```text
ifInOctets[{#IFNAME}]
ifOutOctets[{#IFNAME}]
```

LLD 自动发现后，实际生成：

```text
ifInOctets[tunnel.101]
ifOutOctets[tunnel.101]
```

页面上 `$1` 会根据 Key 第一个参数展示成：

```text
Interfaces: Incoming traffic on interface tunnel.101
```

但是 `$1` 本质上仍然属于参数宏。

Zabbix 4 Dashboard 的 Graph Widget 主要根据：

```text
Host Pattern
+
Item Name Pattern
```

进行 Item 匹配，并不是像传统 Graph 一样直接绑定唯一的 `itemid`。

因此，当 Item Name 使用 `$1` 时，Dashboard 无法准确按照最终解析后的 `tunnel.101` 区分不同 Item，容易将同类型的接口 Item 一起匹配进来。

最终形成：

```text
Incoming traffic on interface $1
              │
              ├── tunnel.18
              ├── tunnel.101
              ├── tunnel.102
              ├── ethernet1/1
              ├── ethernet1/2
              └── ...
```

这也是为什么 Dashboard 中会出现大量接口，而传统 Graph 中只有 `tunnel.101`。

---

## 3. 为什么传统 Graph 更准确

传统 Graph 是直接指定具体 Item：

```text
ifInOctets[tunnel.101]
ifOutOctets[tunnel.101]
```

本质上绑定的是具体 Item ID：

```text
ifInOctets[tunnel.101]  ─┐
                          ├── Graph
ifOutOctets[tunnel.101] ─┘
```

所以不会关联：

```text
tunnel.18
tunnel.102
ethernet1/1
...
```

因此传统 Graph 中看到的趋势更准确。

而当前 Dashboard Graph 实际可能同时画了几十个 Interface Item，因此某个 50 Mbps 的尖峰甚至不一定属于 `tunnel.101`。

---

# 4. 解决方案一：修改 Item Prototype Name

## 推荐方案

保留现有 LLD 自动发现机制，只修改 Item Prototype 的 Name。

### 当前配置

```text
Incoming：

Name:
Interfaces: Incoming traffic on interface $1

Key:
ifInOctets[{#IFNAME}]
```

```text
Outgoing：

Name:
Interfaces: Outgoing traffic on interface $1

Key:
ifOutOctets[{#IFNAME}]
```

### 修改为

```text
Incoming：

Name:
Interfaces: Incoming traffic on interface {#IFNAME}

Key:
ifInOctets[{#IFNAME}]
```

```text
Outgoing：

Name:
Interfaces: Outgoing traffic on interface {#IFNAME}

Key:
ifOutOctets[{#IFNAME}]
```

LLD 发现后直接生成明确的 Item Name：

```text
Interfaces: Incoming traffic on interface tunnel.101
Interfaces: Outgoing traffic on interface tunnel.101
```

对应：

```text
ifInOctets[tunnel.101]
ifOutOctets[tunnel.101]
```

最终效果：

```text
LLD
 │
 ├── tunnel.18
 │    ├── Incoming traffic on interface tunnel.18
 │    └── Outgoing traffic on interface tunnel.18
 │
 ├── tunnel.101
 │    ├── Incoming traffic on interface tunnel.101
 │    └── Outgoing traffic on interface tunnel.101
 │
 └── tunnel.102
      ├── Incoming traffic on interface tunnel.102
      └── Outgoing traffic on interface tunnel.102
```

此时 Dashboard 就可以更加准确地选择：

```text
Incoming traffic on interface tunnel.101
Outgoing traffic on interface tunnel.101
```

### 优点

- 保留 LLD 自动发现能力
- 不需要手工维护每个 Interface
- Key 不发生变化
- 不影响现有历史监控数据
- 后续新增 Tunnel 可以自动发现
- 更适合大量接口监控

### 注意

应该修改：

```text
Discovery rules
    ↓
Item prototypes
```

而不是直接修改已经发现出来的 Item。

因为已经发现出来的 Item 仍然受 LLD 管理，后续自动发现可能重新更新。

---

# 5. 解决方案二：手工创建固定 Item

如果只关注少量固定接口，例如：

```text
tunnel.101
tunnel.102
```

也可以不依赖 LLD，单独创建固定 Item。

例如：

```text
Name:
Tunnel.101 Incoming Traffic

Key:
ifInOctets[tunnel.101]
```

```text
Name:
Tunnel.101 Outgoing Traffic

Key:
ifOutOctets[tunnel.101]
```

这样 Dashboard 就可以直接匹配明确的 Name：

```text
Tunnel.101 Incoming Traffic
Tunnel.101 Outgoing Traffic
```

不会再涉及 `$1`。

## 需要注意 Key 冲突

当前 LLD 已经生成了：

```text
ifInOctets[tunnel.101]
ifOutOctets[tunnel.101]
```

因此不能直接再创建一套完全相同 Key 的 Item。

如果要采用手工 Item，需要先修改 LLD Filter，将：

```text
tunnel.101
```

从自动发现中排除。

例如：

```text
LLD
 │
 ├── tunnel.18       → 自动发现
 ├── tunnel.101      → 排除
 └── tunnel.102      → 自动发现
                           │
                           ↓
                    手工创建 tunnel.101
```

然后再手工创建：

```text
ifInOctets[tunnel.101]
ifOutOctets[tunnel.101]
```

### 优点

- Item Name 可以完全自定义
- Dashboard 匹配最简单
- 适合少量重点 Tunnel
- 不受 `$1` 影响

### 缺点

- 需要人工维护
- 新增 Tunnel 不会自动增加
- 数量较多时维护成本高
- 需要处理与 LLD Item 的 Key 冲突

---

# 6. 两种方案对比

| 项目 | 方案一：修改 Item Prototype | 方案二：手工创建 Item |
|---|---|---|
| 保留 LLD | 是 | 否 / 部分排除 |
| 自动发现新接口 | 是 | 否 |
| 是否需要人工维护 | 少 | 多 |
| 是否解决 `$1` 问题 | 是 | 是 |
| 是否存在 Key 冲突 | 无 | 需要处理 |
| 适合少量固定接口 | 可以 | 非常适合 |
| 适合大量接口 | 非常适合 | 不推荐 |
| 历史数据影响 | 基本无 | 需要注意 |
| 推荐程度 | **推荐** | 备选 |

---

# 7. 最终建议

当前场景建议优先采用 **方案一**。

即将：

```text
Interfaces: Incoming traffic on interface $1
Interfaces: Outgoing traffic on interface $1
```

修改为：

```text
Interfaces: Incoming traffic on interface {#IFNAME}
Interfaces: Outgoing traffic on interface {#IFNAME}
```

保留原来的：

```text
ifInOctets[{#IFNAME}]
ifOutOctets[{#IFNAME}]
```

这样既可以继续使用 LLD 自动发现，又可以规避 Zabbix 4 Dashboard Graph 对 `$1` 匹配不准确的问题。

如果只有极少数关键 Tunnel 需要单独制作 Dashboard，例如：

```text
tunnel.101
tunnel.102
```

也可以采用方案二：

```text
LLD 排除指定 Tunnel
        ↓
手工创建固定 Item
        ↓
Dashboard 精确选择
```

对于当前防火墙存在大量 Interface 的场景，整体上：

```text
修改 Item Prototype
        >
单独手工创建大量 Item
```

更加合理，也更便于后续维护。