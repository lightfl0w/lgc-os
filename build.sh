#!/bin/sh
set -e
cd "$(dirname "$0")"

LGC="${LGC:-../compiler/my_compiler}"
if [ ! -x "$LGC" ]; then
    echo "找不到 lgc 编译器：$LGC" >&2
    echo "先在 ../compiler 里运行 ./build.sh，或设 LGC=... 环境变量" >&2
    exit 1
fi

echo "== 编译内核 =="
"$LGC" kernel/kernel.lg lgc-os.img

echo
echo "== 运行=="
qemu-system-x86_64 -drive format=raw,file=lgc-os.img -serial stdio -nographic