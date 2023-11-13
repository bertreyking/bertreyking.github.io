# chrony 时钟同步

## chrony 与 ntp 之前的区别

`chronyd` 可以优于 `ntpd`:

- `chronyd` 可以正常工作，其中对时间参考的访问是间歇性的，而 `ntpd` 需要定期轮询时间引用才能正常工作。
- `chronyd` 网络较长时间拥塞也能表现良好
- `chronyd` 通常可以更快准确地同步时钟
- `chronyd` 能够快速适应时钟速率的突然变化
- `chronyd` 可以调整较大范围内 Linux 系统上的时钟速率，即使在时钟中断或不稳定的机器上运行。例如，在某些虚拟机上：
- `chronyd` 使用较少的内存

总之一句话，`chrony` 就是牛逼

## chrony 配置

### chronyd 和 chronyc 区别

- `chronyd` 守护进程
- `chronyc` 监控和控制 `chronyd`的 `client` 端

### [chronyd 配置](https://access.redhat.com/documentation/zh-cn/red_hat_enterprise_linux/7/html/system_administrators_guide/sect-understanding_chrony_and-its_configuration)

- 配置文件 - [18.4. 为不同的环境设置 chrony](https://access.redhat.com/documentation/zh-cn/red_hat_enterprise_linux/7/html/system_administrators_guide/sect-setting_up_chrony_for_different_environments) [chrony.conf(5) Manual Page](https://chrony-project.org/doc/3.1/chrony.conf.html)

  ```shell
  # server 端
  [root@10-29-26-144 ~]# cat /etc/chrony.conf
  driftfile /var/lib/chrony/drift
  commandkey 1
  keyfile /etc/chrony.keys # 用于指定包含用于 NTP 数据包身份验证的 ID 密钥对的文件的位置
  initstepslew 10 ntp1.aliyun.com # 步进的方式，来修正时钟，不建议使用，该配置会检查误差是否超过10s，如果是通过 后面的 client1、3、6 来修正 server 端的时钟 
  local stratum 8
  manual # 启用 chronyc 中 使用 settime 命令来修改时间
  allow 10.29.0.0/16 # 允许以下网段访问
  
  # server 端启动后报，修正 initstepslew 指定的同步源即可修复
  root@10-29-26-144 ~]# systemctl status  chronyd
  ● chronyd.service - NTP client/server
     Loaded: loaded (/usr/lib/systemd/system/chronyd.service; enabled; vendor preset: enabled)
     Active: active (running) since Mon 2023-11-13 15:04:24 CST; 2s ago
       Docs: man:chronyd(8)
             man:chrony.conf(5)
    Process: 274162 ExecStartPost=/usr/libexec/chrony-helper update-daemon (code=exited, status=0/SUCCESS)
    Process: 274159 ExecStart=/usr/sbin/chronyd $OPTIONS (code=exited, status=0/SUCCESS)
   Main PID: 274161 (chronyd)
     CGroup: /system.slice/chronyd.service
             └─274161 /usr/sbin/chronyd
  Nov 13 15:04:24 10-29-26-144 systemd[1]: Starting NTP client/server...
  Nov 13 15:04:24 10-29-26-144 chronyd[274161]: chronyd version 3.4 starting (+CMDMON +NTP +REFCLOCK +RTC +PRIVDROP +SCFILTER +SIGND +ASYNCDNS +SECHASH +IPV6 +DEBUG)
  Nov 13 15:04:24 10-29-26-144 chronyd[274161]: commandkey directive is no longer supported
  Nov 13 15:04:24 10-29-26-144 chronyd[274161]: Could not resolve address of initstepslew server client1
  Nov 13 15:04:24 10-29-26-144 chronyd[274161]: Could not resolve address of initstepslew server client3
  Nov 13 15:04:24 10-29-26-144 chronyd[274161]: Could not resolve address of initstepslew server client6
  Nov 13 15:04:24 10-29-26-144 chronyd[274161]: Frequency 0.000 +/- 1000000.000 ppm read from /var/lib/chrony/drift
  Nov 13 15:04:24 10-29-26-144 systemd[1]: Started NTP client/server.
  Hint: Some lines were ellipsized, use -l to show in full.
  
  # client 端
  [root@controller-node-1 ~]# cat /etc/chrony.conf
  server 10.29.26.144 iburst
  driftfile /var/lib/chrony/drift
  logdir /var/log/chrony
  log measurements statistics tracking
  keyfile /etc/chrony.keys
  commandkey 24
  local stratum 10
  initstepslew 20 master
  allow 10.29.26.144
  
  # 检查 (fina.daocloud.io=10.29.26.144)
  [root@controller-node-1 ~]# chronyc sources -v 
  210 Number of sources = 1
  
    .-- Source mode  '^' = server, '=' = peer, '#' = local clock.
   / .- Source state '*' = current synced, '+' = combined , '-' = not combined,
  | /   '?' = unreachable, 'x' = time may be in error, '~' = time too variable.
  ||                                                 .- xxxx [ yyyy ] +/- zzzz
  ||      Reachability register (octal) -.           |  xxxx = adjusted offset,
  ||      Log2(Polling interval) --.      |          |  yyyy = measured offset,
  ||                                \     |          |  zzzz = estimated error.
  ||                                 |    |           \
  MS Name/IP address         Stratum Poll Reach LastRx Last sample               
  ===============================================================================
  ^* fina.daocloud.io              8   6    37    20  +1225ns[+1181us] +/-  159us
  ```

## [chrony 使用](https://access.redhat.com/documentation/zh-cn/red_hat_enterprise_linux/7/html/system_administrators_guide/sect-using_chrony)

### chrony 跟踪

```shell
~]$ chronyc tracking
Reference ID  : CB00710F (foo.example.net)
Stratum     : 3
Ref time (UTC) : Fri Jan 27 09:49:17 2017
System time   : 0.000006523 seconds slow of NTP time
Last offset   : -0.000006747 seconds
RMS offset   : 0.000035822 seconds
Frequency    : 3.225 ppm slow
Residual freq  : 0.000 ppm
Skew      : 0.129 ppm
Root delay   : 0.013639022 seconds
Root dispersion : 0.001100737 seconds
Update interval : 64.2 seconds
Leap status   : Normal
```

### chrony 同步源

```shell
~]$ chronyc sources
	210 Number of sources = 3
MS Name/IP address     Stratum Poll Reach LastRx Last sample
===============================================================================
#* GPS0             0  4  377  11  -479ns[ -621ns] +/- 134ns
^? a.b.c             2  6  377  23  -923us[ -924us] +/-  43ms
^+ d.e.f             1  6  377  21 -2629us[-2619us] +/-  86ms

M
这表示源的模式。^ 表示服务器，= 表示对等，# 代表本地连接的参考时钟

S
"*" 表示当前同步的 chronyd 的源
"+" 表示可接受的源与所选源结合使用
"-" 表示合并算法排除的可接受的源
"?" 表示丢失了哪个连接或者数据包没有通过所有测试的源
"x" 表示 chronyd 认为是 假勾号（ 时间与大多数其他来源不一致
"~" 表示时间似乎有太多变化的来源。
"?" 条件也会在启动时显示，直到从中收集了至少三个样本

LastRx
显示了在多久前从源中获取了最后的样本
Last sample
显示本地时钟和最后一个测量源之间的偏差。方括号中的数字显示了实际测量的误差 ns（代表 nanoseconds）、us（代表 microseconds）、ms（代表 milliseconds）或 s （代表秒）后缀
方括号左边的数字显示了原来的测量，经过调整以允许应用本地时钟
+/- 指示符后的数字显示了测量中的错误裕度。正偏差表示本地时钟在源前面

~]$ chronyc sources -v 
```

### 手动调整时钟

```shell
~]# chronyc makestep # 如果使用了 rtcfile 指令，则不应该手动调整实时时钟
```

