"""CFFI backend"""

from unittest import TestCase

from pycws._cffi import ffi, C

SINGLE_FRAME = bytes([0x81, 0x05, 0x48, 0x65, 0x6c, 0x6c, 0x6f])
FIRST_FRAME = bytes([0x01, 0x03, 0x48, 0x65, 0x6c])
SINGLE_FRAME_UNMASKED = bytes([0x81, 0x05, 0x48, 0x65, 0x6c, 0x6c, 0x6f])

CLIENT_HS1 = b'''GET /mychat HTTP/1.1\r\n\
Host: server.example.com\r\n\
Upgrade: websocket\r\n\
Connection: Upgrade\r\n\
Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==\r\n\
Sec-WebSocket-Protocol: chat\r\n\
Sec-WebSocket-Version: 13\r\n\
Origin: http://cws.com\r\n'''

CLIENT_HS2 = b'''GET /mychat HTTP/1.1\r\n\
Host: server.example.com\r\n\
Upgrade: wEbSoCkEt\r\n\
Connection: UpGradE\r\n\
Sec-WebSocket-Key: x3JJHMbDL1EzLkh9GBhXDw==\r\n\
Sec-WebSocket-Protocol: chat\r\n\
Sec-WebSocket-Version: 13\r\n\
Origin: http://example.com\r\n'''

CLIENT_HS3 = b'''GET /?encoding=text HTTP/1.1\r\n\
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


class PyCWSCffiTest(TestCase):
    """Base CFFI backend tests"""

    def test_pycws_cffi_nullhandshake(self):
        nullhandshake = ffi.new('struct handshake*')
        C.nullhandshake(nullhandshake)

        assert C.nullhandshake
        assert nullhandshake.resource == ffi.NULL
        assert nullhandshake.host == ffi.NULL
        assert nullhandshake.origin == ffi.NULL
        assert nullhandshake.protocol == ffi.NULL
        assert nullhandshake.key == ffi.NULL

    def test_pycws_cffi_parse_bad_handshake(self):
        nullhandshake = ffi.new('struct handshake*')
        C.nullhandshake(nullhandshake)

        requests = (b'GET', b'GET /', b'GET /index.html HTTP/1.1')

        for request_data in requests:
            request = ffi.new('const uint8_t[]', request_data)
            request_len = ffi.cast('size_t', len(request))
            ws_type = C.ws_parse_handshake(request,
                                        request_len,
                                        nullhandshake)

            assert C.WS_ERROR_FRAME == ws_type

    def test_pycws_cffi_parse_handshake(self):
        nullhandshake = ffi.new('struct handshake*')
        C.nullhandshake(nullhandshake)

        requests = (CLIENT_HS1, CLIENT_HS2, CLIENT_HS3)

        for request_data in requests:
            request = ffi.new('char[]', request_data)
            request_len = ffi.cast('size_t', len(request))
            ws_type = C.ws_parse_handshake(request,
                                           request_len,
                                           nullhandshake)

            assert C.WS_OPENING_FRAME == ws_type

    def test_pycws_cffi_parse_input_frame(self):
        frame = ffi.new('const uint8_t[]', SINGLE_FRAME)
        frame_len = ffi.cast('size_t', len(frame))
        ws_type = C.ws_parse_input_frame(frame, frame_len)
        assert C.WS_TEXT_FRAME == ws_type

        uint64 = ffi.new('uint64_t*')
        data = C.extract_payload(frame, uint64)
        data = ffi.buffer(data, uint64[0])[:]
        assert b'Hello' == data


    def test_pycws_cffi_parse_input_single_frame_masked(self):
        frame = ffi.new('const uint8_t[]', SINGLE_FRAME_UNMASKED)
        frame_len = ffi.cast('size_t', len(frame))
        ws_type = C.ws_parse_input_frame(frame, frame_len)
        assert C.WS_TEXT_FRAME == ws_type

        uint64 = ffi.new('uint64_t*')
        data = C.extract_payload(frame, uint64)
        data = ffi.buffer(data, uint64[0])[:]
        assert b'Hello' == data

    def test_pycws_cffi_parse_input_fragmented_text(self):
        FRAG1 = bytes([0x80, 0x02, 0x6c, 0x67])
        FRAG2 = bytes([0x88, 0x00])

        frame = ffi.new('const uint8_t[]', FRAG1)
        frame_len = ffi.cast('size_t', len(frame))
        ws_type = C.ws_parse_input_frame(frame, frame_len)
        assert C.WS_INCOMPLETE_FRAME == ws_type

        frame = ffi.new('const uint8_t[]', FRAG2)
        frame_len = ffi.cast('size_t', len(frame))
        ws_type = C.ws_parse_input_frame(frame, frame_len)
        assert C.WS_CLOSING_FRAME == ws_type

    def test_pycws_cffi_parse_input_single_masked(self):
        FRAME = bytes([0x81, 0x85, 0x37, 0xfa, 0x21, 0x3d, 0x7f, 0x9f, 0x4d, 0x51, 0x58])

        frame = ffi.new('const uint8_t[]', FRAME)
        frame_len = ffi.cast('size_t', len(frame))
        ws_type = C.ws_parse_input_frame(frame, frame_len)
        assert C.WS_TEXT_FRAME == ws_type

        uint64 = ffi.new('uint64_t*')
        data = C.extract_payload(frame, uint64)
        data = ffi.buffer(data, uint64[0])[:]
        assert b'Hello' == data

    def test_pycws_cffi_extract_payload(self):
        LEN_256 = bytes([0x82, 0x7e, 0x01, 0x00, 0x1, 0x1, 0x1, 0x1])


        MASKED_LEN_256 = bytes([0x82, 0xFe, 0x01, 0x00, 0x37, 0xfa, 0x21, 0x3d] + ([0x01] * 256))

        for request in (LEN_256, MASKED_LEN_256, ):
            frame = ffi.new('const uint8_t[]', request)
            frame_len = ffi.cast('size_t', len(frame))
            uint64 = ffi.new('uint64_t*')

            ws_type = C.ws_parse_input_frame(frame, frame_len)
            data = C.extract_payload(frame, uint64)
            assert C.WS_BINARY_FRAME == ws_type
            assert 256 == uint64[0]
