---
layout:  post
title:  "DataFrame.columns 的重命名"
subtitle:  '介绍DataFrame数据的columns的重命名,以及踩过的坑.'
date:  2019-08-28 12:00:00
author:  "rpl"
header-style:  "text"
catalog: true
tags:
    - 原创
    - 技术
    - python
    - pandas
    
---


# 前言

首先，我们创建一个5行4列的DataFrame数据作为示例，进行演示

```python
import pandas as pd
import numpy as np

df = pd.DataFrame(data=np.arange(20).reshape(5,4), columns=['a', 'b', 'c', 'd'])

df
     a      b     c    d
0    0     1     2     3
1    4     5     6     7
2    8     9    10   11
3   12   13    14   15
4   16   17    18   19

```

---

#  一 部分列重命名

有时候，我们只需要将部分列的列名重命名。可以使用字典的方式，更改指定的列名。

```python
df.rename(columns={'a': 'A'})

    A   b   c   d
0   0   1   2   3
1   4   5   6   7
2   8   9  10  11
3  12  13  14  15
4  16  17  18  19
```
没有指定inplace=True， df本身的列名并没有改变。

```python
df
    a   b   c   d
0   0   1   2   3
1   4   5   6   7
2   8   9  10  11
3  12  13  14  15
4  16  17  18  19
```
这种情况下比较适合不变原有数据，通过赋值对新数据列改名，如下：

```python
df2 = df.rename(columns={'a': 'A'})
df2
    A   b   c   d
0   0   1   2   3
1   4   5   6   7
2   8   9  10  11
3  12  13  14  15
4  16  17  18  19
```

如果我们指定inplace=True，则会改变原始数据
```python
df.rename(columns={'a': 'A', 'c': 'C', 'd': 'D'}, inplace=True)
df
    A   b   C   D
0   0   1   2   3
1   4   5   6   7
2   8   9  10  11
3  12  13  14  15
4  16  17  18  19
```

---

# 二 全部列重命名

df.columns = new_columns, new_coumns 可以是列表或元组， 但新旧列名的长度必须一致，否者会不匹配报错。这种改变方式是直接改变了原始数据。

```python
df.columns = ['a1', 'b1', 'c1', 'd1']
df
   a1  b1  c1  d1
0   0   1   2   3
1   4   5   6   7
2   8   9  10  11
3  12  13  14  15
4  16  17  18  19
```

---


# 三 str 批量修改列名

将列名'a1', 'b1'...  批量改为'a2', 'b2’...

```python
df.columns = df.columns.str.replace('1', '2')
df
   a2  b2  c2  d2
0   0   1   2   3
1   4   5   6   7
2   8   9  10  11
3  12  13  14  15
4  16  17  18  19
```
其实str的原理和第二章是一样的，不同的是，我们对列名进行了字符串的操作。

---

# 四 读取csv文件重命名

names = new_columns， 在读取文件的时候直接重命名列名。

```python
df = pd.read_csv('xxx.csv', names=new_columns, header=0)
```

---

# 后记

这里讲一个之前在读csv文件， 重命名时，踩到的一个小坑。

以前读csv文件，读到重命名时，我都是先读文件，转成DataFrame之后再重命名的。

```python
df = pd.read_csv('xxx.csv')
df.columns = new_columns
```
这样做，大部分情况下不会有什么问题，直到有天我读的是无列名的csv文件。pandas默认将第一行数据作为了列名。这时我再进行df.columns = new_columns 时，第一行数据就会因为作为列名，被new_columns替换了。这就导致我第一行数据白白丢失了（想哭）。今天写这篇博客的目的。也就是想记住这个坑。

pandas的read_csv() 函数，其实还踩过很多坑，里面有很多参数，我会在之后的博客里详解read_csv()的各个参数的用法。