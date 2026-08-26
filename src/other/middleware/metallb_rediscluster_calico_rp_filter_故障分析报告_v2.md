# MetalLB + Redis Cluster + Calico 网络访问故障分析报告

## 1. 问题背景

Kubernetes 集群中使用 MetalLB 的 Layer2 模式为 `LoadBalancer` 类型 Service 分配 VIP。

当前涉及两种 Pod 网络形态：

1. **Pod 与 MetalLB VIP 都使用大二层 VLAN 网络地址**
2. **Pod 使用 Calico Pod CIDR，MetalLB VIP 使用大二层 VLAN 地址**

Redis 采用 **Redis Cluster 模式**。

本次典型 Service 信息如下：

```text
Service:      aibot-webui
Type:         LoadBalancer
ClusterIP:    10.233.45.223
MetalLB VIP:  10.110.111.250
Port:         8080
NodePort:     32384
Endpoint:     10.233.94.162:8080
externalTrafficPolicy: Cluster
```

MetalLB L2Advertisement：

```yaml
apiVersion: metallb.io/v1beta1
kind: L2Advertisement
metadata:
  name: default-l2
  namespace: kube-system
spec:
  interfaces:
    - bond0.24
  ipAddressPools:
    - default-pool
```

MetalLB speaker 已经正常选择节点宣告 VIP：

```text
announcing from node "dc3-dce-ec-k8s-node-uat01" with protocol "layer2"
announcing from node "dc3-dce-ec-k8s-node-uat02" with protocol "layer2"
```

---

## 2. 故障现象

### 2.1 第一阶段：MetalLB VIP 外部访问失败

已确认：

- Service 可以正常获取 MetalLB VIP；
- 后端 Pod 正常；
- Pod 内部访问正常；
- NodePort 访问正常；
- 集群内部在 `bond0.24` 对 VIP 执行 `arping` 可以获取 MAC；
- 外部客户端位于 `10.1.32.0/24`；
- 外部客户端访问 VIP `10.110.111.250:8080` 超时。

最初看起来像 MetalLB L2 宣告失败，但节点抓包证明：

```text
10.1.32.174:47040 > 10.110.111.250:8080 Flags [S]
```

说明外部客户端发送的 TCP SYN 已经进入 Kubernetes 节点。

同时能够看到：

```text
ARP Request:
who-has 10.110.111.250 tell 10.110.80.1

ARP Reply:
10.110.111.250 is-at 40:5b:7f:30:cb:10
```

说明：

- 网关可以正常对 VIP 发起 ARP；
- MetalLB speaker 能正确响应 VIP 的 ARP；
- VLAN 24 二层链路正常；
- MetalLB L2Advertisement 正常；
- 外部到 VIP 的三层路由也正常。

但 TCP SYN 持续重传，没有 SYN-ACK：

```text
10.1.32.174 -> 10.110.111.250 SYN
10.1.32.174 -> 10.110.111.250 SYN
10.1.32.174 -> 10.110.111.250 SYN
...
```

因此故障点已经从 MetalLB 收敛到：

```text
外部客户端
    │
    ▼
三层网关
    │
    ▼
MetalLB VIP
    │
    ▼
K8s Node
    │
    X
Linux 内核 / kube-proxy / CNI
```

---

## 3. 第一层根因：rp_filter 严格反向路径检查

### 3.1 rp_filter 是什么

`rp_filter` 全称：

```text
Reverse Path Filtering
```

即 **反向路径过滤**。

它的主要目的，是防止源地址伪造。

Linux 收到一个报文后，会检查：

> 如果我要给这个源 IP 回包，正常情况下应该从哪张网卡出去？

严格模式下，如果：

```text
收到报文的接口
!=
到源 IP 的最佳返回路由接口
```

Linux 会认为该流量存在源地址伪造或非对称路由风险，并直接丢弃。

### 3.2 Linux 常见取值

```text
rp_filter = 0
不做反向路径检查

rp_filter = 1
严格模式
要求报文进入接口和反向最佳路由接口一致

rp_filter = 2
宽松模式
只要求系统存在到源 IP 的可达路由
```

