#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
微信企业号(WeCom) Webhook消息发送模块

该模块提供了与微信企业号Webhook API交互的功能，支持同步和异步两种通信方式，
可以发送文本消息、上传文件等操作，自动处理请求参数构建和响应验证。
"""
import httpx
from jsonschema.validators import Draft202012Validator


class Api:
    """微信企业号Webhook API客户端类

    用于与微信企业号Webhook API交互，提供消息发送、文件上传等功能，
    支持同步和异步两种通信方式，自动处理请求参数构建和响应验证。

    属性:
        base_url: API基础URL，默认值为"https://qyapi.weixin.qq.com"
        key: Webhook密钥，用于API认证
        mentioned_list: 默认提及的用户列表（企业微信用户ID）
        mentioned_mobile_list: 默认提及的手机号码列表

    主要方法:
        client(): 创建同步HTTP客户端
        async_client(): 创建异步HTTP客户端
        send(): 同步发送消息
        async_send(): 异步发送消息
        upload_media(): 同步上传媒体文件
        async_upload_media(): 异步上传媒体文件
    """

    def __init__(
            self,
            base_url: str = "https://qyapi.weixin.qq.com",
            key: str = "",
            mentioned_list: list = [],
            mentioned_mobile_list: list = []
    ):
        """初始化Api实例

        Args:
            base_url: API基础URL，默认使用微信企业号API地址
            key: Webhook密钥，用于API认证
            mentioned_list: 默认提及的用户列表（企业微信用户ID）
            mentioned_mobile_list: 默认提及的手机号码列表
        """
        # 确保URL末尾没有斜杠，统一URL格式
        self.base_url = base_url[:-1] if base_url.endswith("/") else base_url
        self.key = key
        self.mentioned_list = mentioned_list
        self.mentioned_mobile_list = mentioned_mobile_list

    def client(self, **kwargs):
        """创建并返回同步HTTP客户端

        Args:
            **kwargs: 传递给httpx.Client的额外参数
                可覆盖默认配置（base_url, timeout, verify等）

        Returns:
            httpx.Client: 配置好的同步HTTP客户端实例
        """
        # 设置默认基础URL
        kwargs.setdefault("base_url", self.base_url)
        # 设置默认超时时间为120秒
        kwargs.setdefault("timeout", 120)
        # 禁用SSL证书验证
        kwargs.setdefault("verify", False)
        return httpx.Client(**kwargs)

    def async_client(self, **kwargs):
        """创建并返回异步HTTP客户端

        Args:
            **kwargs: 传递给httpx.AsyncClient的额外参数
                可覆盖默认配置（base_url, timeout, verify等）

        Returns:
            httpx.AsyncClient: 配置好的异步HTTP客户端实例
        """
        # 设置默认基础URL
        kwargs.setdefault("base_url", self.base_url)
        # 设置默认超时时间为120秒
        kwargs.setdefault("timeout", 120)
        # 禁用SSL证书验证
        kwargs.setdefault("verify", False)
        return httpx.AsyncClient(**kwargs)

    def send(
            self,
            client: httpx.Client = None,
            validate_json_schema: dict = {
                "properties": {
                    "errcode": {
                        "oneOf": [
                            {"type": "integer", "const": 0},
                            {"type": "string", "const": "0"},
                        ]
                    }
                },
                "required": ["errcode"],
            },
            **kwargs
    ):
        """发送消息（同步方式）

        Args:
            client: 可选的同步HTTP客户端实例，如果不提供则自动创建
            validate_json_schema: JSON Schema校验规则，用于验证API响应的有效性
            **kwargs: 传递给request方法的额外参数，主要用于指定消息内容

        Returns:
            tuple: (发送结果, 响应JSON, 响应对象)
                - 发送结果: bool，True表示发送成功，False表示失败
                - 响应JSON: dict，API返回的JSON数据
                - 响应对象: httpx.Response，原始响应对象
        """
        # 设置默认请求方法为POST
        kwargs.setdefault("method", "POST")
        # 设置默认API端点为webhook消息发送接口
        kwargs.setdefault("url", "/cgi-bin/webhook/send")
        # 获取或创建请求参数字典
        params = kwargs.get("params", dict())
        # 添加webhook密钥到请求参数
        params.setdefault("key", self.key)
        kwargs["params"] = params
        json_data = kwargs.get("json", dict())
        if json_data.get("msgtype", "") == "text":
            text = json_data.get("text", dict())
            mentioned_list = kwargs.get("mentioned_list", [])
            mentioned_mobile_list = kwargs.get("mentioned_mobile_list", [])
            text["mentioned_list"] = self.mentioned_list + mentioned_list
            text["mentioned_mobile_list"] = self.mentioned_mobile_list + mentioned_mobile_list
            json_data["text"] = text
        kwargs["json"] = json_data

        if not isinstance(client, httpx.Client):
            with self.client() as client:
                response = client.request(**kwargs)
        else:
            response = client.request(**kwargs)
        response_json = response.json() if response.is_success else dict()
        return Draft202012Validator(validate_json_schema).is_valid(response_json), response_json, response

    async def async_send(
            self,
            client: httpx.AsyncClient = None,
            validate_json_schema: dict = {
                "properties": {
                    "errcode": {
                        "oneOf": [
                            {"type": "integer", "const": 0},
                            {"type": "string", "const": "0"},
                        ]
                    }
                },
                "required": ["errcode"],
            },
            **kwargs
    ):
        """发送消息（异步方式）

        Args:
            client: 可选的异步HTTP客户端实例，如果不提供则自动创建
            validate_json_schema: JSON Schema校验规则，用于验证API响应的有效性
            **kwargs: 传递给request方法的额外参数，主要用于指定消息内容

        Returns:
            tuple: (发送结果, 响应JSON, 响应对象)
                - 发送结果: bool，True表示发送成功，False表示失败
                - 响应JSON: dict，API返回的JSON数据
                - 响应对象: httpx.Response，原始响应对象
        """
        # 设置默认请求方法为POST
        kwargs.setdefault("method", "POST")
        # 设置默认API端点为webhook消息发送接口
        kwargs.setdefault("url", "/cgi-bin/webhook/send")
        # 获取或创建请求参数字典
        params = kwargs.get("params", dict())
        # 添加webhook密钥到请求参数
        params.setdefault("key", self.key)
        kwargs["params"] = params
        json_data = kwargs.get("json", dict())
        if json_data.get("msgtype", "") == "text":
            text = json_data.get("text", dict())
            mentioned_list = kwargs.get("mentioned_list", [])
            mentioned_mobile_list = kwargs.get("mentioned_mobile_list", [])
            text["mentioned_list"] = self.mentioned_list + mentioned_list
            text["mentioned_mobile_list"] = self.mentioned_mobile_list + mentioned_mobile_list
            json_data["text"] = text
        kwargs["json"] = json_data
        if not isinstance(client, httpx.AsyncClient):
            async with self.async_client() as client:
                response = await client.request(**kwargs)
        else:
            response = await client.request(**kwargs)
        response_json = response.json() if response.is_success else dict()
        return Draft202012Validator(validate_json_schema).is_valid(response_json), response_json, response

    def upload_media(
            self,
            client: httpx.Client = None,
            validate_json_schema: dict = {
                "properties": {
                    "errcode": {
                        "oneOf": [
                            {"type": "integer", "const": 0},
                            {"type": "string", "const": "0"},
                        ]
                    }
                },
                "required": ["errcode"],
            },
            file_type: str = "file",
            **kwargs
    ):
        """上传媒体文件（同步方式）

        Args:
            client: 可选的同步HTTP客户端实例，如果不提供则自动创建
            validate_json_schema: JSON Schema校验规则，用于验证API响应的有效性
            file_type: 文件类型，只允许"file"或"voice"
            **kwargs: 传递给request方法的额外参数，用于指定上传的文件

        Returns:
            tuple: (上传结果, media_id, 响应对象)
                - 上传结果: bool，True表示上传成功，False表示失败
                - media_id: str，上传成功后返回的媒体文件ID，用于后续发送文件消息
                - 响应对象: httpx.Response，原始响应对象
        """
        # 验证并修复文件类型，只允许"file"或"voice"
        file_type = file_type if file_type in ["file", "voice"] else "file"
        # 设置默认请求方法为POST
        kwargs.setdefault("method", "POST")
        # 设置默认API端点为媒体上传接口
        kwargs.setdefault("url", "/cgi-bin/webhook/upload_media")
        # 获取或创建请求参数字典
        params = kwargs.get("params", dict())
        # 添加webhook密钥到请求参数
        params.setdefault("key", self.key)
        # 添加文件类型到请求参数
        params.setdefault("type", file_type)
        kwargs["params"] = params
        if not isinstance(client, httpx.Client):
            with self.client() as client:
                response = client.request(**kwargs)
        else:
            response = client.request(**kwargs)
        response_json = response.json() if response.is_success else dict()
        return Draft202012Validator(validate_json_schema).is_valid(response_json), response_json.get("media_id",
                                                                                                     None), response

    async def async_upload_media(
            self,
            client: httpx.AsyncClient = None,
            validate_json_schema: dict = {
                "properties": {
                    "errcode": {
                        "oneOf": [
                            {"type": "integer", "const": 0},
                            {"type": "string", "const": "0"},
                        ]
                    }
                },
                "required": ["errcode"],
            },
            file_type: str = "file",
            **kwargs
    ):
        """上传媒体文件（异步方式）

        Args:
            client: 可选的异步HTTP客户端实例，如果不提供则自动创建
            validate_json_schema: JSON Schema校验规则，用于验证API响应的有效性
            file_type: 文件类型，只允许"file"或"voice"
            **kwargs: 传递给request方法的额外参数，用于指定上传的文件

        Returns:
            tuple: (上传结果, media_id, 响应对象)
                - 上传结果: bool，True表示上传成功，False表示失败
                - media_id: str，上传成功后返回的媒体文件ID，用于后续发送文件消息
                - 响应对象: httpx.Response，原始响应对象
        """
        file_type = file_type if file_type in ["file", "voice"] else "file"
        # 设置默认请求方法为POST
        kwargs.setdefault("method", "POST")
        # 设置默认API端点为媒体上传接口
        kwargs.setdefault("url", "/cgi-bin/webhook/upload_media")
        # 获取或创建请求参数字典
        params = kwargs.get("params", dict())
        # 添加webhook密钥到请求参数
        params.setdefault("key", self.key)
        # 添加文件类型到请求参数
        params.setdefault("type", file_type)
        kwargs["params"] = params
        if not isinstance(client, httpx.AsyncClient):
            async with self.async_client() as client:
                response = await client.request(**kwargs)
        else:
            response = await client.request(**kwargs)
        response_json = response.json() if response.is_success else dict()
        return Draft202012Validator(validate_json_schema).is_valid(response_json), response_json.get("media_id",
                                                                                                     None), response
