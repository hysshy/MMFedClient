import os
import time
import re

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
                time.sleep(2)
                return 0
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

if __name__ == '__main__':
    epoch_time = get_epoch_time('/home/chase/PycharmProjects/MMFedClient/job/101/0_10.10.5.136/train.log')
    print(epoch_time)