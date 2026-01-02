import os
import threading
import requests
import time
import logging
from typing import Dict, Optional, Any

# 配置日志
logger = logging.getLogger(__name__)

# 确保.env文件被加载
def _load_env():
    """确保环境变量被正确加载"""
    try:
        # 尝试加载.env文件
        from pathlib import Path
        # 从 dc_common/src/dc_common/utils/proxy_utils.py 往上 5 层到项目根目录
        env_path = Path(__file__).parent.parent.parent.parent.parent / '.env'
        if env_path.exists():
            with open(env_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # 移除引号
                        value = value.strip().strip('"').strip("'")
                        os.environ[key] = value
            logger.info(f"[PROXY] 已加载.env文件: {env_path}")
        else:
            logger.warning(f"[PROXY] .env文件不存在: {env_path}")
    except Exception as e:
        logger.warning(f"[PROXY] 加载.env文件失败: {e}")

# 加载环境变量
_load_env()

# 安全存储凭证
_authKey = os.getenv('QG_AUTH_KEY')
_password = os.getenv('QG_AUTH_PASSWORD')

# 记录凭证状态（不记录具体值以保证安全）
if _authKey:
    logger.info(f"[PROXY] QG_AUTH_KEY已加载，长度: {len(_authKey)}")
else:
    logger.warning("[PROXY] QG_AUTH_KEY未设置或为空")

if _password:
    logger.info(f"[PROXY] QG_AUTH_PASSWORD已加载，长度: {len(_password)}")
else:
    logger.warning("[PROXY] QG_AUTH_PASSWORD未设置或为空")

# 配置参数
PROXY_EXPIRE_TIME = 55  # 代理过期时间（秒）
PROXY_TIMEOUT = 10  # 代理超时时间（秒）

class SimpleProxyPool:
    """简化的内存代理池"""

    def __init__(self):
        self._valid_proxy: Optional[str] = None
        self._proxy_expiry: float = 0
        self._lock = threading.Lock()

    def _is_proxy_expired(self) -> bool:
        """检查代理是否过期"""
        return time.time() > self._proxy_expiry

    def _fetch_new_proxy(self) -> Optional[str]:
        """获取新的代理IP"""
        try:
            url = f"https://share.proxy.qg.net/get?key={_authKey}&num=1&area=&isp=0&format=txt&seq=\r\n&distinct=true"
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            ip = response.text.strip()
            if ip:
                logger.info(f"[PROXY] 获取到新代理: {ip}")
            return ip

        except Exception as e:
            logger.error(f"[PROXY] 获取代理失败: {str(e)}")
            return None

    def test_proxy(self, test_url: str, timeout: int = 10) -> bool:
        """测试代理是否可以访问指定URL

        Args:
            test_url: 要测试的URL
            timeout: 超时时间（秒）

        Returns:
            bool: 测试是否成功
        """
        proxy_dict = self.get_proxy()
        if not proxy_dict:
            logger.warning("[PROXY] 无法获取代理进行测试")
            return False

        try:
            response = requests.get(test_url, proxies=proxy_dict, timeout=timeout)
            response.raise_for_status()
            logger.info(f"[PROXY] 代理测试成功: {test_url}")
            return True
        except Exception as e:
            logger.warning(f"[PROXY] 代理测试失败: {test_url}, 错误: {str(e)}")
            return False

    def get_proxy(self) -> Optional[Dict[str, Any]]:
        """获取代理配置（增强版本，包含IP和完整地址）

        Returns:
            dict: 包含代理配置和IP地址的字典
            {
                "proxies": {"http": proxyUrl, "https": proxyUrl},
                "ip": "60.188.79.123",  # 纯IP地址
                "full_address": "60.188.79.123:20012"  # 完整地址
            }

        Raises:
            Exception: 当代理环境变量未配置或获取代理失败时
        """
        # 检查环境变量
        if not _authKey or not _password:
            raise Exception("代理环境变量未配置: QG_AUTH_KEY 或 QG_AUTH_PASSWORD")

        with self._lock:
            # 检查当前代理是否还有效
            if self._valid_proxy and not self._is_proxy_expired():
                return self._build_proxy_info(self._valid_proxy)

            # 代理过期或不存在，获取新代理
            new_proxy = self._fetch_new_proxy()
            if new_proxy:
                self._valid_proxy = new_proxy
                self._proxy_expiry = time.time() + PROXY_EXPIRE_TIME
                return self._build_proxy_info(new_proxy)

            return None

    def get_proxy_dict(self) -> Optional[Dict[str, str]]:
        """获取代理字典（向后兼容）

        Returns:
            dict: 代理配置字典

        Raises:
            Exception: 当代理环境变量未配置或获取代理失败时
        """
        proxy_info = self.get_proxy()
        return proxy_info["proxies"] if proxy_info else None

    def clear_proxy_cache(self) -> None:
        """清空代理缓存（强制下次获取新代理）"""
        with self._lock:
            self._valid_proxy = None
            self._proxy_expiry = 0
            logger.info("[PROXY] 代理缓存已清空")

    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息（用于调试）

        Returns:
            dict: 缓存状态信息
        """
        with self._lock:
            current_time = time.time()
            is_valid = (self._valid_proxy is not None and
                       current_time < self._proxy_expiry)

            return {
                "ip": self._valid_proxy,
                "expire_time": self._proxy_expiry,
                "current_time": current_time,
                "is_valid": is_valid,
                "remaining_seconds": max(0, self._proxy_expiry - current_time) if is_valid else 0
            }

    def _build_proxy_info(self, proxy_ip: str) -> Dict[str, Any]:
        """构建代理信息字典（包含IP和完整地址）"""
        proxy_url = f"http://{_authKey}:{_password}@{proxy_ip}"
        ip = proxy_ip.split(':')[0] if ':' in proxy_ip else proxy_ip

        return {
            "proxies": {
                "http": proxy_url,
                "https": proxy_url
            },
            "ip": ip,
            "full_address": proxy_ip
        }

    def _build_proxy_dict(self, proxy_ip: str) -> Dict[str, str]:
        """构建代理字典（向后兼容）"""
        return self._build_proxy_info(proxy_ip)["proxies"]

# 创建全局代理池实例
_proxy_pool = SimpleProxyPool()

def get_proxy() -> Optional[Dict[str, Any]]:
    """
    获取代理配置信息（增强版本，包含IP和完整地址）

    Returns:
        dict: 包含代理配置和IP地址的字典
        {
            "proxies": {"http": proxyUrl, "https": proxyUrl},
            "ip": "60.188.79.123",  # 纯IP地址
            "full_address": "60.188.79.123:20012"  # 完整地址
        }

    Raises:
        Exception: 当代理环境变量未配置或获取代理失败时
    """
    return _proxy_pool.get_proxy()

def get_proxy_dict() -> Optional[Dict[str, str]]:
    """
    获取代理字典（向后兼容）

    Returns:
        dict: 代理配置字典

    Raises:
        Exception: 当代理环境变量未配置或获取代理失败时
    """
    return _proxy_pool.get_proxy_dict()

def clear_proxy_cache() -> None:
    """
    清空代理缓存（强制下次获取新代理）
    """
    return _proxy_pool.clear_proxy_cache()

def get_cache_info() -> Dict[str, Any]:
    """
    获取缓存信息（用于调试）

    Returns:
        dict: 缓存状态信息
    """
    return _proxy_pool.get_cache_info()

def test_proxy(test_url: str, timeout: int = 10) -> bool:
    """测试代理是否可以访问指定URL

    Args:
        test_url: 要测试的URL
        timeout: 超时时间（秒）

    Returns:
        bool: 测试是否成功
    """
    return _proxy_pool.test_proxy(test_url, timeout)