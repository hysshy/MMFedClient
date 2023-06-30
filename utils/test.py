import torch.cuda
from pynvml import *
import psutil

def show_gpu(simlpe=True):
    # 初始化
    nvmlInit()
    # 获取GPU个数
    deviceCount = nvmlDeviceGetCount()
    total_memory = 0
    total_free = 0
    total_used = 0
    gpu_name = ""
    gpu_num = deviceCount

    for i in range(deviceCount):
        print(i)
        handle = nvmlDeviceGetHandleByIndex(i)
        info = nvmlDeviceGetMemoryInfo(handle)
        gpu_name = nvmlDeviceGetName(handle)
        # 查看型号、显存、温度、电源
        if not simlpe:
            print("[ GPU{}: {}".format(i, gpu_name), end="    ")
            print("总共显存: {}G".format((info.total // 1048576) / 1024), end="    ")
            print("空余显存: {}G".format((info.free // 1048576) / 1024), end="    ")
            print("已用显存: {}G".format((info.used // 1048576) / 1024), end="    ")
            print("显存占用率: {}%".format(info.used / info.total), end="    ")
            print("运行温度: {}摄氏度 ]".format(nvmlDeviceGetTemperature(handle, 0)))

        total_memory += (info.total // 1048576) / 1024
        total_free += (info.free // 1048576) / 1024
        total_used += (info.used // 1048576) / 1024

    print("显卡名称：[{}]，显卡数量：[{}]，总共显存；[{}G]，空余显存：[{}G]，已用显存：[{}G]，显存占用率：[{}%]。".format(gpu_name, gpu_num, total_memory,
                                                                                     total_free, total_used,
                                                                                     (total_used / total_memory)))

    # 关闭管理工具
    nvmlShutdown()

def cpuInfo():
    cpuTimes = psutil.cpu_times()
    # 获取CPU信息中的内存信息
    def memoryInfo(memory):
        print(memory)
        return {
            '总内存(total)': str(round((float(memory.total) / 1024 / 1024 / 1024), 2)) + "G",
            '已使用(used)': str(round((float(memory.used) / 1024 / 1024 / 1024), 2)) + "G",
            '空闲(free)': str(round((float(memory.free) / 1024 / 1024 / 1024), 2)) + "G",
            '使用率(percent)': str(memory.percent) + '%',
            '可用(available)': (memory.available) if hasattr(memory, 'available') else '',
            '活跃(active)': (memory.active) if hasattr(memory, 'active') else '',
            '非活跃(inactive)': (memory.inactive) if hasattr(memory, 'inactive') else '',
            '内核使用(wired)': (memory.wired) if hasattr(memory, 'wired') else ''
        }
    return {
        '物理CPU个数': psutil.cpu_count(logical=False),
        '逻辑CPU个数': psutil.cpu_count(),
        'CPU使用情况': psutil.cpu_percent(percpu=True),
        '虚拟内存': memoryInfo(psutil.virtual_memory()),
        '交换内存': memoryInfo(psutil.swap_memory()),
        '系统启动到当前时刻': {
            pro: getattr(cpuTimes, pro) for pro in dir(cpuTimes) if pro[0:1] != '_' and pro not in ('index', 'count')
        },
    }

if __name__ == '__main__':
    # show_gpu(False)
    # cpu_percent = psutil.cpu_percent(interval=1)
    # print(cpu_percent)
    # computer_info = cpuInfo()
    # print(computer_info)
    # print(psutil.cpu_percent(interval=1))
    # memory = psutil.disk_usage('/')
    # print(str(round((float(memory.total) / 1024 / 1024 / 1024))))
    # print(str(round((float(memory.used) / 1024 / 1024 / 1024))))
    # print(str(round((float(memory.free) / 1024 / 1024 / 1024))))
    nvmlDeviceGetHandleByIndex(0)

