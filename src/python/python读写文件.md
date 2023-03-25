# 读写文件

## open 函数使用

```
- 基础用法
open(str,mode,encodeing)
f = open('file1', 'a+')
f.wirte('this is test file1') # 只能是 str，记得用 str()、jsom.dumps() 方法转换下
print(f.read())
f.cloes()
print(f.closed)

- 进阶用法-会自动关闭文件
with open('file2', 'a+') af file:
	file.wirte('thisi is test file2') # 只能是 str，记得用 str()、jsom.dumps() 方法转换下
	fiLe.wirte('\n') # 多行时进行换行追加
	
- 文件读取
f.read() # 读取文件内容
f.readline() # 从文件中读取单行数据；字符串末尾保留换行符，多行时使用 for 遍历
for line in f:
		print(line,end='')
```

## open 函数读写模式

- mode
  - r : 表示文件只能读取(default)
  - w : 表示只能写入（现有同名文件会被覆盖）
  - a : 表示打开文件并追加内容，任何写入的数据会自动添加到文件末尾
  - r+ : 表示打开文件进行读写

