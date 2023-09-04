---
title: Harbor 部署与维护
author: bertreyking
date: 2023-09-04
keywords: [harbor,docker-compose]
---

# Harbor 部署与维护

## 下载离线介质

- [harbor-offline-installer][harbor-offline-installer]

  ```shell
  wget https://github.com/goharbor/harbor/releases/download/v2.9.0/harbor-offline-installer-v2.9.0.tgz
  ```

## 部署

- [run-installer-script][run-install-script] 安装模式
  1. Just Harbor                # 仅安装 Harbor - 默认
  2. Harbor with Notary    # 带镜像签名工具，来保证镜像层在 pull、push、transfer 过程中的一致性和完整性
  3. Harbor with Clair        # 带镜像漏洞扫描
  4. Harbor with Chart Repository Service    # 带 Helm 支持的 Chart 仓库
  5. Harbor with two or all three of Notary, Clair, and Chart Repository Service    # 基本全部打包安装
  
  ```shell
  - Just Harbor 
  sudo ./install.sh
  
  - 打包安装全部组件，不需要的可以去掉 --with-xxxxx 对应参数即可
  sudo ./install.sh --with-notary --with-clair --with-chartmuseum
  ```

 - 注意事项

   ⚠️： harbor 默认部署时，会将容器内部端口通过 80、443 暴露需要，请确保节点中不会占用这两个端口，或者提前更改 `docker-compose.yml` 文件

   ```yaml
    proxy:
       image: goharbor/nginx-photon:v2.7.1
       container_name: nginx
       restart: always
       cap_drop:
         - ALL
       cap_add:
         - CHOWN
         - SETGID
         - SETUID
         - NET_BIND_SERVICE
       volumes:
         - ./common/config/nginx:/etc/nginx:z
         - type: bind
           source: ./common/config/shared/trust-certificates
           target: /harbor_cust_cert
       networks:
         - harbor
       ports:
         - 80:8080
         - 9090:9090
       depends_on:
         - registry
         - core
         - portal
         - log
       logging:
         driver: "syslog"
         options:
           syslog-address: "tcp://localhost:1514"
           tag: "proxy"
   ```

   

## 维护

- 停止 harbor 组件

  ```shell
  docker-compose down -v
  ```

- 启动 harbor 组件

  ```shell
  docker-compose up -d
  ```

## 访问

- 启动后通过浏览器访问 `http://$ip` 也可以通过  `harbor.yml` 进行自定义

- 默认用户/密码 `admin/Harbor12345`

  

---

附录：

[harbor-offline-installer]: https://github.com/goharbor/harbor/releases/download/v2.9.0/harbor-offline-installer-v2.9.0.tgz '离线安装介质'
[run-install-script]: https://goharbor.io/docs/1.10/install-config/run-installer-script/ '安装步骤'
[Harbor with Notary ]: https://github.com/zj1244/Blog/blob/master/2019/harbor%E7%9A%84Notary%E5%8A%9F%E8%83%BD%E6%B5%8B%E8%AF%95.md