---

## 4. 本次 rp_filter 故障原理

本次客户端：

```text
10.1.32.174
```

VIP：

```text
10.110.111.250
```

MetalLB 宣告接口：

```text
bond0.24
```

外部请求从 `bond0.24` 进入节点：

```text
10.1.32.174
      │
      ▼
10.110.80.1
      │
      ▼
bond0.24
      │
      ▼
10.110.111.250
```

但是节点查询：

```bash
ip route get 10.1.32.174
```

如果得到的最佳返回路径不是 `bond0.24`，而是另外一个接口，那么：

```text
进入接口：bond0.24
返回接口：bond0.210 / bond0.x / 其它接口
```

在：

```text
rp_filter=1
```

的情况下，Linux 会直接丢包。

这也解释了为什么：

```text
tcpdump 可以看到 SYN
```

但业务仍然超时。

因为 tcpdump 能抓到进入网卡的报文，并不等于该报文最终通过 Linux 网络协议栈。

---

## 5. rp_filter 示意图

![rp_filter 请求丢包原理图](/png/rp_filter.png)

一句话理解：

> `rp_filter` 不关心“这个包是不是已经到网卡了”，它关心的是“这个包从这里进来是否符合 Linux 认为的正常返回路径”。

---

## 6. rp_filter 的处理结果

禁用：

```bash
sysctl -w net.ipv4.conf.all.rp_filter=0
sysctl -w net.ipv4.conf.bond0.24.rp_filter=0
```

之后，MetalLB VIP 可以正常访问。

因此第一阶段故障可以确认：

```text
根因：
多网卡 / 多 VLAN 场景存在非对称路由，
rp_filter 严格模式将进入 VIP 的合法流量误判并丢弃。
```

---

# 7. 第二阶段：Redis Cluster + Calico 场景仍然无法正常访问

在 `rp_filter=0` 后，又出现第二个现象。

## 场景 A：Pod 与 MetalLB 都使用大二层网络

例如：

```text
客户端
10.1.32.174
    │
    ▼
MetalLB VIP
10.110.111.250
    │
    ▼
Redis Pod
10.110.111.201
```

Redis Cluster 其它节点：

```text
Redis-0  10.110.111.201
Redis-1  10.110.111.202
Redis-2  10.110.111.203
```

客户端能够正常访问 Redis Cluster。

---

## 场景 B：Pod 使用 Calico，MetalLB 使用大二层

例如：

```text
MetalLB VIP:
10.110.111.250

Redis Pod:
10.233.94.162
10.233.95.23
10.233.92.81
```

此时：

```text
rp_filter=0
```

虽然已经避免 Linux 在 MetalLB 入口处丢包，但 Redis Cluster 客户端仍然无法正常工作。

原因已经不再是 `rp_filter`。

---

# 8. 第二层根因：Redis Cluster 客户端需要直接访问 Cluster Node

Redis Cluster 与普通单实例 Redis 最大的差异是：

> 客户端并不是永远只访问最开始连接的 VIP。

Redis Cluster 会根据 Key 的 Hash Slot 返回对应 Redis 节点。

例如客户端首先连接：

```text
10.110.111.250:6379
```

Redis 可能返回：

```text
MOVED 12539 10.233.95.23:6379
```

客户端随后会直接连接：

```text
10.233.95.23:6379
```

因此 MetalLB VIP 实际上只解决了：

```text
客户端
   │
   ▼
Cluster 入口
```

但 Redis Cluster 还需要：

```text
客户端
   │
   ├── Redis-0
   ├── Redis-1
   └── Redis-2
```

都可达。

---

# 9. 为什么大二层 Pod 可以，Calico Pod 不可以

## 9.1 Pod 使用大二层

Redis Cluster 返回：

```text
MOVED ... 10.110.111.202:6379
```

客户端到：

```text
10.110.111.202
```

存在正常企业网络路由。

所以：

```text
Client
  │
  ├── 10.110.111.201
  ├── 10.110.111.202
  └── 10.110.111.203
```

全部可达。

---

