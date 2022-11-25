
# 2022-11-24 学习循环中 break、continue 语句及 else 子句 用法

# break 语句，可以用于跳出最近的 for / while 循环
# else，当循环语句遍历所有元素后，或者条件为假时，执行 else 子句；
# break，语句终止循环，不执行 else 子句

# 示例如下：
print('学习1： 循环的 else 语句在未运行 break 时执行，和 try ... else 类似，它是在子句'
      '未触发异常时执行')
for n in range(2, 10):
    for x in range(2, n):
        if n % x == 0:
            print(n, 'equals', x, '*', n // x)
            break
    else:
        print(n, 'is a prime number')

print('')
print('学习2： 利用 else 子句在循环最后打印结束语句')
test = ['test1', 'test2', 'test3']
for test_index in range(0, len(test)):
    print(test[test_index])
else:
    print('循环结束！！！')

print('')
print('学习3： continue 子句, 进行匹配并打印出不匹配的')

for  n in range(2, 8):
    if n == 2:
        print(n, '= 2')
        continue
    print(n)


print('')
print('学习4： pass 子句, 不执行任何操作，仅是语法需要这个语句, 相当于占位符')
number = [1, 2, 3, 4, 10]

for n in range(0, len(number)):
    if number[n] != 10:
        pass
    else:
        print(number[n])


print('')
print('学习5：学习定义一个遍历 list 的函数. def 定义函数，后面跟函数名及()内跟形参列表，'
      '且必须缩进')

number = [1, 2, 3, 4]
name = ['test1', 'test2', 'test3']


def traverse(list):
    for x in list:
        print(x)


traverse(name)
traverse(number)


print('')
print('学习6： 函数中的文档字符串、注解')


def docstring():
    """什么时文档字符串.

    1. 第一行，应为对象用途的简短摘要，不要在这里显示说明对象名或类型，应以大写字母开头，以 .
        结尾
    2. 多行时，第二行为空白行，在视觉上将摘要与其余描述分开。后面的行可以包含若干段落，描述对
        象的调用约定，副作用等
    3. python 不会删除多行文档字符串的缩进
    """


print(docstring.__doc__)
print(docstring.__name__)

