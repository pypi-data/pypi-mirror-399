"""
@Author: 馒头 (chocolate)
@Email: neihanshenshou@163.com
@File: HttpRequest.py
@Time: 2023/12/9 18:00
"""

import json as json_v2
from urllib import parse
from urllib.parse import unquote

from requests import Response
from requests import Session

from SteamedBun import logger


def __hook_response(response: Response, **kwargs):
    response.encoding = "utf-8"
    try:
        result = json_v2.dumps(response.json(), ensure_ascii=False)
    except Exception as e:
        result = response.text or e

    kwargs = {"服务code码": response.status_code, **kwargs}
    if kwargs.get("proxies"):
        del kwargs["proxies"]

    query = unquote(parse.urlparse(response.url).query or parse.urlparse(response.url).params)
    body = response.request.body
    trace_id = response.headers.get("traceid")
    try:
        body = body.decode(encoding="utf-8") if body else None
        body = json_v2.dumps(json_v2.loads(body), ensure_ascii=False)
    except Exception as e:
        print("" and e, end="")

    logger.info(f"""
    请求方法: {response.request.method}
    请求地址: {response.request.url.split("?")[0]}
    请求内容: {body or query or {} }
    请求响应: {result}
    请求时长: {response.elapsed.total_seconds()} 秒
    更多内容: {kwargs}
    TraceId: {trace_id}
        """)


def request(url,
            method="post",
            show=True,
            params=None,
            data=None,
            headers=None,
            cookies=None,
            timeout=10,
            verify=None,
            json=None,
            **kwargs):
    """

    :param url:
    :param method:
    :param show:
    :param params:
    :param data:
    :param headers:
    :param cookies:
    :param timeout:
    :param verify:
    :param json:
    :param kwargs:
    :return:
    """
    show = kwargs.get("show") or show
    with Session() as session:
        return session.request(
            method=method,
            url=url,
            params=params,
            data=data,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            verify=verify,
            json=json,
            hooks=dict(response=__hook_response) if show else None,
            **kwargs)
