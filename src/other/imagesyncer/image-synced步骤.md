# image-syncer 使用

## 1.[ 配置文件两种写法](https://github.com/AliyunContainerService/image-syncer/tree/master/example)

### 1.1 认证和镜像清单合并

```json
{
    # auth: 所有源和目标镜像仓库 url 和 认证信息全部放入 auth 字典
    "auth": {
        "harbor.myk8s.paas.com:32080": {
            "username": "admin",
            "password": "xxxxxxxxx",
            "insecure": true
        },
        "registry.cn-beijing.aliyuncs.com": {
            "username": "acr_pusher@1938562138124787",
            "password": "xxxxxxxx"
        }
    },
    # 源仓库和目标仓库以 key:value 的定义
    "images": {
        # 同步 nginx 所有版本到默认的镜像仓库中，默认仓库在 cli 可以进行更改 (default:image-syncer)
        "harbor.myk8s.paas.com:32080/library/nginx": "",
        # 源仓库字段中不包含 tag 时，表示将该仓库所有 tag 同步到目标仓库，此时目标仓库不能包含 tag
        "harbor.myk8s.paas.com:32080/library/nginx": "registry.cn-beijing.aliyuncs.com/library/nginx", # 同步所有 nginx 版本
        # 源仓库字段中包含 tag 时，表示同步源仓库中的一个 tag 到目标仓库，如果目标仓库中不包含tag，则默认使用源 tag
        "harbor.myk8s.paas.com:32080/library/nginx:latest": "registry.cn-beijing.aliyuncs.com/library/nginx", # 同步 nginx:latest 版本
        # 源仓库字段中的 tag 可以同时包含多个（比如"url/library/nginx:v1,v2,v3"），tag之间通过 "," 隔开，此时目标仓库不能包含tag，并且默认使用原来的 tag
        "harbor.myk8s.paas.com:32080/library/nginx:latest,v1,v2,v3": "registry.cn-beijing.aliyuncs.com/library/nginx" # 同步 nginx 4 个版本  
    }
}
```

### 1.2 认证和镜像清单分开 (批量生成镜像清单时较为方便)

```json
auth.json
{
  "harbor.myk8s.paas.com:32080": {
    "username": "admin",
    "password": "xxxxxxxxx",
    "insecure": true
  },
  "registry.cn-beijing.aliyuncs.com": {
    "username": "acr_pusher@1938562138124787",
    "password": "xxxxxxxx"
  }
},

images.json # 使用 images.yaml 更简单，直接换行追加即可
{
  "harbor.myk8s.paas.com:32080/library/nginx": "",
  "harbor.myk8s.paas.com:32080/library/nginx": "registry.cn-beijing.aliyuncs.com/library/nginx",
  "harbor.myk8s.paas.com:32080/library/nginx:latest": "registry.cn-beijing.aliyuncs.com/library/nginx",
  "harbor.myk8s.paas.com:32080/library/nginx:latest,v1,v2,v3": "registry.cn-beijing.aliyuncs.com/library/nginx"
}
```

## 2.[ 开始同步](https://github.com/AliyunContainerService/image-syncer)

```shell
# image-syncer 
--config:       指定配置文件为harbor-to-acr.json，内容如上所述
--registry:     设置默认目标 registry为registry.cn-beijing.aliyuncs.com，
--namespace:    默认目标 namespace 为 image-syncer
--proc:         并发数为10，重试次数为10
--log:          日志输出到 log 文件下，不存在自动创建，默认将日志打印到 stdout


./image-syncer --proc=10 --config=./config.json --registry=registry.cn-beijing.aliyuncs.com --namespace=image-syncer --retries=3 --log=./log

./image-syncer --proc=10 --retries=3 --proc=10 --auth=./auth.json --images=./images.json --retries=10 --log=./log
```

