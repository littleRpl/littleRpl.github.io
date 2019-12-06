---
layout:       post
title:        "python multiprocessing.Manager.dict() 深层赋值无效"
date:         2019-12-06 16:00:00
author:       "Rpl"
header-img:   "img/python6.png"
header-mask:  0.5
catalog:      true

tags:
  - 原创
  - 技术
  - python

---

> 工作中踩到的一个坑，发现多进程之间共享字典变量的时候， 无法深层赋值。很有意思的一个现象，可能是python多进程间的一种变量保护机制。不过没有任何异常报错，就有点坑了。


### 一 共享变量dict

我们在ipython交互环境中演示:

```python
>>> import multiprocessing
>>> m = multiprocessing.Manager()

>>> d = m.dict() # 创建共享字典变量
>>> d
<DictProxy object, typeid 'dict' at 0x7fe211518d68>
```

d['a']赋值常量
```python
>>> d['a'] = 1  # 赋值常量
>>> d['a']
1
```
d['b']赋值可变变量

```python
>>> d['b'] = [1,2,3]  
>>> d['b']
[1, 2, 3]
```

给d['b']深层赋值，可以看到append失败，d['b']的值没有改变
```python
>>> d['b'].append(4) # 深层赋值
>>> d['b']
[1, 2, 3]  # 没有改变，深层赋值失败
```

将d['b']赋值给x1， 查看d['b']的id和x1的id，可以发现d['b']的id与x1的id不一样，说明x1 = d['b']是deepcopy，而不是简单的引用

```python
>>> x1 = d['b']  
[1, 2, 3]
>>> id(d['b'])  
140691592776072

>>> id(x1)  
140691592775944
```

查看d['b']的类型，与x1一样，是普通的list。x1追加5,成功。d['b']再次尝试深层赋值失败， d['b']与x1都是list，赋值结果却大不一样
```python
>>> type(d['b'])
<class 'list'>

>>> type(x1)
<class 'list'>

>>> x1.append(5)
>>> x1
[1, 2, 3, 5]

>>> d['b'].append(5) 
>>> d['b']
[1, 2, 3]
```
***

### 二 共享变量list
继续尝试list类型的共享变量， 可以看到同样无法深层赋值
```python
>>> l = m.list()
>>> l
<ListProxy object, typeid 'list' at 0x7ff54f5571d0>


>>> l.append(1)
>>> l.append(2)
>>> l.append(x1)
>>> for i in l:
...     print(i)
... 
1
2
[1, 2, 3, 5]

>>> l[2].append(6)  # 深层赋值失败
>>> l[2]
[1, 2, 3, 5]

```

### 三 共享变量之间深层赋值

突然想到多进程间的list， dict，已经与普通的dict， list不是一种类型了。如果我们在共享变量上赋值普通变量，python多进程间通信肯定要控制变量的改变。也就不会允许在共享变量中对普通变量深层赋值。

尝试将list共享变量l,赋值给dict共享变量d, 可以看到赋值成功
```python
d['c'] = l
>>> d['c'][2]
[1, 2, 3, 5]

>>> for i in d['c']:
...     print(i)
... 
1
2
[1, 2, 3, 5]

>>> for i in l:
...     print(i)
... 
1
2
[1, 2, 3, 5]

```

看到虽然赋值成功了， 但d['c']与l并不是同一个值，id与内存地址都不同
```python
>>> d['c']
<ListProxy object, typeid 'list' at 0x7ff54f557f28>
>>> l
<ListProxy object, typeid 'list' at 0x7ff54f5571d0>

>>> id(d['c'])
140691574718136
>>> id(l)
140691574714832
```


继续深层赋值，我们看到给d赋值， l的值也改变了，同样l赋值，d的值也同步变化，深层赋值成功了。

```python
>>> d.append(6)
>>> for i in l:
...     print(i)
... 
1
2
[1, 2, 3, 5]
6
7

>>> l.append(7)
>>> for i in d['c']:
...     print(i)
... 
1
2
[1, 2, 3, 5]
6
7

```

### 四 结论

**Manager创建的多进程共享变量，所赋值的普通变量(list, dict)都是不可在改变，如果想赋值可变变量，必须使用manager类型的变量（manager.list, manager.dict等**
