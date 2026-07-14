# Grafana 中相似 Pod 名称匹配问题总结

## 一、问题现象

Kubernetes 中存在两个名称相似的 Deployment：

```text
delivery-test-service
delivery-test-service-special
```

它们生成的 Pod 分别为：

```text
delivery-test-service-6dbf645bdc-zsf79
delivery-test-service-special-5ccc757cbb-78qkw
```

Grafana 变量中需要同时展示这两个服务，但查询中如果使用模糊匹配：

```promql
pod=~"${service:regex}.*"
```

由于两个服务名称存在前缀包含关系，可能导致选择其中一个服务时，将另一个服务的 Pod 也匹配出来。

---

## 二、解决方法一：使用完整的严格正则

```promql
pod=~"^(${service:regex})-[^-]+-[^-]+$"
```

### 正则含义

```text
^                      从 Pod 名称开头匹配
(${service:regex})     匹配 Grafana 中选择的服务名称
-                      匹配连字符
[^-]+                  匹配 ReplicaSet 哈希
-                      匹配连字符
[^-]+                  匹配 Pod 随机后缀
$                      必须匹配到 Pod 名称结尾
```

匹配的 Pod 名称结构为：

```text
服务名称-ReplicaSet哈希-Pod随机后缀
```

例如变量选择：

```text
delivery-test-service
```

可以匹配：

```text
delivery-test-service-6dbf645bdc-zsf79
```

不会匹配：

```text
delivery-test-service-special-5ccc757cbb-78qkw
```

因为在 `delivery-test-service` 后面存在三段内容：

```text
special-5ccc757cbb-78qkw
```

而正则只允许存在两段。

---

## 三、解决方法二：使用简化正则

```promql
pod=~"${service:regex}-[^-]+-[^-]+"
```

该写法与完整写法的匹配效果基本相同。

这是因为 Prometheus 的标签正则匹配默认采用完整字符串匹配，因此通常可以省略：

```text
^    开头限定
$    结尾限定
()   外层分组
```

同样能够保证 Pod 名称符合以下结构：

```text
服务名称-ReplicaSet哈希-Pod随机后缀
```

---

## 四、两种方法的区别

| 对比项                  | 完整写法                               | 简化写法                           |
| -------------------- | ---------------------------------- | ------------------------------ |
| 表达式                  | `^(${service:regex})-[^-]+-[^-]+$` | `${service:regex}-[^-]+-[^-]+` |
| 匹配效果                 | 严格匹配完整 Pod 名称                      | 在 PromQL 中效果基本相同               |
| 可读性                  | 边界表达更明确                            | 更简洁                            |
| 对 Prometheus 默认行为的依赖 | 较少                                 | 依赖 Prometheus 正则默认完整匹配         |
| 适用范围                 | PromQL、普通正则工具、Grafana Regex 过滤     | 更适合直接写在 PromQL 标签条件中           |
| 推荐场景                 | 强调严谨、方便后续维护                        | Grafana 面板查询，追求简洁              |

---

## 五、最终建议

如果该表达式直接用于 Grafana 的 PromQL 查询，推荐使用简化写法：

```promql
pod=~"${service:regex}-[^-]+-[^-]+"
```

如果表达式还可能复制到 Grafana 变量的 Regex 过滤、脚本或其他正则工具中，推荐保留完整写法：

```promql
pod=~"^(${service:regex})-[^-]+-[^-]+$"
```

两种方法的核心逻辑相同：**限制服务名称后面只能存在两段 Pod 后缀，避免名称相似的服务发生前缀误匹配。**
