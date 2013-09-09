from pycws._cffi import C, ffi

WS_OPENING_FRAME = C.WS_OPENING_FRAME

def parse_handshake(request):
    nullhandshake = ffi.new('struct handshake*')
    C.nullhandshake(nullhandshake)
    request = ffi.new('const uint8_t[]', request)
    request_len = ffi.cast('size_t', len(request))
    ws_type = C.ws_parse_handshake(request, request_len, nullhandshake)
    return ws_type

def get_handshake_answer(handshake):
    out_data = ffi.new('uint8_t*')
    size_t = ffi.new('size_t*')
    C.ws_get_handshake_answer(handshake, out_data, size_t)
    return ffi.buffer(out_data, size_t)[:]
