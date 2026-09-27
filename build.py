import os, subprocess, pathlib

root = pathlib.Path(__file__).parent

BLOB_BASE = 0x800000
SLOT_STRIDE = 0x10000

LGC_SRC = os.environ.get("LGC_SRC", "/root/compiler/src/lgc.lg")

SLOTS = [
    ("lgc.elf", "usr/lgc.elf"),
    ("a.lg", "usr/a.lg"),
]


def build_selfhosted_lgc():
    subprocess.run(["lgc", "-f", "elf", "-b", "0x180000", LGC_SRC, "usr/lgc.elf"],
                   check=True, cwd=root)


def gen_userfs():
    lines = ['@import "fs.lg";', '', "func userfs_init() {"]
    for i, (name, path) in enumerate(SLOTS):
        size = (root / path).stat().st_size
        lines.append('    fs_preload(%d, "%s", %d);' % (i, name, size))
    lines += ["    return 0;", "}"]
    (root / "kernel/userfs.lg").write_text("\n".join(lines) + "\n")


def qemu_cmd():
    cmd = ["qemu-system-x86_64", "-drive", "format=raw,file=lgc-os.img"]
    for i, (name, path) in enumerate(SLOTS):
        addr = BLOB_BASE + i * SLOT_STRIDE
        cmd += ["-device", "loader,file=%s,addr=0x%x,force-raw=on" % (path, addr)]
    cmd += ["-no-reboot"]
    return cmd


build_selfhosted_lgc()
gen_userfs()

subprocess.run(["lgc", "kernel/os.lg", "lgc-os.img"], check=True, cwd=root)

subprocess.run(qemu_cmd(), check=True, cwd=root)
