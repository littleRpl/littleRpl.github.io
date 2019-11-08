---
layout:       post
title:        "ssh登录阻塞在pledge: network的解决方法"
subtitle:     'systemctl restart systemd-logind'
date:         2019-11-08 11:30:00
author:       "Rpl"
header-img:   "img/fluc_code2.gif"
header-mask:  0.4
catalog:      true

tags:
  - 技术
  - linux
  - ssh
  - 原创

---


ssh 登录服务器是发生阻塞，大约会15-60秒才能登录成功。
 
 使用 **ssh -v** debug方式登录。可以查看登录过程是在哪一个环节阻塞的。
 ```shell
ssh -v 192.168.0.17
```
如下图可以看到是network这一块发生了阻塞，大约30秒后才登录成功。
![2](/img/ssh/2.png)

查资料，只找到这这样一段话：
```txt
This is probably an issue with D-Bus and systemd. If the dbus service is restarted for some reason, you will also need to restart systemd-logind.

You can check if this is the issue by opening the ssh daemon log (on Ubuntu it should be /var/log/auth.log) and check if it has these lines:


sshd[2721]: pam_systemd(sshd:session): Failed to create session: Connection timed out


If yes, just restart systemd-logind service:


systemctl restart systemd-logind


I had this same issue on CentOS 7, because the messagebus was restarted (which is how the D-Bus service is called on CentOS).
```

大意就是D-Bus服务由于某些原因被重启了，我们需要将systemd-logind也重启。(D-Bus是一个为应用程序间提供通信的消息总线系统, 用于进程之间的通信。)

***

#### 解决方法

Ubuntu上查看/var/log/auth.log的信息，(CentOs cat/var/log/secure）
```shell
cat /var/log/auth.log
```
果然在最后一条，看到了ssh回话创建失败
![1](/img/ssh/2.png)

重启systemd-logind
```shell
systemctl restart systemd-logind
```
重启后，ssh登录没有在卡顿了，非常有效。

***

#### 关于systemd-logind

systemd-logind是一个管理用户登录的系统服务，职责如下：


1. 持续跟踪用户的会话、进程、空闲状态。 这将在 user.slice 之下，为每个用户分配一个 slice 单元、为每个用户的当前会话分配一个 scope 单元。 同时，针对每个已登录的用户，将会启动一个专属的服务管理器(作为user@.service 模版的一个实例)。

2. 生成并管理"session ID"。如果启用了审计并且已经为一个会话设置了审计"session ID"， 那么该ID也将同时被用作"session ID"， 否则将会使用一个独立的会话计数器(也就是独立
 生成一个"session ID")。

3. 为用户的特权操作(例如关闭或休眠系统) 提供基于 polkit 的认证与授权

4. 为应用程序实现 阻止关闭/休眠系统的逻辑

5. 处理 硬件关机/休眠按钮的动作

6. 多席位(Multi-Seat)管理

7. 会话切换管理

8. 管理 用户对设备的访问

9. 在启动虚拟终端时 自动启动文本登录程序(agetty)， 并管理用户的运行时目录。


ssh登录时，systemd-logind负责为这个登录用户创建一个Session ID，并进行管理。我们主要就是阻塞在了这里。

值得一提的是systemd-login的用户会话是通过PAM模块注册的，而PAM模块pam_systemd中有一个desktop选项，因此，**如果你的服务器是桌面版的，重启systemd-logind，这个用户桌面上的一切程序都会被关闭（包括桌面上的开启的终端与程序）**


***

参考：

[1] [ssh connection takes forever to initiate, stuck at “pledge: network”](https://serverfault.com/questions/792486/ssh-connection-takes-forever-to-initiate-stuck-at-pledge-network)

[2] [systemd-logind.service 中文手册](http://www.jinbuguo.com/systemd/systemd-logind.service.html)

[3] [pam_systemd 中文手册](http://www.jinbuguo.com/systemd/pam_systemd.html#)