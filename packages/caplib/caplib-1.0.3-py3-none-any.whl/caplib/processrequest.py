#! /usr/bin/env python
# -*- coding: utf-8 -*-
import grpc

import caplibproto.dqlib_pb2 as dqlib_pb2
import caplibproto.dqlib_pb2_grpc as dqlib_pb2_grpc

#_HOST = 'localhost'
# _PORT = '8080'
# _HOST = '172.25.182.78'
_HOST = '139.196.104.64'
_PORT = '50051'


def process_request(service_name, pb_input_bin, host=None, port=None):
    if host is None:
        host = _HOST
    if port is None:
        port = _PORT
    else:
        port = str(port)
    conn = grpc.insecure_channel(host + ':' + port)
    client = dqlib_pb2_grpc.DqlibServiceStub(channel=conn)
    response = client.RemoteCall(dqlib_pb2.DqlibRequest(name=service_name, serialized_request=pb_input_bin))
    if response.serialized_response == None:
        raise Exception('DqlibRequest: failed!')
    return response.serialized_response
