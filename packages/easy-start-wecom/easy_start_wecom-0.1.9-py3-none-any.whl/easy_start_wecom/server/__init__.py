#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
企业微信服务器API客户端模块
该模块提供了与企业微信服务器API交互的功能，支持同步和异步请求方式
封装了访问令牌管理、IP地址获取、媒体上传、消息发送等核心功能
"""

import diskcache
import httpx
import redis
from jsonschema.validators import Draft202012Validator


class Api:
    """
    企业微信服务器API客户端类
    用于与企业微信服务器API进行交互，提供获取访问令牌、API域名IP等功能
    支持同步和异步两种请求模式，并集成了访问令牌缓存机制
    """

    def __init__(
            self,
            base_url: str = "https://qyapi.weixin.qq.com",
            corpid: str = "",
            corpsecret: str = "",
            cache_config: dict = dict()
    ):
        """
        初始化企业微信服务器API客户端

        参数:
            base_url (str): API基础URL，默认值为企业微信官方API地址
            corpid (str): 企业ID，用于标识企业微信账号
            corpsecret (str): 应用密钥，用于验证应用身份
            cache_config (dict): 缓存配置，用于存储访问令牌，支持diskcache和redis
        """
        # 处理URL末尾的斜杠，确保格式统一
        self.base_url = base_url[:-1] if base_url.endswith("/") else base_url
        self.corpid = corpid  # 企业ID
        self.corpsecret = corpsecret  # 应用密钥
        self.cache_config = cache_config if isinstance(cache_config, dict) else dict()
        self.access_token = ""

        # 设置缓存配置默认值
        self.cache_config.setdefault("key", f"wecom_server_access_token_{self.corpid}")
        self.cache_config.setdefault("expire", 7100)  # 缓存过期时间（秒），比官方7200秒少100秒以确保平滑过渡
        self.cache_config.setdefault("instance", None)  # 缓存实例，支持diskcache.Cache或redis.Redis

    def client(self, **kwargs):
        """
        创建同步HTTP客户端

        参数:
            **kwargs: 传递给httpx.Client的额外参数，可覆盖默认配置

        返回:
            httpx.Client: 配置好的同步HTTP客户端实例
        """
        kwargs.setdefault("base_url", self.base_url)  # 设置基础URL
        kwargs.setdefault("timeout", 120)  # 设置超时时间为120秒
        kwargs.setdefault("verify", False)  # 不验证SSL证书（适合开发环境）
        return httpx.Client(**kwargs)

    def async_client(self, **kwargs):
        """
        创建异步HTTP客户端

        参数:
            **kwargs: 传递给httpx.AsyncClient的额外参数，可覆盖默认配置

        返回:
            httpx.AsyncClient: 配置好的异步HTTP客户端实例
        """
        kwargs.setdefault("base_url", self.base_url)  # 设置基础URL
        kwargs.setdefault("timeout", 120)  # 设置超时时间为120秒
        kwargs.setdefault("verify", False)  # 不验证SSL证书（适合开发环境）
        return httpx.AsyncClient(**kwargs)

    def gettoken(
            self,
            client: httpx.Client = None,
            validate_json_schema: dict = {
                "properties": {
                    "errcode": {
                        "oneOf": [
                            {"type": "integer", "const": 0},
                            {"type": "string", "const": "0"},
                        ]
                    },
                },
                "required": ["errcode"],
            },
            **kwargs
    ):
        """
        获取访问令牌

        @see https://developer.work.weixin.qq.com/document/path/91039

        参数:
            client (httpx.Client): HTTP客户端实例，若为None则自动创建
            validate_json_schema (dict): JSON响应验证模式，用于验证API返回结果
            **kwargs: 传递给client.request的额外参数

        返回:
            tuple: (验证结果, 访问令牌, 响应对象)
                - 验证结果: 布尔值，表示响应是否符合验证模式
                - 访问令牌: 字符串，企业微信API访问令牌，若获取失败则为None
                - 响应对象: httpx.Response实例
        """
        kwargs.setdefault("method", "GET")  # 默认使用GET方法
        kwargs.setdefault("url", "/cgi-bin/gettoken")  # 设置获取令牌的API路径
        params = kwargs.get("params", dict())
        params.setdefault("corpid", self.corpid)  # 设置企业ID参数
        params.setdefault("corpsecret", self.corpsecret)  # 设置应用密钥参数
        kwargs["params"] = params

        # 使用传入的客户端或创建新客户端
        if not isinstance(client, httpx.Client):
            with self.client() as client:
                response = client.request(**kwargs)  # 发送请求
        else:
            response = client.request(**kwargs)  # 发送请求

        # 解析响应JSON（请求失败时返回空字典）
        response_json = response.json() if response.is_success else dict()
        self.access_token = response_json.get("access_token", None)
        return Draft202012Validator(validate_json_schema).is_valid(response_json), response_json.get("access_token",
                                                                                                     None), response

    async def async_gettoken(
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
        """
        异步获取访问令牌

        @see https://developer.work.weixin.qq.com/document/path/91039

        参数:
            client (httpx.AsyncClient): 异步HTTP客户端实例，若为None则自动创建
            validate_json_schema (dict): JSON响应验证模式，用于验证API返回结果
            **kwargs: 传递给client.request的额外参数

        返回:
            tuple: (验证结果, 访问令牌, 响应对象)
                - 验证结果: 布尔值，表示响应是否符合验证模式
                - 访问令牌: 字符串，企业微信API访问令牌，若获取失败则为None
                - 响应对象: httpx.Response实例
        """
        kwargs.setdefault("method", "GET")  # 默认使用GET方法
        kwargs.setdefault("url", "/cgi-bin/gettoken")  # 设置获取令牌的API路径
        params = kwargs.get("params", dict())
        params.setdefault("corpid", self.corpid)  # 设置企业ID参数
        params.setdefault("corpsecret", self.corpsecret)  # 设置应用密钥参数
        kwargs["params"] = params

        # 使用传入的客户端或创建新客户端
        if not isinstance(client, httpx.AsyncClient):
            async with self.async_client() as client:
                response = await client.request(**kwargs)  # 发送异步请求
        else:
            response = await client.request(**kwargs)  # 发送异步请求

        # 解析响应JSON（请求失败时返回空字典）
        response_json = response.json() if response.is_success else dict()
        self.access_token = response_json.get("access_token", None)
        return Draft202012Validator(validate_json_schema).is_valid(response_json), response_json.get("access_token",
                                                                                                     None), response

    def get_api_domain_ip(
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
            access_token: str = None,
            **kwargs
    ):
        """
        获取企业微信API域名IP列表

        @see https://developer.work.weixin.qq.com/document/path/92520

        参数:
            client (httpx.Client): HTTP客户端实例，若为None则自动创建
            validate_json_schema (dict): JSON响应验证模式，用于验证API返回结果
            access_token (str): 访问令牌，若为None则需在kwargs中提供
            **kwargs: 传递给client.request的额外参数

        返回:
            tuple: (验证结果, IP列表, 响应对象)
                - 验证结果: 布尔值，表示响应是否符合验证模式
                - IP列表: 列表，企业微信API域名IP地址列表，若获取失败则为None
                - 响应对象: httpx.Response实例
        """
        access_token = access_token if isinstance(access_token, str) and len(access_token) else self.access_token
        kwargs.setdefault("method", "GET")  # 默认使用GET方法
        kwargs.setdefault("url", "/cgi-bin/get_api_domain_ip")  # 设置获取API域名IP的路径
        params = kwargs.get("params", dict())
        params.setdefault("access_token", access_token)  # 设置访问令牌参数
        kwargs["params"] = params

        # 使用传入的客户端或创建新客户端
        if not isinstance(client, httpx.Client):
            with self.client() as client:
                response = client.request(**kwargs)  # 发送请求
        else:
            response = client.request(**kwargs)  # 发送请求

        # 解析响应JSON（请求失败时返回空字典）
        response_json = response.json() if response.is_success else dict()
        return Draft202012Validator(validate_json_schema).is_valid(response_json), response_json.get("ip_list",
                                                                                                     None), response

    async def async_get_api_domain_ip(
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
            access_token: str = None,
            **kwargs
    ):
        """
        异步获取企业微信API域名IP列表

        @see https://developer.work.weixin.qq.com/document/path/92520

        参数:
            client (httpx.AsyncClient): 异步HTTP客户端实例，若为None则自动创建
            validate_json_schema (dict): JSON响应验证模式，用于验证API返回结果
            access_token (str): 访问令牌，若为None则需在kwargs中提供
            **kwargs: 传递给client.request的额外参数

        返回:
            tuple: (验证结果, IP列表, 响应对象)
                - 验证结果: 布尔值，表示响应是否符合验证模式
                - IP列表: 列表，企业微信API域名IP地址列表，若获取失败则为None
                - 响应对象: httpx.Response实例
        """
        access_token = access_token if isinstance(access_token, str) and len(access_token) else self.access_token
        kwargs.setdefault("method", "GET")  # 默认使用GET方法
        kwargs.setdefault("url", "/cgi-bin/get_api_domain_ip")  # 设置获取API域名IP的路径
        params = kwargs.get("params", dict())
        params.setdefault("access_token", access_token)  # 设置访问令牌参数
        kwargs["params"] = params

        # 使用传入的客户端或创建新客户端
        if not isinstance(client, httpx.AsyncClient):
            async with self.async_client() as client:
                response = await client.request(**kwargs)  # 发送异步请求
        else:
            response = await client.request(**kwargs)  # 发送异步请求

        # 解析响应JSON（请求失败时返回空字典）
        response_json = response.json() if response.is_success else dict()
        return Draft202012Validator(validate_json_schema).is_valid(response_json), response_json.get("ip_list",
                                                                                                     None), response

    def getcallbackip(
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
            access_token: str = None,
            **kwargs
    ):
        """
        获取企业微信回调IP列表

        @see https://developer.work.weixin.qq.com/document/path/92521

        参数:
            client (httpx.Client): HTTP客户端实例，若为None则自动创建
            validate_json_schema (dict): JSON响应验证模式，用于验证API返回结果
            access_token (str): 访问令牌，若为None则需在kwargs中提供
            **kwargs: 传递给client.request的额外参数

        返回:
            tuple: (验证结果, IP列表, 响应对象)
                - 验证结果: 布尔值，表示响应是否符合验证模式
                - IP列表: 列表，企业微信回调IP地址列表，若获取失败则为None
                - 响应对象: httpx.Response实例
        """
        access_token = access_token if isinstance(access_token, str) and len(access_token) else self.access_token
        kwargs.setdefault("method", "GET")  # 默认使用GET方法
        kwargs.setdefault("url", "/cgi-bin/getcallbackip")  # 设置获取回调IP的路径
        params = kwargs.get("params", dict())
        params.setdefault("access_token", access_token)  # 设置访问令牌参数
        kwargs["params"] = params

        # 使用传入的客户端或创建新客户端
        if not isinstance(client, httpx.Client):
            with self.client() as client:
                response = client.request(**kwargs)  # 发送请求
        else:
            response = client.request(**kwargs)  # 发送请求

        # 解析响应JSON（请求失败时返回空字典）
        response_json = response.json() if response.is_success else dict()
        return Draft202012Validator(validate_json_schema).is_valid(response_json), response_json.get("ip_list",
                                                                                                     None), response

    async def async_getcallbackip(
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
            access_token: str = None,
            **kwargs
    ):
        """
        异步获取企业微信回调IP列表

        @see https://developer.work.weixin.qq.com/document/path/92521

        参数:
            client (httpx.AsyncClient): 异步HTTP客户端实例，若为None则自动创建
            validate_json_schema (dict): JSON响应验证模式，用于验证API返回结果
            access_token (str): 访问令牌，若为None则需在kwargs中提供
            **kwargs: 传递给client.request的额外参数

        返回:
            tuple: (验证结果, IP列表, 响应对象)
                - 验证结果: 布尔值，表示响应是否符合验证模式
                - IP列表: 列表，企业微信回调IP地址列表，若获取失败则为None
                - 响应对象: httpx.Response实例
        """
        access_token = access_token if isinstance(access_token, str) and len(access_token) else self.access_token
        kwargs.setdefault("method", "GET")  # 默认使用GET方法
        kwargs.setdefault("url", "/cgi-bin/getcallbackip")  # 设置获取回调IP的路径
        params = kwargs.get("params", dict())
        params.setdefault("access_token", access_token)  # 设置访问令牌参数
        kwargs["params"] = params

        # 使用传入的客户端或创建新客户端
        if not isinstance(client, httpx.AsyncClient):
            async with self.async_client() as client:
                response = await client.request(**kwargs)  # 发送异步请求
        else:
            response = await client.request(**kwargs)  # 发送异步请求

        # 解析响应JSON（请求失败时返回空字典）
        response_json = response.json() if response.is_success else dict()
        return Draft202012Validator(validate_json_schema).is_valid(response_json), response_json.get("ip_list",
                                                                                                     None), response

    def refresh_token(self, client: httpx.Client = None):
        """
        刷新访问令牌（从缓存获取或重新获取）

        参数:
            client (httpx.Client): HTTP客户端实例，若为None则自动创建

        返回:
            str: 有效的企业微信API访问令牌
        """
        cache_key = self.cache_config.get("key", f"wecom_server_access_token_{self.corpid}")
        cache_inst = self.cache_config.get("instance", None)
        cache_expire = self.cache_config.get("expire", 7100)

        # 如果没有缓存实例或缓存实例类型不支持，则直接获取新令牌
        if not isinstance(cache_inst, (diskcache.Cache, redis.Redis, redis.StrictRedis)):
            state, access_token, _ = self.gettoken(client=client)
        else:
            # 从缓存获取访问令牌
            access_token = cache_inst.get(cache_key, None)

        # 验证访问令牌是否有效
        state, _, _ = self.get_api_domain_ip(client=client, access_token=access_token)
        if not state:
            # 访问令牌无效，重新获取
            state, access_token, _ = self.gettoken(client=client)

        # 将访问令牌存入缓存
        if state and isinstance(cache_inst, diskcache.Cache):
            cache_inst.set(cache_key, access_token, expire=cache_expire)
        if state and isinstance(cache_inst, (redis.Redis, redis.StrictRedis)):
            cache_inst.set(cache_key, access_token, ex=cache_expire)
        self.access_token = access_token
        return self

    async def async_refresh_token(self, client: httpx.AsyncClient = None):
        """
        异步刷新访问令牌（从缓存获取或重新获取）

        参数:
            client (httpx.AsyncClient): 异步HTTP客户端实例，若为None则自动创建

        返回:
            str: 有效的企业微信API访问令牌
        """
        cache_key = self.cache_config.get("key", f"wecom_server_access_token_{self.corpid}")
        cache_inst = self.cache_config.get("instance", None)
        cache_expire = self.cache_config.get("expire", 7100)

        # 如果没有缓存实例或缓存实例类型不支持，则直接获取新令牌
        if not isinstance(cache_inst, (diskcache.Cache, redis.Redis, redis.StrictRedis)):
            state, access_token, _ = await self.async_gettoken(client=client)
        else:
            # 从缓存获取访问令牌
            access_token = cache_inst.get(cache_key, None)

        # 验证访问令牌是否有效
        state, _, _ = await self.async_get_api_domain_ip(client=client, access_token=access_token)
        if not state:
            # 访问令牌无效，重新获取
            state, access_token, _ = await self.async_gettoken(client=client)

        # 将访问令牌存入缓存
        if state and isinstance(cache_inst, diskcache.Cache):
            cache_inst.set(cache_key, access_token, expire=cache_expire)
        if state and isinstance(cache_inst, (redis.Redis, redis.StrictRedis)):
            cache_inst.set(cache_key, access_token, ex=cache_expire)
        self.access_token = access_token
        return self

    def media_upload(
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
            access_token: str = None,
            file_type: str = "file",
            **kwargs
    ):
        """
        上传临时素材

        @see https://developer.work.weixin.qq.com/document/path/90253

        参数:
            client (httpx.Client): HTTP客户端实例，若为None则自动创建
            validate_json_schema (dict): JSON响应验证模式，用于验证API返回结果
            access_token (str): 访问令牌，若为None则需在kwargs中提供
            file_type (str): 素材类型，可选值：image(图片)、voice(语音)、video(视频)、file(文件)
            **kwargs: 传递给client.request的额外参数，需包含files参数用于上传文件

        返回:
            tuple: (验证结果, 素材ID, 响应对象)
                - 验证结果: 布尔值，表示响应是否符合验证模式
                - 素材ID: 字符串，上传成功的临时素材ID，若上传失败则为None
                - 响应对象: httpx.Response实例
        """
        # 验证素材类型，默认值为file
        file_type = file_type if file_type in ["image", "voice", "video", "file"] else "file"
        access_token = access_token if isinstance(access_token, str) and len(access_token) else self.access_token
        kwargs.setdefault("method", "POST")  # 默认使用POST方法
        kwargs.setdefault("url", "/cgi-bin/media/upload")  # 设置上传临时素材的API路径

        params = kwargs.get("params", dict())
        params.setdefault("access_token", access_token)  # 设置访问令牌参数
        params.setdefault("type", file_type)  # 设置素材类型参数
        kwargs["params"] = params

        # 使用传入的客户端或创建新客户端
        if not isinstance(client, httpx.Client):
            with self.client() as client:
                response = client.request(**kwargs)
        else:
            response = client.request(**kwargs)  # 发送请求

        # 解析响应JSON（请求失败时返回空字典）
        response_json = response.json() if response.is_success else dict()
        return Draft202012Validator(validate_json_schema).is_valid(response_json), response_json.get("media_id",
                                                                                                     None), response

    async def async_media_upload(
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
            access_token: str = None,
            file_type: str = "file",
            **kwargs
    ):
        """
        异步上传临时素材

        @see https://developer.work.weixin.qq.com/document/path/90253

        参数:
            client (httpx.AsyncClient): 异步HTTP客户端实例，若为None则自动创建
            validate_json_schema (dict): JSON响应验证模式，用于验证API返回结果
            access_token (str): 访问令牌，若为None则需在kwargs中提供
            file_type (str): 素材类型，可选值：image(图片)、voice(语音)、video(视频)、file(文件)
            **kwargs: 传递给client.request的额外参数，需包含files参数用于上传文件

        返回:
            tuple: (验证结果, 素材ID, 响应对象)
                - 验证结果: 布尔值，表示响应是否符合验证模式
                - 素材ID: 字符串，上传成功的临时素材ID，若上传失败则为None
                - 响应对象: httpx.Response实例
        """
        # 验证素材类型，默认值为file
        file_type = file_type if file_type in ["image", "voice", "video", "file"] else "file"
        access_token = access_token if isinstance(access_token, str) and len(access_token) else self.access_token
        kwargs.setdefault("method", "POST")  # 默认使用POST方法
        kwargs.setdefault("url", "/cgi-bin/media/upload")  # 设置上传临时素材的API路径

        params = kwargs.get("params", dict())
        params.setdefault("access_token", access_token)  # 设置访问令牌参数
        params.setdefault("type", file_type)  # 设置素材类型参数
        kwargs["params"] = params

        # 使用传入的客户端或创建新客户端
        if not isinstance(client, httpx.AsyncClient):
            async with self.async_client() as client:
                response = await client.request(**kwargs)
        else:
            response = await client.request(**kwargs)  # 发送请求

        # 解析响应JSON（请求失败时返回空字典）
        response_json = response.json() if response.is_success else dict()
        return Draft202012Validator(validate_json_schema).is_valid(response_json), response_json.get("media_id",
                                                                                                     None), response

    def media_uploadimg(
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
            access_token: str = None,
            **kwargs
    ):
        """
        上传图片并返回URL（用于消息中的图片）

        @see https://developer.work.weixin.qq.com/document/path/90256

        参数:
            client (httpx.Client): HTTP客户端实例，若为None则自动创建
            validate_json_schema (dict): JSON响应验证模式，用于验证API返回结果
            access_token (str): 访问令牌，若为None则需在kwargs中提供
            **kwargs: 传递给client.request的额外参数，需包含files参数用于上传图片

        返回:
            tuple: (验证结果, 图片URL, 响应对象)
                - 验证结果: 布尔值，表示响应是否符合验证模式
                - 图片URL: 字符串，上传成功的图片URL，可直接用于消息发送，若上传失败则为None
                - 响应对象: httpx.Response实例
        """
        access_token = access_token if isinstance(access_token, str) and len(access_token) else self.access_token
        kwargs.setdefault("method", "POST")  # 默认使用POST方法
        kwargs.setdefault("url", "/cgi-bin/media/uploadimg")  # 设置上传图片的API路径

        params = kwargs.get("params", dict())
        params.setdefault("access_token", access_token)  # 设置访问令牌参数
        kwargs["params"] = params

        # 使用传入的客户端或创建新客户端
        if not isinstance(client, httpx.Client):
            with self.client() as client:
                response = client.request(**kwargs)
        else:
            response = client.request(**kwargs)  # 发送请求

        # 解析响应JSON（请求失败时返回空字典）
        response_json = response.json() if response.is_success else dict()
        return Draft202012Validator(validate_json_schema).is_valid(response_json), response_json.get("url",
                                                                                                     None), response

    async def async_media_uploadimg(
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
            access_token: str = None,
            **kwargs
    ):
        """
        异步上传图片并返回URL（用于消息中的图片）

        @see https://developer.work.weixin.qq.com/document/path/90256

        参数:
            client (httpx.AsyncClient): 异步HTTP客户端实例，若为None则自动创建
            validate_json_schema (dict): JSON响应验证模式，用于验证API返回结果
            access_token (str): 访问令牌，若为None则需在kwargs中提供
            **kwargs: 传递给client.request的额外参数，需包含files参数用于上传图片

        返回:
            tuple: (验证结果, 图片URL, 响应对象)
                - 验证结果: 布尔值，表示响应是否符合验证模式
                - 图片URL: 字符串，上传成功的图片URL，可直接用于消息发送，若上传失败则为None
                - 响应对象: httpx.Response实例
        """
        access_token = access_token if isinstance(access_token, str) and len(access_token) else self.access_token
        kwargs.setdefault("method", "POST")  # 默认使用POST方法
        kwargs.setdefault("url", "/cgi-bin/media/uploadimg")  # 设置上传图片的API路径
        params = kwargs.get("params", dict())
        params.setdefault("access_token", access_token)  # 设置访问令牌参数
        kwargs["params"] = params

        # 使用传入的客户端或创建新客户端
        if not isinstance(client, httpx.AsyncClient):
            async with self.async_client() as client:
                response = await client.request(**kwargs)
        else:
            response = await client.request(**kwargs)  # 发送请求

        # 解析响应JSON（请求失败时返回空字典）
        response_json = response.json() if response.is_success else dict()
        return Draft202012Validator(validate_json_schema).is_valid(response_json), response_json.get("url",
                                                                                                     None), response

    def message_send(
            self,
            client: httpx.Client=None,
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
            access_token: str = None,
            **kwargs
    ):
        """
        同步发送企业微信消息

        该函数通过同步HTTP客户端向企业微信API发送消息请求，
        支持灵活配置请求参数，并根据需要返回不同的结果格式。

        @see https://developer.work.weixin.qq.com/document/path/90236

        参数:
            client (httpx.Client): 同步HTTP客户端实例
            validate_json_schema (dict): JSON响应验证模式，用于验证API返回结果
            access_token (str): 企业微信API访问令牌
            **kwargs: 额外的请求参数，将直接传递给client.request方法
                可覆盖默认的method和url等参数

        返回:
            tuple: (验证结果, 响应JSON, 响应对象)
                - 验证结果: 布尔值，表示响应是否符合验证模式
                - 响应JSON: 字典，API返回的JSON数据，若请求失败则返回空字典
                - 响应对象: httpx.Response实例
        """
        access_token = access_token if isinstance(access_token, str) and len(access_token) else self.access_token
        # 设置默认请求方法为POST
        kwargs.setdefault("method", "POST")
        # 设置默认API端点为消息发送接口
        kwargs.setdefault("url", "/cgi-bin/message/send")

        # 获取或创建请求参数字典
        params = kwargs.get("params", dict())
        # 添加访问令牌到请求参数
        params.setdefault("access_token", access_token)
        kwargs["params"] = params

        # 使用传入的客户端或创建新客户端
        if not isinstance(client, httpx.Client):
            with self.client() as client:
                response = client.request(**kwargs)
        else:
            response = client.request(**kwargs)  # 发送请求

        # 解析响应JSON（请求失败时返回空字典）
        response_json = response.json() if response.is_success else dict()
        return Draft202012Validator(validate_json_schema).is_valid(response_json), response_json, response

    async def async_message_send(
            self,
            client: httpx.AsyncClient,
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
            access_token: str = None,
            **kwargs
    ):
        """
        异步发送企业微信消息

        该函数通过异步HTTP客户端向企业微信API发送消息请求，
        支持灵活配置请求参数，并根据需要返回不同的结果格式。

        @see https://developer.work.weixin.qq.com/document/path/90236

        参数:
            client (httpx.AsyncClient): 异步HTTP客户端实例
            validate_json_schema (dict): JSON响应验证模式，用于验证API返回结果
            access_token (str): 企业微信API访问令牌
            **kwargs: 额外的请求参数，将直接传递给client.request方法
                可覆盖默认的method和url等参数

        返回:
            tuple: (验证结果, 响应JSON, 响应对象)
                - 验证结果: 布尔值，表示响应是否符合验证模式
                - 响应JSON: 字典，API返回的JSON数据，若请求失败则返回空字典
                - 响应对象: httpx.Response实例
        """
        access_token = access_token if isinstance(access_token, str) and len(access_token) else self.access_token
        kwargs.setdefault("method", "POST")  # 默认使用POST方法
        kwargs.setdefault("url", "/cgi-bin/message/send")  # 设置消息发送API路径
        params = kwargs.get("params", dict())
        params.setdefault("access_token", access_token)  # 设置访问令牌参数
        kwargs["params"] = params

        # 使用传入的客户端或创建新客户端
        if not isinstance(client, httpx.AsyncClient):
            async with self.async_client() as client:
                response = await client.request(**kwargs)  # 发送异步请求
        else:
            response = await client.request(**kwargs)  # 发送异步请求

        # 解析响应JSON（请求失败时返回空字典）
        response_json = response.json() if response.is_success else dict()
        return Draft202012Validator(validate_json_schema).is_valid(response_json), response_json, response
