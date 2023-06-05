import os.path
from mmcv import Config
from client import app
from flask import request, send_file
import pkg_resources
from utils.Log import logger
from utils.common import is_file_transfer_complete,get_epoch_time

def get_package_version(package_name):
    try:
        package = pkg_resources.get_distribution(package_name)
        return package.version
    except pkg_resources.DistributionNotFound:
        return None

@app.route('/check_envs', methods=['POST'])
def check_envs():
    envs = request.get_json()
    logger.info('检查环境')
    for env in envs.keys():
        version = get_package_version(env)
        envs[env] = version
    logger.info(envs)
    return envs

@app.route('/download_file', methods=['POST'])
def download_file():
    # 检查是否有上传的文件
    if 'file' not in request.files:
        return 'No file uploaded', 400
    # 获取上传的文件对象
    file = request.files['file']
    # 检查文件名是否为空
    if file.filename == '':
        return 'Empty file name', 400
    # 处理文件，保存到本地文件系统
    savepath = request.form['savepath']
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    file.save(savepath+'/'+file.filename)
    logger.info('下载完毕文件:' + savepath+'/'+file.filename)
    # 返回响应
    return savepath+'/'+file.filename, 200

@app.route('/upload_file', methods=['POST'])
def upload_file():
    current_path = os.getcwd()
    filepath = current_path+'/'+request.form['filepath']
    if not os.path.exists(filepath):
        # 获取训练时间
        # init log path
        log_path = ''
        paths = filepath.split('/')
        for i in range(len(paths) - 1):
            log_path = log_path + paths[i] + '/'
        logfile = log_path + 'train.log'
        epoch_time = get_epoch_time(logfile)
        logger.info(':模型训练中,预计训练时间:'+str(epoch_time))
        return str(epoch_time), 400
    else:
        assert is_file_transfer_complete(filepath, 10)
        logger.info('上传模型:'+filepath)
        return send_file(filepath, as_attachment=True), 200

@app.route('/check_dataset', methods=['POST'])
def check_dataset():
    logger.info('检查数据集')
    data_status ={}
    cfg = request.data.decode()
    cfg = Config.fromfile(cfg)
    data_status.setdefault(cfg.data.train.ann_file, os.path.exists(cfg.data.train.ann_file))
    data_status.setdefault(cfg.data.val.ann_file, os.path.exists(cfg.data.val.ann_file))
    data_status.setdefault(cfg.data.test.ann_file, os.path.exists(cfg.data.test.ann_file))
    logger.info(data_status)
    return data_status

@app.route('/check_online', methods=['POST'])
def check_online():
    return {'status':'online'}

@app.route('/download_epoch', methods=['GET'])
def download_epoch():
    # 检查是否有上传的文件
    if 'file' not in request.files:
        return 'No file uploaded', 400
    # 获取cfg路径
    cfg_file = request.data.decode()
    cfg_files = cfg_file.split('/')
    job_dir = ''
    for i in range(len(cfg_files) - 2):
        job_dir = job_dir + cfg_files[i] + '/'
    # 获取上传的文件对象
    file = request.files['file']
    # 检查文件名是否为空
    if file.filename == '':
        return 'Empty file name', 400
    # 处理文件，保存到本地文件系统
    file.save(job_dir+'/'+file.filename)
    # 返回响应
    return job_dir+'/'+file.filename, 200

@app.route('/post_client_loss', methods=['POST'])
def post_client_loss():
    data = request.get_json()
    work_dir = data['work_dir']
    fedbl_num = data['fedbl_num']
    total_fedbl_num = data['total_fedbl_num']
    if os.path.exists(work_dir + '/fedbl.txt'):
        with open(work_dir + '/fedbl.txt', mode='r') as f:
            lines = f.readlines()
            cur_fedbl_num = lines[-3].strip('\n').split(':')[-1]
            if fedbl_num == int(cur_fedbl_num):
                return lines[-1].strip('\n')
    # logfile = work_dir + '/train.log'
    # epoch_time = get_fedbl_iter_time(logfile, total_fedbl_num, fedbl_num)
    epoch_time = 10
    # logger.info(':模型训练中,预计fed_lw_iter时间:' + str(epoch_time))
    return str(epoch_time), 400

@app.route('/get_client_fedbl', methods=['POST'])
def get_client_fedbl():
    data = request.get_json()
    work_dir = data['work_dir']
    fedbl_num = data['fedbl_num']
    bl_w = data['bl_w']
    logger.info('更新fedbl:'+str(bl_w))
    with open(work_dir + '/fedbl.txt', mode='a') as f:
        # lines = f.readlines()
        # cur_fedbl_num = lines[-3].strip('\n').split(':')[-1]
        # assert fedbl_num == int(cur_fedbl_num)
        f.write('bl_w:'+str(bl_w)+'\n')
        f.flush()
        f.close()
    return 'sucess'

# @app.route('/get_client_bl_w', methods=['POST'])
# def get_client_bl_w():
#     data = request.get_json()
#     work_dir = data['work_dir']
#     tasktype = data['tasktype']
#     bl_w = data['bl_w']
#     logger.info('更新bl_w:'+str(bl_w))
#     with open(work_dir + '/fedbl.txt', mode='w') as f:
#         f.write(str(tasktype)+':'+str(bl_w)+'\n')
#         f.flush()
#         f.close()
#     return 'sucess'

if __name__ == '__main__':
    print(get_package_version('mmdet'))