## 9.2 Pod 使用 Calico

Redis Cluster 返回：

```text
MOVED ... 10.233.95.23:6379
```

但是 `10.233.0.0/16` 是 Kubernetes 内部 Pod CIDR。

企业外部网络通常没有：

```text
10.233.0.0/16
```

对应路由。

结果：

```text
Client
  │
  ▼
MetalLB VIP
  │
  ▼
Redis-0
  │
  │ MOVED
  ▼
10.233.95.23
  │
  X
外部无法路由到 Calico Pod
```

因此表现为：

```text
VIP 可以建立初始连接
但 Cluster 模式业务访问失败 / timeout
```

---

## 9.3 进一步验证：仅给每个 Redis Pod 配独立 VIP 仍然不够

进一步测试时，为每个 Redis Pod 创建了独立的 LoadBalancer Service，并分配独立 MetalLB VIP，例如：

```text
redis-0
Pod IP: 10.233.94.162
VIP:    10.110.111.251

redis-1
Pod IP: 10.233.95.23
VIP:    10.110.111.252

redis-2
Pod IP: 10.233.92.81
VIP:    10.110.111.253
```

从 Kubernetes 网络层看，这些 VIP 都可以映射到对应 Pod：

```text
10.110.111.251
      │
      ▼
Service
      │
      ▼
10.233.94.162
```

但这仍然不能保证 Redis Cluster 对外可用。

原因是：

> **MetalLB 只负责提供一个外部可达的 Service 地址，并不会自动修改 Redis Cluster 自己对外发布的 Node 地址。**

如果 Redis Cluster 内部仍然认为自己的地址是：

```text
10.233.94.162:6379
10.233.95.23:6379
10.233.92.81:6379
```

客户端通过 VIP 建立第一次连接后，Redis 仍可能返回：

```text
MOVED 12539 10.233.95.23:6379
```

于是客户端仍然会绕过 VIP，直接连接 Calico Pod IP，最终超时。

因此：

```text
每 Pod 一个 MetalLB VIP
        ≠
Redis Cluster 自动使用这些 VIP
```

完整方案必须同时维护两层映射：

```text
Kubernetes 网络层
redis-0 Pod 10.233.94.162
        ↓
Service / VIP 10.110.111.251

Redis Cluster 配置层
redis-0
cluster-announce-ip = 10.110.111.251
```

并且 Redis Cluster 的客户端端口与 Cluster Bus 端口都要一起考虑：

```text
cluster-announce-ip
cluster-announce-port
cluster-announce-bus-port
```

> 不建议手工直接修改 Redis `nodes.conf`。`nodes.conf` 属于 Redis Cluster 自身维护的集群状态文件。应由 Redis 配置参数或 Operator 负责维护 announce 地址。

---

# 10. 两种网络方案对比

| 对比项 | Pod + MetalLB 都走大二层 | Calico Pod + MetalLB L2 |
|---|---|---|
| Pod 地址 | 企业大二层地址 | Calico Pod CIDR |
| VIP 地址 | 企业大二层地址 | 企业大二层地址 |
| 外部直接访问 Pod | 可以 | 默认不可以 |
| Redis Cluster MOVED 后访问 | 可以 | 通常失败 |
| MetalLB 作用 | VIP 宣告 | VIP 宣告 |
| 对 rp_filter 敏感 | 是 | 是 |
| 对企业网络依赖 | 高 | 相对低 |
| Pod 网络隔离 | 较弱 | 更好 |
| 地址资源占用 | 高 | 低 |
| K8s 原生网络特性 | 较弱 | 更符合 Kubernetes 网络模型 |
| Redis Cluster 外部访问复杂度 | 低 | 高 |
| 运维复杂度 | 网络侧高 | K8s + 路由侧高 |

---

# 11. 可落地的解决方向

针对：

```text
Calico Pod + MetalLB L2 + Redis Cluster
```

当前可以分为三个方向。

---

## 方案一：将 Calico Pod CIDR 对外路由

例如：

```text
Pod CIDR:
10.233.0.0/16
```

让企业网络知道：

