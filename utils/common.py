import os
import time
import re
from pynvml import *
import psutil

def is_file_transfer_complete(filepath, timeout=10):
    """
    检查文件传输是否完成
    :param filepath: 文件路径
    :param timeout: 超时时间，默认为10秒
    :return: True表示文件传输已经完成，False表示文件传输未完成
    """
    start_time = time.time()
    while True:
        # 获取文件的当前大小
        current_size = os.path.getsize(filepath)
        time.sleep(1)  # 等待1秒钟
        # 再次获取文件的大小，检查文件是否在变化
        new_size = os.path.getsize(filepath)
        # 如果文件大小没有发生变化，认为文件传输已经完成
        if new_size == current_size:
            return True
        # 如果已经超过超时时间，认为文件传输已经失败
        if time.time() - start_time > timeout:
            return False

#从mm log中估计每个epoch的训练时间
def get_epoch_time(log_file):
    last_iter = 0
    total_iter = 0
    epoch_time = 20
    iter_time_list = []
    #等待最新训练日志
    get_train_line = False
    while not get_train_line:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            f.close()
        max_line = len(lines)
        for i in range(1, 3):
            last_line = lines[max_line - i]
            if 'Saving checkpoint' in last_line:
                return epoch_time
            elif 'Epoch' not in last_line and ' time: ' not in last_line:
                get_train_line = False
                break

            else:
                get_train_line = True
        time.sleep(10)

    for i in range(1,3):
        last_line = lines[max_line - i]
        if last_iter == 0:
            match_obj = re.match(r'.*\[(\d+)/(\d+)\].*', last_line)
            last_iter = int(match_obj.group(1))
            total_iter = int(match_obj.group(2))
        iter_time = float(last_line.split(' time: ')[-1].split(',')[0])
        iter_time_list.append(iter_time)
    if last_iter != 0:
        epoch_time = (total_iter - last_iter) * min(iter_time_list)
    return epoch_time

#从mm log中估计每个fedlw_iter的训练时间
def get_fedlw_iter_time(log_file, total_fedlw_num, fedlw_num):
    last_iter = 0
    total_iter = 0
    epoch_time = 20
    iter_time_list = []
    #等待最新训练日志
    get_train_line = False
    while not get_train_line:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            f.close()
        max_line = len(lines)
        for i in range(1, 3):
            last_line = lines[max_line - i]
            if 'Epoch' not in last_line and ' time: ' not in last_line:
                get_train_line = False
                break
            else:
                get_train_line = True
        if not get_train_line:
            time.sleep(10)

    for i in range(1,3):
        last_line = lines[max_line - i]
        if last_iter == 0:
            match_obj = re.match(r'.*\[(\d+)/(\d+)\].*', last_line)
            last_iter = int(match_obj.group(1))
            total_iter = int(match_obj.group(2))
        iter_time = float(last_line.split(' time: ')[-1].split(',')[0])
        iter_time_list.append(iter_time)
    if last_iter != 0:
        expect_iter = int(total_iter/total_fedlw_num)*fedlw_num
        epoch_time = (expect_iter - last_iter) * min(iter_time_list)
    return epoch_time

def get_loss(log_file):
    while 1:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            f.close()
        max_line = len(lines)
        for i in range(1, 3):
            last_line = lines[max_line - i].strip('\n')
            if 'Epoch' in last_line and ' time: ' in last_line:
                match_obj = re.match(r'.*\[(\d+)/(\d+)\].*', last_line)
                last_iter = int(match_obj.group(1))
                total_iter = int(match_obj.group(2))
                match_obj = re.match(r'.*\[(\d+)\].*', last_line)
                epoch = int(match_obj.group(1))
                lastlines = last_line.split(',')
                loss = float(lastlines[-1].split(':')[-1].strip(' '))
                curiter = (epoch-1)*total_iter + last_iter
                return {'curiter':curiter, 'loss':loss}
        time.sleep(10)

def get_schedule(log_file):
    while 1:
        with open(log_file, 'r') as f:
            lines = f.readlines()
            f.close()
        max_line = len(lines)
        for i in range(1, 3):
            last_line = lines[max_line - i].strip('\n')
            if 'Epoch' in last_line and ' time: ' in last_line:
                match_obj = re.match(r'.*\[(\d+)/(\d+)\].*', last_line)
                last_iter = int(match_obj.group(1))
                total_iter = int(match_obj.group(2))
                match_obj = re.match(r'.*\[(\d+)\].*', last_line)
                epoch = int(match_obj.group(1))
                curiter = (epoch-1)*total_iter + last_iter
                reponse = str(curiter)+'/'+str(total_iter*12)
                return reponse
        time.sleep(10)

def get_img_file(file_name,type):
    imagelist = []
    for parent, dirnames, filenames in os.walk(file_name):
        for filename in filenames:
            if filename.lower().endswith(type):
                imagelist.append(os.path.join(parent, filename))
        return imagelist

def get_hardware(gpu):
    #GPU使用率
    nvmlInit()
    handle = nvmlDeviceGetHandleByIndex(gpu)
    info = nvmlDeviceGetMemoryInfo(handle)
    total_gpu = str((info.total // 1048576) / 1024)
    used_gpu = str((info.used // 1048576) / 1024)
    info_gpu = str(used_gpu)+'/'+str(total_gpu)
    #CPU使用率
    used_cpu = psutil.cpu_percent(interval=1)
    info_cpu = str(used_cpu)+'/'+str(100)
    #内存使用率
    memory = psutil.virtual_memory()
    total_memory = str(round((float(memory.total) / 1024 / 1024 / 1024), 2))
    used_memory = str(round((float(memory.used) / 1024 / 1024 / 1024), 2))
    info_memory = used_memory+'/'+total_memory
    #磁盘使用率
    disk = psutil.disk_usage('/')
    total_disk = str(round((float(disk.total) / 1024 / 1024 / 1024)))
    used_disk = str(round((float(disk.used) / 1024 / 1024 / 1024)))
    info_disk = used_disk+'/'+total_disk
    return {'GPU':info_gpu, 'CPU':info_cpu, '内存':info_memory, '磁盘':info_disk}

if __name__ == '__main__':
    # print(get_fedloss('/home/chase/PycharmProjects/MMFedClient/job/Public-FedAvg/0_10.10.6.121/train.log'))
    get_hardware(1)