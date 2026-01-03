import requests
import hmac
import hashlib
import time
import random
import os
from typing import Optional
from urllib.parse import urlencode
import platform
from pathlib import Path

class DataCollectionClient:
    def __init__(self, base_url: str, access_key: str, secret_key: str):
        """
        初始化客户端

        :param base_url: API基础URL
        :param access_key: 访问密钥
        :param secret_key: 安全密钥
        """
        self.base_url = base_url.rstrip('/')
        self.access_key = access_key
        self.secret_key = secret_key
        self.session = requests.Session()
        self.access_token = self._get_access_token()
    def _generate_signature(self, params: dict, timestamp: str, nonce: str) -> str:
        """
        生成签名

        :param params: 请求参数
        :param timestamp: 时间戳
        :return: 签名
        """
        # 添加访问密钥和时间戳到参数中
        sign_params = params.copy()
        sign_params['access_key'] = self.access_key
        sign_params['timestamp'] = timestamp
        sign_params['nonce'] = nonce

        # 按键排序并拼接参数
        sorted_params = sorted(sign_params.items())
        query_string = urlencode(sorted_params)

        # 使用 HMAC-SHA256 生成签名
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()

        return signature

    def _make_request(self, method: str, url: str, params: Optional[dict] = None) -> dict:
        """
        发起带签名的请求

        :param method: HTTP方法
        :param url: 请求URL
        :param params: 请求参数
        :return: 响应数据
        """
        headers = {'Authorization': f'Bearer {self.access_token["access_token"]}'}
        # 发起请求
        if method.upper() == 'GET':
            response = self.session.get(url, params=params, headers=headers)
        else:
            response = self.session.post(url, json=params, headers=headers)

        response.raise_for_status()
        return response.json()


    def _get_access_token(self) -> dict:
        """
        获取访问令牌
        :return: 包含访问令牌的字典
        """
        params = {}
        # 获取当前时间戳
        timestamp = str(int(time.time()))
        nonce = str(random.randint(10000000, 99999999))
        # 生成签名
        signature = self._generate_signature(params, timestamp, nonce)

        # 添加认证信息到参数中
        params['access_key'] = self.access_key
        params['timestamp'] = timestamp
        params['nonce'] = nonce
        params['sign'] = signature

        url = f"{self.base_url}/api/v1/system/auth/access_token"
        response = self.session.post(url, json=params)
        response.raise_for_status()
        token = response.json()
        if token["code"] != 0:
            raise Exception(f"获取访问令牌失败: {token['msg']}")

        return token["data"]


    def get_download_url(self, collection_id: int, parent_id: int, version_id: int) -> str:
        """
        根据数据集ID、父目录ID和版本ID获取数据下载链接

        :param collection_id: 数据集ID
        :param parent_id: 父目录ID
        :param version_id: 版本ID
        :return: 下载链接
        """
        url = f"{self.base_url}/api/v1/dataset/fs/resource/pkg_download_path"

        params = {
            'collection_id': collection_id,
            'parent_id': parent_id,
            'version_id': version_id
        }

        result = self._make_request('POST', url, params)
        return result['data']

    def download_file(self, download_url: str, save_path: str) -> str:
        """
        根据下载链接下载文件

        :param download_url: 下载链接
        :param save_path: 保存路径
        :return: 保存文件的路径
        """
        # 创建保存目录（如果不存在）
        save_dir = os.path.dirname(save_path)
        if save_dir and not os.path.exists(save_dir):
            os.makedirs(save_dir)

        # 下载文件
        response = self.session.get(download_url, stream=True)
        response.raise_for_status()

        # 保存文件
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return save_path

    def _get_default_download_path(self,collection_name: str, version_name: str) -> str:
        """根据操作系统获取默认下载路径"""
        system = platform.system()

        if system == "Windows":
            # Windows 系统通常使用用户目录下的 Downloads
            download_dir = Path.home() / "Downloads"
        elif system == "Darwin":  # macOS
            download_dir = Path.home() / "Downloads"
        else:  # Linux 和其他 Unix 系统
            # 检查 XDG_DOWNLOAD_DIR 环境变量
            xdg_download = os.environ.get('XDG_DOWNLOAD_DIR')
            if xdg_download:
                download_dir = Path(xdg_download)
            else:
                download_dir = Path.home() / "Downloads"

        # 确保目录存在
        download_dir.mkdir(parents=True, exist_ok=True)

        return str(download_dir / f"{collection_name}_{version_name}.zip")

    def _is_directory_path(self, path: str) -> bool:
        """
        使用 os.path 判断路径是否为目录路径
        """
        # 如果路径以分隔符结尾，明确表示是目录
        if path.endswith(os.sep) or path.endswith('/'):
            return True

        # 如果路径存在，检查是否为目录
        if os.path.exists(path):
            return os.path.isdir(path)

        # 如果路径不存在，通过扩展名判断
        _, ext = os.path.splitext(path)
        return ext == ''  # 没有扩展名通常表示目录

    # 下载数据集合
    def download_collection(self, collection_name: str,version_name: str, save_path: str = None) :

        if not collection_name or not version_name:
            raise ValueError("数据集合名称或者数据集版本名称不能为空")


        # 根据数据集合名称和数据集和版本名称获取下载URL
        url = f"{self.base_url}/api/v1/dataset/fs/resource/collection_download_path"
        params = {
            'collection_name': collection_name,
            'version_name': version_name
        }
        result = self._make_request('POST', url, params)

        if result['code'] != 0:
            raise Exception(f"获取下载链接失败: {result['msg']}")
        download_url =  result['data']
        # 下载文件到指定目录

        if not save_path:
            # 如果没有指定保存路径，则使用系统临时目录
            save_path = self._get_default_download_path(collection_name = collection_name, version_name = version_name)
        else:
            if self._is_directory_path(save_path):
                save_path = os.path.join(save_path, f"{collection_name}_{version_name}.zip")




        # 下载文件
        response = self.session.get(download_url, stream=True)
        response.raise_for_status()

        # 保存文件
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        return save_path
