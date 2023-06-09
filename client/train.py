# Copyright (c) OpenMMLab. All rights reserved.
import argparse
import copy
import os
import os.path as osp
import time
import mmcv
from mmcv import Config, DictAction
from mmcv.utils import get_git_hash
from mmdet import __version__
from mmdet.apis import init_random_seed, set_random_seed, train_detector
from mmdet.datasets import build_dataset
from mmdet.models import build_detector
from client import app
from flask import request
import multiprocessing
import torch
from utils.common import is_file_transfer_complete
# 注册联邦hook
import client.mmhook.fed_reload
import client.mmhook.fed_bl
multiprocessing.set_start_method('spawn', force=True)


@app.route('/start_train', methods=['POST'])
def start_train():
    cfg_file = request.data.decode()
    t = multiprocessing.Process(target=trainer, args=(cfg_file, ))
    t.start()
    # trainer(model, datasets, cfg, timestamp, meta)
    # print(multiprocessing.get_start_method())
    return 'success'


def pre_train(cfg_file, cfg):
    cfg_files = cfg_file.split('/')
    #init wrok_dir
    work_dir = ''
    for i in range(len(cfg_files) - 1):
        work_dir = work_dir + cfg_files[i] + '/'
    cfg.work_dir = work_dir
    # resume train 加载联邦融合模型
    if cfg.resume_from is not None:
        job_dir = ''
        for i in range(len(cfg_files) - 2):
            job_dir = job_dir + cfg_files[i] + '/'
        merge_epoch_file = job_dir+'merge_'+ cfg.resume_from
        assert is_file_transfer_complete(merge_epoch_file, 10)
        cfg.resume_from = work_dir + cfg.resume_from
        resume_epoch_dict = torch.load(cfg.resume_from, map_location='cpu')
        merge_dict = torch.load(merge_epoch_file, map_location='cpu')
        for key, value in merge_dict.items():
            resume_epoch_dict['state_dict'][key] = value
        torch.save(resume_epoch_dict, cfg.resume_from)


def trainer(cfg_file):
    from mmdet.utils import (collect_env, get_device, get_root_logger,
                             replace_cfg_vals, setup_multi_processes,
                             update_data_root)

    cfg = Config.fromfile(cfg_file)
    #训练前预处理
    pre_train(cfg_file, cfg)
    # init the logger before other steps
    timestamp = time.strftime('%Y%m%d_%H%M%S', time.localtime())
    log_file = osp.join(cfg.work_dir, 'train.log')
    logger = get_root_logger(log_file=log_file, log_level=cfg.log_level)

    # set multi-process settings
    setup_multi_processes(cfg)

    # create work_dir
    mmcv.mkdir_or_exist(osp.abspath(cfg.work_dir))

    # init the meta dict to record some important information such as
    # environment info and seed, which will be logged
    meta = dict()
    # log env info
    env_info_dict = collect_env()
    env_info = '\n'.join([(f'{k}: {v}') for k, v in env_info_dict.items()])
    dash_line = '-' * 60 + '\n'
    logger.info('Environment info:\n' + dash_line + env_info + '\n' +
                dash_line)
    meta['env_info'] = env_info
    meta['config'] = cfg.pretty_text
    # log some basic info
    logger.info(f'Config:\n{cfg.pretty_text}')

    cfg.device = get_device()
    # set random seeds
    seed = init_random_seed(None, device=cfg.device)
    set_random_seed(seed, deterministic=False)
    cfg.seed = seed
    meta['seed'] = seed
    meta['exp_name'] = cfg_file.split('/')[-1]

    model = build_detector(
        cfg.model,
        train_cfg=cfg.get('train_cfg'),
        test_cfg=cfg.get('test_cfg'))
    model.init_weights()

    datasets = [build_dataset(cfg.data.train)]
    if len(cfg.workflow) == 2:
        assert 'val' in [mode for (mode, _) in cfg.workflow]
        val_dataset = copy.deepcopy(cfg.data.val)
        val_dataset.pipeline = cfg.data.train.get(
            'pipeline', cfg.data.train.dataset.get('pipeline'))
        datasets.append(build_dataset(val_dataset))
    if cfg.checkpoint_config is not None:
        # save mmdet version, config file content and class names in
        # checkpoints as meta data
        cfg.checkpoint_config.meta = dict(
            mmdet_version=__version__ + get_git_hash()[:7],
            CLASSES=datasets[0].CLASSES)
    # add an attribute for visualization convenience
    model.CLASSES = datasets[0].CLASSES
    # add fedlw
    fedbl = False
    if hasattr(cfg, 'fedbl'):
        fedbl = cfg.fedbl
    train_detector(
        model,
        datasets,
        cfg,
        distributed=False,
        validate=True,
        timestamp=timestamp,
        meta=meta,
        fedbl=fedbl)

