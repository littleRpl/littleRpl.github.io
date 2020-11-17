---
layout: post
title:  'ssh密钥配合多个github账号'
subtitle: ''
date: 2020-01-15 11:06:29
author: 'rpl'
header-img: ''
header-mask:  0.65
multilingual: false
catalog: true
tags:
      - 原创
      - ssh
      - git
---

> 同一台电脑的同一个ssh共钥无法配置到多个github账号。例如公司的电脑ssh公钥配置到公司的github账号后，无法在使用同一个公钥配置个人的github账号。这时候需要生成多个ssh密钥，分别配置给不同的github账户

### 一 生成新的ssh密钥

```shell
ssh-keygen -t rsa -f "new_name"
```

<code>-f</code> 给新生成的密钥自定义命名，否则生成的是默认密钥：id_rsa与id_rsa.pub 它会覆盖掉现有的默认密钥
生成的密钥文件如下图：
![密钥图1](/img/ssh-keygen-github/ssh-keygen-1.png)

### 二 复制新的公钥到github账号
这一步登陆个人的giuhub账号，将新生成的公钥配置到guthub上即可。

### 三 配置~/.ssh/config 文件
如果没有config文件，就在~/.ssh目录创建config文件， 该文件用于配置ssh私钥对应的服务器

```vim
vim config
```
以下为详细的config配置内容

```vim
# key1 公司的github账号
# github
Host github.com
HostName github.com
PreferredAuthentications publickey
IdentityFile ~/.ssh/id-rsa

# key2 我个人的guthub账号， xxx.github.com. me是自定义的
Host me.github.com
HostName github.com
PreferredAuthentications publickey
IdentityFile ~/.ssh/littlerpl.git
```

### 四 测试ssh到github服务器的连接

```shell
ssh -T git@me.github.com
ssh -T git@github.com 
```
如下图，说明我们的配置成功，到此就可以结束了。
![密钥图1](/img/ssh-keygen-github/ssh-T-2.png)

如果出现如下：
```shell
Permission denied (publickey)
```

需要先查看ssh权限
##### 1、查看系统ssh-key代理,执行如下命令
```shell
ssh-add -l
````
以上命令如果输出<code>The agent has no identities.</code> 则表示没有代理。

如果系统有代理，可以执行下面的命令清除代理:
```shell
ssh-add -D
```

##### 2、然后依次将不同的ssh添加代理，执行命令如下：
```shell
ssh-add ~/.ssh/id_rsa
ssh-add ~/.ssh/littlerpl.git 
```
littlerpl.git是个人密钥文件， 之后再次进行ssh测试即可.

---

### 五 注意事项
在第三步 配置完成后，在连接非默认账号的github仓库时，远程的地址要对应的作出修改.
配置了<code>me.github.com</code>用作个人的git我们就不能在用git@github了，要是用<code>git@me.github.com</code>
例：
```shell
git clone git@me.github.com:账户名/仓库  
git remote add test git@me.github.com/test.git  添加远程仓库
```

