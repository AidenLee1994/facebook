# -*- coding:utf-8 -*-

def add_Header(option, headers):
    for key in headers.keys():
        item=key+"="+str(headers[key])
        option.add_argument(item)

    return option
