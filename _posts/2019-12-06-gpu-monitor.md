---
layout:       post
title:        "linux资源监控——获取GPU信息"
subtitle:     'gpustat --json'
date:         2019-12-06 14:00:00
author:       "Rpl"
header-img:   "img/gpustat/5.png"
header-mask:  0.7
# catalog:      true

tags:
  - 技术
  - linux
  - python
  - gpustat
  - 原创

---

### 前言

linux资源监控系列文章: 
1. [linux资源监控——计算CPU利用率](http://littlerpl.me/2019/06/20/cpu/)
2. [linux资源监控——获取GPU信息](http://littlerpl.me/2019/12/06/gpustat/)
3. [linux资源监控——获取Memory与Swap的使用率](http://littlerpl.me/2019/12/06/memory-swap/)

关联文章:
1. [python NVIDIA显卡查看工具 gpustat](http://littlerpl.me/2019/12/06/gpustat/)


***

### 一 gpu监控信息
主要监控gpu的显卡数，以及每张显卡的利用率，内存使用率，温度等信息。

***

### 二 gpustat

主要使用gpustat获取gpu的各种信息。 gpustat --json 可以将gpu的信息以json的格式展示出来，极大的方便了我们的信息筛选。
关于**gpustat**，点击[NVIDIA显卡查看工具gpustat](http://littlerpl.me/2019/12/06/gpustat/)了解更多。

```shell
gpustat --json
```

```json
{
    "hostname": "roo-21",
    "query_time": "2019-12-06T10:46:13.356002",
    "gpus": [
        {
            "index": 0,
            "uuid": "GPU-4f085884-4260-a21e-25b1-2fa2e6f72f8c",
            "name": "GeForce GTX 1080 Ti",
            "temperature.gpu": 53,
            "utilization.gpu": 2,
            "power.draw": 57,
            "enforced.power.limit": 250,
            "memory.used": 612,
            "memory.total": 11164,
            "processes": [
                {
                    "username": "gdm",
                    "command": "Xorg",
                    "gpu_memory_usage": 19,
                    "pid": 1247
                },
                {
                    "username": "gdm",
                    "command": "gnome-shell",
                    "gpu_memory_usage": 49,
                    "pid": 1340
                },
                {
                    "username": "roo",
                    "command": "Xorg",
                    "gpu_memory_usage": 231,
                    "pid": 2205
                },
                {
                    "username": "roo",
                    "command": "gnome-shell",
                    "gpu_memory_usage": 234,
                    "pid": 2348
                },
                {
                    "username": "roo",
                    "command": "TeamViewer",
                    "gpu_memory_usage": 12,
                    "pid": 2359
                },
                {
                    "username": "roo",
                    "command": "chromium-browser",
                    "gpu_memory_usage": 61,
                    "pid": 3804
                }
            ]
        },
        {
            "index": 1,
            "uuid": "GPU-103ab59c-6a24-1ea0-b1da-9217c750a716",
            "name": "GeForce GTX 1080 Ti",
            "temperature.gpu": 37,
            "utilization.gpu": 0,
            "power.draw": 9,
            "enforced.power.limit": 250,
            "memory.used": 2,
            "memory.total": 11172,
            "processes": []
        },
        {
            "index": 2,
            "uuid": "GPU-06227d9a-a9f8-a653-1dab-b544b4d1535d",
            "name": "GeForce GTX 1080 Ti",
            "temperature.gpu": 34,
            "utilization.gpu": 0,
            "power.draw": 10,
            "enforced.power.limit": 250,
            "memory.used": 2,
            "memory.total": 11172,
            "processes": []
        },
        {
            "index": 3,
            "uuid": "GPU-55757d09-149f-26ad-251d-0a28dc3d5fb5",
            "name": "GeForce GTX 1080 Ti",
            "temperature.gpu": 24,
            "utilization.gpu": 0,
            "power.draw": 9,
            "enforced.power.limit": 250,
            "memory.used": 2,
            "memory.total": 11172,
            "processes": []
        }
    ]
}
```

分析此json的信息，主要包括:
- hostname 主机名
- query_time 查询时间
- gpus: 显卡详细信息
	- index 显卡索引
	- uuid 显卡识别码
	- name 显卡名
	- temperature.gpu 温度
	- utilization.gpu 利用率
	- power.draw 功耗
	- enforced.power.limit 最大功耗
	- memory.used 已用内存
	- memory.total 总内存
	- processes 执行进程
		- username 用户名
		- command 执行命令
		- gpu_memory_used 使用的gpu内存
		- pid 进程id

由此可见，可以通过gpustat --json 获取到gpu的所有信息。

***

### 三 脚本实现

```python
import os
import json
import signal
import subprocess

def get_GpuInfo(ip):
    """
    :param ip: host
    :return: gpu利用率, gpu内存占用率, gpu温度, gpu数量
    """

    utilization_list = []
    memory_usge_list = []
    temperature_list = []
    timeout_seconds = 30

    gpu_cmd = 'ssh -o StrictHostKeyChecking=no %s gpustat --json' % ip  # 通过命令行执行gpustat --json
    gpu_info_dict = {}
    gpu_num = 0

    try:
        res = timeout_Popen(gpu_cmd, timeout_seconds)  # 超过30秒无返回信息,返回空值

        if res:
            res = res.stdout.read().decode()
            if not res:
                print('ssh %s 连接失败, 获取gpu信息失败' % ip)

            else:
                # gpu_info_dict = eval(res)
                gpu_info_dict = json.loads(res)  # str to json
                gpu_num = len(gpu_info_dict['gpus'])
    except:
        pass

    # ------------------------------------------------------------------------------------------------------------------
    if gpu_info_dict:
        for i in gpu_info_dict['gpus']:
            utilization_gpu = float(i['utilization.gpu'])  # gpu利用率
            memory_used_gpu = round(100 * (i['memory.used'] / i['memory.total']), 2)  # gpu内存占用率

            utilization_list.append(str(utilization_gpu))
            memory_usge_list.append(str(memory_used_gpu))
            temperature_list.append(str(i['temperature.gpu'])) # 温度

    else:
        print('{}: timeout > {}s, 获取gpu信息失败\n'.format(ip, timeout_seconds))
        utilization_list = ['-1']*4
        memory_usge_list = ['-1']*4
        temperature_list = ['-1']*4

    gpu_utilization = ','.join(utilization_list)
    gpu_memory_utilization = ','.join(memory_usge_list)
    gpu_temperature = ','.join(temperature_list)

    return [gpu_utilization, gpu_memory_utilization, gpu_temperature, gpu_num]


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