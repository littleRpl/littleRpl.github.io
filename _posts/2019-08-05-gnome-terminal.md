---
layout:       post
title:        "gnome-terminal 终端复用"
date:         2019-08-5 17:00:00
author:       "Rpl"
header-img:   "img/gnome/16.png"
header-mask:  0.7
catalog:      true

tags:
  - 技术
  - linux
  - gnome-terminal
  - 原创
---


#### 前言
>gnome-terminal终端是ubuntu系统自带的终端。
有时候我们想要进行一些自动化工作，希望脚本能自动开启terminal终端运行，或者复用开启多个终端窗口等等，稍微了解一些gnome-terminal的用法，会使工作更加的高效

---

#### 一  gnome-terminal基础用法

1. 在终端中 输出 gnome-terminal，就会自动弹出一个新的终端

2. Ctrl + Alt + Shift键，也会弹出一个新的终端

---

#### 二  gnome-terminal + 命令

```shell
gnome-terminal -e, --command   # 使用-e 或-- 后面跟命令
```
值得注意的是，命令执行完或者遇到错误后，这个新终端也会闪退，如果执行的是例如：ls 等非常快的命令，可能根本就看不到终端弹出。

尤其是当我们执行一个脚本时，如果遇到错误闪退，根本就看不到错误原因，很麻烦。可以如下图所示， 在bash中 加上**exec bash**。这样新终端在执行完命令后也不会退出了。
如下图,退出了python环境,终端没有闪退
![11](/img/gnome/11.png)

---


#### 三  gnome-terminal 多窗口、多标签

--window: 打开一个新窗口

--tab: 在最后一个窗口中打开一个新标签页

```shell
gnome-terminal --window
```
![1](/img/gnome/1.png)


```shell
gnome-teminal  --tab
```
![2](/img/gnome/2.png)

可以看出 一个window 和一个 tab是没啥区别的， 如果需要多个窗口或标签，可以 --window --window ... 或 --tab --tab ... 复写。

![3](/img/gnome/3.png)
![4](/img/gnome/4.png)

注意：--window 是生成多个新的窗口 --tab是在同一个窗口中生成多个标签页。

---
 
#### 四  gonme-terminal 多窗口/标签页 + 执行命令

###### 1. 打开两个标签页， 每个标签页都执行python命令,  

```shell
gnome-terminal -e python3 --tab --tab
```

**-e command 在所有窗口或标签页之前执行时，表示为全部窗口或标签页的默认设置**  结果如下图俩个终端标签页打开时都默认执行了python3
![6](/img/gnome/6.png)

也可以在不同的标签页里执行不同的命令
```shell
gnome-terminal  --tab -e python3 --tab -e python3
```

###### 2. ssh连接远程服务器，cd到自定义目录，执行python3

```shell
gnome-terminal  -e 'ssh -t 192.168.0.10 "cd /home/roo/yn;python3;exec bash"' 
```
注意: ssh -t不能省略. -t 参数显式的告诉 ssh，我们需要一个 TTY 远程 shell 进行交互！添加 -t 参数后，ssh 会保持登录状态，直到你退出需要交互的命令。
![12](/img/gnome/12.png)

###### 3. 复合命令：打开多个标签页并给每个标签页命名， ssh连接到不同的服务器，cd到自定义目录，执行python3

```shell
gnome-terminal  --tab -t '21' -e 'ssh -t 192.168.0.21 "cd /home/roo/yn;python3;exec bash"'   --tab -t '11' -e 'ssh -t 192.168.0.11 "cd /home/roo/yn;python3;exec bash"'  --tab -t '12' -e 'ssh -t 192.168.0.12 "cd /home/roo/yn;python3;exec bash"'  --tab -t '13' -e 'ssh -t 192.168.0.13 "cd /home/roo/yn;python3;exec bash"'  
```
结果如下图：
![13](/img/gnome/13.png)

---


#### 五  其他

###### 1. 自定义命名标签页 -t 
```shell
gnome-terminal -e python3 --tab 1 --tab 2
```
![10](/img/gnome/10.png)

###### 2. 指定终端的的默认工作目录 --working-directory

```shell
gnome-terminal --working-directory=/home/roo/桌面
```
![8](/img/gnome/8.png)

###### 3. 终端缩放 --zoom

```shell
gnome-terminal --working-directory=/home/roo/桌面  --zoom=2
gnome-terminal --working-directory=/home/roo/桌面  --zoom=1.5
gnome-terminal --working-directory=/home/roo/桌面  --zoom=0.5
```
![9](/img/gnome/9.png)

###### 4. 其他配置 
gnome-terminal 还有一些关于gtk的配置和使用，这里没有给出，具体可以使用 --help查看，这里给出一个全部的help信息

```shell
gnome-terminal --help-all
```
![5](/img/gnome/5.png)

