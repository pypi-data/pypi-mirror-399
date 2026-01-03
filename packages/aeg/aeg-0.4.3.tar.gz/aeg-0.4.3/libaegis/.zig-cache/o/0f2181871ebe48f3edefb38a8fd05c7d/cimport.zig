pub const __builtin = @import("std").zig.c_translation.builtins;
pub const __helpers = @import("std").zig.c_translation.helpers;

pub const __u_char = u8;
pub const __u_short = c_ushort;
pub const __u_int = c_uint;
pub const __u_long = c_ulong;
pub const __int8_t = i8;
pub const __uint8_t = u8;
pub const __int16_t = c_short;
pub const __uint16_t = c_ushort;
pub const __int32_t = c_int;
pub const __uint32_t = c_uint;
pub const __int64_t = c_long;
pub const __uint64_t = c_ulong;
pub const __int_least8_t = __int8_t;
pub const __uint_least8_t = __uint8_t;
pub const __int_least16_t = __int16_t;
pub const __uint_least16_t = __uint16_t;
pub const __int_least32_t = __int32_t;
pub const __uint_least32_t = __uint32_t;
pub const __int_least64_t = __int64_t;
pub const __uint_least64_t = __uint64_t;
pub const __quad_t = c_long;
pub const __u_quad_t = c_ulong;
pub const __intmax_t = c_long;
pub const __uintmax_t = c_ulong;
pub const __dev_t = c_ulong;
pub const __uid_t = c_uint;
pub const __gid_t = c_uint;
pub const __ino_t = c_ulong;
pub const __ino64_t = c_ulong;
pub const __mode_t = c_uint;
pub const __nlink_t = c_ulong;
pub const __off_t = c_long;
pub const __off64_t = c_long;
pub const __pid_t = c_int;
pub const __fsid_t = extern struct {
    __val: [2]c_int = @import("std").mem.zeroes([2]c_int),
};
pub const __clock_t = c_long;
pub const __rlim_t = c_ulong;
pub const __rlim64_t = c_ulong;
pub const __id_t = c_uint;
pub const __time_t = c_long;
pub const __useconds_t = c_uint;
pub const __suseconds_t = c_long;
pub const __suseconds64_t = c_long;
pub const __daddr_t = c_int;
pub const __key_t = c_int;
pub const __clockid_t = c_int;
pub const __timer_t = ?*anyopaque;
pub const __blksize_t = c_long;
pub const __blkcnt_t = c_long;
pub const __blkcnt64_t = c_long;
pub const __fsblkcnt_t = c_ulong;
pub const __fsblkcnt64_t = c_ulong;
pub const __fsfilcnt_t = c_ulong;
pub const __fsfilcnt64_t = c_ulong;
pub const __fsword_t = c_long;
pub const __ssize_t = c_long;
pub const __syscall_slong_t = c_long;
pub const __syscall_ulong_t = c_ulong;
pub const __loff_t = __off64_t;
pub const __caddr_t = [*c]u8;
pub const __intptr_t = c_long;
pub const __socklen_t = c_uint;
pub const __sig_atomic_t = c_int;
pub const int_least8_t = __int_least8_t;
pub const int_least16_t = __int_least16_t;
pub const int_least32_t = __int_least32_t;
pub const int_least64_t = __int_least64_t;
pub const uint_least8_t = __uint_least8_t;
pub const uint_least16_t = __uint_least16_t;
pub const uint_least32_t = __uint_least32_t;
pub const uint_least64_t = __uint_least64_t;
pub const int_fast8_t = i8;
pub const int_fast16_t = c_long;
pub const int_fast32_t = c_long;
pub const int_fast64_t = c_long;
pub const uint_fast8_t = u8;
pub const uint_fast16_t = c_ulong;
pub const uint_fast32_t = c_ulong;
pub const uint_fast64_t = c_ulong;
pub const intmax_t = __intmax_t;
pub const uintmax_t = __uintmax_t;
pub const ptrdiff_t = c_long;
pub const wchar_t = c_int;
pub const max_align_t = extern struct {
    __aro_max_align_ll: c_longlong = 0,
    __aro_max_align_ld: c_longdouble = 0,
};
pub const struct_aegis128l_state = extern struct {
    @"opaque": [256]u8 align(32) = @import("std").mem.zeroes([256]u8),
    pub const init = aegis128l_state_init;
    pub const update = aegis128l_state_encrypt_update;
    pub const final = aegis128l_state_encrypt_detached_final;
    pub const final1 = aegis128l_state_encrypt_final;
    pub const update1 = aegis128l_state_decrypt_detached_update;
    pub const final2 = aegis128l_state_decrypt_detached_final;
};
pub const aegis128l_state = struct_aegis128l_state;
pub const struct_aegis128l_mac_state = extern struct {
    @"opaque": [384]u8 align(32) = @import("std").mem.zeroes([384]u8),
    pub const init = aegis128l_mac_init;
    pub const update = aegis128l_mac_update;
    pub const final = aegis128l_mac_final;
    pub const verify = aegis128l_mac_verify;
    pub const reset = aegis128l_mac_reset;
    pub const clone = aegis128l_mac_state_clone;
};
pub const aegis128l_mac_state = struct_aegis128l_mac_state;
pub extern fn aegis128l_keybytes() usize;
pub extern fn aegis128l_npubbytes() usize;
pub extern fn aegis128l_abytes_min() usize;
pub extern fn aegis128l_abytes_max() usize;
pub extern fn aegis128l_tailbytes_max() usize;
pub extern fn aegis128l_encrypt_detached(c: [*c]u8, mac: [*c]u8, maclen: usize, m: [*c]const u8, mlen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis128l_decrypt_detached(m: [*c]u8, c: [*c]const u8, clen: usize, mac: [*c]const u8, maclen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis128l_encrypt(c: [*c]u8, maclen: usize, m: [*c]const u8, mlen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis128l_decrypt(m: [*c]u8, c: [*c]const u8, clen: usize, maclen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis128l_state_init(st_: [*c]aegis128l_state, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis128l_state_encrypt_update(st_: [*c]aegis128l_state, c: [*c]u8, clen_max: usize, written: [*c]usize, m: [*c]const u8, mlen: usize) c_int;
pub extern fn aegis128l_state_encrypt_detached_final(st_: [*c]aegis128l_state, c: [*c]u8, clen_max: usize, written: [*c]usize, mac: [*c]u8, maclen: usize) c_int;
pub extern fn aegis128l_state_encrypt_final(st_: [*c]aegis128l_state, c: [*c]u8, clen_max: usize, written: [*c]usize, maclen: usize) c_int;
pub extern fn aegis128l_state_decrypt_detached_update(st_: [*c]aegis128l_state, m: [*c]u8, mlen_max: usize, written: [*c]usize, c: [*c]const u8, clen: usize) c_int;
pub extern fn aegis128l_state_decrypt_detached_final(st_: [*c]aegis128l_state, m: [*c]u8, mlen_max: usize, written: [*c]usize, mac: [*c]const u8, maclen: usize) c_int;
pub extern fn aegis128l_stream(out: [*c]u8, len: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis128l_encrypt_unauthenticated(c: [*c]u8, m: [*c]const u8, mlen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis128l_decrypt_unauthenticated(m: [*c]u8, c: [*c]const u8, clen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis128l_mac_init(st_: [*c]aegis128l_mac_state, k: [*c]const u8, npub: [*c]const u8) void;
pub extern fn aegis128l_mac_update(st_: [*c]aegis128l_mac_state, m: [*c]const u8, mlen: usize) c_int;
pub extern fn aegis128l_mac_final(st_: [*c]aegis128l_mac_state, mac: [*c]u8, maclen: usize) c_int;
pub extern fn aegis128l_mac_verify(st_: [*c]aegis128l_mac_state, mac: [*c]const u8, maclen: usize) c_int;
pub extern fn aegis128l_mac_reset(st_: [*c]aegis128l_mac_state) void;
pub extern fn aegis128l_mac_state_clone(dst: [*c]aegis128l_mac_state, src: [*c]const aegis128l_mac_state) void;
pub const struct_aegis128x2_state = extern struct {
    @"opaque": [448]u8 align(64) = @import("std").mem.zeroes([448]u8),
    pub const init = aegis128x2_state_init;
    pub const update = aegis128x2_state_encrypt_update;
    pub const final = aegis128x2_state_encrypt_detached_final;
    pub const final1 = aegis128x2_state_encrypt_final;
    pub const update1 = aegis128x2_state_decrypt_detached_update;
    pub const final2 = aegis128x2_state_decrypt_detached_final;
};
pub const aegis128x2_state = struct_aegis128x2_state;
pub const struct_aegis128x2_mac_state = extern struct {
    @"opaque": [704]u8 align(64) = @import("std").mem.zeroes([704]u8),
    pub const init = aegis128x2_mac_init;
    pub const update = aegis128x2_mac_update;
    pub const final = aegis128x2_mac_final;
    pub const verify = aegis128x2_mac_verify;
    pub const reset = aegis128x2_mac_reset;
    pub const clone = aegis128x2_mac_state_clone;
};
pub const aegis128x2_mac_state = struct_aegis128x2_mac_state;
pub extern fn aegis128x2_keybytes() usize;
pub extern fn aegis128x2_npubbytes() usize;
pub extern fn aegis128x2_abytes_min() usize;
pub extern fn aegis128x2_abytes_max() usize;
pub extern fn aegis128x2_tailbytes_max() usize;
pub extern fn aegis128x2_encrypt_detached(c: [*c]u8, mac: [*c]u8, maclen: usize, m: [*c]const u8, mlen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis128x2_decrypt_detached(m: [*c]u8, c: [*c]const u8, clen: usize, mac: [*c]const u8, maclen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis128x2_encrypt(c: [*c]u8, maclen: usize, m: [*c]const u8, mlen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis128x2_decrypt(m: [*c]u8, c: [*c]const u8, clen: usize, maclen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis128x2_state_init(st_: [*c]aegis128x2_state, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis128x2_state_encrypt_update(st_: [*c]aegis128x2_state, c: [*c]u8, clen_max: usize, written: [*c]usize, m: [*c]const u8, mlen: usize) c_int;
pub extern fn aegis128x2_state_encrypt_detached_final(st_: [*c]aegis128x2_state, c: [*c]u8, clen_max: usize, written: [*c]usize, mac: [*c]u8, maclen: usize) c_int;
pub extern fn aegis128x2_state_encrypt_final(st_: [*c]aegis128x2_state, c: [*c]u8, clen_max: usize, written: [*c]usize, maclen: usize) c_int;
pub extern fn aegis128x2_state_decrypt_detached_update(st_: [*c]aegis128x2_state, m: [*c]u8, mlen_max: usize, written: [*c]usize, c: [*c]const u8, clen: usize) c_int;
pub extern fn aegis128x2_state_decrypt_detached_final(st_: [*c]aegis128x2_state, m: [*c]u8, mlen_max: usize, written: [*c]usize, mac: [*c]const u8, maclen: usize) c_int;
pub extern fn aegis128x2_stream(out: [*c]u8, len: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis128x2_encrypt_unauthenticated(c: [*c]u8, m: [*c]const u8, mlen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis128x2_decrypt_unauthenticated(m: [*c]u8, c: [*c]const u8, clen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis128x2_mac_init(st_: [*c]aegis128x2_mac_state, k: [*c]const u8, npub: [*c]const u8) void;
pub extern fn aegis128x2_mac_update(st_: [*c]aegis128x2_mac_state, m: [*c]const u8, mlen: usize) c_int;
pub extern fn aegis128x2_mac_final(st_: [*c]aegis128x2_mac_state, mac: [*c]u8, maclen: usize) c_int;
pub extern fn aegis128x2_mac_verify(st_: [*c]aegis128x2_mac_state, mac: [*c]const u8, maclen: usize) c_int;
pub extern fn aegis128x2_mac_reset(st_: [*c]aegis128x2_mac_state) void;
pub extern fn aegis128x2_mac_state_clone(dst: [*c]aegis128x2_mac_state, src: [*c]const aegis128x2_mac_state) void;
pub const struct_aegis128x4_state = extern struct {
    @"opaque": [832]u8 align(64) = @import("std").mem.zeroes([832]u8),
    pub const init = aegis128x4_state_init;
    pub const update = aegis128x4_state_encrypt_update;
    pub const final = aegis128x4_state_encrypt_detached_final;
    pub const final1 = aegis128x4_state_encrypt_final;
    pub const update1 = aegis128x4_state_decrypt_detached_update;
    pub const final2 = aegis128x4_state_decrypt_detached_final;
};
pub const aegis128x4_state = struct_aegis128x4_state;
pub const struct_aegis128x4_mac_state = extern struct {
    @"opaque": [1344]u8 align(64) = @import("std").mem.zeroes([1344]u8),
    pub const init = aegis128x4_mac_init;
    pub const update = aegis128x4_mac_update;
    pub const final = aegis128x4_mac_final;
    pub const verify = aegis128x4_mac_verify;
    pub const reset = aegis128x4_mac_reset;
    pub const clone = aegis128x4_mac_state_clone;
};
pub const aegis128x4_mac_state = struct_aegis128x4_mac_state;
pub extern fn aegis128x4_keybytes() usize;
pub extern fn aegis128x4_npubbytes() usize;
pub extern fn aegis128x4_abytes_min() usize;
pub extern fn aegis128x4_abytes_max() usize;
pub extern fn aegis128x4_tailbytes_max() usize;
pub extern fn aegis128x4_encrypt_detached(c: [*c]u8, mac: [*c]u8, maclen: usize, m: [*c]const u8, mlen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis128x4_decrypt_detached(m: [*c]u8, c: [*c]const u8, clen: usize, mac: [*c]const u8, maclen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis128x4_encrypt(c: [*c]u8, maclen: usize, m: [*c]const u8, mlen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis128x4_decrypt(m: [*c]u8, c: [*c]const u8, clen: usize, maclen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis128x4_state_init(st_: [*c]aegis128x4_state, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis128x4_state_encrypt_update(st_: [*c]aegis128x4_state, c: [*c]u8, clen_max: usize, written: [*c]usize, m: [*c]const u8, mlen: usize) c_int;
pub extern fn aegis128x4_state_encrypt_detached_final(st_: [*c]aegis128x4_state, c: [*c]u8, clen_max: usize, written: [*c]usize, mac: [*c]u8, maclen: usize) c_int;
pub extern fn aegis128x4_state_encrypt_final(st_: [*c]aegis128x4_state, c: [*c]u8, clen_max: usize, written: [*c]usize, maclen: usize) c_int;
pub extern fn aegis128x4_state_decrypt_detached_update(st_: [*c]aegis128x4_state, m: [*c]u8, mlen_max: usize, written: [*c]usize, c: [*c]const u8, clen: usize) c_int;
pub extern fn aegis128x4_state_decrypt_detached_final(st_: [*c]aegis128x4_state, m: [*c]u8, mlen_max: usize, written: [*c]usize, mac: [*c]const u8, maclen: usize) c_int;
pub extern fn aegis128x4_stream(out: [*c]u8, len: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis128x4_encrypt_unauthenticated(c: [*c]u8, m: [*c]const u8, mlen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis128x4_decrypt_unauthenticated(m: [*c]u8, c: [*c]const u8, clen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis128x4_mac_init(st_: [*c]aegis128x4_mac_state, k: [*c]const u8, npub: [*c]const u8) void;
pub extern fn aegis128x4_mac_update(st_: [*c]aegis128x4_mac_state, m: [*c]const u8, mlen: usize) c_int;
pub extern fn aegis128x4_mac_final(st_: [*c]aegis128x4_mac_state, mac: [*c]u8, maclen: usize) c_int;
pub extern fn aegis128x4_mac_verify(st_: [*c]aegis128x4_mac_state, mac: [*c]const u8, maclen: usize) c_int;
pub extern fn aegis128x4_mac_reset(st_: [*c]aegis128x4_mac_state) void;
pub extern fn aegis128x4_mac_state_clone(dst: [*c]aegis128x4_mac_state, src: [*c]const aegis128x4_mac_state) void;
pub const struct_aegis256_state = extern struct {
    @"opaque": [192]u8 align(16) = @import("std").mem.zeroes([192]u8),
    pub const init = aegis256_state_init;
    pub const update = aegis256_state_encrypt_update;
    pub const final = aegis256_state_encrypt_detached_final;
    pub const final1 = aegis256_state_encrypt_final;
    pub const update1 = aegis256_state_decrypt_detached_update;
    pub const final2 = aegis256_state_decrypt_detached_final;
};
pub const aegis256_state = struct_aegis256_state;
pub const struct_aegis256_mac_state = extern struct {
    @"opaque": [288]u8 align(16) = @import("std").mem.zeroes([288]u8),
    pub const init = aegis256_mac_init;
    pub const update = aegis256_mac_update;
    pub const final = aegis256_mac_final;
    pub const verify = aegis256_mac_verify;
    pub const reset = aegis256_mac_reset;
    pub const clone = aegis256_mac_state_clone;
};
pub const aegis256_mac_state = struct_aegis256_mac_state;
pub extern fn aegis256_keybytes() usize;
pub extern fn aegis256_npubbytes() usize;
pub extern fn aegis256_abytes_min() usize;
pub extern fn aegis256_abytes_max() usize;
pub extern fn aegis256_tailbytes_max() usize;
pub extern fn aegis256_encrypt_detached(c: [*c]u8, mac: [*c]u8, maclen: usize, m: [*c]const u8, mlen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis256_decrypt_detached(m: [*c]u8, c: [*c]const u8, clen: usize, mac: [*c]const u8, maclen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis256_encrypt(c: [*c]u8, maclen: usize, m: [*c]const u8, mlen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis256_decrypt(m: [*c]u8, c: [*c]const u8, clen: usize, maclen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis256_state_init(st_: [*c]aegis256_state, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis256_state_encrypt_update(st_: [*c]aegis256_state, c: [*c]u8, clen_max: usize, written: [*c]usize, m: [*c]const u8, mlen: usize) c_int;
pub extern fn aegis256_state_encrypt_detached_final(st_: [*c]aegis256_state, c: [*c]u8, clen_max: usize, written: [*c]usize, mac: [*c]u8, maclen: usize) c_int;
pub extern fn aegis256_state_encrypt_final(st_: [*c]aegis256_state, c: [*c]u8, clen_max: usize, written: [*c]usize, maclen: usize) c_int;
pub extern fn aegis256_state_decrypt_detached_update(st_: [*c]aegis256_state, m: [*c]u8, mlen_max: usize, written: [*c]usize, c: [*c]const u8, clen: usize) c_int;
pub extern fn aegis256_state_decrypt_detached_final(st_: [*c]aegis256_state, m: [*c]u8, mlen_max: usize, written: [*c]usize, mac: [*c]const u8, maclen: usize) c_int;
pub extern fn aegis256_stream(out: [*c]u8, len: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis256_encrypt_unauthenticated(c: [*c]u8, m: [*c]const u8, mlen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis256_decrypt_unauthenticated(m: [*c]u8, c: [*c]const u8, clen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis256_mac_init(st_: [*c]aegis256_mac_state, k: [*c]const u8, npub: [*c]const u8) void;
pub extern fn aegis256_mac_update(st_: [*c]aegis256_mac_state, m: [*c]const u8, mlen: usize) c_int;
pub extern fn aegis256_mac_final(st_: [*c]aegis256_mac_state, mac: [*c]u8, maclen: usize) c_int;
pub extern fn aegis256_mac_verify(st_: [*c]aegis256_mac_state, mac: [*c]const u8, maclen: usize) c_int;
pub extern fn aegis256_mac_reset(st_: [*c]aegis256_mac_state) void;
pub extern fn aegis256_mac_state_clone(dst: [*c]aegis256_mac_state, src: [*c]const aegis256_mac_state) void;
pub const struct_aegis256x2_state = extern struct {
    @"opaque": [320]u8 align(32) = @import("std").mem.zeroes([320]u8),
    pub const init = aegis256x2_state_init;
    pub const update = aegis256x2_state_encrypt_update;
    pub const final = aegis256x2_state_encrypt_detached_final;
    pub const final1 = aegis256x2_state_encrypt_final;
    pub const update1 = aegis256x2_state_decrypt_detached_update;
    pub const final2 = aegis256x2_state_decrypt_detached_final;
};
pub const aegis256x2_state = struct_aegis256x2_state;
pub const struct_aegis256x2_mac_state = extern struct {
    @"opaque": [512]u8 align(32) = @import("std").mem.zeroes([512]u8),
    pub const init = aegis256x2_mac_init;
    pub const update = aegis256x2_mac_update;
    pub const final = aegis256x2_mac_final;
    pub const verify = aegis256x2_mac_verify;
    pub const reset = aegis256x2_mac_reset;
    pub const clone = aegis256x2_mac_state_clone;
};
pub const aegis256x2_mac_state = struct_aegis256x2_mac_state;
pub extern fn aegis256x2_keybytes() usize;
pub extern fn aegis256x2_npubbytes() usize;
pub extern fn aegis256x2_abytes_min() usize;
pub extern fn aegis256x2_abytes_max() usize;
pub extern fn aegis256x2_tailbytes_max() usize;
pub extern fn aegis256x2_encrypt_detached(c: [*c]u8, mac: [*c]u8, maclen: usize, m: [*c]const u8, mlen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis256x2_decrypt_detached(m: [*c]u8, c: [*c]const u8, clen: usize, mac: [*c]const u8, maclen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis256x2_encrypt(c: [*c]u8, maclen: usize, m: [*c]const u8, mlen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis256x2_decrypt(m: [*c]u8, c: [*c]const u8, clen: usize, maclen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis256x2_state_init(st_: [*c]aegis256x2_state, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis256x2_state_encrypt_update(st_: [*c]aegis256x2_state, c: [*c]u8, clen_max: usize, written: [*c]usize, m: [*c]const u8, mlen: usize) c_int;
pub extern fn aegis256x2_state_encrypt_detached_final(st_: [*c]aegis256x2_state, c: [*c]u8, clen_max: usize, written: [*c]usize, mac: [*c]u8, maclen: usize) c_int;
pub extern fn aegis256x2_state_encrypt_final(st_: [*c]aegis256x2_state, c: [*c]u8, clen_max: usize, written: [*c]usize, maclen: usize) c_int;
pub extern fn aegis256x2_state_decrypt_detached_update(st_: [*c]aegis256x2_state, m: [*c]u8, mlen_max: usize, written: [*c]usize, c: [*c]const u8, clen: usize) c_int;
pub extern fn aegis256x2_state_decrypt_detached_final(st_: [*c]aegis256x2_state, m: [*c]u8, mlen_max: usize, written: [*c]usize, mac: [*c]const u8, maclen: usize) c_int;
pub extern fn aegis256x2_stream(out: [*c]u8, len: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis256x2_encrypt_unauthenticated(c: [*c]u8, m: [*c]const u8, mlen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis256x2_decrypt_unauthenticated(m: [*c]u8, c: [*c]const u8, clen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis256x2_mac_init(st_: [*c]aegis256x2_mac_state, k: [*c]const u8, npub: [*c]const u8) void;
pub extern fn aegis256x2_mac_update(st_: [*c]aegis256x2_mac_state, m: [*c]const u8, mlen: usize) c_int;
pub extern fn aegis256x2_mac_final(st_: [*c]aegis256x2_mac_state, mac: [*c]u8, maclen: usize) c_int;
pub extern fn aegis256x2_mac_verify(st_: [*c]aegis256x2_mac_state, mac: [*c]const u8, maclen: usize) c_int;
pub extern fn aegis256x2_mac_reset(st_: [*c]aegis256x2_mac_state) void;
pub extern fn aegis256x2_mac_state_clone(dst: [*c]aegis256x2_mac_state, src: [*c]const aegis256x2_mac_state) void;
pub const struct_aegis256x4_state = extern struct {
    @"opaque": [576]u8 align(64) = @import("std").mem.zeroes([576]u8),
    pub const init = aegis256x4_state_init;
    pub const update = aegis256x4_state_encrypt_update;
    pub const final = aegis256x4_state_encrypt_detached_final;
    pub const final1 = aegis256x4_state_encrypt_final;
    pub const update1 = aegis256x4_state_decrypt_detached_update;
    pub const final2 = aegis256x4_state_decrypt_detached_final;
};
pub const aegis256x4_state = struct_aegis256x4_state;
pub const struct_aegis256x4_mac_state = extern struct {
    @"opaque": [960]u8 align(64) = @import("std").mem.zeroes([960]u8),
    pub const init = aegis256x4_mac_init;
    pub const update = aegis256x4_mac_update;
    pub const final = aegis256x4_mac_final;
    pub const verify = aegis256x4_mac_verify;
    pub const reset = aegis256x4_mac_reset;
    pub const clone = aegis256x4_mac_state_clone;
};
pub const aegis256x4_mac_state = struct_aegis256x4_mac_state;
pub extern fn aegis256x4_keybytes() usize;
pub extern fn aegis256x4_npubbytes() usize;
pub extern fn aegis256x4_abytes_min() usize;
pub extern fn aegis256x4_abytes_max() usize;
pub extern fn aegis256x4_tailbytes_max() usize;
pub extern fn aegis256x4_encrypt_detached(c: [*c]u8, mac: [*c]u8, maclen: usize, m: [*c]const u8, mlen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis256x4_decrypt_detached(m: [*c]u8, c: [*c]const u8, clen: usize, mac: [*c]const u8, maclen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis256x4_encrypt(c: [*c]u8, maclen: usize, m: [*c]const u8, mlen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis256x4_decrypt(m: [*c]u8, c: [*c]const u8, clen: usize, maclen: usize, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) c_int;
pub extern fn aegis256x4_state_init(st_: [*c]aegis256x4_state, ad: [*c]const u8, adlen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis256x4_state_encrypt_update(st_: [*c]aegis256x4_state, c: [*c]u8, clen_max: usize, written: [*c]usize, m: [*c]const u8, mlen: usize) c_int;
pub extern fn aegis256x4_state_encrypt_detached_final(st_: [*c]aegis256x4_state, c: [*c]u8, clen_max: usize, written: [*c]usize, mac: [*c]u8, maclen: usize) c_int;
pub extern fn aegis256x4_state_encrypt_final(st_: [*c]aegis256x4_state, c: [*c]u8, clen_max: usize, written: [*c]usize, maclen: usize) c_int;
pub extern fn aegis256x4_state_decrypt_detached_update(st_: [*c]aegis256x4_state, m: [*c]u8, mlen_max: usize, written: [*c]usize, c: [*c]const u8, clen: usize) c_int;
pub extern fn aegis256x4_state_decrypt_detached_final(st_: [*c]aegis256x4_state, m: [*c]u8, mlen_max: usize, written: [*c]usize, mac: [*c]const u8, maclen: usize) c_int;
pub extern fn aegis256x4_stream(out: [*c]u8, len: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis256x4_encrypt_unauthenticated(c: [*c]u8, m: [*c]const u8, mlen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis256x4_decrypt_unauthenticated(m: [*c]u8, c: [*c]const u8, clen: usize, npub: [*c]const u8, k: [*c]const u8) void;
pub extern fn aegis256x4_mac_init(st_: [*c]aegis256x4_mac_state, k: [*c]const u8, npub: [*c]const u8) void;
pub extern fn aegis256x4_mac_update(st_: [*c]aegis256x4_mac_state, m: [*c]const u8, mlen: usize) c_int;
pub extern fn aegis256x4_mac_final(st_: [*c]aegis256x4_mac_state, mac: [*c]u8, maclen: usize) c_int;
pub extern fn aegis256x4_mac_verify(st_: [*c]aegis256x4_mac_state, mac: [*c]const u8, maclen: usize) c_int;
pub extern fn aegis256x4_mac_reset(st_: [*c]aegis256x4_mac_state) void;
pub extern fn aegis256x4_mac_state_clone(dst: [*c]aegis256x4_mac_state, src: [*c]const aegis256x4_mac_state) void;
pub extern fn aegis_init() c_int;
pub extern fn aegis_verify_16(x: [*c]const u8, y: [*c]const u8) c_int;
pub extern fn aegis_verify_32(x: [*c]const u8, y: [*c]const u8) c_int;

pub const __VERSION__ = "Aro aro-zig";
pub const __Aro__ = "";
pub const __STDC__ = @as(c_int, 1);
pub const __STDC_HOSTED__ = @as(c_int, 1);
pub const __STDC_UTF_16__ = @as(c_int, 1);
pub const __STDC_UTF_32__ = @as(c_int, 1);
pub const __STDC_EMBED_NOT_FOUND__ = @as(c_int, 0);
pub const __STDC_EMBED_FOUND__ = @as(c_int, 1);
pub const __STDC_EMBED_EMPTY__ = @as(c_int, 2);
pub const __STDC_VERSION__ = @as(c_long, 201710);
pub const __GNUC__ = @as(c_int, 7);
pub const __GNUC_MINOR__ = @as(c_int, 1);
pub const __GNUC_PATCHLEVEL__ = @as(c_int, 0);
pub const __ARO_EMULATE_CLANG__ = @as(c_int, 1);
pub const __ARO_EMULATE_GCC__ = @as(c_int, 2);
pub const __ARO_EMULATE_MSVC__ = @as(c_int, 3);
pub const __ARO_EMULATE__ = __ARO_EMULATE_GCC__;
pub const __OPTIMIZE__ = @as(c_int, 1);
pub const linux = @as(c_int, 1);
pub const __linux = @as(c_int, 1);
pub const __linux__ = @as(c_int, 1);
pub const unix = @as(c_int, 1);
pub const __unix = @as(c_int, 1);
pub const __unix__ = @as(c_int, 1);
pub const __code_model_small__ = @as(c_int, 1);
pub const __amd64__ = @as(c_int, 1);
pub const __amd64 = @as(c_int, 1);
pub const __x86_64__ = @as(c_int, 1);
pub const __x86_64 = @as(c_int, 1);
pub const __SEG_GS = @as(c_int, 1);
pub const __SEG_FS = @as(c_int, 1);
pub const __seg_gs = @compileError("unable to translate macro: undefined identifier `address_space`"); // <builtin>:32:9
pub const __seg_fs = @compileError("unable to translate macro: undefined identifier `address_space`"); // <builtin>:33:9
pub const __LAHF_SAHF__ = @as(c_int, 1);
pub const __AES__ = @as(c_int, 1);
pub const __VAES__ = @as(c_int, 1);
pub const __PCLMUL__ = @as(c_int, 1);
pub const __VPCLMULQDQ__ = @as(c_int, 1);
pub const __LZCNT__ = @as(c_int, 1);
pub const __RDRND__ = @as(c_int, 1);
pub const __FSGSBASE__ = @as(c_int, 1);
pub const __BMI__ = @as(c_int, 1);
pub const __BMI2__ = @as(c_int, 1);
pub const __POPCNT__ = @as(c_int, 1);
pub const __PRFCHW__ = @as(c_int, 1);
pub const __RDSEED__ = @as(c_int, 1);
pub const __ADX__ = @as(c_int, 1);
pub const __MOVBE__ = @as(c_int, 1);
pub const __FMA__ = @as(c_int, 1);
pub const __F16C__ = @as(c_int, 1);
pub const __GFNI__ = @as(c_int, 1);
pub const __SHA__ = @as(c_int, 1);
pub const __FXSR__ = @as(c_int, 1);
pub const __XSAVE__ = @as(c_int, 1);
pub const __XSAVEOPT__ = @as(c_int, 1);
pub const __XSAVEC__ = @as(c_int, 1);
pub const __XSAVES__ = @as(c_int, 1);
pub const __CLFLUSHOPT__ = @as(c_int, 1);
pub const __CLWB__ = @as(c_int, 1);
pub const __SHSTK__ = @as(c_int, 1);
pub const __RDPID__ = @as(c_int, 1);
pub const __WAITPKG__ = @as(c_int, 1);
pub const __MOVDIRI__ = @as(c_int, 1);
pub const __MOVDIR64B__ = @as(c_int, 1);
pub const __INVPCID__ = @as(c_int, 1);
pub const __AVXVNNI__ = @as(c_int, 1);
pub const __SERIALIZE__ = @as(c_int, 1);
pub const __CRC32__ = @as(c_int, 1);
pub const __AVX2__ = @as(c_int, 1);
pub const __AVX__ = @as(c_int, 1);
pub const __SSE4_2__ = @as(c_int, 1);
pub const __SSE4_1__ = @as(c_int, 1);
pub const __SSSE3__ = @as(c_int, 1);
pub const __SSE3__ = @as(c_int, 1);
pub const __SSE2__ = @as(c_int, 1);
pub const __SSE__ = @as(c_int, 1);
pub const __SSE_MATH__ = @as(c_int, 1);
pub const __MMX__ = @as(c_int, 1);
pub const __GCC_HAVE_SYNC_COMPARE_AND_SWAP_8 = @as(c_int, 1);
pub const __SIZEOF_FLOAT128__ = @as(c_int, 16);
pub const __FLOAT128__ = @as(c_int, 1);
pub const __ORDER_LITTLE_ENDIAN__ = @as(c_int, 1234);
pub const __ORDER_BIG_ENDIAN__ = @as(c_int, 4321);
pub const __ORDER_PDP_ENDIAN__ = @as(c_int, 3412);
pub const __BYTE_ORDER__ = __ORDER_LITTLE_ENDIAN__;
pub const __LITTLE_ENDIAN__ = @as(c_int, 1);
pub const __ELF__ = @as(c_int, 1);
pub const __ATOMIC_RELAXED = @as(c_int, 0);
pub const __ATOMIC_CONSUME = @as(c_int, 1);
pub const __ATOMIC_ACQUIRE = @as(c_int, 2);
pub const __ATOMIC_RELEASE = @as(c_int, 3);
pub const __ATOMIC_ACQ_REL = @as(c_int, 4);
pub const __ATOMIC_SEQ_CST = @as(c_int, 5);
pub const __ATOMIC_BOOL_LOCK_FREE = @as(c_int, 1);
pub const __ATOMIC_CHAR_LOCK_FREE = @as(c_int, 1);
pub const __ATOMIC_CHAR16_T_LOCK_FREE = @as(c_int, 1);
pub const __ATOMIC_CHAR32_T_LOCK_FREE = @as(c_int, 1);
pub const __ATOMIC_WCHAR_T_LOCK_FREE = @as(c_int, 1);
pub const __ATOMIC_SHORT_LOCK_FREE = @as(c_int, 1);
pub const __ATOMIC_INT_LOCK_FREE = @as(c_int, 1);
pub const __ATOMIC_LONG_LOCK_FREE = @as(c_int, 1);
pub const __ATOMIC_LLONG_LOCK_FREE = @as(c_int, 1);
pub const __ATOMIC_POINTER_LOCK_FREE = @as(c_int, 1);
pub const __CHAR_BIT__ = @as(c_int, 8);
pub const __BOOL_WIDTH__ = @as(c_int, 8);
pub const __SCHAR_MAX__ = @as(c_int, 127);
pub const __SCHAR_WIDTH__ = @as(c_int, 8);
pub const __SHRT_MAX__ = @as(c_int, 32767);
pub const __SHRT_WIDTH__ = @as(c_int, 16);
pub const __INT_MAX__ = __helpers.promoteIntLiteral(c_int, 2147483647, .decimal);
pub const __INT_WIDTH__ = @as(c_int, 32);
pub const __LONG_MAX__ = __helpers.promoteIntLiteral(c_long, 9223372036854775807, .decimal);
pub const __LONG_WIDTH__ = @as(c_int, 64);
pub const __LONG_LONG_MAX__ = @as(c_longlong, 9223372036854775807);
pub const __LONG_LONG_WIDTH__ = @as(c_int, 64);
pub const __WCHAR_MAX__ = __helpers.promoteIntLiteral(c_int, 2147483647, .decimal);
pub const __WCHAR_WIDTH__ = @as(c_int, 32);
pub const __INTMAX_MAX__ = __helpers.promoteIntLiteral(c_long, 9223372036854775807, .decimal);
pub const __INTMAX_WIDTH__ = @as(c_int, 64);
pub const __SIZE_MAX__ = __helpers.promoteIntLiteral(c_ulong, 18446744073709551615, .decimal);
pub const __SIZE_WIDTH__ = @as(c_int, 64);
pub const __UINTMAX_MAX__ = __helpers.promoteIntLiteral(c_ulong, 18446744073709551615, .decimal);
pub const __UINTMAX_WIDTH__ = @as(c_int, 64);
pub const __PTRDIFF_MAX__ = __helpers.promoteIntLiteral(c_long, 9223372036854775807, .decimal);
pub const __PTRDIFF_WIDTH__ = @as(c_int, 64);
pub const __INTPTR_MAX__ = __helpers.promoteIntLiteral(c_long, 9223372036854775807, .decimal);
pub const __INTPTR_WIDTH__ = @as(c_int, 64);
pub const __UINTPTR_MAX__ = __helpers.promoteIntLiteral(c_ulong, 18446744073709551615, .decimal);
pub const __UINTPTR_WIDTH__ = @as(c_int, 64);
pub const __SIG_ATOMIC_MAX__ = __helpers.promoteIntLiteral(c_int, 2147483647, .decimal);
pub const __SIG_ATOMIC_WIDTH__ = @as(c_int, 32);
pub const __BITINT_MAXWIDTH__ = __helpers.promoteIntLiteral(c_int, 65535, .decimal);
pub const __SIZEOF_FLOAT__ = @as(c_int, 4);
pub const __SIZEOF_DOUBLE__ = @as(c_int, 8);
pub const __SIZEOF_LONG_DOUBLE__ = @as(c_int, 10);
pub const __SIZEOF_SHORT__ = @as(c_int, 2);
pub const __SIZEOF_INT__ = @as(c_int, 4);
pub const __SIZEOF_LONG__ = @as(c_int, 8);
pub const __SIZEOF_LONG_LONG__ = @as(c_int, 8);
pub const __SIZEOF_POINTER__ = @as(c_int, 8);
pub const __SIZEOF_PTRDIFF_T__ = @as(c_int, 8);
pub const __SIZEOF_SIZE_T__ = @as(c_int, 8);
pub const __SIZEOF_WCHAR_T__ = @as(c_int, 4);
pub const __SIZEOF_INT128__ = @as(c_int, 16);
pub const __INTPTR_TYPE__ = c_long;
pub const __UINTPTR_TYPE__ = c_ulong;
pub const __INTMAX_TYPE__ = c_long;
pub const __INTMAX_C_SUFFIX__ = @compileError("unable to translate macro: undefined identifier `L`"); // <builtin>:149:9
pub const __UINTMAX_TYPE__ = c_ulong;
pub const __UINTMAX_C_SUFFIX__ = @compileError("unable to translate macro: undefined identifier `UL`"); // <builtin>:151:9
pub const __PTRDIFF_TYPE__ = c_long;
pub const __SIZE_TYPE__ = c_ulong;
pub const __WCHAR_TYPE__ = c_int;
pub const __CHAR16_TYPE__ = c_ushort;
pub const __CHAR32_TYPE__ = c_uint;
pub const __INT8_TYPE__ = i8;
pub const __INT8_FMTd__ = "hhd";
pub const __INT8_FMTi__ = "hhi";
pub const __INT8_C_SUFFIX__ = "";
pub const __INT16_TYPE__ = c_short;
pub const __INT16_FMTd__ = "hd";
pub const __INT16_FMTi__ = "hi";
pub const __INT16_C_SUFFIX__ = "";
pub const __INT32_TYPE__ = c_int;
pub const __INT32_FMTd__ = "d";
pub const __INT32_FMTi__ = "i";
pub const __INT32_C_SUFFIX__ = "";
pub const __INT64_TYPE__ = c_long;
pub const __INT64_FMTd__ = "ld";
pub const __INT64_FMTi__ = "li";
pub const __INT64_C_SUFFIX__ = @compileError("unable to translate macro: undefined identifier `L`"); // <builtin>:172:9
pub const __UINT8_TYPE__ = u8;
pub const __UINT8_FMTo__ = "hho";
pub const __UINT8_FMTu__ = "hhu";
pub const __UINT8_FMTx__ = "hhx";
pub const __UINT8_FMTX__ = "hhX";
pub const __UINT8_C_SUFFIX__ = "";
pub const __UINT8_MAX__ = @as(c_int, 255);
pub const __INT8_MAX__ = @as(c_int, 127);
pub const __UINT16_TYPE__ = c_ushort;
pub const __UINT16_FMTo__ = "ho";
pub const __UINT16_FMTu__ = "hu";
pub const __UINT16_FMTx__ = "hx";
pub const __UINT16_FMTX__ = "hX";
pub const __UINT16_C_SUFFIX__ = "";
pub const __UINT16_MAX__ = __helpers.promoteIntLiteral(c_int, 65535, .decimal);
pub const __INT16_MAX__ = @as(c_int, 32767);
pub const __UINT32_TYPE__ = c_uint;
pub const __UINT32_FMTo__ = "o";
pub const __UINT32_FMTu__ = "u";
pub const __UINT32_FMTx__ = "x";
pub const __UINT32_FMTX__ = "X";
pub const __UINT32_C_SUFFIX__ = @compileError("unable to translate macro: undefined identifier `U`"); // <builtin>:194:9
pub const __UINT32_MAX__ = __helpers.promoteIntLiteral(c_uint, 4294967295, .decimal);
pub const __INT32_MAX__ = __helpers.promoteIntLiteral(c_int, 2147483647, .decimal);
pub const __UINT64_TYPE__ = c_ulong;
pub const __UINT64_FMTo__ = "lo";
pub const __UINT64_FMTu__ = "lu";
pub const __UINT64_FMTx__ = "lx";
pub const __UINT64_FMTX__ = "lX";
pub const __UINT64_C_SUFFIX__ = @compileError("unable to translate macro: undefined identifier `UL`"); // <builtin>:202:9
pub const __UINT64_MAX__ = __helpers.promoteIntLiteral(c_ulong, 18446744073709551615, .decimal);
pub const __INT64_MAX__ = __helpers.promoteIntLiteral(c_long, 9223372036854775807, .decimal);
pub const __INT_LEAST8_TYPE__ = i8;
pub const __INT_LEAST8_MAX__ = @as(c_int, 127);
pub const __INT_LEAST8_WIDTH__ = @as(c_int, 8);
pub const INT_LEAST8_FMTd__ = "hhd";
pub const INT_LEAST8_FMTi__ = "hhi";
pub const __UINT_LEAST8_TYPE__ = u8;
pub const __UINT_LEAST8_MAX__ = @as(c_int, 255);
pub const UINT_LEAST8_FMTo__ = "hho";
pub const UINT_LEAST8_FMTu__ = "hhu";
pub const UINT_LEAST8_FMTx__ = "hhx";
pub const UINT_LEAST8_FMTX__ = "hhX";
pub const __INT_FAST8_TYPE__ = i8;
pub const __INT_FAST8_MAX__ = @as(c_int, 127);
pub const __INT_FAST8_WIDTH__ = @as(c_int, 8);
pub const INT_FAST8_FMTd__ = "hhd";
pub const INT_FAST8_FMTi__ = "hhi";
pub const __UINT_FAST8_TYPE__ = u8;
pub const __UINT_FAST8_MAX__ = @as(c_int, 255);
pub const UINT_FAST8_FMTo__ = "hho";
pub const UINT_FAST8_FMTu__ = "hhu";
pub const UINT_FAST8_FMTx__ = "hhx";
pub const UINT_FAST8_FMTX__ = "hhX";
pub const __INT_LEAST16_TYPE__ = c_short;
pub const __INT_LEAST16_MAX__ = @as(c_int, 32767);
pub const __INT_LEAST16_WIDTH__ = @as(c_int, 16);
pub const INT_LEAST16_FMTd__ = "hd";
pub const INT_LEAST16_FMTi__ = "hi";
pub const __UINT_LEAST16_TYPE__ = c_ushort;
pub const __UINT_LEAST16_MAX__ = __helpers.promoteIntLiteral(c_int, 65535, .decimal);
pub const UINT_LEAST16_FMTo__ = "ho";
pub const UINT_LEAST16_FMTu__ = "hu";
pub const UINT_LEAST16_FMTx__ = "hx";
pub const UINT_LEAST16_FMTX__ = "hX";
pub const __INT_FAST16_TYPE__ = c_short;
pub const __INT_FAST16_MAX__ = @as(c_int, 32767);
pub const __INT_FAST16_WIDTH__ = @as(c_int, 16);
pub const INT_FAST16_FMTd__ = "hd";
pub const INT_FAST16_FMTi__ = "hi";
pub const __UINT_FAST16_TYPE__ = c_ushort;
pub const __UINT_FAST16_MAX__ = __helpers.promoteIntLiteral(c_int, 65535, .decimal);
pub const UINT_FAST16_FMTo__ = "ho";
pub const UINT_FAST16_FMTu__ = "hu";
pub const UINT_FAST16_FMTx__ = "hx";
pub const UINT_FAST16_FMTX__ = "hX";
pub const __INT_LEAST32_TYPE__ = c_int;
pub const __INT_LEAST32_MAX__ = __helpers.promoteIntLiteral(c_int, 2147483647, .decimal);
pub const __INT_LEAST32_WIDTH__ = @as(c_int, 32);
pub const INT_LEAST32_FMTd__ = "d";
pub const INT_LEAST32_FMTi__ = "i";
pub const __UINT_LEAST32_TYPE__ = c_uint;
pub const __UINT_LEAST32_MAX__ = __helpers.promoteIntLiteral(c_uint, 4294967295, .decimal);
pub const UINT_LEAST32_FMTo__ = "o";
pub const UINT_LEAST32_FMTu__ = "u";
pub const UINT_LEAST32_FMTx__ = "x";
pub const UINT_LEAST32_FMTX__ = "X";
pub const __INT_FAST32_TYPE__ = c_int;
pub const __INT_FAST32_MAX__ = __helpers.promoteIntLiteral(c_int, 2147483647, .decimal);
pub const __INT_FAST32_WIDTH__ = @as(c_int, 32);
pub const INT_FAST32_FMTd__ = "d";
pub const INT_FAST32_FMTi__ = "i";
pub const __UINT_FAST32_TYPE__ = c_uint;
pub const __UINT_FAST32_MAX__ = __helpers.promoteIntLiteral(c_uint, 4294967295, .decimal);
pub const UINT_FAST32_FMTo__ = "o";
pub const UINT_FAST32_FMTu__ = "u";
pub const UINT_FAST32_FMTx__ = "x";
pub const UINT_FAST32_FMTX__ = "X";
pub const __INT_LEAST64_TYPE__ = c_long;
pub const __INT_LEAST64_MAX__ = __helpers.promoteIntLiteral(c_long, 9223372036854775807, .decimal);
pub const __INT_LEAST64_WIDTH__ = @as(c_int, 64);
pub const INT_LEAST64_FMTd__ = "ld";
pub const INT_LEAST64_FMTi__ = "li";
pub const __UINT_LEAST64_TYPE__ = c_ulong;
pub const __UINT_LEAST64_MAX__ = __helpers.promoteIntLiteral(c_ulong, 18446744073709551615, .decimal);
pub const UINT_LEAST64_FMTo__ = "lo";
pub const UINT_LEAST64_FMTu__ = "lu";
pub const UINT_LEAST64_FMTx__ = "lx";
pub const UINT_LEAST64_FMTX__ = "lX";
pub const __INT_FAST64_TYPE__ = c_long;
pub const __INT_FAST64_MAX__ = __helpers.promoteIntLiteral(c_long, 9223372036854775807, .decimal);
pub const __INT_FAST64_WIDTH__ = @as(c_int, 64);
pub const INT_FAST64_FMTd__ = "ld";
pub const INT_FAST64_FMTi__ = "li";
pub const __UINT_FAST64_TYPE__ = c_ulong;
pub const __UINT_FAST64_MAX__ = __helpers.promoteIntLiteral(c_ulong, 18446744073709551615, .decimal);
pub const UINT_FAST64_FMTo__ = "lo";
pub const UINT_FAST64_FMTu__ = "lu";
pub const UINT_FAST64_FMTx__ = "lx";
pub const UINT_FAST64_FMTX__ = "lX";
pub const __FLT16_DENORM_MIN__ = @as(f16, 5.9604644775390625e-8);
pub const __FLT16_HAS_DENORM__ = "";
pub const __FLT16_DIG__ = @as(c_int, 3);
pub const __FLT16_DECIMAL_DIG__ = @as(c_int, 5);
pub const __FLT16_EPSILON__ = @as(f16, 9.765625e-4);
pub const __FLT16_HAS_INFINITY__ = "";
pub const __FLT16_HAS_QUIET_NAN__ = "";
pub const __FLT16_MANT_DIG__ = @as(c_int, 11);
pub const __FLT16_MAX_10_EXP__ = @as(c_int, 4);
pub const __FLT16_MAX_EXP__ = @as(c_int, 16);
pub const __FLT16_MAX__ = @as(f16, 6.5504e+4);
pub const __FLT16_MIN_10_EXP__ = -@as(c_int, 4);
pub const __FLT16_MIN_EXP__ = -@as(c_int, 13);
pub const __FLT16_MIN__ = @as(f16, 6.103515625e-5);
pub const __FLT_DENORM_MIN__ = @as(f32, 1.40129846e-45);
pub const __FLT_HAS_DENORM__ = "";
pub const __FLT_DIG__ = @as(c_int, 6);
pub const __FLT_DECIMAL_DIG__ = @as(c_int, 9);
pub const __FLT_EPSILON__ = @as(f32, 1.19209290e-7);
pub const __FLT_HAS_INFINITY__ = "";
pub const __FLT_HAS_QUIET_NAN__ = "";
pub const __FLT_MANT_DIG__ = @as(c_int, 24);
pub const __FLT_MAX_10_EXP__ = @as(c_int, 38);
pub const __FLT_MAX_EXP__ = @as(c_int, 128);
pub const __FLT_MAX__ = @as(f32, 3.40282347e+38);
pub const __FLT_MIN_10_EXP__ = -@as(c_int, 37);
pub const __FLT_MIN_EXP__ = -@as(c_int, 125);
pub const __FLT_MIN__ = @as(f32, 1.17549435e-38);
pub const __DBL_DENORM_MIN__ = @as(f64, 4.9406564584124654e-324);
pub const __DBL_HAS_DENORM__ = "";
pub const __DBL_DIG__ = @as(c_int, 15);
pub const __DBL_DECIMAL_DIG__ = @as(c_int, 17);
pub const __DBL_EPSILON__ = @as(f64, 2.2204460492503131e-16);
pub const __DBL_HAS_INFINITY__ = "";
pub const __DBL_HAS_QUIET_NAN__ = "";
pub const __DBL_MANT_DIG__ = @as(c_int, 53);
pub const __DBL_MAX_10_EXP__ = @as(c_int, 308);
pub const __DBL_MAX_EXP__ = @as(c_int, 1024);
pub const __DBL_MAX__ = @as(f64, 1.7976931348623157e+308);
pub const __DBL_MIN_10_EXP__ = -@as(c_int, 307);
pub const __DBL_MIN_EXP__ = -@as(c_int, 1021);
pub const __DBL_MIN__ = @as(f64, 2.2250738585072014e-308);
pub const __LDBL_DENORM_MIN__ = @as(c_longdouble, 3.64519953188247460253e-4951);
pub const __LDBL_HAS_DENORM__ = "";
pub const __LDBL_DIG__ = @as(c_int, 18);
pub const __LDBL_DECIMAL_DIG__ = @as(c_int, 21);
pub const __LDBL_EPSILON__ = @as(c_longdouble, 1.08420217248550443401e-19);
pub const __LDBL_HAS_INFINITY__ = "";
pub const __LDBL_HAS_QUIET_NAN__ = "";
pub const __LDBL_MANT_DIG__ = @as(c_int, 64);
pub const __LDBL_MAX_10_EXP__ = @as(c_int, 4932);
pub const __LDBL_MAX_EXP__ = @as(c_int, 16384);
pub const __LDBL_MAX__ = @as(c_longdouble, 1.18973149535723176502e+4932);
pub const __LDBL_MIN_10_EXP__ = -@as(c_int, 4931);
pub const __LDBL_MIN_EXP__ = -@as(c_int, 16381);
pub const __LDBL_MIN__ = @as(c_longdouble, 3.36210314311209350626e-4932);
pub const __FLT_EVAL_METHOD__ = @as(c_int, 0);
pub const __FLT_RADIX__ = @as(c_int, 2);
pub const __DECIMAL_DIG__ = __LDBL_DECIMAL_DIG__;
pub const __pic__ = @as(c_int, 2);
pub const __PIC__ = @as(c_int, 2);
pub const NDEBUG = @as(c_int, 1);
pub const __GLIBC_MINOR__ = @as(c_int, 39);
pub const aegis_H = "";
pub const __CLANG_STDINT_H = "";
pub const _STDINT_H = @as(c_int, 1);
pub const _FEATURES_H = @as(c_int, 1);
pub const __KERNEL_STRICT_NAMES = "";
pub inline fn __GNUC_PREREQ(maj: anytype, min: anytype) @TypeOf(((__GNUC__ << @as(c_int, 16)) + __GNUC_MINOR__) >= ((maj << @as(c_int, 16)) + min)) {
    _ = &maj;
    _ = &min;
    return ((__GNUC__ << @as(c_int, 16)) + __GNUC_MINOR__) >= ((maj << @as(c_int, 16)) + min);
}
pub inline fn __glibc_clang_prereq(maj: anytype, min: anytype) @TypeOf(@as(c_int, 0)) {
    _ = &maj;
    _ = &min;
    return @as(c_int, 0);
}
pub const __GLIBC_USE = @compileError("unable to translate macro: undefined identifier `__GLIBC_USE_`"); // /usr/include/features.h:188:9
pub const _DEFAULT_SOURCE = @as(c_int, 1);
pub const __GLIBC_USE_ISOC2X = @as(c_int, 0);
pub const __USE_ISOC11 = @as(c_int, 1);
pub const __USE_POSIX_IMPLICITLY = @as(c_int, 1);
pub const _POSIX_SOURCE = @as(c_int, 1);
pub const _POSIX_C_SOURCE = @as(c_long, 200809);
pub const __USE_POSIX = @as(c_int, 1);
pub const __USE_POSIX2 = @as(c_int, 1);
pub const __USE_POSIX199309 = @as(c_int, 1);
pub const __USE_POSIX199506 = @as(c_int, 1);
pub const __USE_XOPEN2K = @as(c_int, 1);
pub const __USE_ISOC95 = @as(c_int, 1);
pub const __USE_ISOC99 = @as(c_int, 1);
pub const __USE_XOPEN2K8 = @as(c_int, 1);
pub const _ATFILE_SOURCE = @as(c_int, 1);
pub const __WORDSIZE = @as(c_int, 64);
pub const __WORDSIZE_TIME64_COMPAT32 = @as(c_int, 1);
pub const __SYSCALL_WORDSIZE = @as(c_int, 64);
pub const __TIMESIZE = __WORDSIZE;
pub const __USE_MISC = @as(c_int, 1);
pub const __USE_ATFILE = @as(c_int, 1);
pub const __USE_FORTIFY_LEVEL = @as(c_int, 0);
pub const __GLIBC_USE_DEPRECATED_GETS = @as(c_int, 0);
pub const __GLIBC_USE_DEPRECATED_SCANF = @as(c_int, 0);
pub const __GLIBC_USE_C2X_STRTOL = @as(c_int, 0);
pub const _STDC_PREDEF_H = @as(c_int, 1);
pub const __STDC_IEC_559__ = @as(c_int, 1);
pub const __STDC_IEC_60559_BFP__ = @as(c_long, 201404);
pub const __STDC_IEC_559_COMPLEX__ = @as(c_int, 1);
pub const __STDC_IEC_60559_COMPLEX__ = @as(c_long, 201404);
pub const __STDC_ISO_10646__ = @as(c_long, 201706);
pub const __GNU_LIBRARY__ = @as(c_int, 6);
pub const __GLIBC__ = @as(c_int, 2);
pub inline fn __GLIBC_PREREQ(maj: anytype, min: anytype) @TypeOf(((__GLIBC__ << @as(c_int, 16)) + __GLIBC_MINOR__) >= ((maj << @as(c_int, 16)) + min)) {
    _ = &maj;
    _ = &min;
    return ((__GLIBC__ << @as(c_int, 16)) + __GLIBC_MINOR__) >= ((maj << @as(c_int, 16)) + min);
}
pub const _SYS_CDEFS_H = @as(c_int, 1);
pub const __glibc_has_attribute = @compileError("unable to translate macro: undefined identifier `__has_attribute`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:45:10
pub inline fn __glibc_has_builtin(name: anytype) @TypeOf(__builtin.has_builtin(name)) {
    _ = &name;
    return __builtin.has_builtin(name);
}
pub const __glibc_has_extension = @compileError("unable to translate macro: undefined identifier `__has_extension`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:55:10
pub const __LEAF = @compileError("unable to translate macro: undefined identifier `__leaf__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:65:11
pub const __LEAF_ATTR = @compileError("unable to translate macro: undefined identifier `__leaf__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:66:11
pub const __THROW = @compileError("unable to translate macro: undefined identifier `__nothrow__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:79:11
pub const __THROWNL = @compileError("unable to translate macro: undefined identifier `__nothrow__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:80:11
pub const __NTH = @compileError("unable to translate macro: undefined identifier `__nothrow__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:81:11
pub const __NTHNL = @compileError("unable to translate macro: undefined identifier `__nothrow__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:82:11
pub const __COLD = @compileError("unable to translate macro: undefined identifier `__cold__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:102:11
pub inline fn __P(args: anytype) @TypeOf(args) {
    _ = &args;
    return args;
}
pub inline fn __PMT(args: anytype) @TypeOf(args) {
    _ = &args;
    return args;
}
pub const __CONCAT = @compileError("unable to translate C expr: unexpected token '##'"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:131:9
pub const __STRING = @compileError("unable to translate C expr: unexpected token ''"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:132:9
pub const __ptr_t = ?*anyopaque;
pub const __BEGIN_DECLS = "";
pub const __END_DECLS = "";
pub inline fn __bos(ptr: anytype) @TypeOf(__builtin.object_size(ptr, __USE_FORTIFY_LEVEL > @as(c_int, 1))) {
    _ = &ptr;
    return __builtin.object_size(ptr, __USE_FORTIFY_LEVEL > @as(c_int, 1));
}
pub inline fn __bos0(ptr: anytype) @TypeOf(__builtin.object_size(ptr, @as(c_int, 0))) {
    _ = &ptr;
    return __builtin.object_size(ptr, @as(c_int, 0));
}
pub inline fn __glibc_objsize0(__o: anytype) @TypeOf(__bos0(__o)) {
    _ = &__o;
    return __bos0(__o);
}
pub inline fn __glibc_objsize(__o: anytype) @TypeOf(__bos(__o)) {
    _ = &__o;
    return __bos(__o);
}
pub const __warnattr = @compileError("unable to translate macro: undefined identifier `__warning__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:212:10
pub const __errordecl = @compileError("unable to translate macro: undefined identifier `__error__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:213:10
pub const __flexarr = @compileError("unable to translate C expr: unexpected token '['"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:225:10
pub const __glibc_c99_flexarr_available = @as(c_int, 1);
pub const __REDIRECT = @compileError("unable to translate C expr: unexpected token ''"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:256:10
pub const __REDIRECT_NTH = @compileError("unable to translate C expr: unexpected token ''"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:263:11
pub const __REDIRECT_NTHNL = @compileError("unable to translate C expr: unexpected token ''"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:265:11
pub const __ASMNAME = @compileError("unable to translate macro: undefined identifier `__USER_LABEL_PREFIX__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:268:10
pub const __ASMNAME2 = @compileError("unable to translate C expr: unexpected token ''"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:269:10
pub const __REDIRECT_FORTIFY = __REDIRECT;
pub const __REDIRECT_FORTIFY_NTH = __REDIRECT_NTH;
pub const __attribute_malloc__ = @compileError("unable to translate macro: undefined identifier `__malloc__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:298:10
pub const __attribute_alloc_size__ = @compileError("unable to translate macro: undefined identifier `__alloc_size__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:306:10
pub const __attribute_alloc_align__ = @compileError("unable to translate macro: undefined identifier `__alloc_align__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:315:10
pub const __attribute_pure__ = @compileError("unable to translate macro: undefined identifier `__pure__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:325:10
pub const __attribute_const__ = @compileError("unable to translate C expr: unexpected token '__attribute__'"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:332:10
pub const __attribute_maybe_unused__ = @compileError("unable to translate macro: undefined identifier `__unused__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:338:10
pub const __attribute_used__ = @compileError("unable to translate macro: undefined identifier `__used__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:347:10
pub const __attribute_noinline__ = @compileError("unable to translate macro: undefined identifier `__noinline__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:348:10
pub const __attribute_deprecated__ = @compileError("unable to translate macro: undefined identifier `__deprecated__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:356:10
pub const __attribute_deprecated_msg__ = @compileError("unable to translate macro: undefined identifier `__deprecated__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:366:10
pub const __attribute_format_arg__ = @compileError("unable to translate macro: undefined identifier `__format_arg__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:379:10
pub const __attribute_format_strfmon__ = @compileError("unable to translate macro: undefined identifier `__format__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:389:10
pub const __attribute_nonnull__ = @compileError("unable to translate macro: undefined identifier `__nonnull__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:401:11
pub inline fn __nonnull(params: anytype) @TypeOf(__attribute_nonnull__(params)) {
    _ = &params;
    return __attribute_nonnull__(params);
}
pub const __returns_nonnull = @compileError("unable to translate macro: undefined identifier `__returns_nonnull__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:414:10
pub const __attribute_warn_unused_result__ = @compileError("unable to translate macro: undefined identifier `__warn_unused_result__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:423:10
pub const __wur = "";
pub const __always_inline = @compileError("unable to translate macro: undefined identifier `__always_inline__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:441:10
pub const __attribute_artificial__ = @compileError("unable to translate macro: undefined identifier `__artificial__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:450:10
pub const __extern_inline = @compileError("unable to translate C expr: unexpected token 'extern'"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:472:11
pub const __extern_always_inline = @compileError("unable to translate C expr: unexpected token 'extern'"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:473:11
pub const __fortify_function = __extern_always_inline ++ __attribute_artificial__;
pub const __va_arg_pack = @compileError("unable to translate macro: undefined identifier `__builtin_va_arg_pack`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:484:10
pub const __va_arg_pack_len = @compileError("unable to translate macro: undefined identifier `__builtin_va_arg_pack_len`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:485:10
pub const __restrict_arr = @compileError("unable to translate C expr: unexpected token '__restrict'"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:512:10
pub inline fn __glibc_unlikely(cond: anytype) @TypeOf(__builtin.expect(cond, @as(c_int, 0))) {
    _ = &cond;
    return __builtin.expect(cond, @as(c_int, 0));
}
pub inline fn __glibc_likely(cond: anytype) @TypeOf(__builtin.expect(cond, @as(c_int, 1))) {
    _ = &cond;
    return __builtin.expect(cond, @as(c_int, 1));
}
pub const __attribute_nonstring__ = "";
pub const __attribute_copy__ = @compileError("unable to translate C expr: unexpected token ''"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:561:10
pub const __LDOUBLE_REDIRECTS_TO_FLOAT128_ABI = @as(c_int, 0);
pub const __LDBL_REDIR1 = @compileError("unable to translate C expr: unexpected token ''"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:634:10
pub const __LDBL_REDIR = @compileError("unable to translate C expr: unexpected token ''"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:635:10
pub const __LDBL_REDIR1_NTH = @compileError("unable to translate C expr: unexpected token ''"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:636:10
pub const __LDBL_REDIR_NTH = @compileError("unable to translate C expr: unexpected token ''"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:637:10
pub const __LDBL_REDIR2_DECL = @compileError("unable to translate C expr: unexpected token ''"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:638:10
pub const __LDBL_REDIR_DECL = @compileError("unable to translate C expr: unexpected token ''"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:639:10
pub inline fn __REDIRECT_LDBL(name: anytype, proto: anytype, alias: anytype) @TypeOf(__REDIRECT(name, proto, alias)) {
    _ = &name;
    _ = &proto;
    _ = &alias;
    return __REDIRECT(name, proto, alias);
}
pub inline fn __REDIRECT_NTH_LDBL(name: anytype, proto: anytype, alias: anytype) @TypeOf(__REDIRECT_NTH(name, proto, alias)) {
    _ = &name;
    _ = &proto;
    _ = &alias;
    return __REDIRECT_NTH(name, proto, alias);
}
pub const __glibc_macro_warning1 = @compileError("unable to translate macro: undefined identifier `_Pragma`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:653:10
pub const __glibc_macro_warning = @compileError("unable to translate macro: undefined identifier `GCC`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:654:10
pub const __HAVE_GENERIC_SELECTION = @as(c_int, 1);
pub const __fortified_attr_access = @compileError("unable to translate C expr: unexpected token ''"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:699:11
pub const __attr_access = @compileError("unable to translate C expr: unexpected token ''"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:700:11
pub const __attr_access_none = @compileError("unable to translate C expr: unexpected token ''"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:701:11
pub const __attr_dealloc = @compileError("unable to translate C expr: unexpected token ''"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:711:10
pub const __attr_dealloc_free = "";
pub const __attribute_returns_twice__ = @compileError("unable to translate macro: undefined identifier `__returns_twice__`"); // /usr/include/x86_64-linux-gnu/sys/cdefs.h:718:10
pub const __USE_EXTERN_INLINES = @as(c_int, 1);
pub const __GLIBC_USE_LIB_EXT2 = @as(c_int, 0);
pub const __GLIBC_USE_IEC_60559_BFP_EXT = @as(c_int, 0);
pub const __GLIBC_USE_IEC_60559_BFP_EXT_C2X = @as(c_int, 0);
pub const __GLIBC_USE_IEC_60559_EXT = @as(c_int, 0);
pub const __GLIBC_USE_IEC_60559_FUNCS_EXT = @as(c_int, 0);
pub const __GLIBC_USE_IEC_60559_FUNCS_EXT_C2X = @as(c_int, 0);
pub const __GLIBC_USE_IEC_60559_TYPES_EXT = @as(c_int, 0);
pub const _BITS_TYPES_H = @as(c_int, 1);
pub const __S16_TYPE = c_short;
pub const __U16_TYPE = c_ushort;
pub const __S32_TYPE = c_int;
pub const __U32_TYPE = c_uint;
pub const __SLONGWORD_TYPE = c_long;
pub const __ULONGWORD_TYPE = c_ulong;
pub const __SQUAD_TYPE = c_long;
pub const __UQUAD_TYPE = c_ulong;
pub const __SWORD_TYPE = c_long;
pub const __UWORD_TYPE = c_ulong;
pub const __SLONG32_TYPE = c_int;
pub const __ULONG32_TYPE = c_uint;
pub const __S64_TYPE = c_long;
pub const __U64_TYPE = c_ulong;
pub const _BITS_TYPESIZES_H = @as(c_int, 1);
pub const __SYSCALL_SLONG_TYPE = __SLONGWORD_TYPE;
pub const __SYSCALL_ULONG_TYPE = __ULONGWORD_TYPE;
pub const __DEV_T_TYPE = __UQUAD_TYPE;
pub const __UID_T_TYPE = __U32_TYPE;
pub const __GID_T_TYPE = __U32_TYPE;
pub const __INO_T_TYPE = __SYSCALL_ULONG_TYPE;
pub const __INO64_T_TYPE = __UQUAD_TYPE;
pub const __MODE_T_TYPE = __U32_TYPE;
pub const __NLINK_T_TYPE = __SYSCALL_ULONG_TYPE;
pub const __FSWORD_T_TYPE = __SYSCALL_SLONG_TYPE;
pub const __OFF_T_TYPE = __SYSCALL_SLONG_TYPE;
pub const __OFF64_T_TYPE = __SQUAD_TYPE;
pub const __PID_T_TYPE = __S32_TYPE;
pub const __RLIM_T_TYPE = __SYSCALL_ULONG_TYPE;
pub const __RLIM64_T_TYPE = __UQUAD_TYPE;
pub const __BLKCNT_T_TYPE = __SYSCALL_SLONG_TYPE;
pub const __BLKCNT64_T_TYPE = __SQUAD_TYPE;
pub const __FSBLKCNT_T_TYPE = __SYSCALL_ULONG_TYPE;
pub const __FSBLKCNT64_T_TYPE = __UQUAD_TYPE;
pub const __FSFILCNT_T_TYPE = __SYSCALL_ULONG_TYPE;
pub const __FSFILCNT64_T_TYPE = __UQUAD_TYPE;
pub const __ID_T_TYPE = __U32_TYPE;
pub const __CLOCK_T_TYPE = __SYSCALL_SLONG_TYPE;
pub const __TIME_T_TYPE = __SYSCALL_SLONG_TYPE;
pub const __USECONDS_T_TYPE = __U32_TYPE;
pub const __SUSECONDS_T_TYPE = __SYSCALL_SLONG_TYPE;
pub const __SUSECONDS64_T_TYPE = __SQUAD_TYPE;
pub const __DADDR_T_TYPE = __S32_TYPE;
pub const __KEY_T_TYPE = __S32_TYPE;
pub const __CLOCKID_T_TYPE = __S32_TYPE;
pub const __TIMER_T_TYPE = ?*anyopaque;
pub const __BLKSIZE_T_TYPE = __SYSCALL_SLONG_TYPE;
pub const __FSID_T_TYPE = @compileError("unable to translate macro: undefined identifier `__val`"); // /usr/include/x86_64-linux-gnu/bits/typesizes.h:73:9
pub const __SSIZE_T_TYPE = __SWORD_TYPE;
pub const __CPU_MASK_TYPE = __SYSCALL_ULONG_TYPE;
pub const __OFF_T_MATCHES_OFF64_T = @as(c_int, 1);
pub const __INO_T_MATCHES_INO64_T = @as(c_int, 1);
pub const __RLIM_T_MATCHES_RLIM64_T = @as(c_int, 1);
pub const __STATFS_MATCHES_STATFS64 = @as(c_int, 1);
pub const __KERNEL_OLD_TIMEVAL_MATCHES_TIMEVAL64 = @as(c_int, 1);
pub const __FD_SETSIZE = @as(c_int, 1024);
pub const _BITS_TIME64_H = @as(c_int, 1);
pub const __TIME64_T_TYPE = __TIME_T_TYPE;
pub const _BITS_WCHAR_H = @as(c_int, 1);
pub const __WCHAR_MAX = __WCHAR_MAX__;
pub const __WCHAR_MIN = -__WCHAR_MAX - @as(c_int, 1);
pub const _BITS_STDINT_INTN_H = @as(c_int, 1);
pub const _BITS_STDINT_UINTN_H = @as(c_int, 1);
pub const _BITS_STDINT_LEAST_H = @as(c_int, 1);
pub const __intptr_t_defined = "";
pub const __INT64_C = __helpers.L_SUFFIX;
pub const __UINT64_C = __helpers.UL_SUFFIX;
pub const INT8_MIN = -@as(c_int, 128);
pub const INT16_MIN = -@as(c_int, 32767) - @as(c_int, 1);
pub const INT32_MIN = -__helpers.promoteIntLiteral(c_int, 2147483647, .decimal) - @as(c_int, 1);
pub const INT64_MIN = -__INT64_C(__helpers.promoteIntLiteral(c_int, 9223372036854775807, .decimal)) - @as(c_int, 1);
pub const INT8_MAX = @as(c_int, 127);
pub const INT16_MAX = @as(c_int, 32767);
pub const INT32_MAX = __helpers.promoteIntLiteral(c_int, 2147483647, .decimal);
pub const INT64_MAX = __INT64_C(__helpers.promoteIntLiteral(c_int, 9223372036854775807, .decimal));
pub const UINT8_MAX = @as(c_int, 255);
pub const UINT16_MAX = __helpers.promoteIntLiteral(c_int, 65535, .decimal);
pub const UINT32_MAX = __helpers.promoteIntLiteral(c_uint, 4294967295, .decimal);
pub const UINT64_MAX = __UINT64_C(__helpers.promoteIntLiteral(c_int, 18446744073709551615, .decimal));
pub const INT_LEAST8_MIN = -@as(c_int, 128);
pub const INT_LEAST16_MIN = -@as(c_int, 32767) - @as(c_int, 1);
pub const INT_LEAST32_MIN = -__helpers.promoteIntLiteral(c_int, 2147483647, .decimal) - @as(c_int, 1);
pub const INT_LEAST64_MIN = -__INT64_C(__helpers.promoteIntLiteral(c_int, 9223372036854775807, .decimal)) - @as(c_int, 1);
pub const INT_LEAST8_MAX = @as(c_int, 127);
pub const INT_LEAST16_MAX = @as(c_int, 32767);
pub const INT_LEAST32_MAX = __helpers.promoteIntLiteral(c_int, 2147483647, .decimal);
pub const INT_LEAST64_MAX = __INT64_C(__helpers.promoteIntLiteral(c_int, 9223372036854775807, .decimal));
pub const UINT_LEAST8_MAX = @as(c_int, 255);
pub const UINT_LEAST16_MAX = __helpers.promoteIntLiteral(c_int, 65535, .decimal);
pub const UINT_LEAST32_MAX = __helpers.promoteIntLiteral(c_uint, 4294967295, .decimal);
pub const UINT_LEAST64_MAX = __UINT64_C(__helpers.promoteIntLiteral(c_int, 18446744073709551615, .decimal));
pub const INT_FAST8_MIN = -@as(c_int, 128);
pub const INT_FAST16_MIN = -__helpers.promoteIntLiteral(c_long, 9223372036854775807, .decimal) - @as(c_int, 1);
pub const INT_FAST32_MIN = -__helpers.promoteIntLiteral(c_long, 9223372036854775807, .decimal) - @as(c_int, 1);
pub const INT_FAST64_MIN = -__INT64_C(__helpers.promoteIntLiteral(c_int, 9223372036854775807, .decimal)) - @as(c_int, 1);
pub const INT_FAST8_MAX = @as(c_int, 127);
pub const INT_FAST16_MAX = __helpers.promoteIntLiteral(c_long, 9223372036854775807, .decimal);
pub const INT_FAST32_MAX = __helpers.promoteIntLiteral(c_long, 9223372036854775807, .decimal);
pub const INT_FAST64_MAX = __INT64_C(__helpers.promoteIntLiteral(c_int, 9223372036854775807, .decimal));
pub const UINT_FAST8_MAX = @as(c_int, 255);
pub const UINT_FAST16_MAX = __helpers.promoteIntLiteral(c_ulong, 18446744073709551615, .decimal);
pub const UINT_FAST32_MAX = __helpers.promoteIntLiteral(c_ulong, 18446744073709551615, .decimal);
pub const UINT_FAST64_MAX = __UINT64_C(__helpers.promoteIntLiteral(c_int, 18446744073709551615, .decimal));
pub const INTPTR_MIN = -__helpers.promoteIntLiteral(c_long, 9223372036854775807, .decimal) - @as(c_int, 1);
pub const INTPTR_MAX = __helpers.promoteIntLiteral(c_long, 9223372036854775807, .decimal);
pub const UINTPTR_MAX = __helpers.promoteIntLiteral(c_ulong, 18446744073709551615, .decimal);
pub const INTMAX_MIN = -__INT64_C(__helpers.promoteIntLiteral(c_int, 9223372036854775807, .decimal)) - @as(c_int, 1);
pub const INTMAX_MAX = __INT64_C(__helpers.promoteIntLiteral(c_int, 9223372036854775807, .decimal));
pub const UINTMAX_MAX = __UINT64_C(__helpers.promoteIntLiteral(c_int, 18446744073709551615, .decimal));
pub const PTRDIFF_MIN = -__helpers.promoteIntLiteral(c_long, 9223372036854775807, .decimal) - @as(c_int, 1);
pub const PTRDIFF_MAX = __helpers.promoteIntLiteral(c_long, 9223372036854775807, .decimal);
pub const SIG_ATOMIC_MIN = -__helpers.promoteIntLiteral(c_int, 2147483647, .decimal) - @as(c_int, 1);
pub const SIG_ATOMIC_MAX = __helpers.promoteIntLiteral(c_int, 2147483647, .decimal);
pub const SIZE_MAX = __helpers.promoteIntLiteral(c_ulong, 18446744073709551615, .decimal);
pub const WCHAR_MIN = __WCHAR_MIN;
pub const WCHAR_MAX = __WCHAR_MAX;
pub const WINT_MIN = @as(c_uint, 0);
pub const WINT_MAX = __helpers.promoteIntLiteral(c_uint, 4294967295, .decimal);
pub inline fn INT8_C(c: anytype) @TypeOf(c) {
    _ = &c;
    return c;
}
pub inline fn INT16_C(c: anytype) @TypeOf(c) {
    _ = &c;
    return c;
}
pub inline fn INT32_C(c: anytype) @TypeOf(c) {
    _ = &c;
    return c;
}
pub const INT64_C = __helpers.L_SUFFIX;
pub inline fn UINT8_C(c: anytype) @TypeOf(c) {
    _ = &c;
    return c;
}
pub inline fn UINT16_C(c: anytype) @TypeOf(c) {
    _ = &c;
    return c;
}
pub const UINT32_C = __helpers.U_SUFFIX;
pub const UINT64_C = __helpers.UL_SUFFIX;
pub const INTMAX_C = __helpers.L_SUFFIX;
pub const UINTMAX_C = __helpers.UL_SUFFIX;
pub const CRYPTO_ALIGN = @compileError("unable to translate macro: undefined identifier `aligned`"); // /home/user/pyaegis/libaegis/src/include/aegis.h:17:17
pub const aegis128l_H = "";
pub const __STDC_VERSION_STDDEF_H__ = @as(c_long, 202311);
pub const NULL = __helpers.cast(?*anyopaque, @as(c_int, 0));
pub const offsetof = @compileError("unable to translate macro: undefined identifier `__builtin_offsetof`"); // /opt/zig/lib/compiler/aro/include/stddef.h:18:9
pub const aegis128l_KEYBYTES = @as(c_int, 16);
pub const aegis128l_NPUBBYTES = @as(c_int, 16);
pub const aegis128l_ABYTES_MIN = @as(c_int, 16);
pub const aegis128l_ABYTES_MAX = @as(c_int, 32);
pub const aegis128l_TAILBYTES_MAX = @as(c_int, 31);
pub const aegis128x2_H = "";
pub const aegis128x2_KEYBYTES = @as(c_int, 16);
pub const aegis128x2_NPUBBYTES = @as(c_int, 16);
pub const aegis128x2_ABYTES_MIN = @as(c_int, 16);
pub const aegis128x2_ABYTES_MAX = @as(c_int, 32);
pub const aegis128x2_TAILBYTES_MAX = @as(c_int, 63);
pub const aegis128x4_H = "";
pub const aegis128x4_KEYBYTES = @as(c_int, 16);
pub const aegis128x4_NPUBBYTES = @as(c_int, 16);
pub const aegis128x4_ABYTES_MIN = @as(c_int, 16);
pub const aegis128x4_ABYTES_MAX = @as(c_int, 32);
pub const aegis128x4_TAILBYTES_MAX = @as(c_int, 127);
pub const aegis256_H = "";
pub const aegis256_KEYBYTES = @as(c_int, 32);
pub const aegis256_NPUBBYTES = @as(c_int, 32);
pub const aegis256_ABYTES_MIN = @as(c_int, 16);
pub const aegis256_ABYTES_MAX = @as(c_int, 32);
pub const aegis256_TAILBYTES_MAX = @as(c_int, 15);
pub const aegis256x2_H = "";
pub const aegis256x2_KEYBYTES = @as(c_int, 32);
pub const aegis256x2_NPUBBYTES = @as(c_int, 32);
pub const aegis256x2_ABYTES_MIN = @as(c_int, 16);
pub const aegis256x2_ABYTES_MAX = @as(c_int, 32);
pub const aegis256x2_TAILBYTES_MAX = @as(c_int, 31);
pub const aegis256x4_H = "";
pub const aegis256x4_KEYBYTES = @as(c_int, 32);
pub const aegis256x4_NPUBBYTES = @as(c_int, 32);
pub const aegis256x4_ABYTES_MIN = @as(c_int, 16);
pub const aegis256x4_ABYTES_MAX = @as(c_int, 32);
pub const aegis256x4_TAILBYTES_MAX = @as(c_int, 63);
