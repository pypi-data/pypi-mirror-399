import os
from subprocess import run, CalledProcessError, PIPE
import shutil
from time import time
from liam_tools import path, ustr

class VideoProcessor:

    def __init__(self):

        # 视频后缀集合建议定义为类常量
        self.VIDEO_SUFFIX_SET = {
            "wmv", "asf", "asx", "rm", "rmvb", "mp4", "3gp", 
            "mov", "m4v", "avi", "dat", "mkv", "flv", "vob"
        }

    def isVideo(self, filePath: str) -> bool:

        """检查文件是否为视频格式"""
        if not filePath:
            return False
        suffix = filePath.rsplit(".", 1)[-1].lower()
        return suffix in self.VIDEO_SUFFIX_SET

    def checkFfmpeg(self) -> bool:

        """检查系统是否安装了 ffmpeg"""
        return shutil.which("ffmpeg") is not None

    def generateOutPath(self, inFile: str) -> str:

        """生成默认的输出路径"""
        pathName, fileName = path.split(inFile)
        outFile = path.cacheVideo(f"{time()}_{fileName}")
        # 确保输出目录存在
        targetDir = os.path.dirname(outFile)
        if not os.path.exists(targetDir):
            path.mkfolder(targetDir)
        return outFile

    def resizeVideo(self, inFile: str, outFile: str = None) -> str:

        """
        使用 FFmpeg 压缩视频
        :param inFile: 输入视频路径
        :param outFile: 输出视频路径
        """
        # 1. 预检查
        if not self.checkFfmpeg():
            return "Error: FFmpeg is not installed"

        fileSizeKb = os.path.getsize(inFile) / 1024
        if fileSizeKb < 2048:  # 小于 2MB 则不压缩
            return inFile

        if outFile is None:
            outFile = self.generateOutPath(inFile)

        # 2. 构建命令 (使用列表形式更安全，防止路径空格导致的命令注入)
        command = [
            "ffmpeg", "-i", inFile,
            "-r", "10",                # 帧率
            "-pix_fmt", "yuv420p",      # 像素格式
            "-vcodec", "libx264",       # 视频编码
            "-preset", "veryslow",      # 预设
            "-profile:v", "baseline",   # 画质档次
            "-crf", "23",               # 恒定质量因子
            "-acodec", "aac",           # 音频编码
            "-b:a", "32k",              # 音频比特率
            "-y",                       # 覆盖已有文件
            outFile
        ]

        try:
            # 3. 执行并捕获错误
            run(command, check=True, stdout=PIPE, stderr=PIPE)
            return outFile
        except CalledProcessError as e:
            return f"Error: Compression failed. {str(e)}"

    def createThumbnail(self, videoPath: str) -> str:

        """
        截取视频第一帧作为缩略图
        """
        if not self.checkFfmpeg():
            return "Error: FFmpeg is not installed"

        # 获取后缀名并替换为 jpg
        suffix = ustr.fileSuffix(videoPath)
        thumbnailPath = videoPath.replace(suffix, '.jpg')

        if not os.path.exists(thumbnailPath):
            command = [
                "ffmpeg", "-i", videoPath,
                "-ss", "00:00:00.000",   # 起始位置
                "-vframes", "1",         # 只截取一帧
                "-q:v", "2",             # 图片质量
                "-y",                    # 覆盖已有文件
                thumbnailPath
            ]
            try:
                run(command, check=True, stdout=PIPE, stderr=PIPE)
            except CalledProcessError:
                return "Error: Failed to create thumbnail"

        return thumbnailPath

if __name__ == '__main__':
    processor = VideoProcessor()
    result = processor.resizeVideo('bbt.mp4')
    print(f"Processed Result: {result}")