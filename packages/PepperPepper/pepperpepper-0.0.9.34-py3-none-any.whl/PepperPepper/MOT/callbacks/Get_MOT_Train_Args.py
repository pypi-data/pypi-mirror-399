import argparse

# PepperPepper/MOT/callbacks/RGBT_Get_Args_Train.py
def get_args_parser_train():
    parser = argparse.ArgumentParser('MOT Track for RGBT-Tiny', add_help=True) # the name of the script 
    parser.add_argument('--ignoreIsCrowd', action='store_true') # 是否忽略IsCrowd标志，但实际未使用
    parser.add_argument('--lr', default=2e-5, type=float)   # initial learning rate
    parser.add_argument('--lr_linear_proj_names', default=['reference_points', 'sampling_offsets'], type=str, nargs='+') # the names of parameters to apply a different learning rate
    parser.add_argument('--lr_linear_proj_mult', default=0.1, type=float) # multiplier for the learning rate of linear projection parameters
    parser.add_argument('--batch_size', default=4, type=int) # batch size for training
    parser.add_argument('--weight_decay', default=1e-4, type=float) # weight decay for optimizer(训练过程中的权重会进行衰减)
    parser.add_argument('--epochs', default=10, type=int) # number of training epochs
    parser.add_argument('--lr_drop', default=40, type=int) # number of epochs after which to drop the learning rate
    parser.add_argument('--lr_drop_epochs', default=None, type=int, nargs='+') #未使用
    parser.add_argument('--clip_max_norm', default=0.1, type=float,
                        help='gradient clipping max norm') # maximum norm for gradient clipping

    # Model parameters 
    # 设置被冻结的权重路径
    parser.add_argument('--frozen_weights', type=str, default=None,
                        help="Path to the pretrained model. If set, only the mask head will be trained")
    
    # 预训练的权重路径
    parser.add_argument('--pretrained', type=str,
                        default=None,
                        help="pretrained")

    # * Transformer
    parser.add_argument('--d_model', default=[64, 128, 320, 512], type=int, nargs='+',
                        help="model dimensions in the transformer")

    parser.add_argument('--nheads', default=[1, 2, 5, 8], type=int, nargs='+',
                        help="Number of attention heads inside the transformer's attentions")

    parser.add_argument('--num_encoder_layers', default=[3, 4, 6, 3], type=int, nargs='+',
                        help="Number of encoding layers in the transformer")

    parser.add_argument('--num_decoder_layers', default=6, type=int,
                        help="Number of decoding layers in the transformer")

    parser.add_argument('--dim_feedforward_ratio', default=[8, 8, 4, 4], type=int, nargs='+',
                        help="Intermediate size of the feedforward layers dim ratio in the transformer blocks")

    parser.add_argument('--dropout', default=0.1, type=float,
                        help="Dropout applied in the transformer")

    parser.add_argument('--num_feature_levels', default=1, type=int, help='number of feature levels')

    parser.add_argument('--dec_n_points', default=9, type=int)

    parser.add_argument('--enc_n_points', default=[8, 8, 8, 8], type=int, nargs='+')

    parser.add_argument('--down_sample_ratio', default=[8, 4, 2, 1], type=int, nargs='+')

    parser.add_argument('--hidden_dim', default=256, type=int,
                        help="Size of the embeddings (dimension of the transformer)")
    parser.add_argument('--linear', action='store_true',
                        help='linear vit')

    parser.add_argument('--heads', default=['hm', 'reg', 'wh', 'center_offset', 'tracking'], type=str, nargs='+')

    # * Loss coefficients
    parser.add_argument('--hm_weight', default=1, type=float)
    parser.add_argument('--off_weight', default=1, type=float)
    parser.add_argument('--wh_weight', default=0.1, type=float)
    parser.add_argument('--ct_offset_weight', default=0.1, type=float)
    parser.add_argument('--boxes_weight', default=0.5, type=float)
    parser.add_argument('--giou_weight', default=0.4, type=float)
    parser.add_argument('--norm_factor', default=1.0, type=float)
    parser.add_argument('--tracking_weight', default=1, type=float)
    parser.add_argument('--gnn_weight', default=0.01, type=float)

    # dataset parameters
    parser.add_argument('--dataset_file', default='rgbt_tiny')
    parser.add_argument('--datatype', default='rgb')
    parser.add_argument('--data_dir', default='/mnt/d/code/IRSTD/datasets/VT-Tiny-MOT', type=str)
    parser.add_argument('--data_dir_ch', default='', type=str)
    parser.add_argument('--remove_difficult', action='store_true')
    parser.add_argument('--gnn_layer_num', default=1, type=int,
                        help="Layer numbers of gnn")
    parser.add_argument('--output_dir', default='./worksdir/rgbt/det_graph_track2_1gnnlayer_gnnloss++',
                        help='path where to save, empty for no saving')
    parser.add_argument('--device', default='cuda:0',
                        help='device to use for training / testing')
    parser.add_argument('--seed', default=42, type=int)

    parser.add_argument('--resume',
                        default='',
                        help='resume from checkpoint')
    parser.add_argument('--start_epoch', default=5, type=int, metavar='5',
                        help='start epoch')
    parser.add_argument('--eval', default=False, action='store_true')
    parser.add_argument('--num_workers', default=8, type=int)
    parser.add_argument('--cache_mode', default=False, action='store_true', help='whether to cache images on memory')
    parser.add_argument('--half', default=False, action='store_true', help='half precision')

    # centers
    parser.add_argument('--num_classes', default=7, type=int)
    parser.add_argument('--input_h', default=512, type=int)
    parser.add_argument('--input_w', default=640, type=int)
    parser.add_argument('--down_ratio', default=4, type=int) # downsample ratio for embedding layers
    parser.add_argument('--dense_reg', type=int, default=1, help='')
    parser.add_argument('--trainval', action='store_true',
                        help='include validation in training and '
                             'test on test set')

    parser.add_argument('--K', type=int, default=150,
                        help='max number of output objects.')

    parser.add_argument('--debug', action='store_true')

    # noise
    parser.add_argument('--not_rand_crop', action='store_true',
                        help='not use the random crop data augmentation'
                             'from CornerNet.')
    parser.add_argument('--not_max_crop', action='store_true',
                        help='used when the training dataset has'
                             'inbalanced aspect ratios.')
    parser.add_argument('--shift', type=float, default=0.05,
                        help='when not using random crop'
                             'apply shift augmentation.')
    parser.add_argument('--scale', type=float, default=0.05,
                        help='when not using random crop'
                             'apply scale augmentation.')
    parser.add_argument('--rotate', type=float, default=0,
                        help='when not using random crop'
                             'apply rotation augmentation.')
    parser.add_argument('--flip', type=float, default=0.5,
                        help='probability of applying flip augmentation.')
    parser.add_argument('--no_color_aug', action='store_true',
                        help='not use the color augmenation '
                             'from CornerNet')
    parser.add_argument('--aug_rot', type=float, default=0.2,
                        help='probability of applying '
                             'rotation augmentation.')

    # tracking
    parser.add_argument('--max_frame_dist', type=int, default=3)
    parser.add_argument('--merge_mode', type=int, default=1)
    parser.add_argument('--tracking', default=True, action='store_true')
    parser.add_argument('--pre_hm', action='store_true')
    parser.add_argument('--same_aug_pre', action='store_true')
    parser.add_argument('--zero_pre_hm', action='store_true')
    parser.add_argument('--hm_disturb', type=float, default=0.05)
    parser.add_argument('--lost_disturb', type=float, default=0.4)
    parser.add_argument('--fp_disturb', type=float, default=0.1)
    parser.add_argument('--pre_thresh', type=float, default=-1)
    parser.add_argument('--track_thresh', type=float, default=0.3)
    parser.add_argument('--new_thresh', type=float, default=0.3)
    parser.add_argument('--ltrb_amodal', action='store_true')
    parser.add_argument('--ltrb_amodal_weight', type=float, default=0.1)
    parser.add_argument('--public_det', action='store_true')
    parser.add_argument('--no_pre_img', action='store_true')
    parser.add_argument('--zero_tracking', action='store_true')
    parser.add_argument('--hungarian', action='store_true')
    parser.add_argument('--max_age', type=int, default=-1)
    parser.add_argument('--out_thresh', type=float, default=-1,
                        help='')
    parser.add_argument('--image_blur_aug', action='store_true',
                        help='blur image for aug.')
    parser.add_argument('--adaptive_clip', action='store_true',
                        help='adaptive_clip')
    
    parser.add_argument('--clip', type=bool, default=False,
                        help='whether to use gradient clipping')

    parser.add_argument('--small', action='store_true',
                        help='smaller dataset')

    parser.add_argument('--recover', action='store_true',
                        help='recovery optimizer.')
    
    
    return parser