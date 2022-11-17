1. 查找大文件
```
find / -type f -size +500M -print0 | xargs -0 ls -lrth
find / -type f -size +500M -print | xargs ls -lrth
find / -type f -size +500M -print | xargs /bin/rm -rf 
```
2. 查找大目录
```
df -h --max-depth=2
```
3. 查找并mv文件到指定目录
```
find /logs/xxxx/ -mtime +30 -name "*.log" -exec mv {} /logs/tmp_backup/xxxx \; 

访问时间戳（atime）：表示最后一次访问文件的时间。
修改时间戳 (mtime)：这是文件内容最后一次修改的时间。
更改时间戳（ctime）：指上次更改与文件相关的某些元数据的时间。
```
4. 指定目录深度，查找并删除60天前的文件
```
find /logs/xxxx/appname -maxdepth 10 -name *.tar -mtime +60 -type f -delete
```
