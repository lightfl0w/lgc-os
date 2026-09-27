#!/bin/bash
cd "$(dirname "$0")/.." || exit 1

SRC_IMG=lgc-os.img
WORK_IMG=/tmp/selfhost-work.img   
NEW_IMG=lgc-os-selfhost.img
WORK_SIZE=4M
SAVE_LBA=4096   
BLOB_LBA=256      
BOOT_LOG=/tmp/selfhost-boot1.log
RUN_LOG=/tmp/selfhost-boot2.log

if [ ! -f "$SRC_IMG" ]; then
    echo "找不到 $SRC_IMG" >&2
    exit 1
fi

run_until() {  
    qemu-system-x86_64 -drive format=raw,file="$1" -display none -serial stdio -no-reboot \
        < "$2" > "$3" 2>&1 &
    local pid=$! n=0
    while [ "$n" -lt "$5" ]; do
        grep -q "$4" "$3" 2>/dev/null && break
        sleep 1
        n=$((n + 1))
    done
    sleep 1
    kill -9 "$pid" 2>/dev/null
    wait "$pid" 2>/dev/null
    return 0
}

echo "自举内核并写回磁盘"
cp "$SRC_IMG" "$WORK_IMG"
truncate -s "$WORK_SIZE" "$WORK_IMG"
printf 'exec lgc.elf os.lg os.bin\nsave os.bin %s\n' "$SAVE_LBA" > /tmp/selfhost-in.txt
run_until "$WORK_IMG" /tmp/selfhost-in.txt "$BOOT_LOG" 'sectors=' 90
tail -5 "$BOOT_LOG"

NSECT=$(sed -n 's/.*sectors=\([0-9][0-9]*\).*/\1/p' "$BOOT_LOG" | tail -1)
if [ -z "$NSECT" ]; then
    echo "自举编译或保存失败" >&2
    exit 1
fi
sync

echo "尝试提取镜像"
rm -f "$NEW_IMG"
dd if="$WORK_IMG" of="$NEW_IMG" bs=512 skip="$SAVE_LBA" count="$NSECT" status=none
dd if="$SRC_IMG" of="$NEW_IMG" bs=512 skip="$BLOB_LBA" seek="$BLOB_LBA" conv=notrunc status=none
ls -la "$NEW_IMG"

MAGIC=$(dd if="$NEW_IMG" bs=1 skip=510 count=2 status=none | xxd -p)
if [ "$MAGIC" != "55aa" ]; then
    echo "新镜像编译失败" >&2
    exit 1
fi

echo "运行内核"
printf 'ls\nexec hello_c\nexec lgc.elf a.lg a.elf\ninfo\n' > /tmp/selfhost-in2.txt
run_until "$NEW_IMG" /tmp/selfhost-in2.txt "$RUN_LOG" 'files=' 60
tail -30 "$RUN_LOG"
