# Request 使用

## 导入 reqeusts 模块

```
import requests
```

## 定义环境变量

```
- auth 信息

auth = ('admin', 'xxxxxxx')

- api 接口
url = ‘http://x.x.x.x/apis/apps/v1beata1/deployments’
```

## 使用 get 方法获取数据

```
- 定义 requests.get 方便变量

r = requests.get(url,auth)

- 打印 status_code
print(r.status.code)
```

