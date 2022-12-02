# docker SDK 的 简单使用

## DockerClient 实例

```python
- 导入 docker 库
import docker

1. 使用环境变量
client = docker.from_env()

2. 实例化 dockerClient
client = docker.Dockerclien(base_url="unix:/var/run/docker.sock", timeout=180, max_pool_size=200)

参数解读
- timeout(int)：180 超时时间
- base_url: -- 2.dockerClient
	- unix://var/run/docker.sock 
	- tcp://127.0.0.1:1234
- max_pool_size(int): 180 最大连接数

```

## Login 函数

```python
client.login(username='xxxx', password='xx@xxxxx', registry='x.x.x.x'， reauth=True)

参数解读：
-	reauth(bool): 说是可以覆盖 dockerClient 主机的认证信息，我尝试了几次并没覆盖
```

## Pull 函数

```python
1. 先登陆，后 pull
client.login(username='xxxx', password='xx@xxxxx', registry='x.x.x.x'， reauth=True)
client.images.pull('x.x.x.x/xxxx/xxxx', tag='latest')

2. 直接带上认证信息进行 pull
auth = {
	'username': 'xxxx',
	'password': 'xx@xxxx'
}
client.images.pull('x.x.x.x/xxxx/xxxx', tag='latest',auth_config=auth)

参数解读：
- auth_config(dict): 定义一个 dict 类型的认证信息
- tag(str)：如果不写，默认 latest
- all(bool): True 下载所有 tag
```

## 代码示例

```python
import docker

client = client = docker.Dockerclien(base_url="unix:/var/run/docker.sock", timeout=180, max_pool_size=200)

auth = {
	'username': 'xxxx',
	'password': 'xx@xxxx'
}

# 使用 try ... except 进行处理和抛出异常
try:
  client.images.pull('x.x.x.x/xxxx/xxxx', tag='latest',auth_config=auth)
  
except Exception as err:
  print(err.__dice__)
```

## 部署遇到的问题

- docker sdk 作为容器的生命周期管理工具被 flask/diango 调用 push/pull/run 操作时，如果我们是 container 部署在 docker 主机上，需要将 docker.sock 文件挂载到容器内部、网络模式建议 host 模式，可以避免一些网络问题。也可以尝试使用 docker in docker 的方式

## [参阅文档](https://docker-py.readthedocs.io/en/stable/index.html)
