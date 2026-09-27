import os, subprocess, pathlib

root = pathlib.Path(__file__).parent

IMG = "lgc-os.img"
BLOB_LBA = 256         
SECTOR = 512
PAGE = 0x1000

RAMFS_BASE = 0x4000000  
SCRATCH_BASE = 0x6000000 
SCRATCH_LIMIT = 0x8000000  

LGC_SRC = os.environ.get("LGC_SRC", "/root/compiler/src/lgc.lg")
if LGC_SRC == "NO":
    raise RuntimeError("请设置LGC自举版源码路径")

C_SRC = "usr/hello_c.c"
C_OUT = "usr/hello_c"
SPIN_SRC = "usr/spin_c.c"
SPIN_OUT = "usr/spin_c"

USERFS_LG = "kernel/userfs.lg"
USERFS_SIZE = 4096

SLOTS = [
    ("usr/lgc.elf", "lgc.elf"),
    ("usr/a.lg", "a.lg"),
    (C_OUT, "hello_c"),
    (SPIN_OUT, "spin_c"),
    ("kernel/ata.lg", "ata.lg"),
    ("kernel/core.lg", "core.lg"),
    ("kernel/elf.lg", "elf.lg"),
    ("kernel/fs.lg", "fs.lg"),
    ("kernel/heap.lg", "heap.lg"),
    ("kernel/io.lg", "io.lg"),
    ("kernel/mm.lg", "mm.lg"),
    ("kernel/os.lg", "os.lg"),
    ("kernel/shell.lg", "shell.lg"),
    ("kernel/vga.lg", "vga.lg"),
    ("usr/hello_c.c", "hello_c.c"),
    ("usr/spin_c.c", "spin_c.c"),
    ("usr/busybox", "busybox"),
    ("README.md", "README.md"),
    ("build.py", "build.py"),
    (USERFS_LG, "userfs.lg"),
]


def build_selfhosted_lgc():
    subprocess.run(["lgc", "-f", "elf", "-b", "0x180000", LGC_SRC, "usr/lgc.elf"],
                   check=True, cwd=root)


def build_c_program():
    subprocess.run(["gcc", "-static", "-no-pie", "-O2", "-o", C_OUT, C_SRC],
                   check=True, cwd=root)
    subprocess.run(["gcc", "-static", "-no-pie", "-O2", "-o", SPIN_OUT, SPIN_SRC],
                   check=True, cwd=root)


def disk_layout():
    layout = []
    lba = BLOB_LBA
    addr = RAMFS_BASE
    for path, name in SLOTS:
        size = USERFS_SIZE if path == USERFS_LG else (root / path).stat().st_size
        nsect = (size + SECTOR - 1) // SECTOR
        layout.append((name, path, size, lba, nsect, addr))
        lba += nsect
        addr = (addr + size + PAGE - 1) & ~(PAGE - 1)
    name, path, size, lba, nsect, addr = layout[-1]
    if addr + size > SCRATCH_BASE:
        raise RuntimeError("RAMFS 预载区超出 0x%X，请调整布局" % SCRATCH_BASE)
    return layout


def gen_userfs(layout):
    lines = ['@import "fs.lg";', '', "func userfs_init() {"]
    for i, (name, path, size, lba, nsect, addr) in enumerate(layout):
        lines.append('    fs_preload(%d, "%s", 0x%X, %d);' % (i, name, addr, size))
    for i, (name, path, size, lba, nsect, addr) in enumerate(layout):
        lines.append('    fs_load_disk(%d, %d, %d);' % (i, lba, nsect))
    lines += ["    return 0;", "}"]
    text = "\n".join(lines) + "\n"
    if len(text) > USERFS_SIZE:
        raise RuntimeError("userfs.lg 超过 %d 字节，请调大 USERFS_SIZE" % USERFS_SIZE)
    (root / USERFS_LG).write_bytes(text.encode() + b"\n" * (USERFS_SIZE - len(text)))


def append_blobs(layout):
    with (root / IMG).open("r+b") as f:
        for name, path, size, lba, nsect, addr in layout:
            data = (root / path).read_bytes()
            f.seek(lba * SECTOR)
            f.write(data)
            f.write(b"\x00" * (nsect * SECTOR - size))


build_selfhosted_lgc()
build_c_program()

layout = disk_layout()
gen_userfs(layout)

subprocess.run(["lgc", "kernel/os.lg", IMG], check=True, cwd=root)
append_blobs(layout)

subprocess.run(["qemu-system-x86_64", "-drive", "format=raw,file=" + IMG, "-no-reboot"],
                check=True, cwd=root)
