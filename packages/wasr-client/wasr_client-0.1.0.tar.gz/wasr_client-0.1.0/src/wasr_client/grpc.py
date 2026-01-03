import time
import numpy as np
from typing import Dict, Union, Callable, Any, Tuple, Literal
from seldon_core.proto import prediction_pb2
from seldon_core.utils import array_to_grpc_datadef
from google.protobuf import json_format
from google.protobuf.json_format import MessageToDict, ParseDict
from seldon_core.proto import prediction_pb2_grpc
import grpc
from grpc_interceptor import ClientInterceptor, ClientCallDetails


class HeaderClientInterceptor(ClientInterceptor):
    def __init__(self, head_map):
        self.head_map = head_map

    def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        call_details: grpc.ClientCallDetails,
    ):
        new_details = ClientCallDetails(
            call_details.method,
            call_details.timeout,
            self.head_map,
            call_details.credentials,
            call_details.wait_for_ready,
            call_details.compression,
        )

        return method(request_or_iterator, new_details)


def construct_client_request(
    request_data: Union[np.ndarray, str, bytes, dict], tags: Dict = {}
) -> prediction_pb2.SeldonMessage:
    """构建客户端请求对象

    Args:
        request_data (Union[np.ndarray, str, bytes, dict]): 请求数据
        tags (Dict, optional):  请求参数. Defaults to {}.

    Raises:
        Exception: 未知数据类型

    Returns:
        prediction_pb2.SeldonMessage: 请求对象
    """
    # 构建参数对象
    meta = prediction_pb2.Meta()
    meta_json: Dict = {}
    if tags:
        meta_json["tags"] = tags
    json_format.ParseDict(meta_json, meta)
    # 构建请求对象
    if isinstance(request_data, np.ndarray) or isinstance(request_data, list):
        request_data = np.array(request_data)
        data = array_to_grpc_datadef("ndarray", request_data, "x")
        return prediction_pb2.SeldonMessage(data=data, meta=meta)
    elif isinstance(request_data, str):
        return prediction_pb2.SeldonMessage(strData=request_data, meta=meta)
    elif isinstance(request_data, dict):
        jsonDataResponse = ParseDict(
            request_data, prediction_pb2.SeldonMessage().jsonData
        )
        return prediction_pb2.SeldonMessage(jsonData=jsonDataResponse, meta=meta)
    elif isinstance(request_data, (bytes, bytearray)):
        return prediction_pb2.SeldonMessage(binData=request_data, meta=meta)
    else:
        raise Exception("Unknown data" + request_data)


# 创建拦截器
def create_interceptor(head_map: dict) -> HeaderClientInterceptor:
    return HeaderClientInterceptor(head_map)


def get_grpc_result(
    inputs: dict,
    task_id: str,
    business: str = "huangye",
    env: Literal["test", "ol"] = "test",
) -> Union[Dict, Tuple[Dict, float]]:
    """调用wpai test环境服务"""
    ## 构建请求对象
    request = construct_client_request(inputs)
    ## 请求的host地址
    host = f"{env}-lbg-{business}.wpai.58dns.org:8866"
    ## 设置请求的任务taskid
    task_id = str(task_id)
    head_map = [("taskid", task_id)]
    interceptor = create_interceptor(head_map)
    with grpc.insecure_channel(host) as channel:
        intercept_channel = grpc.intercept_channel(channel, interceptor)
        stub = prediction_pb2_grpc.ModelStub(intercept_channel)
        ## 发送请求，此处超时时间timeout的单位为秒(s)
        response = stub.Predict(request, timeout=1000)
        result = MessageToDict(response)
    return eval(result["strData"])
