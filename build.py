import subprocess, sys, pathlib

root = pathlib.Path(__file__).parent

subprocess.run([sys.executable, "tools/mkelf.py",
                "RING3!", "0x180000", "usr/hello.elf",
                "kernel/usrelf.lg", "42"], check=True, cwd=root)

subprocess.run(["lgc", "kernel/os.lg", "lgc-os.img"], check=True, cwd=root)

subprocess.run(["qemu-system-x86_64", "-drive", "format=raw,file=lgc-os.img",
                "-no-reboot"], check=True, cwd=root)