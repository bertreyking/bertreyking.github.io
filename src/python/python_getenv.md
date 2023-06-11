# Python 获取环境变量 （OpenAI）

在Python中，你可以使用不同的方法来获取环境变量。下面是几种常见的方法：

- 使用`os`模块：`os`模块提供了一种获取环境变量的简单方法。你可以使用`os.environ`字典来获取当前进程的所有环境变量，并使用变量名作为键来访问相应的值。例如：

```python
import os

# 获取单个环境变量
value = os.environ.get('VAR_NAME')

# 打印所有环境变量
for var, value in os.environ.items():
    print(f'{var}: {value}')
```

- 使用`os.getenv()`函数：`os`模块还提供了`getenv()`函数，它可以直接获取指定环境变量的值。例如：

```python
import os

value = os.getenv('VAR_NAME')
```

- 使用`environ`模块：`environ`模块是`os`模块的一部分，可以直接从中导入。它提供了与`os.environ`相同的功能。例如：

```python
from os import environ

value = environ.get('VAR_NAME')
```

这些方法都可以根据你的需求来选择使用。无论使用哪种方法，确保在访问环境变量之前，首先了解环境变量的存在与否，以及其命名方式。