```text
10.233.0.0/16
    │
    ▼
Kubernetes / Calico
```

可以采用：

- Calico BGP；
- ToR 与 Calico 建立 BGP；
- 上层增加静态路由；
- 核心交换机学习 Pod CIDR。

此时 Redis Cluster 即使返回：

```text
MOVED ... 10.233.95.23:6379
```

客户端仍然可以通过企业三层网络访问该 Pod。

### 优点

- 保留 Redis Cluster 原生 Smart Client 机制；
- Redis 可以继续使用真实 Pod IP 作为 Cluster Node 地址；
- 不需要给每个 Redis Pod 单独维护 MetalLB VIP；
- Cluster 扩缩容后网络模型更自然；
- 对 Redis Operator 本身要求较低。

### 缺点

- Pod CIDR 需要进入企业路由域；
- 需要网络设备或 BGP 配合；
- 必须配套 ACL / NetworkPolicy；
- 要避免 Pod CIDR 与现有企业地址冲突；
- Calico BGP、路由收敛和故障排查复杂度会上升。

---

## 方案二：使用 Kubeblock Operator 管理每个 Cluster Node 的外部 Endpoint

该方案不是简单地：

```text
每 Pod 创建一个 MetalLB VIP
```

而是需要 Operator 同时理解：

```text
Kubernetes Service
+
MetalLB VIP
+
Redis Cluster Node
+
Redis cluster-announce-*
```

例如：

```text
redis-0
Pod IP:       10.233.94.162
External VIP: 10.110.111.251

redis-1
Pod IP:       10.233.95.23
External VIP: 10.110.111.252

redis-2
Pod IP:       10.233.92.81
External VIP: 10.110.111.253
```

同时 Redis 必须对外公布：

```text
redis-0
cluster-announce-ip 10.110.111.251

redis-1
cluster-announce-ip 10.110.111.252

redis-2
cluster-announce-ip 10.110.111.253
```

并同步维护：

```text
cluster-announce-port
cluster-announce-bus-port
```

### Operator 需要负责

- 每个 Pod 独立 Service；
- 每个 Service 独立外部 Endpoint/VIP；
- StatefulSet ordinal 与 Service 固定关系；
- Redis `cluster-announce-ip`；
- Redis `cluster-announce-port`；
- Redis `cluster-announce-bus-port`；
- Pod 重建；
- Master / Replica 切换；
- Cluster Failover；
- 横向扩缩容；
- VIP 与 Redis Node 映射关系更新。

### 为什么普通 Redis Operator 可能不支持

普通 Redis Operator 通常重点管理 Redis Pod 生命周期、Cluster 拓扑、故障转移和配置，但不一定具备：

```text
Per-Pod External Service
+
External VIP
+
Redis Cluster announce 地址联动
```

因此手工创建多个 LoadBalancer Service，只解决了“VIP 能到 Pod”，没有解决“Redis Cluster 应该向客户端公布哪个地址”。

### KubeBlocks 这类方案

KubeBlocks 官方将 Redis、MongoDB、Kafka 这类数据库归为具有 **Smart Client** 特征的场景，并提供 **Pod Service** 这类能力，为每个 Pod 提供独立 Service 地址。

这类 Redis-aware Operator 的核心价值是：不仅管理 Kubernetes Service，还能够围绕数据库的节点寻址语义做联动，避免客户端继续拿到不可达的 Calico Pod IP。

### 优点

- 不需要把整个 Calico Pod CIDR 暴露到企业网络；
- 外部只访问受控 VIP；
- Redis Cluster Node 对外地址固定且清晰；
- ACL、安全审计边界清楚；
- Operator 可以处理扩缩容和故障转移后的地址联动。

### 缺点

- 对 Operator 能力要求高；
- 当前使用的原生 Redis Operator 未必支持；
- 每个 Redis Cluster Node 需要独立 Endpoint/VIP；
- Operator 与 MetalLB / LoadBalancer 的集成复杂度更高；
- 引入 KubeBlocks 等新 Operator 需要额外评估迁移与运维成本。

---

## 方案三：Redis Pod 继续使用企业大二层 VLAN 地址

