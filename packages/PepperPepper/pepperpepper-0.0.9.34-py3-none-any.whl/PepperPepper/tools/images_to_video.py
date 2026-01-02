import cv2
import os
from PIL import Image


def images_to_video(input_dir, output_path, fps=30, image_format='png'):
    """
    将目录中的图片合成为视频
    :param input_dir: 图片目录路径
    :param output_path: 输出视频路径（以.mp4结尾）
    :param fps: 帧率（默认30帧/秒）
    :param image_format: 图片格式（默认jpg）
    """
    # 获取图片文件列表并按文件名排序
    images = [img for img in os.listdir(input_dir) if img.endswith(image_format)]
    images.sort()  # 确保按顺序处理

    if not images:
        raise ValueError("未找到图片文件")

    # 读取第一张图片获取尺寸
    img_path = os.path.join(input_dir, images[0])
    frame = cv2.imread(img_path)
    height, width, layers = frame.shape

    # 创建视频编码器
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # MP4编码
    video = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # 逐帧写入视频
    for image in images:
        img_path = os.path.join(input_dir, image)
        img = cv2.imread(img_path)
        video.write(img)
        print(f"已添加: {image}")

    video.release()
    print(f"视频保存至: {output_path}")


# 使用示例
if __name__ == "__main__":
    input_directory = "images/"  # 图片目录
    output_video = "output_video.mp4"  # 输出视频路径
    images_to_video(input_directory, output_video, fps=24)  # 24帧/秒