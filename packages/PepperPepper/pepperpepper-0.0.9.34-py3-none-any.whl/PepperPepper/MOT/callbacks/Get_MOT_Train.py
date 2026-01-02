import torch
from torch.utils.data import DataLoader
from torch.utils.tensorboard import SummaryWriter
import os
import numpy as np
import random
import time
import datetime
import json
from pathlib import Path
from PepperPepper.MOT.datasets import DataSetLoader_RGBT_Tiny as RGB_T
from PepperPepper.MOT.utils import misc as utils 
from PepperPepper.MOT.callbacks.engine_RGBT_graph_track_gnnloss import train_one_epoch, evaluate
import PepperPepper.MOT.datasets.samplers as samplers   
from PepperPepper.MOT.models.HGT_Track.deformable_detr_graph_track_gnnloss import build as build_model









def train(args):
    # 并没有使用到这个函数，无多卡。
    utils.init_distributed_mode(args)
    
    # 记录日志
    if utils.is_main_process():
        logger = SummaryWriter(os.path.join(args.output_dir, 'log'))
    my_map = 0 # 记录最好的mAP

    # 并没有发现masks相关的参数设置
    # if args.frozen_weights is not None:
    #     assert args.masks, "Frozen training is meant for segmentation only"
    # os.environ['CUDA_LAUNCH_BLOCKING'] = '0'
    device = torch.device(args.device)

    dataset_train = RGB_T(args, 'train')
    dataset_val = RGB_T(args, 'test')

    # input output shapes 自定义设置
    dataset_val.default_resolution[0], dataset_val.default_resolution[1] = args.input_h, args.input_w
    print(args.input_h, args.input_w)
    print(dataset_val.default_resolution)
    args.output_h = args.input_h // args.down_ratio
    args.output_w = args.input_w // args.down_ratio
    args.input_res = max(args.input_h, args.input_w)
    args.output_res = max(args.output_h, args.output_w)
    # threshold
    args.out_thresh = max(args.track_thresh, args.out_thresh)
    args.pre_thresh = max(args.track_thresh, args.pre_thresh)
    args.new_thresh = max(args.track_thresh, args.new_thresh)
    args.match_thresh = 0.9
    print(args)
    print("trainset #samples: ", len(dataset_train))
    print("valset #samples: ", len(dataset_val))

    # fix the seed for reproducibility
    seed = args.seed + utils.get_rank()
    torch.manual_seed(seed)

    def worker_init_fn(worker_id):
        np.random.seed(seed + worker_id)
        random.seed(seed + worker_id)

    # create model for tracking
    model, criterion, postprocessors = build_model(args)
    model.to(device)
    # print(model)

    model_without_ddp = model
    n_parameters = sum(p.numel() for p in model.parameters() if p.requires_grad)
    print('number of params:', n_parameters)

    if args.distributed:
        if args.cache_mode:
            sampler_train = samplers.NodeDistributedSampler(dataset_train)
            sampler_val = samplers.NodeDistributedSampler(dataset_val, shuffle=False)
        else:
            sampler_train = samplers.DistributedSampler(dataset_train)
            sampler_val = samplers.DistributedSampler(dataset_val, shuffle=False)
    else:
        sampler_train = torch.utils.data.RandomSampler(dataset_train)
        sampler_val = torch.utils.data.SequentialSampler(dataset_val)

    batch_sampler_train = torch.utils.data.BatchSampler(
        sampler_train, args.batch_size, drop_last=True)

    data_loader_train = DataLoader(dataset_train, batch_sampler=batch_sampler_train, num_workers=args.num_workers,
                                   pin_memory=True, worker_init_fn=worker_init_fn)
    data_loader_val = DataLoader(dataset_val, 1, sampler=sampler_val,
                                 drop_last=False, num_workers=args.num_workers,
                                 pin_memory=True)

    def match_name_keywords(n, name_keywords):
        out = False
        for b in name_keywords:
            if b in n:
                out = True
                break
        return out

    param_dicts = [
        {
            "params":
                [p for n, p in model_without_ddp.named_parameters()
                 if not match_name_keywords(n, args.lr_linear_proj_names) and p.requires_grad],
            "lr": args.lr,
        },
        {
            "params": [p for n, p in model_without_ddp.named_parameters() if
                       match_name_keywords(n, args.lr_linear_proj_names) and p.requires_grad],
            "lr": args.lr * args.lr_linear_proj_mult,
        }
    ]
    optimizer = torch.optim.AdamW(param_dicts, lr=args.lr,
                                  weight_decay=args.weight_decay)

    lr_scheduler = torch.optim.lr_scheduler.StepLR(optimizer, args.lr_drop)

    if args.distributed:
        # sync BN #
        model = torch.nn.SyncBatchNorm.convert_sync_batchnorm(model).to(device)
        model = torch.nn.parallel.DistributedDataParallel(model, device_ids=[args.gpu], find_unused_parameters=True)
        model_without_ddp = model.module

    print("Loading base ds...")

    base_ds_r = dataset_val.coco_r
    base_ds_i = dataset_val.coco_i
    print("Loading base ds done.")

    if args.frozen_weights is not None:
        checkpoint = torch.load(args.frozen_weights, map_location='cpu')
        model_without_ddp.detr.load_state_dict(checkpoint['model'])

    output_dir = Path(args.output_dir)
    if args.resume:
        if args.resume.startswith('https'):
            checkpoint = torch.hub.load_state_dict_from_url(
                args.resume, map_location='cpu', check_hash=True)
        else:
            checkpoint = torch.load(args.resume, map_location='cpu')
        model_without_ddp.load_state_dict(checkpoint['model'])
        missing_keys = []
        unexpected_keys = []
        print("Loading ", args.resume)
        print("loading all.")

        unexpected_keys = [k for k in unexpected_keys if not (k.endswith('total_params') or k.endswith('total_ops'))]
        if len(missing_keys) > 0:
            print('Missing Keys: {}'.format(missing_keys))
        if len(unexpected_keys) > 0:
            print('Unexpected Keys: {}'.format(unexpected_keys))
        if not args.eval and 'optimizer' in checkpoint and 'lr_scheduler' in checkpoint and 'epoch' in checkpoint and args.recover:
            import copy
            p_groups = copy.deepcopy(optimizer.param_groups)
            optimizer.load_state_dict(checkpoint['optimizer'])
            for pg, pg_old in zip(optimizer.param_groups, p_groups):
                pg['lr'] = pg_old['lr']
                pg['initial_lr'] = pg_old['initial_lr']
            # print(optimizer.param_groups)
            lr_scheduler.load_state_dict(checkpoint['lr_scheduler'])
            # todo: this is a hack for doing experiment that resume from checkpoint and also modify lr scheduler (e.g., decrease lr in advance).
            args.override_resumed_lr_drop = True
            if args.override_resumed_lr_drop:
                print(
                    'Warning: (hack) args.override_resumed_lr_drop is set to True, so args.lr_drop would override lr_drop in resumed lr_scheduler.')
                lr_scheduler.step_size = args.lr_drop
                lr_scheduler.base_lrs = list(map(lambda group: group['initial_lr'], optimizer.param_groups))
            lr_scheduler.step(lr_scheduler.last_epoch)
            args.start_epoch = checkpoint['epoch'] + 1

    if args.eval:
        test_stats_r, coco_evaluator_r = evaluate(model, criterion, postprocessors,
                                                  data_loader_val, base_ds_r, device, args.output_dir, args.half, True)
        test_stats_i, coco_evaluator_i = evaluate(model, criterion, postprocessors,
                                                  data_loader_val, base_ds_i, device, args.output_dir, args.half, False)

        if args.output_dir:
            utils.save_on_master(coco_evaluator_r.coco_eval["bbox"].eval, output_dir / "eval_r.pth")
            utils.save_on_master(coco_evaluator_i.coco_eval["bbox"].eval, output_dir / "eval_i.pth")
        return

    print("Start training")
    start_time = time.time()
    scaler = torch.cuda.amp.GradScaler(enabled=args.half)
    for epoch in range(args.start_epoch, args.epochs):
        if args.distributed:
            sampler_train.set_epoch(epoch)

        train_stats = train_one_epoch(
            model, criterion, data_loader_train, optimizer, device, epoch, args.clip_max_norm,
            adaptive_clip=args.adaptive_clip, scaler=scaler, half=args.half, args=args)
        lr_scheduler.step()

        if args.output_dir:
            checkpoint_paths = [output_dir / 'checkpoint.pth']
            # extra checkpoint before LR drop and every 5 epochs
            if (epoch + 1) % args.lr_drop == 0 or (epoch + 1) % 50 == 0:
                checkpoint_paths.append(output_dir / f'checkpoint{epoch:04}.pth')
            for checkpoint_path in checkpoint_paths:
                utils.save_on_master({
                    'model': model_without_ddp.state_dict(),
                    'optimizer': optimizer.state_dict(),
                    'lr_scheduler': lr_scheduler.state_dict(),
                    'epoch': epoch,
                    'args': args,
                }, checkpoint_path)

            log_stats = {**{f'train_{k}': v for k, v in train_stats.items()},
                         'epoch': epoch,
                         'n_parameters': n_parameters}

            # tensorboard logger #
            if utils.is_main_process():
                logger.add_scalar("LR/train", log_stats['train_lr'], epoch)
                logger.add_scalar("Loss/train", log_stats['train_loss'], epoch)
                logger.add_scalar("HMLoss/train", log_stats['train_hm'], epoch)
                logger.add_scalar("REGLoss/train", log_stats['train_reg'], epoch)
                logger.add_scalar("WHLoss/train", log_stats['train_wh'], epoch)
                logger.add_scalar("GIOULoss/train", log_stats['train_giou'], epoch)
                logger.add_scalar("BOXLoss/train", log_stats['train_boxes'], epoch)
                logger.add_scalar("TrackingLoss/train", log_stats['train_tracking'], epoch)

        if epoch % 1 == 0:
            test_stats, coco_evaluator = evaluate(model, criterion, postprocessors,
                                                  data_loader_val, base_ds_r, device, args.output_dir, args.half,
                                                  True)

            # valbest save#
            avg_map = np.mean([
                test_stats['coco_eval_bbox'][0],
                test_stats['coco_eval_bbox'][1],
                test_stats['coco_eval_bbox'][3],
                test_stats['coco_eval_bbox'][4],
                test_stats['coco_eval_bbox'][5]

            ])
            if avg_map >= my_map:
                my_map = float(avg_map)
                utils.save_on_master({
                    'model': model_without_ddp.state_dict(),
                    'optimizer': optimizer.state_dict(),
                    'lr_scheduler': lr_scheduler.state_dict(),
                    'epoch': epoch,
                    'args': args,
                    'mAP': [
                        test_stats['coco_eval_bbox'][0],
                        test_stats['coco_eval_bbox'][1],
                        test_stats['coco_eval_bbox'][3],
                        test_stats['coco_eval_bbox'][4],
                        test_stats['coco_eval_bbox'][5]

                    ],
                }, output_dir / 'val_best_r.pth')

        # log_stats = {**{f'train_{k}': v for k, v in train_stats.items()},
        #              **{f'test_{k}': v for k, v in test_stats.items()},
        #              'epoch': epoch,
        #              'n_parameters': n_parameters}
        #
        # # tensorboard logger #
        # if args.output_dir and utils.is_main_process():
        #     logger.add_scalar("VISBLE: *************************************************", epoch)
        #     logger.add_scalar("Loss/test", log_stats['test_loss'], epoch)
        #     logger.add_scalar("HMLoss/test", log_stats['test_hm'], epoch)
        #     logger.add_scalar("REGLoss/test", log_stats['test_reg'], epoch)
        #     logger.add_scalar("WHLoss/test", log_stats['test_wh'], epoch)
        #     logger.add_scalar("GIOULoss/test", log_stats['test_giou'], epoch)
        #     logger.add_scalar("BOXLoss/test", log_stats['test_boxes'], epoch)
        #     logger.add_scalar("TrackingLoss/test", log_stats['test_tracking'], epoch)
        #
        #     logger.add_scalar("mAP_ALL/test", log_stats['test_coco_eval_bbox'][0], epoch)
        #     logger.add_scalar("mAP_ALL_05/test", log_stats['test_coco_eval_bbox'][1], epoch)
        #     logger.add_scalar("mAP_SMALL/test", log_stats['test_coco_eval_bbox'][3], epoch)
        #     logger.add_scalar("mAP_MEDIUM/test", log_stats['test_coco_eval_bbox'][4], epoch)
        #     logger.add_scalar("mAP_Large/test", log_stats['test_coco_eval_bbox'][5], epoch)
        #
        #     if args.output_dir and utils.is_main_process():
        #         with (output_dir / "log_r.txt").open("a") as f:
        #             f.write(json.dumps(log_stats) + "\n")
        # #######################################################################################################################################
            test_stats, coco_evaluator = evaluate(model, criterion, postprocessors,
                                                  data_loader_val, base_ds_i, device, args.output_dir, args.half,
                                                  False)

            # valbest save#
            avg_map = np.mean([
                test_stats['coco_eval_bbox'][0],
                test_stats['coco_eval_bbox'][1],
                test_stats['coco_eval_bbox'][3],
                test_stats['coco_eval_bbox'][4],
                test_stats['coco_eval_bbox'][5]

            ])
            if avg_map >= my_map:
                my_map = float(avg_map)
                utils.save_on_master({
                    'model': model_without_ddp.state_dict(),
                    'optimizer': optimizer.state_dict(),
                    'lr_scheduler': lr_scheduler.state_dict(),
                    'epoch': epoch,
                    'args': args,
                    'mAP': [
                        test_stats['coco_eval_bbox'][0],
                        test_stats['coco_eval_bbox'][1],
                        test_stats['coco_eval_bbox'][3],
                        test_stats['coco_eval_bbox'][4],
                        test_stats['coco_eval_bbox'][5]

                    ],
                }, output_dir / 'val_best_i.pth')
        #
        # log_stats = {**{f'train_{k}': v for k, v in train_stats.items()},
        #              **{f'test_{k}': v for k, v in test_stats.items()},
        #              'epoch': epoch,
        #              'n_parameters': n_parameters}
        #
        # # tensorboard logger #
        # if args.output_dir and utils.is_main_process():
        #     logger.add_scalar("THERMAL: *************************************************", epoch)
        #     logger.add_scalar("Loss/test", log_stats['test_loss'], epoch)
        #     logger.add_scalar("HMLoss/test", log_stats['test_hm'], epoch)
        #     logger.add_scalar("REGLoss/test", log_stats['test_reg'], epoch)
        #     logger.add_scalar("WHLoss/test", log_stats['test_wh'], epoch)
        #     logger.add_scalar("GIOULoss/test", log_stats['test_giou'], epoch)
        #     logger.add_scalar("BOXLoss/test", log_stats['test_boxes'], epoch)
        #     logger.add_scalar("TrackingLoss/test", log_stats['test_tracking'], epoch)
        #
        #     logger.add_scalar("mAP_ALL/test", log_stats['test_coco_eval_bbox'][0], epoch)
        #     logger.add_scalar("mAP_ALL_05/test", log_stats['test_coco_eval_bbox'][1], epoch)
        #     logger.add_scalar("mAP_SMALL/test", log_stats['test_coco_eval_bbox'][3], epoch)
        #     logger.add_scalar("mAP_MEDIUM/test", log_stats['test_coco_eval_bbox'][4], epoch)
        #     logger.add_scalar("mAP_Large/test", log_stats['test_coco_eval_bbox'][5], epoch)

        if args.output_dir and utils.is_main_process():
            with (output_dir / "log_i.txt").open("a") as f:
                f.write(json.dumps(log_stats) + "\n")

            # # for evaluation logs
            # if coco_evaluator is not None:
            #     (output_dir / 'eval').mkdir(exist_ok=True)
            #     if "bbox" in coco_evaluator.coco_eval:
            #         filenames = ['latest_r.pth']
            #         if epoch % 50 == 0:
            #             filenames.append(f'{epoch:03}_r.pth')
            #         for name in filenames:
            #             torch.save(coco_evaluator.coco_eval["bbox"].eval,
            #                        output_dir / "eval" / name)

    total_time = time.time() - start_time
    total_time_str = str(datetime.timedelta(seconds=int(total_time)))
    print('Training time {}'.format(total_time_str))
