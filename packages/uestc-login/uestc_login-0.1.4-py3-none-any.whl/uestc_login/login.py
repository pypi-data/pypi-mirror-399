# login_uestc.py
import requests
import json
import os
from bs4 import BeautifulSoup
import random
from .utils import encrypt_password, get_random_user_agent
from .exceptions import NetworkError, ExtractionError, CredentialError, CookieError

LOGIN_DIR = os.path.dirname(__file__)
COOKIE_DIR = os.path.join(LOGIN_DIR, 'cookies')


class UestcUser:
    def __init__(self, username, password, cookie_file=None):
        """
        初始化用户
        :param username: 用户名 (学号)
        :param password: 原始密码
        """


        self.username = username
        self.password = password

        if cookie_file is None:
            self.cookie_file = os.path.join(COOKIE_DIR, f'{self.username}_cookie.json')
        else:
            self.cookie_file = cookie_file

        directory = os.path.dirname(self.cookie_file)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)


        self.session = requests.Session()
        self.session.headers.update({"User-Agent": get_random_user_agent()})
        self.is_logged_in = False

    def _save_cookies(self):
        """将会话中的 cookies 保存到文件"""
        with open(self.cookie_file, 'w', encoding='utf-8') as f:
            json.dump(self.session.cookies.get_dict(), f, ensure_ascii=False, indent=4)
        print(f"Cookies 已保存到 {self.cookie_file}")

    def load_cookies(self):
        """从文件加载 cookies 到会话"""
        if os.path.exists(self.cookie_file):
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
                self.session.cookies.update(cookies)
            print(f"从 {self.cookie_file} 加载 Cookies 成功。")
            return True
        return False

    def _check_cookie_validity(self, check_url = "https://idas.uestc.edu.cn/personalInfo/common/getUserConf"):
        """
        通过访问一个需要登录的 API 来检查当前 cookie 是否有效
        :return: bool, True 表示有效, False 表示无效
        """
        # check_url = "https://mooc2.uestc.edu.cn/api/user/search"
        # https://webvpn.uestc.edu.cn/https/77726476706e69737468656265737421f9f3408f69256d436a0bc7a99c406d3652/personalInfo/common/getUserConf
        try:
            self.session.post(check_url, json = {"n":str(random.random())} ,timeout=10).json() # 如果被重定向到登录应该报错！！
            print("Cookie 验证通过，当前为登录状态。")
            return True

        except requests.exceptions.RequestException:
            return False

        except Exception as e:
            print(f"验证cookie时发生错误：{e}  cookie已失效")
            return False

    def _perform_login(self, login_url = "https://idas.uestc.edu.cn/authserver/login"):
        """执行完整的登录流程"""
        # https://webvpn.uestc.edu.cn/https/77726476706e69737468656265737421f9f3408f69256d436a0bc7a99c406d3652/authserver/login?service=https://webvpn.uestc.edu.cn/login?cas_login=true
        try:
            print("正在访问统一认证页面...")
            self.session.cookies.clear()  #  清除cookies
            resp_get = self.session.get(login_url)

            soup = BeautifulSoup(resp_get.text, 'html.parser')
            execution_tag = soup.find('input', {'name': 'execution'})
            salt_tag = soup.find('input', {'id': 'pwdEncryptSalt'})

            if not all([execution_tag, salt_tag]):
                raise ExtractionError("无法在登录页面中找到 execution 或 salt！")

            execution = execution_tag.get('value')
            salt = salt_tag.get('value')

            encrypted_password = encrypt_password(self.password, salt)

            post_data = {
                'username': self.username, 'password': encrypted_password,
                'captcha': '', 'rememberMe': 'true', '_eventId': 'submit',
                'cllt': 'userNameLogin', 'dllt': 'generalLogin', 'lt': '',
                'execution': execution,
            }
            print("正在发送登录请求...")
            resp_post = self.session.post(login_url, data=post_data)

            soup_post = BeautifulSoup(resp_post.text, 'html.parser')
            if 'CASTGC' not in self.session.cookies:
                error_msg_span = soup_post.find('span', {'id': 'showErrorTip'})
                error_msg = error_msg_span.text.strip() if error_msg_span else "未知错误"
                if error_msg_span:
                    if "图形" in error_msg_span:
                        raise CredentialError(f"登陆失败，检测到图形验证码！请手动登录统一身份认证以完成人机验证后继续使用（爆破密码推荐看看：https://hq.uestc.edu.cn/service/login）")
                    else:
                        raise CredentialError(f"登录认证失败: {error_msg}")

            print("统一认证成功!!!")

        except requests.exceptions.RequestException as exp:
            raise NetworkError(f"登录过程中发生网络错误: {exp}")

    def login(self, login_url = "https://idas.uestc.edu.cn/authserver/login"):
        if login_url == "https://idas.uestc.edu.cn/authserver/login":
            if self.load_cookies() and self._check_cookie_validity():
                self.is_logged_in = True
                return self.session

        print("本地 Cookie 无效或不存在，开始使用账号密码登录...")
        self._perform_login(login_url=login_url)

        if not self._check_cookie_validity(check_url="https://webvpn.uestc.edu.cn/https/77726476706e69737468656265737421f9f3408f69256d436a0bc7a99c406d3652/personalInfo/common/getUserConf"):
            raise CookieError("登录后，cookie验证失败！")

        self.is_logged_in = True
        self._save_cookies()

        return self.session

    def login_mooc(self):
        self.login()

        self.session.get("https://mooc2.uestc.edu.cn/")
        self.session.get("https://mooc.uestc.edu.cn/home/index/gologin.html")
        self.session.get("https://mooc2.uestc.edu.cn:8643/auth/realms/uestc/protocol/openid-connect/auth?client_id=menu&response_type=code&redirect_uri=https://mooc.uestc.edu.cn/api/callback&state=1&login=true&scope=openid&realms=uestc")

        return self.session

    def login_chat(self):
        """成电seek登录"""
        self.session = self.login()

        self.session.get("https://chat.uestc.edu.cn", allow_redirects=True)
        self.session.get("https://chat.uestc.edu.cn/terminator/agent/home", allow_redirects=True)
        self.session.get("https://chat.uestc.edu.cn/unifiedlogin/v1/loginmanage/login/direction?redirect_url=/terminator/agent/home", allow_redirects=True)
        self.session.get("https://idas.uestc.edu.cn/authserver/login?service=https://chat.uestc.edu.cn/unifiedlogin/v1/cas/login?redirect_url=/terminator/agent/home", allow_redirects=True)
        self.session.get("https://chat.uestc.edu.cn/terminator/agent/home", allow_redirects=True)

        return self.session

    def login_resource(self):
        """和chat高度相似，其实本来就是一个东西"""
        self.session = self.login()

        self.session.get("https://resource.uestc.edu.cn", allow_redirects=True)
        self.session.get("https://resource.uestc.edu.cn/terminator/agent/home", allow_redirects=True)
        self.session.get("https://resource.uestc.edu.cn/unifiedlogin/v1/loginmanage/login/direction?redirect_url=/terminator/agent/home", allow_redirects=True)
        self.session.get("https://idas.uestc.edu.cn/authserver/login?service=https://resource.uestc.edu.cn/unifiedlogin/v1/cas/login?redirect_url=/terminator/agent/home", allow_redirects=True)
        self.session.get("https://resource.uestc.edu.cn/terminator/agent/home", allow_redirects=True)

        return self.session

    def login_exams(self):
        """教务系统登录"""
        self.session = self.login()

        self.session.get("https://eams.uestc.edu.cn/eams/home!submenus.action?menu.id=", allow_redirects=True)  # 202
        self.session.get("https://eams.uestc.edu.cn/eams/home!submenus.action?menu.id=", allow_redirects=True)  # 302

        self.session.get("https://idas.uestc.edu.cn/authserver/login?service=https://eams.uestc.edu.cn/eams/home!submenus.action?menu.id=", allow_redirects=True) # 哦哦 ticket是302重定向过去的，我想错了

        self.session.get("https://eams.uestc.edu.cn/eams/home!submenus.action?menu.id=")  # 可能会失败，有个ticket涉及到麻烦的js逆向并没有解决
        return self.session

    def login_vpn(self):
        self.session.get("https://webvpn.uestc.edu.cn", allow_redirects=True)
        self.session.get("https://webvpn.uestc.edu.cn/login", allow_redirects=True)
        self.session = self.login(login_url="https://webvpn.uestc.edu.cn/https/77726476706e69737468656265737421f9f3408f69256d436a0bc7a99c406d3652/authserver/login?service=https://webvpn.uestc.edu.cn/login?cas_login=true")

        return self.session

    def login_jzsz(self):
        """测试成功，精准思政平台登录"""
        self.session = self.login()

        self.session.get("https://jzsz.uestc.edu.cn/")
        self.session.get("https://idas.uestc.edu.cn/authserver/login?service=https://jzsz.uestc.edu.cn/", allow_redirects=True)
        self.session.get("https://jzsz.uestc.edu.cn/")

        return self.session



    def check_cookie(self):
        if os.path.exists(self.cookie_file):
            with open(self.cookie_file, 'r', encoding='utf-8') as f:
                cookies = json.load(f)
            try:
                res = requests.post(headers={"User-Agent": get_random_user_agent()}, cookies=cookies,url = "https://idas.uestc.edu.cn/personalInfo/common/getUserConf", json = {"n":str(random.random())} ,timeout=10)
                if res.status_code == 200:
                    return True
            except requests.exceptions.RequestException:
                return False
        return False
