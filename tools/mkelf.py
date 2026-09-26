import sys, struct

SYS_PUTC = 0
SYS_EXIT = 1
SYS_PUTS = 2

PREFIX_LEN = 24

def code_bytes(msg, entry, exitcode):
    out = bytearray()
    out += b'\xb8' + struct.pack('<I', SYS_PUTS)
    out += b'\xbf' + struct.pack('<I', entry + PREFIX_LEN)
    out += b'\xcd\x80'
    out += b'\xb8' + struct.pack('<I', SYS_EXIT)
    out += b'\xbf' + struct.pack('<I', exitcode & 0xFFFFFFFF)
    out += b'\xcd\x80'
    assert len(out) == PREFIX_LEN
    return bytes(out) + msg.encode() + b'\x00'

def build_elf(msg, entry, exitcode):
    code = code_bytes(msg, entry, exitcode)
    ehsize, phentsize, phnum = 64, 56, 1
    phoff = ehsize
    off = phoff + phentsize * phnum
    hdr = bytearray()
    hdr += b'\x7fELF'
    hdr += bytes([2, 1, 1, 0]) + bytes(8)
    hdr += struct.pack('<HHI', 2, 0x3e, 1)
    hdr += struct.pack('<QQQ', entry, phoff, 0)
    hdr += struct.pack('<I', 0)
    hdr += struct.pack('<HHHHHH', ehsize, phentsize, phnum, 0, 0, 0)
    ph = struct.pack('<IIQQQQQQ', 1, 5, off, entry, entry, len(code), len(code), 0x1000)
    return hdr + ph + code

def emit_lg(image, path):
    with open(path, 'w') as f:
        f.write('@import "io.lg";\n\n')
        f.write('const USRELF_LEN = %d;\n\n' % len(image))
        f.write('func usrelf_bytes(dst) {\n')
        n = len(image)
        full = n - (n % 4)
        for i in range(0, full, 4):
            v = struct.unpack('<I', image[i:i+4])[0]
            f.write('    mem_write32(dst, %d, 0x%08x);\n' % (i, v))
        for i in range(full, n):
            f.write('    mem_write8(dst, %d, %d);\n' % (i, image[i]))
        f.write('    return %d;\n}\n' % n)

if __name__ == '__main__':
    msg = sys.argv[1] if len(sys.argv) > 1 else 'RING3!'
    entry = int(sys.argv[2], 0) if len(sys.argv) > 2 else 0x180000
    elf_path = sys.argv[3] if len(sys.argv) > 3 else 'usr/hello.elf'
    lg_path = sys.argv[4] if len(sys.argv) > 4 else 'kernel/usrelf.lg'
    exitcode = int(sys.argv[5], 0) if len(sys.argv) > 5 else 0
    image = build_elf(msg, entry, exitcode)
    with open(elf_path, 'wb') as f:
        f.write(image)
    emit_lg(image, lg_path)
    print('wrote %s (%d bytes, exit=%d) and %s' % (elf_path, len(image), exitcode, lg_path))
