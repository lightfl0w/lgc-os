#!/bin/sh
set -e
cd "$(dirname "$0")"

LGC="${LGC:-./lgc}"
if [ ! -x "$LGC" ]; then
    echo "找不到 lgc 编译器：$LGC" >&2
    exit 1
fi

python3 tools/mkelf.py "RING3!" 0x180000 usr/hello.elf kernel/usrelf.lg 42

"$LGC" kernel/os.lg lgc-os.img

exec qemu-system-x86_64 -drive format=raw,file=lgc-os.img -no-reboot
