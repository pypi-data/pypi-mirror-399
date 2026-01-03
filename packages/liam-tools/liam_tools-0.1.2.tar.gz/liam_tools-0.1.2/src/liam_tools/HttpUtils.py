from requests import post as rpost
from requests import get as rget
from requests.exceptions import RequestException
from requests_toolbelt import MultipartEncoder
from time import sleep
from liam_tools import pl
from liam_tools.ustr import getRandom
from liam_tools.path import filterName

# 配置常量
# 修正：确保 READ 超时与 CONNECT 超时分别定义
MAX_RETRIES = 3
HTTP_TIME_OUT_CONNECT = 5
HTTP_TIME_OUT_READ = 30
HTTP_DEFAULT_HEADERS = {'User-Agent': 'Mozilla/5.0 (Linux; Android 13; Pixel 10 Build/MRA58K; wv)  AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/104.0.5112.102 Mobile Safari/537.36'}

class HttpUtils:
    """
    HTTP POST 请求工具类，支持 Form 和 FormData 模式
    """

    # 默认代理配置（建议按需传入，而非硬编码）
    defaultSocks5 = 'socks5://127.0.0.1:1080'
    defaultProxies = {
        'http': defaultSocks5,
        'https': defaultSocks5,
    }

    @staticmethod
    def sget(url, params=None, headers=None, retry=MAX_RETRIES, **kwargs):
        """
        封装 requests.get 方法
        :param url: 请求地址
        :param params: 查询参数
        :param headers: 请求头
        :param retry: 失败重试次数
        :return: Response 对象或 None
        """
        for i in range(retry):
            try:
                # 合并默认超时时间
                kwargs.setdefault('timeout', HTTP_TIME_OUT_CONNECT)
                resp = rget(url, params=params, headers=headers if headers else HTTP_DEFAULT_HEADERS, **kwargs)
                
                # 检查状态码
                if resp.status_code == 200:
                    return resp
                else:
                    pl.w(f"Request Error: Status Code {resp.status_code} | URL: {url}")
                    
            except RequestException as e:
                pl.w(f"Attempt {i+1} failed: {str(e)}")
                if i < retry - 1:
                    sleep(1)  # 等待后重试
                else:
                    pl.w(f"All {retry} attempts failed for URL: {url}")
        
        return None

    @staticmethod
    def postForm(url, data=None, jsonData=None, filePath=None, 
                 timeout=(HTTP_TIME_OUT_CONNECT, HTTP_TIME_OUT_READ), 
                 headers=None, proxies=None, enableLog=False):
        
        currentHeaders = HTTP_DEFAULT_HEADERS.copy()
        if headers:
            currentHeaders.update(headers)

        try:
            # 如果没有文件，直接发送请求
            if not filePath:
                resp = rpost(url, data=data, json=jsonData, headers=currentHeaders, timeout=timeout, proxies=proxies)
            else:
                # 使用 with 语句，确保文件在请求完成后立即关闭
                with open(filePath, 'rb') as fs:
                    files = {'file': (filePath, fs)}
                    resp = rpost(
                        url, 
                        data=data, 
                        json=jsonData, 
                        files=files, 
                        headers=currentHeaders, 
                        timeout=timeout, 
                        proxies=proxies
                    )

            resp.encoding = 'utf-8'
            if enableLog:
                pl.d(f'http form\ncode:{resp.status_code}\ntext:{resp.text}')
                
            return resp.status_code, resp.text

        except Exception as e:
            if enableLog:
                pl.d(f'http post error: {str(e)}')
            return -1, str(e)

    @staticmethod
    def postFormData(url, filePath, timeout=(HTTP_TIME_OUT_CONNECT, HTTP_TIME_OUT_READ), 
                     headers=None, proxies=None, enableLog=False):
        """
        使用 MultipartEncoder 提交二进制流数据
        """
        if not filePath:
            return -1, "File path is empty"

        try:
            with open(filePath, "rb") as fs:
                binaryData = fs.read()
                fileName = filterName(filePath)
                
                # 构建 Form Data 字段
                fileField = {"file": (fileName, binaryData, "application/octet-stream")}
                
                # 生成自定义 Boundary
                boundary = f'----WebKitFormBoundary{getRandom(16)}'
                multiData = MultipartEncoder(fields=fileField, boundary=boundary)

                # 设置请求头
                currentHeaders = {'Content-Type': multiData.content_type}
                if headers:
                    currentHeaders.update(headers)

                response = rpost(
                    url=url, 
                    headers=currentHeaders, 
                    data=multiData, 
                    timeout=timeout, 
                    proxies=proxies
                )
                
                if enableLog:
                    pl.d(f'http formdata\ncode:{response.status_code}\ntext:{response.text}')
                    
                return response.status_code, response.text

        except Exception as e:
            if enableLog:
                pl.d(f'http formdata error: {str(e)}')
            return -1, str(e)

# 示例调用
# code, text = HttpPostUtils.postForm("http://example.com", data={"key": "value"})