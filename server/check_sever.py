#向客户端发送文件
from utils.Log import logger
import requests

def upload_file(filepath, savepath, ip, port):
    logger.info('向客户端发送文件-' + ip +':'+filepath)
    with open(filepath, 'rb') as f:
        response = requests.post('http://{}:{}/download_file'.format(ip, port), files={'file': f}, data={'savepath':savepath})
    # 检查响应状态码是否为 200
    if response.status_code == 200:
        logger.info('File uploaded successfully')
        return response, True
    else:
        logger.info('Failed to upload file')
        return response, False