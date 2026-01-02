import os
import cv2
import numpy as np
from pathlib import Path
import re


def process_directory(img_path, mask_path, output_img_dir, output_txt_dir, new_filename=None):
    """
    处理图像和对应的mask，生成YOLO格式的标注文件，并将图像保存为JPG格式
    优化处理：每个类别在一帧中只出现一次，但可能有多个不同类别的目标

    参数:
    img_path: 原始图像路径
    mask_path: mask图像路径
    output_img_dir: 输出图像目录
    output_txt_dir: 输出标注文件目录
    new_filename: 新的文件名（不含扩展名）
    """
    # 确保输出目录存在
    os.makedirs(output_img_dir, exist_ok=True)
    os.makedirs(output_txt_dir, exist_ok=True)

    # 读取原始图像
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
    if img is None:
        print(f"错误：无法读取图像 {img_path}")
        return []

    # 获取图像尺寸
    img_height, img_width = img.shape[:2]

    # 转换图像为三通道BGR格式（确保能保存为JPG）
    if len(img.shape) == 2 or img.shape[2] == 1:  # 灰度图或单通道
        img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    elif img.shape[2] == 4:  # 四通道（RGBA）
        img_bgr = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
    elif img.shape[2] == 3:  # 三通道
        img_bgr = img.copy()
    else:
        print(f"警告：未知图像通道数 {img.shape}，尝试转换为三通道")
        img_bgr = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR) if len(img.shape) == 2 else img

    # 存储YOLO格式的标注信息
    yolo_annotations = []

    # 如果提供了mask路径，则处理mask
    if mask_path and os.path.exists(mask_path):
        mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)
        if mask is None:
            print(f"错误：无法读取mask {mask_path}")
        else:
            # 获取所有唯一像素值（目标ID）
            unique_vals = np.unique(mask)
            # 移除背景值0
            target_vals = [v for v in unique_vals if v > 0]

            # 处理每个目标值（每个值代表一个类别）
            for target_val in target_vals:
                # 创建当前目标的二值掩码
                target_mask = np.zeros_like(mask, dtype=np.uint8)
                target_mask[mask == target_val] = 255
                # class_id = target_val
                class_id = 0
                # 找到所有非零像素的位置
                y_coords, x_coords = np.where(target_mask == 255)

                if len(x_coords) == 0:
                    continue

                # 计算边界框（包含该类别所有像素）
                x_min, x_max = np.min(x_coords), np.max(x_coords)
                y_min, y_max = np.min(y_coords), np.max(y_coords)

                # 计算边界框尺寸
                w = x_max - x_min + 1
                h = y_max - y_min + 1

                # 计算YOLO格式的归一化坐标
                center_x = (x_min + w / 2) / img_width
                center_y = (y_min + h / 2) / img_height
                norm_width = w / img_width
                norm_height = h / img_height

                # 保存YOLO格式的标注
                yolo_annotations.append(
                    f"{int(class_id)} {center_x:.6f} {center_y:.6f} {norm_width:.6f} {norm_height:.6f}")

    # 确定输出文件名
    if new_filename:
        base_name = new_filename + ".jpg"
    else:
        base_name = os.path.splitext(os.path.basename(img_path))[0] + ".jpg"

    output_img_path = os.path.join(output_img_dir, base_name)

    # 保存图像为JPG格式（质量设为95）
    cv2.imwrite(output_img_path, img_bgr, [int(cv2.IMWRITE_JPEG_QUALITY), 95])

    # 保存YOLO格式的标注文件
    txt_filename = base_name.replace('.jpg', '.txt')
    output_txt_path = os.path.join(output_txt_dir, txt_filename)

    with open(output_txt_path, 'w') as f:
        for annotation in yolo_annotations:
            f.write(annotation + "\n")

    if yolo_annotations:
        print(f"已保存YOLO标注: {output_txt_path} (包含 {len(yolo_annotations)} 个目标)")
    else:
        print(f"已创建空标注文件: {output_txt_path}")

    return yolo_annotations


def extract_frame_number(filename):
    """从文件名中提取帧号，支持多种命名格式"""
    # 尝试匹配常见的帧号格式
    match = re.search(r'(\d+)\.(?:png|jpg|jpeg|bmp|tif|tiff|pgm|pbm)$', filename, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # 尝试匹配带前缀的帧号
    match = re.search(r'frame_?(\d+)\.', filename, re.IGNORECASE)
    if match:
        return int(match.group(1))

    # 尝试匹配带后缀的帧号
    match = re.search(r'_(\d+)\.', filename)
    if match:
        return int(match.group(1))

    # 如果以上都不匹配，尝试提取所有数字
    numbers = re.findall(r'\d+', filename)
    if numbers:
        return int(numbers[-1])  # 使用最后一个数字

    return 0  # 默认返回0


def satvideoirstd2Yolo(root_dir="train", output_dir="datasets"):
    output_datasets_dir = Path(output_dir)
    output_img_dir = output_datasets_dir / "images"
    output_labels_dir = output_datasets_dir / "labels"

    # 遍历根目录下的所有子目录（每个视频序列）
    for seq_dir in Path(root_dir).iterdir():
        if not seq_dir.is_dir():
            continue

        # 获取视频序列ID（目录名）
        seq_id = seq_dir.name

        img_dir = seq_dir / "img"
        mask_dir = seq_dir / "mask"

        # 确保img目录存在
        if not img_dir.exists():
            print(f"跳过序列 {seq_id}，缺少img文件夹")
            continue

        # 获取所有图像文件
        img_files = []
        for ext in ["*.png", "*.jpg", "*.jpeg", "*.bmp", "*.tif", "*.tiff", "*.pgm", "*.pbm"]:
            img_files.extend(sorted(img_dir.glob(ext)))  # 按文件名排序

        # 处理序列中的所有帧
        for img_path in img_files:
            # 提取帧号
            frame_num = extract_frame_number(img_path.name)

            # 创建新的文件名：序列ID_帧号
            new_filename = f"{seq_id}_{frame_num:06d}"  # 使用6位数字填充

            # 查找对应的mask文件
            mask_path = None
            if mask_dir.exists():
                # 尝试多种可能的扩展名
                for ext in [".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff", ".pgm", ".pbm"]:
                    candidate = mask_dir / f"{img_path.stem}{ext}"
                    if candidate.exists():
                        mask_path = candidate
                        break

            print(f"处理序列 {seq_id} 帧 {frame_num}: {img_path.name}")

            process_directory(
                str(img_path),
                str(mask_path) if mask_path else None,
                str(output_img_dir),
                str(output_labels_dir),
                new_filename=new_filename
            )

    print(f"完成所有处理！图像保存在: {output_img_dir}")
    print(f"标注文件保存在: {output_labels_dir}")


if __name__ == "__main__":
    # 设置根目录
    satvideoirstd2Yolo(
        "/mnt/d/code/CSIG/DeepPro/datasets/SatVideoIRSDT/train",
        "/mnt/d/code/CSIG/DeepPro/datasets/SatVideoIRSDT/yolo/train"
    )