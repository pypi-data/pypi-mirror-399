from PIL.Image import open
from PIL.Image import Resampling
from os import path as ospath
from time import time
from liam_tools import path

def sizeKB(file_path):

    """获取文件大小: KB"""
    return ospath.getsize(file_path) / 1024 if ospath.isfile(file_path) else 0

def imgInfo(file_path):

    """获取图片信息"""
    if ospath.isfile(file_path):
        with open(file_path) as img:
            return img.width, img.height, img.format
    return 0, 0, None

def generateOutfile(infile):

    """通用生成输出路径逻辑"""
    path_name, file_name = path.split(infile)
    # 使用 utime.ftime() 生成唯一文件名
    new_name = f"{time()}_{file_name}"
    outfile = path.cacheImg(new_name)
    
    # 确保文件夹存在
    out_dir = ospath.dirname(outfile)
    if out_dir:
        path.mkfolder(out_dir)
    return outfile

def compressByQuality(infile, outfile=None, target_kb=128, step=10, initial_quality=80) -> str:
    """
    不改变图片尺寸压缩到指定大小
    """
    if outfile is None:
        outfile = generateOutfile(infile)

    current_size = sizeKB(infile)
    if current_size <= target_kb:
        return infile

    # 只打开一次源文件
    with open(infile) as im:
        # 如果是 RGBA 模式（PNG），保存为 JPEG 需要转为 RGB
        if im.mode in ("RGBA", "P"):
            im = im.convert("RGB")
        
        tmp_quality = initial_quality
        while current_size > target_kb and tmp_quality > 0:
            im.save(outfile, "JPEG", quality=tmp_quality, optimize=True)
            current_size = sizeKB(outfile)
            tmp_quality -= step
            
    return outfile

def resizeImage(infile, outfile=None, target_width=720) -> str:

    """
    等比例修改图片尺寸
    """
    if outfile is None:
        outfile = generateOutfile(infile)

    with open(infile) as im:
        x, y = im.size
        if x <= target_width: # 如果原图已经更小，直接保存或返回
            im.save(outfile)
            return outfile
            
        target_height = int(y * target_width / x)
        # 使用更现代的 Resampling 接口
        out = im.resize((target_width, target_height), Resampling.LANCZOS)
        
        # 保持原图模式或转为兼容模式
        if out.mode in ("RGBA", "P") and outfile.lower().endswith(('.jpg', '.jpeg')):
            out = out.convert("RGB")
            
        out.save(outfile, optimize=True)
        
    return outfile

if __name__ == '__main__':
    # 示例调用
    # res = resize_image('1001.jpg', target_width=1080)
    # final = compress_by_quality(res, target_kb=200)
    pass