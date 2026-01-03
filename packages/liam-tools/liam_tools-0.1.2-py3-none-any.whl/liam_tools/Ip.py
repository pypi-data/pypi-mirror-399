from requests import get as rget
import socket
import contextlib
from liam_tools import pl

class IpUtils:
    """
    网络 IP 及端口检测工具类
    """

    @staticmethod
    def getMyIp():
        """获取当前外网出口 IP"""
        try:
            # 增加超时处理，防止阻塞
            with rget('https://api.myip.la', timeout=5) as resp:
                return resp.text.strip() if resp.status_code==200 else ''
        except Exception as e:
            pl.w(f"Get outer IP failed: {e}")
            return ""

    @staticmethod
    def getMyLocation():
        """获取当前地理位置信息 (中文 JSON)"""
        try:
            with rget('https://api.myip.la/cn?json', timeout=5) as resp:
                return resp.text.strip() if resp.status_code==200 else ''
        except Exception as e:
            pl.w(f"Get location failed: {e}")
            return ""

    @staticmethod
    def getLocalIp():
        """
        获取本地局域网 IP
        改良版：通过连接一个外部地址来探测本地真实的出口网卡 IP
        """
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            # 不会真正建立连接，但能触发系统选择最优网卡
            s.connect(('8.8.8.8', 80))
            return s.getsockname()[0]
        except Exception:
            # 备选方案：原始方法
            return socket.gethostbyname(socket.getfqdn(socket.gethostname()))
        finally:
            s.close()

    @staticmethod
    def checkTcpPort(ip='0.0.0.0', port=80, timeout=3):
        """检测 TCP 端口是否开放"""
        # 使用 closing 确保 socket 自动关闭
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as sock:
            sock.settimeout(timeout)
            try:
                sock.connect((ip, port))
                # 某些协议可能需要 shutdown，但在检测开放性时 connect 成功即可
                return True
            except Exception as e:
                pl.w(f"TCP Port {port} on {ip} is closed: {e}")
                return False

    @staticmethod
    def checkUdpPort(ip='0.0.0.0', port=80, timeout=3):
        """检测 UDP 端口"""
        with contextlib.closing(socket.socket(socket.AF_INET, socket.SOCK_DGRAM)) as sock:
            sock.settimeout(timeout)
            try:
                # UDP 是无连接的，connect 仅检查路由是否可达
                sock.connect((ip, port))
                return True
            except Exception as e:
                pl.w(f"UDP Port {port} on {ip} error: {e}")
                return False

# 使用示例
if __name__ == "__main__":
    print(f"Outer IP: {IpUtils.getMyIp()}")
    print(f"Local IP: {IpUtils.getLocalIp()}")
    isWebOpen = IpUtils.checkTcpPort('127.0.0.1', 80)
    print(f"Local Port 80 status: {isWebOpen}")