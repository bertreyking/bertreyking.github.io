# yum update 和 upgrade 的区别

- update:  更新软件包时会保留老版本的软件包(前提是: /etc/yum.conf 配置文件中该参数 obsoletes=0. default: 1)
- upgrade: 更新软件包时会清理老版本的软件包
- obsoletes=1 时两者没有区别

