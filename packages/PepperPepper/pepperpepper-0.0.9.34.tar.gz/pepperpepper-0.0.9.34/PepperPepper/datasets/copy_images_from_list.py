import os
import shutil


def copy_images_from_list(txt_path, src_img_folder, dest_folder):
    """
    从文本文件中读取图片路径列表，并将图片复制到目标文件夹

    参数:
        txt_path (str): 包含图片路径列表的文本文件路径
        src_img_folder (str): 原始图片所在的根目录
        dest_folder (str): 目标文件夹路径（图片将复制到这里）
    """
    # 创建目标文件夹（如果不存在）
    os.makedirs(dest_folder, exist_ok=True)
    image_exts = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff'}

    # 读取文本文件内容
    with open(txt_path, 'r', encoding='utf-8') as file:
        image_paths = [line.strip() for line in file if line.strip()]

    # 复制图片
    copied_count = 0
    for rel_path in image_paths:
        # 构建完整源路径
        for ext in image_exts:
            src_path = os.path.join(src_img_folder, rel_path+ext)

            # 检查文件是否存在
            if not os.path.exists(src_path):
                print(f"警告: 文件不存在 - {src_path}")
                continue

            # 构建目标路径（保持原文件名）
            filename = os.path.basename(rel_path)
            dest_path = os.path.join(dest_folder, filename)

            # 处理重名文件（避免覆盖）
            counter = 1
            base, ext = os.path.splitext(filename)
            while os.path.exists(dest_path):
                new_name = f"{base}_{counter}{ext}"
                dest_path = os.path.join(dest_folder, new_name)
                counter += 1

            # 复制文件
            shutil.copy2(src_path, dest_path)
            print(f"已复制: {src_path} -> {dest_path}")
            copied_count += 1

    print(f"\n操作完成! 成功复制 {copied_count}/{len(image_paths) * len(image_exts)} 张图片")
    print(f"目标文件夹: {os.path.abspath(dest_folder)}")


# 示例用法
if __name__ == "__main__":
    # 替换为你的实际路径
    text_file = "/mnt/d/code/algorithms/IRSTD/BasicIRSTD/datasets/NUDT-SIRST/img_idx/test_NUDT-SIRST.txt"  # 包含图片路径列表的文本文件
    source_folder = "/mnt/d/code/algorithms/IRSTD/BasicIRSTD/datasets/NUDT-SIRST/images"  # 原始图片文件夹
    destination_folder = "/mnt/d/code/algorithms/IRSTD/BasicIRSTD/datasets/NUDT-SIRST/images_test"  # 目标文件夹

    copy_images_from_list(text_file, source_folder, destination_folder)