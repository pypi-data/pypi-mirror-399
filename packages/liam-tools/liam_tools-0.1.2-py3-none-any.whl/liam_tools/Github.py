from os import path as ospath
from os import getcwd
from requests import put
from base64 import b64encode
from json import dumps

class GithubUploader:
    """
    封装 GitHub 文件上传功能
    """
    def __init__(self, userName, repoName, token):
        self.userName = userName
        self.repoName = repoName
        self.token = token
        self.baseUrl = f"https://api.github.com/repos/{userName}/{repoName}/contents/"

    def uploadFile(self, localFilePath, targetDir='', commitMsg='upload file'):
        """
        上传文件到 GitHub 仓库
        """
        # 参数校验
        if not all([self.userName, self.repoName, self.token]):
            return -1, "Auth parameters missing"
        
        if not ospath.isfile(localFilePath):
            return -1, f"File not found: {localFilePath}"

        try:
            # 读取并编码文件
            with open(localFilePath, "rb") as f:
                fileData = f.read()
                if not fileData:
                    return -1, "File content is empty"
                encodedContent = b64encode(fileData).decode('utf-8')

            # 构建请求 URL 和 Payload
            fileName = ospath.basename(localFilePath)
            # 确保目录路径以 / 结尾
            pathPrefix = f"{targetDir.strip('/')}/" if targetDir.strip('/') else ""
            uploadUrl = f"{self.baseUrl}{pathPrefix}{fileName}"

            headers = {
                "Authorization": f"token {self.token}",
                "Accept": "application/vnd.github.v3+json"
            }
            
            payload = {
                "message": commitMsg,
                "committer": {
                    "name": self.userName,
                    "email": f"{self.userName}@users.noreply.github.com"
                },
                "content": encodedContent
            }

            # 执行 PUT 请求
            response = put(
                url=uploadUrl, 
                data=dumps(payload), 
                headers=headers,
                timeout=30
            )
            
            return response.status_code, response.json()

        except Exception as e:
            return -2, str(e)

# --- 测试用例 ---
if __name__ == '__main__':
    # 建议从环境变量获取 Token 保护隐私
    # import env (使用您之前 env.py 中的方法)
    # myToken = env.by('GITHUB_TOKEN') 
    
    myToken = "ghp_xxxxxxxxxxxx" # 生产环境请替换为环境变量读取
    
    uploader = GithubUploader(
        userName="respondnet", 
        repoName="cloudflare-files", 
        token=myToken
    )

    testFilePath = ospath.join(getcwd(), 'xq-16x16.ico')
    targetDirectory = 'doc/'

    statusCode, result = uploader.uploadFile(testFilePath, targetDirectory)

    if statusCode == 201:
        downloadUrl = result.get('content', {}).get('download_url')
        print(f"Upload Success!")
        print(f"Github URL: {downloadUrl}")
        # 假设使用了 Cloudflare Pages 映射
        fileName = ospath.basename(testFilePath)
        print(f"CF URL: https://files-c1z.pages.dev/{targetDirectory}{fileName}")
    else:
        print(f"Error {statusCode}: {result}")