---
layout:       post
title:        "Linux 安装 MooseFS 分布式文件系统"
date:         2019-08-07 15:30:00
author:       "Rpl"
header-img:   "img/moosefs/bg2.png"
header-mask:  0.4
catalog:      true

tags:
  - 技术
  - linux
  - moosefs
  - 原创

---

### 前言
本篇文章，我们将安装 MooseFS 的 MasterServer（主服务器）， ChunkServer（数据服务器），MooseFS CGI（监控界面接口）， MooseFS CLI（命令行接口）， Metalogger（日志服务器）和 MooseFS client（客户端）

就本文，我们假设所有的机器使用以下ip:

* Master Server:
    * 192.168.0.1
* Metalogger: 
    * 192.168.0.2
* Chunkserver:
    * 192.168.0.11
    * 192.168.0.12
    * 192.168.0.13
 * Client:
    * 192.168.0.2x


注意：本文所有操作都是以root身份运行的，执行下面命令，切换到root：
```shell
sudo su -
```

---
### 一 环境配置、安装包准备
在安装之前我们需要做一些准备工作。
##### 1. 配置DNS
在开始安装 MooseFS 之前，你的服务器集群要有正常的DNS。MooseFS要与多台主服务器之间正常工作，就需要 DNS 来解析。如果所有机器在一个段内，其实不用特别注意DNS配置这一块，这一步可以跳过，安装 MooseFS 失败的话，可以在回头来看看是否是 DNS 的问题。具体 DNS 的配置[点击这个链接](https://moosefs.com/blog/how-to-set-up-a-dns-server-for-moosefs-on-debian-ubuntu/)

##### 2. 准备适合的MooseFS安装版本
本文使用的 Ubuntu，这里只给出Ubuntu版本的 MooseFS 下载步骤。其他Linux版本可以[点击这里](https://moosefs.com/download/)查看具体的安装步骤。

首先，我们查看Ubuntu的发行版本：
```shell
lsb_release -a
```
结果为：
```shell
No LSB modules are available.
Distributor ID:	Ubuntu
Description:	Ubuntu 17.10
Release:	17.10
Codename:	artful

```
注意记下 Release：17.10  codename：artful，[点击此链接](http://ppa.moosefs.com/moosefs-3/apt/ubuntu/)查看对应的 MooseFS 发行包。

![1](/img/moosefs/1.png)

会发现目录中根本没有 codename叫 artful的版本 哭唧唧。

这个是因为Ubuntu17是非长期支持的版本号， ubuntu 每两年的 4 月份，都会推出一个长期支持版本（LTS），其支持期长达五年，而非 LTS 版本的支持期通常只有半年。

那这样我们就向前用最近的长期版本 16.04 Xenial，所以我们需要的版本是xenial


接下来的安装步骤：

添加moosefs.key:
```shell
wget -O - https://ppa.moosefs.com/moosefs.key | apt-key add -
```

配置版本库列表文件，这里我们是 <code>xenial</code>， 如果你是其他版本，请将下面的 <code>xenial</code> 替换成你需要的版本，例如：<code>bionic</code>

```shell
echo "deb http://ppa.moosefs.com/moosefs-3/apt/ubuntu/xenial xenial main" > /etc/apt/sources.list.d/moosefs.list
```

接着运行：
```shell
apt run
```

到此，准备工作结束，我们开始 MooseFS 的安装与配置工作

---
### 二 安装Master Server

在主服务器上安装 Master Server：
```shell
apt install moosefs-master
```
示例配置文件将在/etc/mfs中创建，扩展名为  \*.sample (MooseFS 3.0+)或  \*.dist (MooseFS 2.0)。使用这些文件作为您的目标配置文件:
```shell
cd /etc/mfs 
cp mfsmaster.cfg.sample mfsmaster.cfg 
cp mfsexports.cfg.sample mfsexports.cfg
```
如果要改变配置文件，需要将对应的行取消掉注释，然后设置想要的值就可以了。对于已经注释掉的行，系统将使用默认内建的值，即当前被注释的行内的值。

mfsmaster.cfg 是Master Server的配置文件，可以通过 **man mfsmaster.cfg** 找到更多的信息。

mfsexports.cfg 文件指定哪台用户主机可以挂载文件系统，以及挂载的权限。

例如：我们指定只有 为192.168.0.2x ip段的主机 可以挂载整个MooseFS文件系统（/) 并拥有可读可写权限。将没有注释掉的第一行的 * 改为：
```shell
192.168.0.2.0/24   /   rw,alldirs,maproot=0
```
如果想要Master Server 开机自启动：
```shell
systemctl enable moosefs-master.service
```

现在我们可以开启 Master Server
```shell
systemctl start moosefs-master.service
```
查看Master Server开启状态：
```shell
systemctl status moosefs-master.service
```


如果要安装第二台，第三台。。。Master Server 只需要重复以上步骤即可。

---
### 三 安装MooseFS CGI 和 CGI Server 
MooseFS CGI监控界面用于让用户观察和分析当前MooseFS的状态(如下面的截图所示):

![2](/img/moosefs/2.png)
![6](/img/moosefs/6.png)

建议所有的主服务器都安装MooseFS CGI 和 CGI服务器
```shell
apt install moosefs-cgiserv
apt install moosefs-cgi
```

如果想要MooseFS CGI 开机自启动：
```shell
systemctl enable moosefs-cgiserv.service
```

现在我们可以开启 MooseFS CGI Server
```shell
systemctl start moosefs-cgiserv.service
```
查看MooseFS CGI开启状态：
```shell
systemctl status moosefs-cgiserv.service
```
现在我们能够通过 http://192.168.0.1:9425 查看 CGI的监控信息了(192.168.0.1 是MooseFS Server的主服务器， 9425是监控端口号)

当然数据服务器我们现在还没安装，但是能看到web监控界面，就表示我们已经成功一大半了。

---
### 四 安装MooseFS CLI
MooseFS CLI 是 MooseFS 命令行接口工具，可以使用它在命令行里查看 MooseFS 的各种状态信息。这个工具有许多选项可以允许你查看所有能在 MooseFS CGI 里看到的信息，因此可以将它使用在脚本里。


您可以通过调用-h或-help 来列出所有选项，或者在[https://moosefs.com/manpages/mfscli.html](https://moosefs.com/manpages/mfscli.html)中检查它。例如 mfscli with -SIN 选项将显示基本信息，类似于 CGI 中的“信息”选项卡。

建议将它安装到所有的主服务器。
```shell
apt install moosefs-cli
```

---
### 五 安装 Metadata backup servers（Metaloggers）
 强烈建议至少在一台服务器上安装 Metalogger。因为它会实时备份主服务器 Master Server 的信息。如果主服务器挂掉了， Metalogger 服务器会临时接管M aster Server 保证 MooseFS 能正常工作，保证数据不会丢失。如果没有安装metalogger日志服务器，等到主服务器挂了，数据就JJ了。 如果服务器多，甚至可以多装几台Metalogger服务器，这毕竟是个容灾。


使用默认设置安装和配置 Metalogger
```shell
apt install moosefs-metalogger
cd /etc/mfs
cp mfsmetalogger.cfg.sample mfsmetalogger.cfg
```
对于我们今天的测试安装，可以保持 mfsmetalogger.cfg 不变，但是如果你的 Master Server 不一样，你可以在 mfsmelogger.cfg 文件中将 MASRER_HOST 这一项的默认名称 mfsmaster 更改为你需要配置的名称，并取消注释。

关于 mfsmetalogger.cfg 的更多信息可以使用 man mfsmetalogger.cfg 查看。


如果想要 Metalogger 开机自启动：
```shell
systemctl enable moosefs-metalogger.service
```

现在我们可以开启 Metalogger
```shell
systemctl start moosefs-metalogger.service
```
查看 Metalogger 开启状态：
```shell
systemctl status moosefs-metalogger.service
```

---
### 六 安装 Chunkservers

在需要安装 Chunkserver 的机器上，使用一下命名安装
```shell
apt install moosefs-chunkserver
```
准备 Chunkserver 的配置文件
```shell
cd /etc/mfs 
cp mfschunkserver.cfg.sample mfschunkserver.cfg 
cp mfshdd.cfg.sample mfshdd.cfg
```
和安装 Metalogger 时一样，对于我们今天的测试安装，可以保持 mfschunkserver.cfg  不变，但是如果你的 Master Server 不一样，你需要在 mfschunkserver.cfg  文件中将MASRER_HOST 这一项的默认名称 mfsmaster 更改为你需要配置的名称，并取消注释。

关于 mfschunkserver.cfg  的更多信息可以使用 man mfschunkserver.cfg  查看。

建议将整块磁盘专门用于 MooseFS， 这对于磁盘的空间空间管理是需要的。
现在开始进行磁盘的划分，假设我们的挂载在/dev/sdb 和 /dev/sdc 这两块磁盘分配作为 Moosef 的存储块。首先，创建分区表，并分区磁盘：
```shell
parted --align optimal /dev/sdb
(parted) mklabel gpt 
(parted) mkpart mfschunks1 0% 100% 
(parted) q
```
```shell
parted --align optimal /dev/sdc
(parted) mklabel gpt 
(parted) mkpart mfschunks2 0% 100% 
(parted) q
```
安装 XFS Progs：
```shell
apt install xfsprogs
```
然后用XFS文件系统格式化新创建的分区：
```shell
mkfs.xfs /dev/sdb1 
mkfs.xfs /dev/sdc1
```
如果您有4k物理扇区大小的磁盘(大多数2和4 TiB 现代 hdd 都有4k物理扇区大小)，使用下面的命令进行格式化：
```shell
mkfs.xfs -s size=4k /dev/sdb1 
mkfs.xfs -s size=4k /dev/sdc1
```
然后将这个创建好的磁盘，添加到/etc/fstab 文件：
```shell
/dev/sdb1    /mnt/mfschunks1    xfs    defaults    0 0 
/dev/sdc1    /mnt/mfschunks2    xfs    defaults    0 0
```
接着， 创建新的空目录， 并将刚创建的分区挂载到上面
```shell
mkdir /mnt/mfschunks1 
mkdir /mnt/mfschunks2


mount /mnt/mfschunks1 
mount /mnt/mfschunks2
```
更改挂载点的所有权和访问权限，让 MooseFS Chunkserver 写入它们:
```shell
chown mfs:mfs /mnt/mfschunks1 
chown mfs:mfs /mnt/mfschunks2 

chmod 770 /mnt/mfschunks1 
chmod 770 /mnt/mfschunks2
```
此时，在 mfshdd.cfg 文件末尾输入挂载点:
```shell
/mnt/mfschunks1 
/mnt/mfschunks2
```

如果想要 Chunkservers 开机自启动：
```shell
systemctl enable moosefs-chunkserver.service
```

现在我们可以开启 Chunkservers
```shell
systemctl start moosefs-chunkserver.service
```
查看 Chunkservers 开启状态：
```shell
systemctl status moosefs-chunkserver.service
```

在其他需要安装 Chunkserver 的机器上重复以上步骤即可完成安装。

此时我们已经完成了Chunkserver的安装，通过 http://192.168.0.1:9425 打开CGI监视界面，可以看到包括 Master Server， Metalogger，以及Chunkserver的所有信息。

---
### 七 用户机安装 Client

为了安装基于 MooseFS 的文件系统，用户机必须有 FUSE 包(至少在2.6版本中，建议≥2.7.2)。如果不存在，安装：
```shell
apt install fuse libfuse2
```

然后再以相同的方式安装 moosefs-client:
```shell
apt install moosefs-client
```

假设,您将系统挂载到客户机上的/mnt/mfs文件夹中:
```shell
mkdir -p /mnt/mfs 
mfsmount /mnt/mfs -H mfsmaster
```
现在，我们通过 df -h |grep mfs 查看是否挂载成功：
```shell
df -h |grep mfs
```

挂载信息如下：
```shell
/dev/sdb       2.0G  69M  1.9G  4%  /mnt/mfschunks1 
/dev/sdc       2.0G  69M  1.9G  4%  /mnt/mfschunks2 
mfsmaster:9421 3.2G  0    3.2G  0%  /mnt/mf
```

在其他需要安装 moosefs-clent 的机器上重复以上步骤即可完成安装。

到此，MooseFS 文件系统，已经在集群上安装成功了。