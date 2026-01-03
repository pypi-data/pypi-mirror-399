from builtins import str as str14, int as int19, RuntimeError as RuntimeError49
from typing import Union as Union17
from concurrent.futures import Future as Future65
from abc import ABCMeta as ABCMeta48, abstractmethod as abstractmethod51
from temper_core import std_net_send as std_net_send64
std_net_send_2597 = std_net_send64
class NetRequest:
    '*NetRequest* is a builder class for an HTTP send.\nNone of the methods except *send* actually initiate anything.'
    url_17: 'str14'
    method_18: 'str14'
    body_content_19: 'Union17[str14, None]'
    body_mime_type_20: 'Union17[str14, None]'
    __slots__ = ('url_17', 'method_18', 'body_content_19', 'body_mime_type_20')
    def post(this_0, content_22: 'str14', mime_type_23: 'str14') -> 'None':
        '*Post* switches the HTTP method to "POST" and makes sure that\na body with the given textual content and mime-type will be sent\nalong.\n\nthis__0: NetRequest\n\ncontent__22: String\n\nmimeType__23: String\n'
        this_0.method_18 = 'POST'
        this_0.body_content_19 = content_22
        t_50: 'Union17[str14, None]' = this_0.body_mime_type_20
        this_0.body_mime_type_20 = t_50
    def send(this_1) -> 'Future65[NetResponse]':
        '*Send* makes a best effort to actual send an HTTP method.\nBackends may or may not support all request features in which\ncase, send should return a broken promise.\n\nthis__1: NetRequest\n'
        return std_net_send_2597(this_1.url_17, this_1.method_18, this_1.body_content_19, this_1.body_mime_type_20)
    def __init__(this_5, url_28: 'str14') -> None:
        this_5.url_17 = url_28
        this_5.method_18 = 'GET'
        this_5.body_content_19 = None
        this_5.body_mime_type_20 = None
class NetResponse(metaclass = ABCMeta48):
    @property
    @abstractmethod51
    def status(self) -> 'int19':
        pass
    @property
    @abstractmethod51
    def content_type(self) -> 'Union17[str14, None]':
        pass
    @property
    @abstractmethod51
    def body_content(self) -> 'Future65[(Union17[str14, None])]':
        pass
def send_request_16(url_35: 'str14', method_36: 'str14', body_content_37: 'Union17[str14, None]', body_mime_type_38: 'Union17[str14, None]') -> 'Future65[NetResponse]':
    raise RuntimeError49()
