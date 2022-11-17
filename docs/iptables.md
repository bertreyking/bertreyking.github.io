# iptables 开启/禁用端口
```
命令：iptables
参数：
- -A 添加一条 input 规则, INPUT 进、OUTPUT 出
- -p 指定协议类型，如 tcp / udp
- -s 源地址
- -d 目标地址
- --dport 目标端口
- --sport 与 dport 相反为源端口 
- -j 决定是接受还是丢掉数据包，ACCEPT 表示接受，DROP 表示丢掉相关数据包

示例1： (开启22端口，接受来自任何节点的ssh 会话，此处需要添加 2 条规则，允许进出都开启 22 端口)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT
iptables -A OUTPUT -p tcp --sport 22 -j ACCEPT

示例2：（禁止某主机访问节点的 ssh端口）
iptables -A INPUT -p tcp -s 192.168.1.x -j DROP

示例3 （禁止节点与 某主机的 22 端口进行通信）
iptables -A OUTPUT -p tcp -d 192.168.1.x --dport 22 -j DROP

示例4 （删除规则）
iptables -D OUTPUT -p tcp -d 192.168.1.x --dport 22 -j DROP

iptables -L -n --line-number
iptables -D INPUT 2
```

[iptables_nat规则](https://gist.github.com/tomasinouk/eec152019311b09905cd)
