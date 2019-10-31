---
layout:       post
title:        "moosefs使用辅助文件系统，恢复文件"
date:         2019-10-31 11:00:00
author:       "Rpl"
header-img:   "img/moosefs/bg2.png"
header-mask:  0.4
catalog:      true

tags:
  - 技术
  - linux
  - python
  - moosefs
  - 原创

---


moosefs文件系统，client客户端误删除或丢失的文件是可以通过moosefs的文件辅助系统恢复的。

# 一 查看moosefs垃圾回收时间
回收时间是一个文件被删除后还能保留的时间， 单位是秒， 如果被删除的文件过了回收时间，就没法再恢复了，所以第一点要先查看moosefs的文件回收时间

在客服端使用**mfsgettrashtime**命令，查看moosefs文件的回收清空时间
![6](/img/moosefs2/6.png)

上图mfs文件的回收时间是 86400秒，也就是24小时。 mfsdata是我的mfs挂载目录。

如果你想自己设置回收时间的话，使用**mfssettrashtime  \[time] [dir]** 


***
# 二 挂载moosefs辅助文件系统 

moosefs的辅助文件系统，可以看成是你客户端的mfs回收站（以下简称mfs回收站）可以通过挂载这个文件系统，恢复文件。

不同客户端里的mfs回收站里的内容是不一样的。比如你在10机器上删除的文件，只能通过10上的mfs回收站恢复，11上的mfs回收站只包含本机上删除的文件，10上删除的只能去10恢复。

开始挂载moosefs回收站, 和挂载moosefs文件系统类似。
```shell
mkdir /home/roo/mfsmeta  (新建一个空目录作为mfs回收站)

mfsmount -m /home/roo/mfsmeta -H 192.168.0.21  (192.168.0.21 是我的moosfs master主机IP)

cd /home/roo/mfsmeta 
```
进入到mfsmeta之后，查看mfsmeta的文件结构。如图：
![7](/img/moosefs2/7.png)

你也可以使用tree查看，因为我删除的文件太多了，这里就不放tree目录结构图了。

如果你在查看文件的时候,报了如下错误:
```shell
ls: error while loading shared libraries: libfuse.so.2: cannot open shared object file: No such file or directory
```
解决方法:输入以下命令更新/etc/ld.so.conf即可:
```shell
sudo ldconfig
```

mfsmeta里基本上就是 **sustained**， **trash** 这两个文件夹， 可能还有 **reserved**

sustained， reserved里面是已经删除的但是仍然被其他用户一直打开的文件，在其他用户释放后就会被删除，不是我们的目标，不用管这两个文件夹。

我们的目标是**trash** 文件夹， 它包含这所有在本机上被删除的mfs文件

**trash** 的里面 只有两类文件， 第一类是包含被删除信息的文件夹，第二类是**undel**文件夹，我们主要就是通过undel文件夹恢复被删除文件的。
![4](/img/moosefs2/4.png)

上图就是trash里的内容， 这些文件夹都包含着被删除的文件， moosefs使用了十六进制统一管理这些目录，进入其中一个文件夹：
![5](/img/moosefs2/5.png)

这些就是被删除掉的文件。这里面还有一个**undel**，**将被删除的文件mv到undel里就可以实现文件的恢复**。

***
### 三 undel恢复文件

#### 1 单文件恢复
如果你只要恢复一两个文件， 直接在../trash/文件夹下面 find 文件名 寻找到文件所在目录，进入后将指定文件mv 到 当前目录下的undel里即可恢复，如图：
先创建一个测试文件，然后删除
![91](/img/moosefs2/91.png)

cd 进入 .../xxx/trash/ 进行恢复：
![10](/img/moosefs2/10.png)

查看恢复结果：
![92](/img/moosefs2/92.png)

#### 2 多文件批量恢复
如果我们是误操作 rm -rf 删除了很多文件， 一个个恢复简直不可能。
我尝试了 mv ??? ./undel 将trash目录下所有非undel的都已移入到undel里，结果不可行， 
又尝试 mv 001 undel 将trash目录下的一个文件夹001移入到undel里，也不行。

看来只能是像单文件恢复那样操作恢复了。

于是我花5分钟写了个python脚本，实现了批量恢复.
```python
import os
import shutil
import traceback

parent_dir = '/home/roo/mfsmeta/trash/'  # 替换成你自己的路径

sub_dir_list = []
err_list = []

for name in os.listdir(parent_dir):
    if name != 'undel':
        sub_dir = os.path.join(parent_dir, name)
        sub_dir_list.append(sub_dir)

        ssub_undel = os.path.join(sub_dir, 'undel')
        for name2 in os.listdir(sub_dir):
            if name2 != 'undel':
                ssub_file = os.path.join(sub_dir, name2)
                try:
                    shutil.move(ssub_file, ssub_undel)
                    print('{} is ok'.format(ssub_file))
                except:
                    print(traceback.format_exc())

                    err_list.append(ssub_file)

print()
print('------ err file list -----')
for i in err_list:  # 打印出所有执行失败的文件
    print(i)
```

效果很好，一次就成功恢复了所有误删的文件。如图：
![11](/img/moosefs2/11.png)

脚本打印出了一些恢复失败的错误信息，
![2](/img/moosefs2/2.png)

最后结尾统计了恢复失败的文件:
![1](/img/moosefs2/1.png)

可以看到恢复失败的都是.pyc文件，以及回收箱里的文件，都是非目标文件。

如果脚本一次执行没有全部恢复，可以多执行几遍。
