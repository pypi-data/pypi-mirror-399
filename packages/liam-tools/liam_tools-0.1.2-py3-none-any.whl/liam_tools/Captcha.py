from os import path as ospath
from os import makedirs
from captcha.image import ImageCaptcha
from liam_tools.ustr import getRandom

def captchaImage(length=6, width=256, height=64, output_dir='captchas'):
    """
    生成验证码图片并保存到指定目录
    :param length: 验证码字符长度
    :param width: 图片宽度
    :param height: 图片高度
    :param output_dir: 存储目录
    :return: 保存后的完整文件路径
    """
    # 1. 确保输出目录存在
    if not ospath.exists(output_dir):
        makedirs(output_dir)

    # 2. 初始化生成器
    generator = ImageCaptcha(width=width, height=height)
    
    # 3. 获取随机字符
    captcha_text = getRandom(length)
    
    # 4. 构建文件路径
    file_name = f"{captcha_text}.png"
    file_path = ospath.join(output_dir, file_name)
    
    try:
        # 5. 直接写入文件
        generator.write(captcha_text, file_path)
        return file_path
    except Exception as e:
        # 实际开发中建议使用 logging 记录
        print(f"生成验证码失败: {e}")
        return None

if __name__ == '__main__':
    path = captchaImage(length=4, output_dir='temp_images')
    if path:
        print(f"验证码已保存至: {path}")