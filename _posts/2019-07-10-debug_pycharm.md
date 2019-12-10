---
layout:       post
title:        "PyCharm Debug远程服务器程序"
date:         2019-7-10 14:30:00
author:       "Rpl"

# header-style:   text
header-img:   "img/python6.png"
header-mask:  0.5
catalog:      true

multilingual: false

tags:
  - 原创
  - 技术
  - python
  - pycharm

---

### 一 安装pydevd包
```shell
pip install pydevd  
```
 
### 二 pychram配置远程调试

##### 1. pycharm 中打开 Run --> Edit Configurations... 
![1](/img/pycharm/1.png)

##### 2. 添加一个新的debug配置
![2](/img/pycharm/2.png)

##### 3. 具体配置如下图所示
![3](/img/pycharm/3.png)

##### 4. Run -- > debug 开启远程debug服务 
![4](/img/pycharm/4.png)

开启后开到如下信息，表示配置成功
![5](/img/pycharm/5.png)

在远程需要执行的代码头加入:
```python
import pydevd
pydevd.settrace('192.168.1.113', port=19931, stdoutToServer=True, stderrToServer=True) 
```
这两句代码要放在开头， 程序执行到时，便会与本地开启的远程debug服务建立连接，开始远程debug，如下图
![6](/img/pycharm/6.png)

点击下载后 ，便可以同步调试了。

