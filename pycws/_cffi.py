import cffi

ffi = cffi.FFI()

ffi.cdef("""
struct handshake {
    char *resource;
    char *host;
    char *origin;
    char *protocol;
    char *key;
};

enum ws_frame_type {
    WS_ERROR_FRAME = 0,
    WS_INCOMPLETE_FRAME = 0x08,
    WS_TEXT_FRAME = 0x01,
    WS_BINARY_FRAME = 0x02,
    WS_OPENING_FRAME = 0x05,
    WS_CLOSING_FRAME = 0x06,
    WS_PING_FRAME = 0x09,
    WS_PONG_FRAME = 0x0A
};

void
    nullhandshake(struct handshake *hs);

enum ws_frame_type
    ws_parse_handshake(const uint8_t *input_frame,
                       size_t input_len,
                       struct handshake *hs);

enum ws_frame_type
    ws_get_handshake_answer(const struct handshake *hs,
                            uint8_t *out_frame,
                            size_t *out_len);

enum ws_frame_type
    ws_parse_input_frame(uint8_t *input_frame,
                         size_t input_len);

enum ws_frame_type
    ws_make_frame(uint8_t *data,
                  size_t data_len,
                  uint8_t **out_frame,
                  size_t *out_len,
                  enum ws_frame_type frame_type,
                  int options);

enum ws_frame_type
    type(uint8_t* frame);

uint8_t*
    extract_payload(uint8_t* frame, uint64_t *length);

uint8_t*
    make_header(size_t data_len,
                enum ws_frame_type frame_type,
                int *header_len,
                int options);
""")

C = ffi.verify("""
#include <cws.h>
#include <stdint.h>
""", libraries=['cws'])
