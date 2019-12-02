---
layout: post
title: "多台linux服务器实现ssh免密互连"
date: 2019-11-08 18:00:00
author: "rpl"
header-img: 'img/post-bg-infinity.jpg'
header-mask:  0.4
catalog:      true
tags:
      - 原创
      - 技术
      - ssh
      - linux
      - python
      
---


### 一 单向无密码访问

A -> B (A免密访问B),  实验A的ip：192.168.0.21， B的ip：192.168.0.22

#### 1. 在服务器A生成密钥对
```shell
ssh-keygen -t rsa
```
之后如果没有特别需要，根据提示无脑操作，一直按回车键即可。
执行完后，会生成一个密钥图：
![3](/img/ssh/3.jpg)

在\~/.ssh目录下会生成两个文件**id_rsa.pub**和**id_rsa**,  其中id_rsa是私钥，id_rsa.pub是公钥。

```shell
cat ~/.ssh/id_rsa.pub
```

查看到的公钥，如下图所示
![3](/img/ssh/4.png)

#### 2. 上传公钥到B服务器

如果B还没有生成过ssh密钥的话，按上述1，将B服务器也生成自己的密钥
然后，将A的公钥上传的B的~/.ssh下，并改名为**authorized_keys**
```shell
scp ~/.ssh/id_rsa.pub roo@192.168.0.22:~/.ssh/authorized_keys
```
服务器B ~/.ssh/authorized_keys 文件夹内有 A的公钥，那么A就可以免密访问B了。


***
### 二 多台服务器互相免密登录

多台服务器相互无密码访问，与两台服务器单向无密码访问的原理是一样的，只不过由于是多台服务器之间相互无密码访问，不能象两台服务器无密码登录那样直接上传。

#### 1. 所有服务器生成ssh密钥
如上述步骤将每台服务器都执行 **ssh-keygen -t rsa** 生成密钥对

#### 2. 执行ssh-copy-id命令
如 A:192.168.0.21,  B:192.168.0.22,  C:192.168.0.23,

在服务器A上执行：
```shell
ssh-copy-id ~/.ssh/id_rsa.pub roo@192.168.0.21
ssh-copy-id ~/.ssh/id_rsa.pub roo@192.168.0.22
ssh-copy-id ~/.ssh/id_rsa.pub roo@192.168.0.23
```
以上可以将A的公钥自动添加到 A, B, C两台服务器的authorized_keys文件内，这样A就可以免密登录A,B,C了（没错，服务器 **A** ssh登录 **A** 也要这样才能实现免密登录）

同理，在服务器B， C分别上执行：
```shell
ssh-copy-id ~/.ssh/id_rsa.pub roo@192.168.0.21
ssh-copy-id ~/.ssh/id_rsa.pub roo@192.168.0.22
ssh-copy-id ~/.ssh/id_rsa.pub roo@192.168.0.23
```

这样A, B, C 三台机器就可以免密互连了。


查看 A,  B，C 任意一台机器内的authorized_keys文件，
```shell
cat ~/.ssh/authorized_keys
```

里面保存的是A, B， C的公钥串，因此**ssh无密码访问的原理是将本机的公钥串添加到远程服务器的authorized_keys文件内**。

***
### 三 实现超多服务器的免密互连

以上3台服务器的免密互连，我们就已经操作起来很麻烦了，要重复执行很多命令。

如果这时再加一台服务器 D，要实现A, B, C, D之间的免密互连，那么就需要全部更新 A, B, C, D的authori_keys文件。

如果是几十上百台服务器呢？为了一台新增的服务器能加入全部机器的互连，我们就要更新所有机器。单凭双手是不可能的，这时就需要脚本来批量更新了。

我们已经知道ssh免密访问的原理是authoried_keys文件里的公钥。因此，我们只需要将所有机器的公钥都收集起来写入一份新的authoried_keys文件内，然后将这份最新的authoried_keys上传到所有机器即可实现免密互连了。

以下脚本使用python实现，
```python
# coding=utf-8

"""
Author: rpl

date: 18-10-30 下午2:19
desc: multiple Linux servers realize SSH free and secure interconnection
"""

from SSH_API_Class import SSH
import os
import time

import shutil

SLAVE_USER = 'roo'
SLAVE_PASSWORD = 'xxxx'
SLAVE_PASSWORD2 = 'xxxx'


# 需要互连的机器ip
Host_list = [
        '192.168.0.10', '192.168.0.11', '192.168.0.12',
        '192.168.0.13', '192.168.0.14', '192.168.0.15',
        '192.168.0.16', '192.168.0.17', '192.168.0.18',
        '192.168.0.19', '192.168.0.20', '192.168.0.21',
        '192.168.0.22', '192.168.0.23', '192.168.0.24',
        '192.168.0.25', '192.168.0.26', '192.168.0.27',
        '192.168.0.28', '192.168.0.33', '192.168.0.34',
        '192.168.0.35', '192.168.0.36', '192.168.0.37',
        '192.168.0.38', '192.168.0.39', '192.168.0.40',
]


# 实现所有主机ssh互相连通
def ssh_interConnect():

    file_dir = os.path.join(os.path.dirname(__file__), 'authorized_keys')
    if os.path.exists(file_dir):
        os.remove(file_dir)
        time.sleep(0.01)

    f = open(file_dir, 'a')

    # 1. 循环获取每个主机的ssh公钥，添加到一个新的authorized_keys文件中
    for ip in Host_list:
        print(ip)
        if ip in ['192.168.0.21', '192.168.0.20']:  # 如果不同机器的密码不同,需要单独给相应的密码
            passwd = SLAVE_PASSWORD2
        else:
            passwd = SLAVE_PASSWORD

        ssh = SSH(ip=ip, username=SLAVE_USER, password=passwd)
        ssh.connect()

        cat_cmd = 'cat /home/roo/.ssh/id_rsa.pub'
        if cat_cmd != 'cat: /home/roo/.ssh/id_rsa.pub: 没有那个文件或目录':

            res = ssh.execute_cmd(cat_cmd)
            print(res)
            f.write(res)
            ssh.close()

    f.close()

    # 2.将新的authorized_keys文件替换掉旧的authorized文件
    for ip in Host_list:
        print(ip)
        if ip in ['192.168.0.20', '192.168.0.21']:
            password = SLAVE_PASSWORD2
        else:
            password = SLAVE_PASSWORD

        ssh = SSH(ip=ip, username='roo', password=password)
        ssh.connect()

        del_cmd = 'rm -r /home/roo/.ssh/authorized_keys'
        res = ssh.execute_cmd(del_cmd)
        print(res)

        ssh.sftp_put(file_dir, '/home/roo/.ssh/authorized_keys')
        print('%s is ok\n' % ip)
        ssh.close()


if __name__ == '__main__':
    ssh_interConnect()

```

需要注意的是脚本中导入的**SSH**类，是我封装实现ssh连接登录， 文件上传与下载， 以及文件夹的上传与下载等功能的一个类。使用SSH类的目的是**在无免密互连之前可以使用密码登录**，只有实现这个前提，才能批量访问服务器，获取公钥。[这篇文章是SSH类的实现，以及全部源码](https://littlerpl.me/2019/04/19/paramiko%E6%A8%A1%E5%9D%97/)。


当然,这个脚本不一定完全适合你,你只要弄清楚实现原理,就可以定制自己的脚本了。