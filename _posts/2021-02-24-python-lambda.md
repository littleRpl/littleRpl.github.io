---
layout: post
title:  "python lambda在列表推导式中的闭包问题"
subtitle: "分享一道有关于lambda与闭包的面试题"
date: 2021-02-24 15:14:54
author: "rpl"
header-img: "img/python5.png"
header-mask:  0.65
multilingual: false
catalog: true
tags:
      - 原创
---


## 一、一道面试题

给出以下代码的pirnt结果
```python
li = [lambda : x for x in range(10)]
ret = li[0]()

print(ret)
```
答案是9，出乎意料的是li内的所有匿名函数的结果都是9。

![image-20210224144611247](/img/python-lambda/image-20210224144611247.png)

***

## 二、闭包产生的影响

Python 闭包的后期绑定导致的 late binding，这意味着在 <code>闭包中的变量是在内部函数被调用的时候被查找</code>。所以结果是，当任何 li 内的匿名函数被调用时，x的值是在它被调用时的周围作用域中查找，无论哪个lambda函数被调用，for 循环都已经完成了，x 最后的值是9，因此，每个lambda函数返回的值都是 9。



我们从下图中能更好的理解这个列表推导式

![image-20210224142051162](/img/python-lambda/image-20210224142051162.png)
整体上li是一个`[  xxx for x in range(10) ]` 列表推导式，重点是这个<code>xxx</code> 又是一个匿名函数表达式`lambda :x`。 这个函数在调用时会返回x的值。

因此li表达式的第一步是生成了10个匿名表达式， 在这一步循环是已经结束了的， 循环的目的是生成10个匿名函数。如图：

![image-20210224142701879](/img/python-lambda/image-20210224142701879.png)

但是匿名函数的内部变量又使用了循环产生的变量x,   x与匿名函数形成了一个闭包。  循环结束x的值只能是9，所以在每个函数调用时，结果都是9。

通过以下等同的代码，我们可以明确的看出闭包的形成：

```
li = list()
for x in range(10):
	def test():
		return x
	li.append(test)
```



此外，我们可以通过变量赋值的方式，保存每次循环时x的值，就可以得到正确的结果了：

```python
li = [lambda j=x: j for x in range(10)]
```

![image-20210224144346811](/img/python-lambda/image-20210224144346811.png)


***

 ## 三、lambda 的简单应用

1. 什么是 lambda？
	匿名函数表达式，目的是简略函数的定义，使用简单的一行代码就实现一个函数功能。如果超过2行代码，就不要使用lambda了。lambda表达式的意义就是简洁明了。过于复杂不利于代码的可读性。
	
2. 无参数的lambda， 上例就是一个无参的匿名函数。

3. 带参数的lambda
  lambda x: x+1 这个匿名函数的功能是返回每次传入的参数+1，如下图：

  ![image-20210224145452529](/img/python-lambda/image-20210224145452529.png)

  
4. 带表达式的lambda
  上例`li = [lambda j=x: j for x in range(10)]` 就是一个带有表达式的匿名函数。但是匿名函数不要过于复杂化。大多时候太复杂话不利于代码的可读性，同时又容易出现不易察觉bug。所以炫技要适当，不然就容易翻车了，还是老老实实写简单易懂的代码吧。



