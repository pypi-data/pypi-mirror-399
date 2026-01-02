# import os
# import cv2
# import numpy as np
# from pathlib import Path
#
#
# def process_directory(img_path, mask_path, output_img_dir, output_txt_dir):
#     # 确保输出目录存在
#     os.makedirs(output_img_dir, exist_ok=True)
#     os.makedirs(output_txt_dir, exist_ok=True)
#
#     # 读取原始图像和mask图像
#     img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)  # 保留原始通道数
#     mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)  # 以灰度模式读取mask
#
#     if img is None:
#         print(f"错误：无法读取图像 {img_path}")
#         return []
#     if mask is None:
#         print(f"错误：无法读取mask {mask_path}")
#         return []
#
#     # 转换灰度图为三通道（如果是灰度图）
#     if len(img.shape) == 2:  # 灰度图只有一个通道
#         img_display = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
#     elif img.shape[2] == 1:  # 单通道图像
#         img_display = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
#     elif img.shape[2] == 3:  # 三通道图像
#         img_display = img.copy()
#     elif img.shape[2] == 4:  # 四通道图像（带透明度）
#         img_display = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
#     else:
#         print(f"警告：未知图像通道数 {img.shape}，尝试转换为三通道")
#         img_display = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
#
#     # 获取所有唯一像素值（目标ID）
#     unique_vals = np.unique(mask)
#     # 移除背景值0
#     target_vals = [v for v in unique_vals if v > 0]
#
#     # 存储目标信息
#     target_info = []
#
#     # 处理每个目标
#     for target_val in target_vals:
#         # 创建当前目标的二值掩码
#         target_mask = np.zeros_like(mask, dtype=np.uint8)
#         target_mask[mask == target_val] = 255
#
#         # 获取所有非零像素的坐标
#         points = np.argwhere(target_mask == 255)
#         if len(points) == 0:
#             continue
#
#         # 提取x和y坐标
#         y_coords = points[:, 0]
#         x_coords = points[:, 1]
#
#         # 计算边界框 [x, y, w, h]
#         x_min = np.min(x_coords)
#         x_max = np.max(x_coords)
#         y_min = np.min(y_coords)
#         y_max = np.max(y_coords)
#         w = x_max - x_min + 1  # 加1确保包含所有像素
#         h = y_max - y_min + 1  # 加1确保包含所有像素
#         x = x_min
#         y = y_min
#
#         # 计算边界框中心点
#         bbox_center_x = x_min + w // 2
#         bbox_center_y = y_min + h // 2
#
#         # 计算质心（几何中心）
#         centroid_x = np.mean(x_coords)
#         centroid_y = np.mean(y_coords)
#
#         # 在原始图像上绘制边界框和中心点
#         # 对于单个点目标，绘制一个小的矩形框
#         if w == 1 and h == 1:
#             # 绘制一个小矩形（3x3像素）表示单个点
#             cv2.rectangle(img_display, (x_min - 1, y_min - 1), (x_min + 1, y_min + 1), (0, 0, 255), 1)
#         else:
#             cv2.rectangle(img_display, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)
#
#         # 绘制中心点
#         cv2.circle(img_display, (int(bbox_center_x), int(bbox_center_y)), 3, (0, 255, 0), -1)  # 绿色：边界框中心
#         cv2.circle(img_display, (int(centroid_x), int(centroid_y)), 3, (255, 0, 0), -1)  # 蓝色：质心
#
#         # 绘制连接线
#         cv2.line(img_display,
#                  (int(bbox_center_x), int(bbox_center_y)),
#                  (int(centroid_x), int(centroid_y)),
#                  (0, 255, 255), 1)
#
#         # 添加目标ID标签
#         cv2.putText(img_display, f"ID:{target_val}", (int(x_min), int(y_min) - 5),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)
#
#         # 保存目标信息 (目标ID, 质心x, 质心y, 边界框中心x, 边界框中心y, 高度h, 宽度w)
#         target_info.append((
#             target_val,
#             centroid_x, centroid_y,
#             bbox_center_x, bbox_center_y,
#             h, w
#         ))
#
#     # 保存标记图像
#     output_img_path = os.path.join(output_img_dir, os.path.basename(img_path))
#
#     # 根据原始图像类型保存
#     if len(img.shape) == 2:  # 原始是灰度图
#         # 转换为灰度保存
#         result_gray = cv2.cvtColor(img_display, cv2.COLOR_BGR2GRAY)
#         cv2.imwrite(output_img_path, result_gray)
#     else:
#         cv2.imwrite(output_img_path, img_display)
#
#     # 保存目标信息到TXT文件
#     if target_info:
#         txt_filename = os.path.splitext(os.path.basename(img_path))[0] + ".txt"
#         output_txt_path = os.path.join(output_txt_dir, txt_filename)
#
#         with open(output_txt_path, 'w') as f:
#             # 写入图片名称
#             f.write(f"{os.path.basename(img_path)}")
#
#             # 写入每个目标的信息（按目标ID排序）
#             for info in sorted(target_info, key=lambda x: x[0]):
#                 # 解包信息
#                 target_id, cx, cy, bcx, bcy, h, w = info
#                 # 格式：目标ID 质心x 质心y 边界框中心x 边界框中心y 高度 宽度
#                 f.write(f"\t{target_id}\t{cx:.1f}\t{cy:.1f}\t{bcx:.1f}\t{bcy:.1f}\t{h}\t{w}")
#
#         print(f"已保存目标信息: {output_txt_path}")
#
#     print(f"已保存标记图像: {output_img_path}")
#     return target_info
#
#
#
#
#
#
#
#
#
#
#
# def draw_bounding_boxes_from_mask(root_dir="train"):
#     # 遍历根目录下的所有子目录
#     for class_dir in Path(root_dir).iterdir():
#         if not class_dir.is_dir():
#             continue
#
#         img_dir = class_dir / "img"
#         mask_dir = class_dir / "mask"
#         output_img_dir = class_dir / "annotated"  # 输出图像目录
#         output_txt_dir = class_dir / "bbox_info"  # 输出TXT目录
#
#
#         # 确保img和mask目录存在
#         if not img_dir.exists() or not mask_dir.exists():
#             print(f"跳过目录 {class_dir}，缺少img或mask文件夹")
#             continue
#
#         # 遍历目录中所有常见图片格式的文件
#         for img_path in img_dir.rglob("*"):
#             # 检查文件扩展名是否为常见图片格式
#             if img_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp"}:
#                 # 获取不带扩展名的文件名
#                 base_name = img_path.stem
#
#                 # 在mask目录中查找匹配的文件（不考虑扩展名）
#                 mask_candidates = list(mask_dir.glob(f"{base_name}.*"))
#
#                 # 过滤掉非图像文件
#                 mask_candidates = [f for f in mask_candidates if f.suffix.lower() in {
#                     ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp", ".pgm", ".pbm", ".tif"}]
#
#                 # 检查是否找到掩码文件
#                 if not mask_candidates:
#                     print(f"警告：找不到 {base_name} 对应的mask文件")
#                     continue
#
#                 # 如果有多个匹配，取第一个
#                 if len(mask_candidates) > 1:
#                     print(f"警告：找到多个匹配的mask文件，使用第一个: {mask_candidates[0]}")
#
#                 mask_path = mask_candidates[0]
#                 print(f"处理图像: {img_path} -> 掩码: {mask_path}")
#
#                 process_directory(
#                     str(img_path),
#                     str(mask_path),
#                     str(output_img_dir),
#                     str(output_txt_dir)
#                 )
#             else:
#                 print(f"找不到图像:{img_path}")
#
# if __name__ == "__main__":
#     # 设置根目录（默认当前目录下的train文件夹）
#     draw_bounding_boxes_from_mask("train")