也就是当前已经验证能够正常工作的模式：

```text
Redis Pod IP
=
Redis Cluster announce IP
=
企业网络可路由 IP
```

例如：

```text
Redis-0 10.110.111.201
Redis-1 10.110.111.202
Redis-2 10.110.111.203
```

客户端收到：

```text
MOVED ... 10.110.111.202:6379
```

后，可以直接访问对应 Redis Pod。

### 优点

- 网络模型最直观；
- Redis 不需要额外做 announce 地址转换；
- Cluster Client 天然能够访问每个节点；
- 当前场景已经验证可用；
- 对 Redis Operator 改造最少。

### 缺点

- Pod 直接占用企业大二层地址；
- 对 VLAN、交换机和二层网络依赖较高；
- IP 地址资源消耗更多；
- Kubernetes Pod 网络与企业网络耦合较深；
- 多节点、多 VLAN 环境仍然需要关注 `rp_filter`；
- 相比 Calico 网络，网络隔离和地址管理复杂度更高。

---

# 12. 三种方案对比

| 对比项 | 方案一：Calico Pod CIDR 对外路由 | 方案二：Redis-aware Operator + Per-Pod VIP | 方案三：Redis Pod 大二层 |
|---|---|---|---|
| Redis Cluster 客户端兼容性 | 高 | 高 | 高 |
| Redis 对外公布地址 | Calico Pod IP | 独立 VIP | Pod 大二层 IP |
| 是否暴露 Pod CIDR | 是 | 否 | 不涉及 Calico Pod CIDR |
| 是否需要每 Pod VIP | 否 | 是 | 否 |
| 是否需要维护 announce | 通常不需要 | 需要，由 Operator 自动维护 | 通常不需要 |
| 对 Redis Operator 要求 | 低 | 高 | 低 |
| 网络设备改造 | 较高 | 较低 | 中 |
| 对企业二层网络依赖 | 低~中 | 中 | 高 |
| IP/VIP 资源消耗 | Pod CIDR | 每节点一个 VIP | 每 Pod 一个企业 IP |
| 扩缩容便利性 | 高 | Operator 支持时高 | 需要协调二层 IP |
| 安全边界 | Pod 网段需要精细控制 | 清晰 | Pod 直接进入企业网络 |
| 故障排查重点 | BGP / 路由 / Calico | Operator / Service / VIP / Redis announce | VLAN / 二层 / rp_filter |
| 当前环境落地难度 | 中~高 | 原生 Operator 下高 | 低 |
| 当前验证状态 | 待验证 | 手工 VIP 已验证“不完整” | 已验证可用 |

---

# 13. 当前建议

结合本次实际测试结果，建议调整原来的方案优先级。

## 第一选择：继续使用 Redis Pod 大二层网络

这是目前已经验证能够工作的方案：

```text
Redis Pod
使用企业可路由的大二层地址
```

Redis Cluster 返回的 Node 地址天然对客户端可达，不需要额外维护 `cluster-announce-*` 与 VIP 映射。

适合当前规模可控、大二层网络成熟、希望尽量少改 Redis Operator 的场景。

---

## 第二选择：如果希望保留 Calico，评估将 Pod CIDR 纳入企业三层路由

这种方案从 Redis Cluster 角度最自然：

```text
Redis 继续公布真实 Pod IP
+
外部网络能够路由 Pod CIDR
```

重点评估：Calico BGP、核心路由、ACL、NetworkPolicy、Pod CIDR 地址规划和路由收敛。

---

## 第三选择：引入支持 Smart Client / Pod Service 的 Kubeblock Operator

如果目标架构明确要求：

```text
Redis Pod 使用 Calico
+
不允许 Pod CIDR 对外路由
+
客户端需要从集群外访问 Redis Cluster
```

那么应考虑支持：

```text
Per-Pod Service
+
External Endpoint/VIP
+
Redis cluster-announce-* 自动维护
```

的 Operator。

KubeBlocks 属于可以重点验证的产品方向。

在正式替换当前 Redis Operator 前，需要重点验证：

