#!/usr/bin/env python

import json
import requests

GET_IP_URL = "http://httpbin.org/ip"
SOCKS_ADDR = "127.0.0.1"
SOCKS_PORT = 9050


def req_via_proxy(url: str, addr: str, port: int) -> None:
    proxy = f"socks5://user:pass@{SOCKS_ADDR}:{SOCKS_PORT}"
    try:
        resp = requests.get(url, proxies={"http": proxy})
        content = json.loads(resp.content.decode())
        origin = content["origin"]
    except:
        raise UserWarning("proxy fetch is failing")


def socat_dns_test():
    pass


req_via_proxy(url=GET_IP_URL, addr=SOCKS_ADDR, port=SOCKS_PORT)