import os
import cv2
import numpy as np
from pathlib import Path

def process_directory(img_path, mask_path, output_img_dir, output_txt_dir):
    # 确保输出目录存在
    os.makedirs(output_img_dir, exist_ok=True)
    os.makedirs(output_txt_dir, exist_ok=True)

    # 读取原始图像和mask图像
    img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)  # 保留原始通道数
    mask = cv2.imread(mask_path, cv2.IMREAD_GRAYSCALE)  # 以灰度模式读取mask

    if img is None:
        print(f"错误：无法读取图像 {img_path}")
        return []
    if mask is None:
        print(f"错误：无法读取mask {mask_path}")
        return []

    # 创建用于显示标记的三通道图像
    if len(img.shape) == 2:  # 灰度图只有一个通道
        # 创建三通道版本用于标记
        img_display = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        # 保留原始灰度图像用于背景
        img_gray = img.copy()
    elif img.shape[2] == 1:  # 单通道图像
        img_display = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        img_gray = img[:, :, 0].copy()
    elif img.shape[2] == 3:  # 三通道图像
        img_display = img.copy()
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)  # 创建灰度版本
    elif img.shape[2] == 4:  # 四通道图像（带透明度）
        img_display = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        img_gray = cv2.cvtColor(img_display, cv2.COLOR_BGR2GRAY)
    else:
        print(f"警告：未知图像通道数 {img.shape}，尝试转换为三通道")
        img_display = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        img_gray = img_display.copy() if len(img_display.shape) == 2 else cv2.cvtColor(img_display, cv2.COLOR_BGR2GRAY)

    # 获取所有唯一像素值（目标ID）
    unique_vals = np.unique(mask)
    # 移除背景值0
    target_vals = [v for v in unique_vals if v > 0]

    # 存储目标信息
    target_info = []

    # 处理每个目标
    for target_val in target_vals:
        # 创建当前目标的二值掩码
        target_mask = np.zeros_like(mask, dtype=np.uint8)
        target_mask[mask == target_val] = 255

        # 获取所有非零像素的坐标
        points = np.argwhere(target_mask == 255)
        if len(points) == 0:
            continue

        # 提取x和y坐标
        y_coords = points[:, 0]
        x_coords = points[:, 1]

        # 计算边界框 [x, y, w, h]
        x_min = np.min(x_coords)
        x_max = np.max(x_coords)
        y_min = np.min(y_coords)
        y_max = np.max(y_coords)
        w = x_max - x_min + 1  # 加1确保包含所有像素
        h = y_max - y_min + 1  # 加1确保包含所有像素
        x = x_min
        y = y_min

        # 计算边界框中心点
        bbox_center_x = x_min + w // 2
        bbox_center_y = y_min + h // 2

        # 计算质心（几何中心）
        centroid_x = np.mean(x_coords)
        centroid_y = np.mean(y_coords)

        # 在标记图像上绘制边界框和中心点
        # 对于单个点目标，绘制一个小的矩形框
        if w == 1 and h == 1:
            # 绘制一个小矩形（3x3像素）表示单个点
            cv2.rectangle(img_display, (x_min - 1, y_min - 1), (x_min + 1, y_min + 1), (0, 0, 255), 1)
        else:
            cv2.rectangle(img_display, (x_min, y_min), (x_max, y_max), (0, 0, 255), 2)

        # 绘制中心点 - 质心为红色，边界框中心为绿色
        cv2.circle(img_display, (int(bbox_center_x), int(bbox_center_y)), 3, (0, 255, 0), -1)  # 绿色：边界框中心
        cv2.circle(img_display, (int(centroid_x), int(centroid_y)), 3, (0, 0, 255), -1)  # 红色：质心

        # 绘制连接线
        cv2.line(img_display,
                 (int(bbox_center_x), int(bbox_center_y)),
                 (int(centroid_x), int(centroid_y)),
                 (0, 255, 255), 1)

        # 添加目标ID标签
        cv2.putText(img_display, f"ID:{target_val}", (int(x_min), int(y_min) - 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 255), 1)

        # 保存目标信息 (目标ID, 质心x, 质心y, 边界框中心x, 边界框中心y, 高度h, 宽度w)
        target_info.append((
            target_val,
            centroid_x, centroid_y,
            bbox_center_x, bbox_center_y,
            h, w
        ))

    # 保存标记图像 - 总是保存为彩色标记图像
    output_img_path = os.path.join(output_img_dir, os.path.basename(img_path))
    cv2.imwrite(output_img_path, img_display)

    # 保存目标信息到TXT文件
    if target_info:
        txt_filename = os.path.splitext(os.path.basename(img_path))[0] + ".txt"
        output_txt_path = os.path.join(output_txt_dir, txt_filename)

        with open(output_txt_path, 'w') as f:
            # 写入图片名称
            f.write(f"{os.path.basename(img_path)}\n")

            # 写入每个目标的信息（按目标ID排序）
            for info in sorted(target_info, key=lambda x: x[0]):
                # 解包信息
                target_id, cx, cy, bcx, bcy, h, w = info
                # 格式：目标ID 质心x 质心y 边界框中心x 边界框中心y 高度 宽度
                f.write(f"{target_id}\t{cx:.1f}\t{cy:.1f}\t{bcx:.1f}\t{bcy:.1f}\t{h}\t{w}\n")

        print(f"已保存目标信息: {output_txt_path}")

    print(f"已保存标记图像: {output_img_path}")
    return target_info

