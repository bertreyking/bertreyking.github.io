 # linux下域名解析顺序及nameserver配置-[参考链接1](https://www.thegeekdiary.com/centos-rhel-dns-servers-in-etcresolv-conf-change-after-a-rebootnetwork-service-restart-how-to-make-them-permanent/)[参考链接2](https://ma.ttias.be/centos-7-networkmanager-keeps-overwriting-etcresolv-conf/)
 ```
 1. linux主机内解析的顺序
 取决与/etc/nsswitch.conf 配置文件中hosts顺序
 hosts:      files dns myhostname   
 说明：
 #files 表示先去解析/etc/hosts文件中的记录，其实就类似于直接用ip访问后端应用
 node1-web >> node2-data
 #dns   表示去解析/etc/resolv.confg中的dns地址，由dns_server去正向和反向解析对应的记录，解析到后转发至后端应用
 node1-web >> dns_server(node2-data记录) >> node2-data
 #myhostname 类似于127.0.0.1,有点自己ping自己的意思
 2. nameserver 如何配置更改
 方法一：无需重启网络服务直接生效
 vi /etc/resolv.conf
 nameserver 1.1.1.1
 nameserver 2.2.2.2
 重启网络服务后可能会丢失,怎么才不会丢失呢？ 更改/etc/sysconfig/network-scripts/ifcfg-ens2f0 配置文件新增会更改PEERDNS=no，这样重启网络服务就不会有影响了
 方法二：需要重启网络服务
 vi /etc/sysconfig/network-scripts/ifcfg-ens2f0
 DNS1=1.1.1.1
 DNS2=1.1.1.2
 
 PEERDNS=no 实际是禁用使用dhcp_server 所下发的dns配置，禁用后，重启网络不会更改/etc/resolv.conf下的dns配置(但前提是网卡配置文件不要配置dns)
 PEERDNS=yes 生产一般都是静态配置文件，不会使用dhcp，所以yes的话，重启网络服务也不会更改/etc/resolv.conf下的dns配置
 
 其实无论 yes/no, 只要在/etc/resolv.conf文件下追加的dns-server是有效的，均配置即生效！！！
 ```
