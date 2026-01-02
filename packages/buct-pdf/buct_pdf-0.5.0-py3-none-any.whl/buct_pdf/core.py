import requests
import os
from PIL import Image
import re
from bs4 import BeautifulSoup as bs
import shutil


# 自定义异常类
class LoginError(Exception):
    """登录相关错误"""
    pass


class NetworkError(Exception):
    """网络相关错误"""
    pass


class GetsPdf(object):
    """北化课程平台PDF下载器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.base_url = "https://course.buct.edu.cn"
        self.logged_in = False

    def login(self, username, password):
        """
        登录到北化课程平台

        Args:
            username: 学号
            password: 密码

        Returns:
            bool: 登录是否成功

        Raises:
            LoginError: 登录失败时抛出
            NetworkError: 网络错误时抛出
        """
        try:
            # 先清空旧session，确保重新登录时使用全新的session
            self.session = requests.Session()
            self.logged_in = False

            login_url = f"{self.base_url}/meol/loginCheck.do"
            response = self.session.post(login_url, data={
                "IPT_LOGINUSERNAME": username,
                "IPT_LOGINPASSWORD": password
            }, timeout=10)

            # 检查登录是否成功
            # 假设成功登录会重定向到非登录页，失败则停留在登录页或重定向回登录页
            # 检查最终的URL是否仍然包含"login.do"或"loginCheck.do"
            if "login.do" in response.url or "loginCheck.do" in response.url:
                self.logged_in = False
            else:
                self.logged_in = True

            if not self.logged_in:
                # 可以在这里添加更详细的错误信息解析，如果服务器有提供的话
                raise LoginError("登录失败，请检查用户名和密码。")

            return self.logged_in

        except requests.exceptions.Timeout:
            raise NetworkError("登录请求超时")
        except requests.exceptions.ConnectionError:
            raise NetworkError("网络连接错误")
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"网络请求错误: {str(e)}")

    def get_session(self):
        """
        获取登录后的session

        Returns:
            requests.Session: 认证后的会话对象

        Raises:
            LoginError: 如果未登录时调用
        """
        if not self.logged_in:
            raise LoginError("请先调用login方法进行登录")
        return self.session

    def is_logged_in(self):
        """检查是否已登录"""
        return self.logged_in

    def logout(self):
        """注销登录"""
        try:
            # 尝试调用服务器注销接口
            logout_url = "https://portal.buct.edu.cn/cas/logout"
            self.session.get(logout_url, timeout=10)
        except Exception:
            # 忽略注销接口的错误，继续清理本地session
            pass
        finally:
            # 无论如何都要清空本地session
            self.session.close()  # 关闭连接
            self.session = requests.Session()  # 创建新的session
            self.logged_in = False

    def set_base_url(self, base_url):
        """设置基础URL（用于测试或其他环境）"""
        self.base_url = base_url.rstrip('/')

    def download_ppt_to_pdf(self, url, output_dir="."):
        """
        下载PPT并转换为PDF

        Args:
            url: 页面URI
            output_dir: 输出目录，默认为当前目录

        Returns:
            str: 生成的PDF文件路径

        Raises:
            LoginError: 未登录时抛出
            NetworkError: 网络错误时抛出
        """
        if not self.logged_in:
            raise LoginError("请先登录")

        headers = self._set_headers()

        try:
            if "columnId" not in url:
                # 获取页面内容
                res = self.session.get(url, headers=headers).text

                # 获取第二个页面链接
                base_url = "https://course.buct.edu.cn/meol/common/script/preview/"
                url2 = base_url+re.findall(r'src=".*?"', res)[-1].replace('src="', '').replace('"', '')
                res2 = self.session.get(url2, headers=headers).text

                # 获取图片链接
                pattern = r'Html = ".*?"'
                image_url_connected = re.findall(pattern, res2)[0]
                image_url_connected = image_url_connected.replace('Html = "', '').replace('"', '')
                image_urls = image_url_connected.split(',')

                # 获取标题作为文件夹名称
                soup = bs(res2, 'html.parser')
                dir_name = soup.select_one('title').text.strip()[:-4]

                # 创建临时目录
                temp_dir = os.path.join(output_dir, dir_name)
                os.makedirs(temp_dir, exist_ok=True)

                # 下载所有图片
                for idx, img_url in enumerate(image_urls):
                    response = self.session.get(img_url, headers=headers)
                    with open(os.path.join(temp_dir, f"{idx+1}.png"), "wb") as f:
                        f.write(response.content)

                # 转换为PDF
                images = [Image.open(os.path.join(temp_dir, f"{i+1}.png")).convert("RGB") for i in range(len(image_urls))]
                pdf_path = os.path.join(output_dir, f"{dir_name}.pdf")
                images[0].save(pdf_path, save_all=True, append_images=images[1:])

                # 清理临时目录
                shutil.rmtree(temp_dir)

                return pdf_path

            else:
                res = self.session.get(url, headers=headers).text

                base_url = "https://course.buct.edu.cn"

                url1 = re.findall(r'src=".*?"', res)[-1].replace('src="', '').replace('"', '')
                res1 = self.session.get(url1, headers=headers).text


                url2 = base_url + re.findall(r'src=".*?"', res1)[-1].replace('src="', '').replace('"', '')
                res2 = self.session.get(url2, headers=headers).text

                # 获取图片链接
                pattern = r'Html = ".*?"'
                image_url_connected = re.findall(pattern, res2)[0]
                image_url_connected = image_url_connected.replace('Html = "', '').replace('"', '')
                image_urls = image_url_connected.split(',')

                # 获取标题作为文件夹名称
                soup = bs(res2, 'html.parser')
                dir_name = soup.select_one('title').text.strip()
                if ".pptx" in dir_name:
                    dir_name = dir_name[:-5]
                elif ".ppt" in dir_name:
                    dir_name = dir_name[:-4]
                elif ".pdf" in dir_name:
                    dir_name = dir_name[:-4]

                # 创建临时目录
                temp_dir = os.path.join(output_dir, dir_name)
                os.makedirs(temp_dir, exist_ok=True)

                # 下载所有图片
                for idx, img_url in enumerate(image_urls):
                    response = self.session.get(img_url, headers=headers)
                    with open(os.path.join(temp_dir, f"{idx+1}.png"), "wb") as f:
                        f.write(response.content)

                # 转换为PDF
                images = [Image.open(os.path.join(temp_dir, f"{i+1}.png")).convert("RGB") for i in range(len(image_urls))]
                pdf_path = os.path.join(output_dir, f"{dir_name}.pdf")
                images[0].save(pdf_path, save_all=True, append_images=images[1:])

                # 清理临时目录
                shutil.rmtree(temp_dir)

                return pdf_path

        except Exception as e:
            raise NetworkError(f"下载失败: {str(e)}")

    def download_pdf(self, url, output_dir="."):
        """
        下载PDF文件

        Args:
            url: 页面URI
            output_dir: 输出目录，默认为当前目录

        Returns:
            str: 下载的PDF文件路径

        Raises:
            LoginError: 未登录时抛出
            NetworkError: 网络错误时抛出
        """
        if not self.logged_in:
            raise LoginError("请先登录")

        headers = self._set_headers()

        try:
            if "resid" in url:
                res = self.session.get(url, headers=headers).text

                # 获取文件名
                soup = bs(res, 'html.parser')
                file_name = soup.select_one('title').text.strip()

                # 重新拼接url
                base_url = "https://course.buct.edu.cn/meol/analytics/resPdfShow.do?"
                components = url.replace('resid','resId').split("&")[-2:]
                download_url = base_url + components[0] + "&" + components[1]

                # 下载pdf
                response = self.session.get(download_url, headers=headers)
                pdf_path = os.path.join(output_dir, f"{file_name}.pdf")
                with open(pdf_path, "wb") as f:
                    f.write(response.content)

                return pdf_path

            elif "columnId" in url:
                res = self.session.get(url, headers=headers).text

                base_url = "https://course.buct.edu.cn"

                # 获取请求
                url1 = re.findall(r'src=".*?"', res)[-1].replace('src="', '').replace('"', '')
                res1 = self.session.get(url1, headers=headers).text

                # 拼接download_url
                download_url = base_url + re.findall(r'"/meol.*?;',res1)[0].replace('"','').replace(');','')

                # 获取文件名
                soup = bs(res1,'html.parser')
                file_name = soup.find_all('title')[-1].text.strip()
                print(file_name)

                # 下载pdf
                response = self.session.get(download_url, headers=headers)
                pdf_path = os.path.join(output_dir, f"{file_name}.pdf")
                with open(pdf_path, "wb") as f:
                    f.write(response.content)

                return pdf_path

        except Exception as e:
            raise NetworkError(f"下载失败: {str(e)}")

    def _set_headers(self):
        """设置请求头"""
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/",
            "Referer": "https://course.buct.edu.cn/meol/analytics/resPdfShow.do?file=%2Fmeol%2Fanalytics%2FresPdfShow.do%3FresId%3D423050%26lid%3D20904&lid=20904&resId=423050",
        }
        return headers