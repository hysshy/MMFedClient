import os
import time

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