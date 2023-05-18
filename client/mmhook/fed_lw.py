from mmcv.runner.hooks import HOOKS, Hook
from utils.Log import logger
import os
import time
import numpy as np

@HOOKS.register_module()
class FedLW(Hook):

    def __init__(self, total_fedlw_num=1):
        self.total_fedlw_num = total_fedlw_num
        self.lossList = []

    def after_iter(self, runner):
        self.lossList.append(runner.outputs['loss'].data.cpu().numpy())
        max_iter_per_epoch = runner.max_iters/runner.max_epochs
        loss_fed_interval = int(max_iter_per_epoch/self.total_fedlw_num)
        # if self.every_n_iters(runner, loss_fed_interval):
        if (runner.inner_iter + 1) % loss_fed_interval == 0:
            with open(runner.work_dir+'/fedlw.txt', mode='a+') as f:
                # f.write('fedlw_num:'+str(int(((runner.iter + 1) % max_iter_per_epoch)/loss_fed_interval))+'\n')
                f.write('fedlw_num:' + str(int((runner.inner_iter + 1) / loss_fed_interval)) + '\n')
                f.write('iter:'+str(runner.iter)+'\n')
                f.write('loss:'+str(np.mean(self.lossList))+'\n')
                f.flush()
                f.close()
            self.lossList = []
            while(1):
                with open(runner.work_dir + '/fedlw.txt', mode='r') as f:
                    lines = f.readlines()
                    if lines[-1].startswith('fedlw'):
                        break
                    else:
                        time.sleep(10)