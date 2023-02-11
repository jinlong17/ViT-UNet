MMSEG_HOME_PATH = '/home/gpu02/maskrcnn-lymphocyte-detection/mmsegmentation'
DATASET_HOME_PATH = '/home/gpu02/maskrcnn-lymphocyte-detection/datasets'
S = 1
DATASET = 'lysto'
MODEL_NAME = 'mobilenet_v3'
PATH_DATASET = f'{DATASET_HOME_PATH}/{DATASET}'
CONFIG_FILE_NAME = MODEL_NAME + '_s' + str(S)
PATH_CONFIG_FILE = f'{MMSEG_HOME_PATH}/configs/{DATASET}/{CONFIG_FILE_NAME}.py'
PATH_WORK_DIR = f'{MMSEG_HOME_PATH}/trained_models/{DATASET}/{MODEL_NAME}/setting{S}/'

# The new config inherits a base config to highlight the necessary modification
_base_ = '../mobilenet_v3/lraspp_m-v3-d8_512x1024_320k_cityscapes.py'

model = dict(
    type='EncoderDecoder',
    # backbone=dict(
    #     type='MobileNetV3',
    #     arch='large',
    #     out_indices=(1, 3, 16),
    #     norm_cfg=norm_cfg),
    decode_head=dict(
        type='LRASPPHead',
        # in_channels=(16, 24, 960),
        # in_index=(0, 1, 2),
        # channels=128,
        # input_transform='multiple_select',
        # dropout_ratio=0.1,
        num_classes=2,
        # norm_cfg=norm_cfg,
        # act_cfg=dict(type='ReLU'),
        # align_corners=False,
        loss_decode=dict(
            type='CrossEntropyLoss', use_sigmoid=False, loss_weight=1.0)),
    )

custom_imports = dict(
    imports=[
        # 'mmseg.models.backbones.lympnet2',
        'mmseg.core.utils.lymph_count_eval_hook',
    ],
    allow_failed_imports=False)

# Modify dataset related settings
dataset_type = 'LystoDataset'
data_root = PATH_DATASET
classes = ('background', 'lymphocyte')

data = dict(
    samples_per_gpu=1,
    workers_per_gpu=1,
    train=dict(
        type=dataset_type,
        data_root=data_root,
        img_dir='train_IHC',
        ann_dir='train_circular_masks_label',
        split='mmseg_splits/train_circular_masks.txt',
        # pipeline=[
        #     dict(type='LoadImageFromFile'),
        #     dict(type='LoadAnnotations'),
        #     dict(type='Resize', img_scale=(256, 256), keep_ratio=True),
        #     dict(type='RandomFlip', flip_ratio=0.5),
        #     dict(type='PhotoMetricDistortion'),
        #     dict(type='Normalize', mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True),
        #     dict(type='Pad', size=(256, 256), pad_val=0, seg_pad_val=255),
        #     dict(type='DefaultFormatBundle'),
        #     dict(type='Collect', keys=['img', 'gt_semantic_seg'])
        # ]
        ),
    val=dict(
        type=dataset_type,
        data_root=data_root,
        img_dir='val_IHC',
        ann_dir='val_circular_masks_label',
        split='mmseg_splits/val_circular_masks.txt',
        # pipeline=[
        #     dict(type='LoadImageFromFile'),
        #     dict(
        #         type='MultiScaleFlipAug',
        #         img_scale=(224, 224),
        #         flip=False,
        #         transforms=[
        #             dict(type='Resize', keep_ratio=True),
        #             dict(type='RandomFlip'),
        #             dict(type='Normalize', mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True),
        #             # dict(type='Pad', size_divisor=32),
        #             dict(type='ImageToTensor', keys=['img']),
        #             dict(type='Collect', keys=['img'])
        #         ])
        # ]
        ),
    test=dict(
        type=dataset_type,
        data_root=data_root,
        img_dir='test_IHC',
        ann_dir='test_circular_masks_label',
        split='mmseg_splits/test_circular_masks.txt',
        # pipeline=[
        #     dict(type='LoadImageFromFile'),
        #     dict(
        #         type='MultiScaleFlipAug',
        #         img_scale=(224, 224),
        #         flip=False,
        #         transforms=[
        #             dict(type='Resize', keep_ratio=True),
        #             dict(type='RandomFlip'),
        #             dict(type='Normalize', mean=[123.675, 116.28, 103.53], std=[58.395, 57.12, 57.375], to_rgb=True),
        #             # dict(type='Pad', size_divisor=32),
        #             dict(type='ImageToTensor', keys=['img']),
        #             dict(type='Collect', keys=['img'])
        #         ])
        # ]
        ))

custom_hooks = [
    dict(
        type='LymphCountEvalHook',
        eval_interval=2,
        file_prefix=MODEL_NAME,
        path_config=PATH_CONFIG_FILE,
        base_dir='eval1_circular_masks_label')
]

work_dir = PATH_WORK_DIR
load_from = f'{MMSEG_HOME_PATH}/checkpoints/lraspp_m-v3-d8_512x1024_320k_cityscapes_20201224_220337-cfe8fb07.pth'
# load_from = os.path.join(PATH_WORK_DIR, 'latest.pth')
# resume_from = os.path.join(PATH_WORK_DIR, 'latest.pth')

total_epochs = max_epochs = 30
runner = dict(_delete_=True, type='EpochBasedRunner', max_epochs=max_epochs)
optimizer = dict(type='SGD', lr=0.00025, momentum=0.9, weight_decay=0.0001, nesterov=True)
lr_config = dict(_delete_=True, policy='step', warmup='linear', warmup_iters=500, warmup_ratio=0.0025, step=[12, 20, 28])
# lr_config = dict(policy='poly', power=0.9, min_lr=0.0001, by_epoch=True)
evaluation = dict(interval=2, metric=['mIoU', 'mDice'], pre_eval=True)
log_config = dict(interval=10, hooks=[dict(type='TextLoggerHook'), dict(type='TensorboardLoggerHook')])
checkpoint_config = dict(interval=2, by_epoch=True)
dist_params = dict(backend='nccl')
# cudnn_benchmark = True
seed = 0
gpu_ids = range(1)
workflow = [('train', 1), ('val', 1)]