- Redis Cluster 模式；
- Per-Pod Service；
- LoadBalancer / MetalLB；
- `cluster-announce-ip`；
- `cluster-announce-port`；
- `cluster-announce-bus-port`；
- Master/Replica Failover；
- Pod 重建后 VIP 是否保持；
- Redis 扩缩容；
- Cluster 节点地址是否自动更新。

---

## 不再推荐：手工每 Pod 创建 MetalLB VIP

单独做：

```text
redis-0 → VIP 10.110.111.251
redis-1 → VIP 10.110.111.252
redis-2 → VIP 10.110.111.253
```

但不修改 Redis Cluster announce 地址，属于不完整方案。

最终仍然会出现：

```text
Client
   │
   ▼
VIP 10.110.111.251
   │
   ▼
Redis-0
   │
   │ MOVED
   ▼
10.233.95.23
   │
   X
外部不可达
```

因此：

> **MetalLB 解决的是“这个 VIP 怎么到 Pod”，Redis Operator 还必须解决“Redis Cluster 告诉客户端应该连接哪个地址”。**

---

# 14. 最终故障结论

本次实际上包含 **两个独立的问题**。

## 问题一：MetalLB VIP 外部访问超时

根因：

```text
多网卡 / 多 VLAN
+
非对称路由
+
rp_filter=1
```

导致 Linux 在 VIP 报文进入节点以后进行严格反向路径检查，并将合法流量丢弃。

解决：

```text
rp_filter=0
```

或者根据网络规范调整为宽松模式，并确保返回路由设计合理。

---

## 问题二：Calico Pod 下 Redis Cluster 仍然无法正常使用

根因：

```text
Redis Cluster Client
需要根据 MOVED/Slot 信息
直接访问每个 Redis Cluster Node
```

但是 Redis 返回的是：

```text
10.233.x.x
```

即 Calico Pod IP。

外部客户端没有到 Calico Pod CIDR 的路由，因此：

```text
MetalLB VIP 初始入口可达
≠
Redis Cluster 整体可用
```

进一步测试也证明：

```text
每个 Redis Pod 独立 MetalLB VIP
```

本身仍然不能解决问题。

如果 Redis Cluster 仍然向客户端公布：

```text
10.233.x.x
```

客户端收到 `MOVED` 后依旧会直接访问 Calico Pod IP。

所以完整条件应该是：

```text
Per-Pod Service / VIP
+
Redis cluster-announce-ip
+
cluster-announce-port
+
cluster-announce-bus-port
+
Operator 自动维护 Node 与 VIP 的映射关系
```

---

# 15. 故障链路总结

```text
第一阶段
────────────────────────────────────────

Client 10.1.32.174
       │
       ▼
Gateway
       │
       ▼
MetalLB VIP 10.110.111.250
       │
       ▼
bond0.24
       │
       ▼
rp_filter
       │
       ├── rp_filter=1 → 丢包
       │
       └── rp_filter=0 → 放行


第二阶段
────────────────────────────────────────

Client
       │
       ▼
MetalLB VIP
       │
       ▼
Redis Cluster Node-0
       │
       │ MOVED
       ▼
Client 尝试连接 10.233.x.x
       │
       X
Calico Pod CIDR 外部不可路由


进一步测试
────────────────────────────────────────

redis-0 Pod 10.233.94.162
       │
       ▼
Service / VIP 10.110.111.251
       │
       │ 仅 Kubernetes 网络层可达
       ▼
Redis Cluster 仍 announce 10.233.94.162
       │
       ▼
Client 收到 MOVED 10.233.x.x
       │
       X
仍然失败

正确思路：
VIP 与 Redis announce 地址必须联动
```

最终可以总结为：

> **`rp_filter` 解决的是“流量能不能进入 Kubernetes 节点”；Redis Cluster + Calico 解决的是“客户端能不能访问 Redis 对外公布的每一个 Cluster Node”。如果使用 VIP 隐藏 Calico Pod IP，Operator 还必须同步维护 Redis `cluster-announce-*`，仅创建 MetalLB Service/VIP 并不足够。**
