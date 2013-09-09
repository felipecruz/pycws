"""Pycws API"""

from unittest import TestCase

from pycws.base import parse_handshake, WS_OPENING_FRAME

CLIENT_HS1 = b'''GET /?encoding=text HTTP/1.1\r\n\
Host: rp:9090\r\n\
Accept-Language: en-us,en;q=0.5\r\n\
Accept-Encoding: gzip, deflate\r\n\
Connection: keep-alive, Upgrade\r\n\
Sec-WebSocket-Version: 13\r\n\
Origin: http://www.websocket.org\r\n\
Sec-WebSocket-Key: Gkh97AFkYNotSwJSdgvXEA==\r\n\
Pragma: no-cache\r\n\
Cache-Control: no-cache\r\n\
Upgrade: websocket\r\n'''

class PyCWSTest(TestCase):
    """Base CFFI backend tests"""

    def test_pycws_parse_handshake(self):
        ws_type = parse_handshake(CLIENT_HS1)

        assert WS_OPENING_FRAME == ws_type
