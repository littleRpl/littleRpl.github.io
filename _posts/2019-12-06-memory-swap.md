---
layout:       post
title:        "linux资源监控——获取Memory与Swap的使用率"
# subtitle:     ''
date:         2019-12-06 14:30:00
author:       "Rpl"
header-img:   "img/memory-swap-info/4.png"
header-mask:  0.5
catalog:      true

tags:
  - 技术
  - linux
  - python
  - swap
  - memory
  - 原创

---

### 前言

linux资源监控系列文章: 
1. [linux资源监控——计算CPU利用率](http://littlerpl.me/2019/06/20/cpu/)
2. [linux资源监控——获取GPU信息](http://littlerpl.me/2019/12/06/gpustat/)
3. [linux资源监控——获取Memory与Swap的使用率](http://littlerpl.me/2019/12/06/memory-swap/)

关联文章:
1. [Ubuntu扩展Swap交换空间](http://littlerpl.me/2019/06/17/swap/)


### 一 free命令获取内存信息

通过free 命令查看内存和交换空间的使用情况
```shell
free
```
![1](/img/memory-swap-info/1.png)

free 默认单位为KB， 可以使用free -m 以MB为单位，或者 free -g 以GB为单位显示。

```shell
free -m
```
![2](/img/memory-swap-info/2.png)

```shell
free -g
```
![3](/img/memory-swap-info/3.png)

***

### 二 python脚本实现

```python
import os
import subprocess
import signal

# 获取内存信息
def get_MemoryInfo(ip):

    timeout_seconds = 30
    cmd = 'ssh -o StrictHostKeyChecking=no %s free' % ip
    # res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    memory_utilization = '-1'
    swap_utilization = '-1'

    res = timeout_Popen(cmd, timeout=timeout_seconds)

    if res:

        stdout = res.stdout.readlines()

        if not stdout:
            print('ssh %s 连接失败, 获取memory信息失败' % ip)
            return [memory_utilization, swap_utilization]

        memory_info = stdout[1].decode().split()
        swap_info = stdout[2].decode().split()

        totoal_memory = int(memory_info[1])
        available_memory = int(memory_info[-1])

        # used_memory = float(memory_info[2])
        # memory_utilization = str(round((used_memory / totoal_memory) *100, 2))

        memory_utilization = ((totoal_memory-available_memory)/totoal_memory)*100
        memory_utilization = str(round(memory_utilization, 2))

        totoal_swap = int(swap_info[1])
        if totoal_swap == 0:
            print('ip: %s,交换空间为0' % ip)

        available_swap = int(swap_info[-1])
        swap_utilization = ((totoal_swap - available_swap) / totoal_swap) * 100
        swap_utilization = str(round(swap_utilization, 2))

        # used_swap = float(swap_info[2])
        # swap_utilization = str(round((used_swap / totoal_swap)*100, 2))

        # print('--------- ip:%s----------' % ip)
        # print('swap: %d, %d, %s' % (totoal_swap, available_swap, swap_utilization))
        # print('memory: %d, %d, %s\n' %(totoal_memory, available_memory, memory_utilization))

    else:
        print('{}: timeout > {}s, 获取memory信息失败'.format(ip, timeout_seconds))

    return [memory_utilization, swap_utilization]


# 处理popen等待超时:
def timeout_Popen(cmd, timeout=30):
    start = time.time()
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while process.poll() is None:  # 是否结束
        time.sleep(0.2)
        now = time.time()
        if now - start >= timeout:
            os.kill(process.pid, signal.SIGKILL)

            # pid=-1 等待当前进程的all子进程, os.WNOHANG 没有子进程退出,
            os.waitpid(-1, os.WNOHANG)
            return None

    return process

```