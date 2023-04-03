from mmcv.runner.hooks import HOOKS, Hook
from utils.Log import logger
import os
import time
from utils.common import is_file_transfer_complete

@HOOKS.register_module()
class FedReload(Hook):

    def __init__(self, interval=1):
        self.interval = interval

    def after_train_epoch(self, runner):
        if self.every_n_epochs(runner, self.interval):
            # finish_train = True
            logger.info('完成第{}次训练,等待联邦融合'.format(str(runner.epoch+1)))
            self.reload_model(runner)


    def reload_model(self, runner):
        # 检查融合模型是否已分布
        work_dir = ''
        work_dirs = runner.work_dir.split('/')
        for i in range(len(work_dirs) - 1):
            work_dir = work_dir + work_dirs[i] + '/'
        reload_model_file = work_dir+'merge_epoch_'+str(runner.epoch+1)+'.pth'
        while 1:
            if os.path.exists(reload_model_file):
                assert is_file_transfer_complete(reload_model_file, 10)
                runner.load_checkpoint(reload_model_file)
                break
            time.sleep(5)







