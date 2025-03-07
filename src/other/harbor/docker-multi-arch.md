# docker 多架构镜像构建

## pull 镜像

```shell
- arm64
docker pull rancher/local-path-provisioner:v0.0.31 --platform linux/arm64

- amd64
docker pull rancher/local-path-provisioner:v0.0.31 --platform linux/amd64
```

## tag 镜像

```shell
docker tag rancher/local-path-provisioner-amd64:v0.0.31 154.39.81.129:5000/rancher/local-path-provisioner:v0.0.31-amd
docker tag rancher/local-path-provisioner-arm64:v0.0.31 154.39.81.129:5000/rancher/local-path-provisioner:v0.0.31-arm
```

## 创建多架构 `manifest`

```shell
docker manifest create --insecure --amend 154.39.81.129:5000/rancher/local-path-provisioner:v0.0.31 154.39.81.129:5000/rancher/local-path-provisioner:v0.0.31-arm 154.39.81.129:5000/rancher/local-path-provisioner:v0.0.31-amd 

docker manifest inspect 154.39.81.129:5000/rancher/local-path-provisioner:v0.0.31
```

## push 镜像

```shell
docker manifest push --insecure 154.39.81.129:5000/rancher/local-path-provisioner:v0.0.31
```

