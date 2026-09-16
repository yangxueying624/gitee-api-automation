import requests
from config import TIMEOUT
from utils.log import logger
from typing import Optional, Dict, Any


class RequestUtil:
    """
    通用HTTP请求工具类

    @staticmethod 静态方法装饰器，无需实例化即可调用（RequestUtil.send_request()）
    为什么用静态方法？因为send_request不需要访问实例属性（self）或类属性（cls），它只依赖传入的参数，所以适合定义为静态方法
    """

    @staticmethod
    def send_requests(
        method: str,
        url: str,
        # Optional[X]代表允许传 X 或者 None，= None时表示不传入时默认值为 None
        headers: Optional[Dict[str, str]] = None,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Optional[requests.Response]:  # 这里不能加= None，返回值不存在默认值
        """
        通用HTTP请求工具：支持GET/POST/DELETE等所有请求方法
        :param method: 请求方法（get / post / delete）
        :param url: 请求URL
        :param headers: 请求头（字典格式，默认None）
        :param json: 请求体（Json格式，默认None）
        :param params: URL参数（字典格式，默认None）
        :return: 成功返回requests.Response对象，异常时返回None
        """
        headers = headers if headers else {}
        # method.upper()将请求方法转为大写（get -> GET）
        logger.info(
            f"发送{method.upper()}请求：URL={url},Headers={headers},Json={json}"
        )
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                json=json,
                params=params,
                timeout=TIMEOUT,
            )
            # 只显示日志前500个字符，避免日志过长
            logger.info(
                f"接受响应：状态码={response.status_code}，响应体={response.text[:500]}"
            )
            return response
        except Exception as e:
            logger.error(f"{method.upper()}请求异常：URL={url}，错误信息={str(e)}")
            return None
