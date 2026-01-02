from PepperPepper.environment import torch, nn, torchvision, Dataset, os, Image, np, transforms

class DGDataSetLoader(Dataset):
    def __init__(self, dataset_dir, train_name=['NUDT-SIRST', 'NUAA-SIRST'], eval_name=['IRSTD-1K'], patch_size=256, mode='train'):
        super(DGDataSetLoader, self).__init__()
        self.dataset_dir = dataset_dir
        self.train_name = train_name
        self.eval_name = eval_name
        self.patch_size = patch_size
        self.mode = mode

        if mode == 'train':
            self.image_names = []
            for name in self.train_name:
                with open(os.path.join(self.dataset_dir, name, 'img_idx', 'train_set.txt'), 'r') as f:
                    lines = f.read().splitlines()
                    self.image_names.extend([os.path.join(self.dataset_dir, name, 'images', line + '.png') for line in lines])
        elif mode == 'test':
            self.image_names = []
            for name in self.eval_name:
                with open(os.path.join(self.dataset_dir, name, 'img_idx', 'all_images.txt'), 'r') as f:
                    lines = f.read().splitlines()
                    self.image_names.extend([os.path.join(self.dataset_dir, name, 'images', line + '.png') for line in lines])
        else:
            self.image_names = []
            for name in self.train_name:
                with open(os.path.join(self.dataset_dir, name, 'img_idx', 'val_set.txt'), 'r') as f:
                    lines = f.read().splitlines()
                    self.image_names.extend([os.path.join(self.dataset_dir, name, 'images', line + '.png') for line in lines])


        self.transform = self.augmentation(mode=self.mode)


    def augmentation(self, mode='train'):
        if mode == 'train':
            transform = transforms.Compose([
                transforms.RandomHorizontalFlip(p=0.5),  # 随机水平翻转
                transforms.RandomVerticalFlip(p=0.5)    # 随机垂直翻转
            ])
        else:
            transform = transforms.Compose([
                transforms.RandomHorizontalFlip(p=0.5),  # 随机水平翻转
                transforms.RandomVerticalFlip(p=0.5)    # 随机垂直翻转
            ])

        return transform
    



    def __len__(self):
        return len(self.image_names)
    


    def __getitem__(self, idx):
        img = Image.open((self.image_names[idx]).replace('//', '/')).convert('I')
        mask_path = self.image_names[idx].replace('/images/', '/masks/')
        mask = Image.open((mask_path).replace('//', '/')).convert('I')


        # 转换为 PyTorch 张量
        img = torch.tensor(np.array(img, dtype=np.float32))/255.0  # 转换为浮点型张量
        mask = torch.tensor(np.array(mask, dtype=np.float32)) / 255.0  # 将掩码归一化到 [0, 1]

        # 如果掩码有多个通道，仅保留第一个通道
        if len(mask.shape) > 2:
            mask = mask[:, :, 0]


        # 添加通道维度
        img = img.unsqueeze(0)  # (H, W) -> (1, H, W)
        mask = mask.unsqueeze(0)  # (H, W) -> (1, H, W)


        # if img.shape != mask.shape:
        img = transforms.Resize((self.patch_size, self.patch_size), interpolation=Image.BILINEAR)(img)

        # mask = transforms.Resize((self.patch_size, self.patch_size), interpolation=Image.NEAREST)(mask)
        mask = transforms.Resize((self.patch_size, self.patch_size), interpolation=Image.BILINEAR)(mask)

        augmented = self.transform(torch.cat([img, mask], dim=0))
        img_patch, mask_patch = augmented[0:1], augmented[1:2]

        return img_patch, mask_patch




