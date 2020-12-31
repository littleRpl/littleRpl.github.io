---
layout:  post
title:  "Robot 监控服务器资源"
subtitle:  "通过微信机器人推送信息到企业微信，进行日报统计或性能预警"
date:  2020-12-31 17:50:04
author:  "rpl"
header-style:  "text"
catalog: true
tags:
    - 原创
    - 技术
    - python
    - matplotlib
    - psutils
---

> python脚本监控服务器的cpu， memory， swap等资源信息，可视化数据
>  通过微信机器人推送到企业微信，进行日报统计或性能预警


对于此监控脚本，我的设想是每隔10秒去获取一次系统信息，每隔6小时统计一次6小时内的历史数据，并可视化6小时历史监控信息。 如果服务器超出预警阈值，可视化5分钟内的历史监控信息。以下是脚本的配置信息：

```python
# ------------ config -------------
host_name ='Semacare-uat'  # 服务器名
warning_level = 30  # 预警阈值
interal_time = 10  # 监测间隔时间
warning_time = 5 * 60  # 5 minute  5分钟预警一次
note_time = 6 * 3600  # 6 hour汇报一次服务器资源信息
```


## 一 psutils 监控资源信息

关于python是如何监控服务器cpu，memory等信息的，可查看一下几篇文章：