def draw_bounding_boxes_from_mask(root_dir="train"):
    # 遍历根目录下的所有子目录
    for class_dir in Path(root_dir).iterdir():
        if not class_dir.is_dir():
            continue

        img_dir = class_dir / "img"
        mask_dir = class_dir / "mask"
        output_img_dir = class_dir / "annotated"  # 输出图像目录
        output_txt_dir = class_dir / "bbox_info"  # 输出TXT目录

        # 确保img和mask目录存在
        if not img_dir.exists() or not mask_dir.exists():
            print(f"跳过目录 {class_dir}，缺少img或mask文件夹")
            continue

        # 遍历目录中所有常见图片格式的文件
        for img_path in img_dir.rglob("*"):
            # 检查文件扩展名是否为常见图片格式
            if img_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp"}:
                # 获取不带扩展名的文件名
                base_name = img_path.stem

                # 在mask目录中查找匹配的文件（不考虑扩展名）
                mask_candidates = list(mask_dir.glob(f"{base_name}.*"))

                # 过滤掉非图像文件
                mask_candidates = [f for f in mask_candidates if f.suffix.lower() in {
                    ".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tiff", ".webp", ".pgm", ".pbm", ".tif"}]

                # 检查是否找到掩码文件
                if not mask_candidates:
                    print(f"警告：找不到 {base_name} 对应的mask文件")
                    continue

                # 如果有多个匹配，取第一个
                if len(mask_candidates) > 1:
                    print(f"警告：找到多个匹配的mask文件，使用第一个: {mask_candidates[0]}")

                mask_path = mask_candidates[0]
                print(f"处理图像: {img_path} -> 掩码: {mask_path}")

                process_directory(
                    str(img_path),
                    str(mask_path),
                    str(output_img_dir),
                    str(output_txt_dir)
                )

if __name__ == "__main__":
    # 设置根目录（默认当前目录下的train文件夹）
    draw_bounding_boxes_from_mask("train")






















