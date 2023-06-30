from mmcv.runner.hooks import HOOKS, Hook
from utils.Log import logger
import os
import time
import numpy as np

@HOOKS.register_module()
class FedBL(Hook):

    def __init__(self, total_fedbl_num=1):
        self.total_fedbl_num = total_fedbl_num
        self.lossList = []
        self.cur_fedbl_num = 0
        self.first_interval = 200

    def fedbl_onece(self, runner ,loss_fed_interval):
        self.cur_fedbl_num += 1
        with open(runner.work_dir + '/fedbl.txt', mode='a+') as f:
            # f.write('fedbl_num:'+str(int(((runner.iter + 1) % max_iter_per_epoch)/loss_fed_interval))+'\n')
            f.write('fedbl_num:' + str(self.cur_fedbl_num) + '\n')
            f.write('iter:' + str(runner.iter) + '\n')
            f.write('loss:' + str(np.mean(self.lossList)) + '\n')
            f.flush()
            f.close()
        self.lossList = []
        while (1):
            with open(runner.work_dir + '/fedbl.txt', mode='r') as f:
                lines = f.readlines()
                if lines[-1].startswith('bl_w'):
                    break
                else:
                    time.sleep(10)

    def after_iter(self, runner):
        self.lossList.append(runner.outputs['loss'].data.cpu().numpy())
        if self.cur_fedbl_num < self.total_fedbl_num:
            max_iter_per_epoch = runner.max_iters/runner.max_epochs
            loss_fed_interval = int(max_iter_per_epoch/(self.total_fedbl_num))
            if loss_fed_interval > self.first_interval:
                if runner.inner_iter + 1 == self.first_interval:
                    self.fedbl_onece(runner, loss_fed_interval)
            # if self.every_n_iters(runner, loss_fed_interval):
            if (runner.inner_iter + 1) % (loss_fed_interval*(self.cur_fedbl_num+1))== 0:
                self.fedbl_onece(runner ,loss_fed_interval)


    def after_train_epoch(self, runner):
        self.lossList = []
        self.cur_fedbl_num = 0
        # with open(runner.work_dir + '/fedbl.txt', mode='a+') as f:
        #     # f.write('fedbl_num:'+str(int(((runner.iter + 1) % max_iter_per_epoch)/loss_fed_interval))+'\n')
        #     f.write('fedbl_num:0' + '\n')
        #     f.write('iter:' + str(runner.iter) + '\n')
        #     f.write('loss:' + str(np.mean(self.lossList)) + '\n')
        #     f.write('bl_w:1' + '\n')
        #     f.flush()
        #     f.close()