1. [linux资源监控——计算CPU利用率](https://littlerpl.me/2019/06/20/cpu/)
2. [linux资源监控——获取GPU信息](https://littlerpl.me/2019/12/06/gpu-monitor/)
3. [linux资源监控——获取Memory与Swap的使用率](https://littlerpl.me/2019/12/06/memory-swap/)



这次我们将使用一个python的第三方库：<code>psutil</code> 来获取服务器的各种信息。

psutil(process and system utilities)是一个跨平台库， 用于在Python中检索有关运行进程和系统利用率(CPU、内存、磁盘、网络、传感器)的信息。

它主要用于系统监视、分析和限制进程资源以及管理正在运行的进程。它实现了ps、top、iotop、lsof、netstat、ifconfig、free等经典UNIX命令行工具所提供的许多功能。 psutil使用非常简单，具体教程可参考此链接：[https://pypi.org/project/psutil/](https://pypi.org/project/psutil/) 

以下代码是使用psutil获取cpu， memory， swap：
```python
# 受用psutils包 获取cpu， memory信息
def get_CpuInfo():
    try:
        cpu_percent = psutil.cpu_percent(0.1)
    except:
        cpu_percent = -1
        print('cpu获取失败')
    return cpu_percent


def get_MemoryInfo():
    try:
        mem_percent = psutil.virtual_memory().percent
        swap_percent = psutil.swap_memory().percent
    except:
        mem_percent, swap_percent = -1, -1
        print('获取内存信息失败')

    return mem_percent, swap_percent

```
***

## 二 数据可视化

### 1. deque双端队列的应用

我们需要这样一种数据结构：长度大小固定，可以不停的压入数据，当长度超出设定值时会丢弃最老的数据，压入最新的数据。

python的双端队列deque可以满足要求。
```python
from collections import deque

dq = deque(maxlen=5)  # 设定最大长度为5
for i in range(5):
	dq.append(i)
    
dq
Out[5]: deque([0, 1, 2, 3, 4])
    
dq.append('a')
dq
Out[7]: deque([1, 2, 3, 4, 'a'])  # 压入'a'，最老的0会被丢弃。
```


### 2. 平滑曲线

在绘制5分钟的预警信息图时，大概只有30个点的数据，绘制出来的是折线图，不美观。如下图
![image-20201231164156447](/img/reboot-monitor/image-20201231164156447.png)


以下是插值法平滑曲线的代码：
```python
# 插值法平滑曲线
new_x = np.linspace(min(x_list), max(x_list), 300)
cpu_smooth = make_interp_spline(x_list, cpu_list,)(new_x)
mem_smooth = make_interp_spline(x_list, mem_list)(new_x)
```

![image-20201231164438010](/img/reboot-monitor/image-20201231164438010.png)
可以看到折线图被平滑成了曲线。


### 3. 图像数据流转换与加密

如果要将绘制的图片通过微信机器人推送，就必须把图片进行md5加密，并且转化成base64编码的数据。一般来说我们需要先将图片保存到磁盘，然后在读文件，转化成md5值和base64值。这样我们需要给需要保存的图片开辟临时的磁盘空间，之后我们还需要在删除图片，维护起来比较麻烦。

更好的选择是，使用<code>io.BytesIO()</code> 直接跳过磁盘io，将图片转成数据流，保存在内存里，然在进行md5加密和base64转换。代码如下：
```python
# 图片md5加密， 转base64
def img_encryption(plt):
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes, format='png')
    
    pic_IObytes.seek(0)
    content = pic_IObytes.read()
    
    pic_md5 = hashlib.md5(content).hexdigest()  # md5
    pic_hash = base64.b64encode(content).decode()  # base64

    return pic_md5, pic_hash
```

### 4. 给不同级别的数据指定不同的颜色

例如 cpu 性能在0 ～ 30%时 我们使用蓝色绘制，30% ～ 80% 时使用橘黄色绘制， 超过80% 的使用红色绘制。

实现很简单，实现一个数据与颜色对应的映射表。代码如下：
```python
cpu_colors = []
for i in cpu_list:
    if i >= 80:
        cpu_colors.append('red')
    elif 30 < i <= 80:
        cpu_colors.append('orange')
    else:
        cpu_colors.append('blue')

    mem_colors = []
    for i in mem_list:
        if i >= 80:
            mem_colors.append('red')
        elif 30 < i <= 80:
            mem_colors.append('orange')
        else:
            mem_colors.append('blue')
                

plt.sca(ax1)
plt.ylim(0, 100)
plt.vlines(range(len(cpu_list)), 0, cpu_list, colors=cpu_colors)  # 指定颜色映射

plt.sca(ax2)
plt.ylim(0, 100)
plt.vlines(range(len(mem_list)), 0, mem_list, colors=mem_colors)
```

下图是实现效果：
![image-20201231171546011](/img/reboot-monitor/image-20201231171546011.png)



## 三 企业微信机器人推送

### 1. 配置机器人

添加一个群聊机器人，右键选择的群组，点击添加群机器人，即可添加一个群机器人。
![image-20201231172402913](/img/reboot-monitor/image-20201231172402913.png)

点击机器人，查看机器人信息。
![image-20201231172940744](/img/reboot-monitor/image-20201231172940744.png)
点击Webhook，可以查看机器人的各种配置，以及消息推送的不同方式及模版。



### 2. 推送信息编辑

本脚本使用的是markdown推送文本信息，使用图片格式推送绘图信息。

以下是markdown推送的模版：

![image-20201231173727560](/img/reboot-monitor/image-20201231173727560.png)

代码如下：

```python
def post_info(cpu, memory, swap, host, type='warning'):
    webhook_url = 'https://qyapi.weixin.qq.com/xxxxeqwrfwetgerqw54361fsdagfas23435xxx'
    colors = []
    for i in [cpu, memory, swap]:
        if i <= 30:
            colors.append('info')
        elif i < 80:
            colors.append('warning')
        else:
            colors.append('red')

    warning_info = f'服务器:**<font color=\"blue\">{host}</font>**性能预警报告：\n' \
              f'>CPU: <font color=\"{colors[0]}\">{cpu}</font> % \n' \
              f'>MEM: <font color=\"{colors[1]}\">{memory}</font> % \n' \
              f'>SWP: <font color=\"{colors[2]}\">{swap}</font> % \n\n' \
              f'--------\n' \
              f'<font color=\"#FF99CC">粉粉</font>会持续为主人监测服务器的性能～'

    note_info = f'服务器:**<font color=\"blue\">{host}</font>**监测时报：\n' \
                f'>CPU: <font color=\"{colors[0]}\">{cpu}</font> % \n' \
                f'>MEM: <font color=\"{colors[1]}\">{memory}</font> % \n' \
                f'>SWP: <font color=\"{colors[2]}\">{swap}</font> % \n\n' \
                f'--------\n' \
                f'<font color=\"#FF99CC">粉粉</font>会持续为主人监测服务器的性能～'

    content = {
        'msgtype': 'markdown',
        'markdown': {'content': warning_info if type == 'warning' else note_info},
    }

    r = requests.post(webhook_url, json.dumps(content))
    print(f'{type} event post status code: {r.status_code}')
    
```


以下是图片推送的模版：
![image-20201231173629960](/img/reboot-monitor/image-20201231173629960.png)

图片推送的代码如下：
```python
def post_img(pic_md5, pic_hash):
    if not pic_md5:
        return
    webhook_url = 'https://qyapi.weixxxxxxxxxx234235dfgdfsgdxxxxxxxx'
    content = {
        'msgtype': 'image',
        'image': {'base64': pic_hash,
                  'md5': pic_md5}
    }

    r = requests.post(webhook_url, json.dumps(content))
```


下面是推送的真实效果：
![image-20201231174313214](/img/reboot-monitor/image-20201231174313214.png)

![image-20201231174450228](/img/reboot-monitor/image-20201231174450228.png)



## 四 脚本完整代码

```python
# -*- coding: utf-8 -*-
"""
-------------------------------------------------
  File Name：  reboot_push_message
  Description : 企业微信机器人，推送服务器资源：cpu， memory， swap， disk预警信息到企业微信群。
  Author :    Gray-rpl
  date：     2020/12/18
-------------------------------------------------
  Change Activity:
          2020/12/18: v1
          2020/12/25: v2 添加CPU，Mem的小时统计图， 分钟统计图，并推送图片。使用psutil获取系统信息
-------------------------------------------------
"""
import os
import io
import time
import json
import base64
import hashlib
import psutil
import requests

from threading import Timer
from collections import deque
import matplotlib.pyplot as plt

import numpy as np
from scipy.interpolate import make_interp_spline

# ------------ config -------------
host_name ='Semacare-uat'  # 服务器名
warning_level = 80  # 预警阈值
interal_time = 10  # 监测间隔时间
warning_time = 5 * 60  # 5 minute  5分钟预警一次
note_time = 6 * 3600  # 6 hour汇报一次服务器资源信息
# --------------------------------

pre_warning_time = 0
pre_note_time = 0

cpu_dq = deque(maxlen=int(note_time // interal_time))
mem_dq = deque(maxlen=int(note_time // interal_time))

def post_info(cpu, memory, swap, host, type='warning'):
    webhook_url = 'https://qyapi.weixin.qq.com/cgi-bin/webgsdfgw543623dsf123233254'
    colors = []
    for i in [cpu, memory, swap]:
        if i <= 30:
            colors.append('info')
        elif i < 80:
            colors.append('warning')
        else:
            colors.append('red')

    warning_info = f'服务器:**<font color=\"blue\">{host}</font>**性能预警报告：\n' \
              f'>CPU: <font color=\"{colors[0]}\">{cpu}</font> % \n' \
              f'>MEM: <font color=\"{colors[1]}\">{memory}</font> % \n' \
              f'>SWP: <font color=\"{colors[2]}\">{swap}</font> % \n\n' \
              f'--------\n' \
              f'<font color=\"#FF99CC">粉粉</font>会持续为主人监测服务器的性能～'

    note_info = f'服务器:**<font color=\"blue\">{host}</font>**监测时报：\n' \
                f'>CPU: <font color=\"{colors[0]}\">{cpu}</font> % \n' \
                f'>MEM: <font color=\"{colors[1]}\">{memory}</font> % \n' \
                f'>SWP: <font color=\"{colors[2]}\">{swap}</font> % \n\n' \
                f'--------\n' \
                f'<font color=\"#FF99CC">粉粉</font>会持续为主人监测服务器的性能～'

    content = {
        'msgtype': 'markdown',
        'markdown': {'content': warning_info if type == 'warning' else note_info},
    }

    r = requests.post(webhook_url, json.dumps(content))
    print(f'{type} event post status code: {r.status_code}')


def post_img(pic_md5, pic_hash):
    if not pic_md5:
        return
    webhook_url = 'https://qyapi.weixin.frwqerqwr234264324123qesfsadcwxxxxxxx'
    content = {
        'msgtype': 'image',
        'image': {'base64': pic_hash,
                  'md5': pic_md5}
    }

    r = requests.post(webhook_url, json.dumps(content))


# 获取cpu信息
def get_CpuInfo():
    total_list = []
    idle_list = []

    # 连续取2次文件
    for k in range(2):
        data = []
        # 这里是使用ssh命令获， 去服务器上获取信息
        # grep -w cpu 只过滤含cpu字段的行，刚好也就是我们需要的那一行信息
        cpu_cmd = 'cat /proc/stat |grep -w cpu'

        res = os.popen(cpu_cmd, ).read().split()
        if not res:
            break
        for i in res:
            try:
                if isinstance(eval(i), int):
                    data.append(i)
            except:
                continue

        time.sleep(0.01)
        # print('cpu：' + str(data))
        total_cpu_time = sum([int(i) for i in data])
        total_list.append(total_cpu_time)
        idle_list.append(int(data[3]))

    if len(total_list) == 2:
        total = total_list[1] - total_list[0]
        idle = idle_list[1] - idle_list[0]
        pcpu = str(round(100 * (total - idle) / total, 2))
    else:
        print('%s:获取cpu信息失败')
        pcpu = '-1'

    return float(pcpu)

# 获取内存信息
def get_MemoryInfo():
    timeout_seconds = 30
    cmd = 'free'
    # res = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    memory_utilization = -1
    swap_utilization = -1
    res = os.popen(cmd,)

    if res:
        stdout = res.readlines()
        if not stdout:
            print('获取memory信息失败')
            return [memory_utilization, swap_utilization]

        memory_info = stdout[1].split()
        swap_info = stdout[2].split()

        totoal_memory = int(memory_info[1])
        available_memory = int(memory_info[-1])

        # used_memory = float(memory_info[2])
        # memory_utilization = str(round((used_memory / totoal_memory) *100, 2))

        memory_utilization = ((totoal_memory-available_memory)/totoal_memory)*100
        memory_utilization = str(round(memory_utilization, 2))

        totoal_swap = int(swap_info[1])
        if totoal_swap == 0:
            print(',交换空间为0')
            swap_utilization = 0
        else:
            available_swap = int(swap_info[-1])
            swap_utilization = ((totoal_swap - available_swap) / totoal_swap) * 100
            swap_utilization = round(swap_utilization, 2)
    else:
        print('timeout > {}s, 获取memory信息失败'.format(timeout_seconds))

    return [float(memory_utilization), float(swap_utilization)]


# 受用psutils包 获取cpu， memory信息
def get_CpuInfo2():
    try:
        cpu_percent = psutil.cpu_percent(0.1)
    except:
        cpu_percent = -1
        print('cpu获取失败')
    return cpu_percent


def get_MemoryInfo2():
    try:
        mem_percent = psutil.virtual_memory().percent
        swap_percent = psutil.swap_memory().percent
    except:
        mem_percent, swap_percent = -1, -1
        print('获取内存信息失败')

    return mem_percent, swap_percent


# 绘制每6小时一次的资源通知图
def draw_note_figure():
    # note_count = note_time // interal_time
    cpu_list = list(cpu_dq)
    mem_list = list(mem_dq)

    if len(cpu_list) < 30:
        print('Note statistic not enough data, drop img...')
        return (None, None)

    # import random
    # cpu_list = [random.randrange(0, 101) for i in range(2160)]
    # mem_list = [random.randrange(0, 101) for i in range(2160)]

    cpu_colors = []
    for i in cpu_list:
        if i >= 80:
            cpu_colors.append('red')
        elif 30 < i <= 80:
            cpu_colors.append('orange')
        else:
            cpu_colors.append('blue')

        mem_colors = []
        for i in mem_list:
            if i >= 80:
                mem_colors.append('red')
            elif 30 < i <= 80:
                mem_colors.append('orange')
            else:
                mem_colors.append('blue')

    plt.figure(figsize=(9, 4))
    ax1 = plt.subplot(2, 1, 1)
    ax2 = plt.subplot(2, 1, 2)

    # 添加子图的标题信息
    ax1.set_title(f'{host_name}: {note_time // 3600} hours CPU statistic')
    ax2.set_title(f'{host_name}: {note_time // 3600} hours Memory statistic')

    # 设置背景网格类型，颜色，透明度
    ax1.grid(color='#FF0000', linestyle='-.', linewidth=1, alpha=0.2)
    ax2.grid(color='#FF0000', linestyle='-.', linewidth=1, alpha=0.2)

    plt.sca(ax1)  # 选择子图1
    plt.ylim(0, 100)  # 限制y轴高度
    plt.vlines(range(len(cpu_list)), 0, cpu_list, colors=cpu_colors)  # 指定颜色映射

    plt.sca(ax2)  # 选择子图2
    plt.ylim(0, 100)
    plt.vlines(range(len(mem_list)), 0, mem_list, colors=mem_colors)

    plt.tight_layout()  # 严谨布局

    # 将图片直接转base64， 跳过磁盘IO
    return img_encryption(plt)


# 图片md5加密， 转base64
def img_encryption(plt):
    pic_IObytes = io.BytesIO()
    plt.savefig(pic_IObytes, format='png')
    pic_IObytes.seek(0)
    content = pic_IObytes.read()
    pic_md5 = hashlib.md5(content).hexdigest()  # md5
    pic_hash = base64.b64encode(content).decode()  # base64

    return pic_md5, pic_hash


# 绘制5分钟的预警信息图
def draw_warning_figure():
    count = warning_time // interal_time
    cpu_list = list(cpu_dq)[-count:]
    mem_list = list(mem_dq)[-len(cpu_list):]

    if len(cpu_list) < 5:
        return (None, None)

    import random
    cpu_list = [random.randrange(30, 101) for i in range(30)]
    mem_list = [random.randrange(0, 30) for i in range(30)]

    x_list = list(range(len(cpu_list)))

    # 插值法平滑曲线
    new_x = np.linspace(min(x_list), max(x_list), 300)
    cpu_smooth = make_interp_spline(x_list, cpu_list,)(new_x)
    mem_smooth = make_interp_spline(x_list, mem_list)(new_x)

    plt.figure(figsize=(9, 3))
    plt.plot(new_x, cpu_smooth,)
    plt.plot(new_x, mem_smooth,)
    # plt.plot(x_list, cpu_list, mem_list)
    plt.ylim(0, 100)
    plt.title(f'{host_name}: {warning_time // 60} minutes statistic')
    plt.legend(['Cpu', 'Memory'])
    plt.grid(color='#FF0000', linestyle='-.', linewidth=1, alpha=0.1)

    # ax = plt.gca()
    # 去顶部边框
    # ax.spines['top'].set_color('none')
    # ax.spines['right'].set_color('none')
    # 坐标原点相交
    # ax.xaxis.set_ticks_position('bottom')
    # ax.spines['bottom'].set_position(('data', 0))
    # ax.yaxis.set_ticks_position('left')
    # ax.spines['left'].set_position(('data', 0))

    return img_encryption(plt)


# 监控资源
def get_server_info():
    global pre_note_time
    global pre_warning_time

    cpu = get_CpuInfo2()
    mem, swp = get_MemoryInfo2()

    global cpu_dq, mem_dq
    cpu_dq.append(cpu)
    mem_dq.append(mem)

    cpu_avg = sum(list(cpu_dq)[-5:]) // len(list(cpu_dq)[-5:])
    mem_avg = sum(list(mem_dq)[-5:]) // len(list(mem_dq)[-5:])
    print(f'cpu: {cpu} %, mem: {mem} %, swap: {swp} %')

    if cpu_avg >= warning_level or mem_avg >= warning_level:
        if time.time() - pre_warning_time >= warning_time:
            img_md5, img_hash = draw_warning_figure()
            post_info(cpu, mem, swp, host_name, )
            post_img(img_md5, img_hash)
            pre_warning_time = time.time()

    if time.time() - pre_note_time >= note_time:
        img_md5, img_hash = draw_note_figure()
        post_info(cpu, mem, swp, host_name, type='note')
        post_img(img_md5, img_hash)

        pre_note_time = time.time()

    print()


def main():
    while True:
        get_server_info()
        time.sleep(interal_time)


if __name__ == "__main__":
    main()

```


