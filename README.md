# lgc-os

用 [lgc](https://github.com/lightfl0w/lgc) 编译器写的 64 位微内核，设计上参考了《操作系统真相还原》。

## 结构

```
os.lg     @boot 入口
shell.lg  一个微shell
vga.lg    VGA 文本模式输出、滚动
core.lg   GDT/TSS、页表、IDT、PIC/PIT IRQ0、ring3 + syscall/sysret (Linux ABI) 与 int 0x80 系统调用
io.lg     COM1 串口和读写字节的助手
ata.lg    ATA PIO 读写扇区，开机把用户程序与源码从磁盘载入 RAMFS
heap.lg   内核堆
fs.lg     一个简易 RAMFS
elf.lg    ELF64 加载器，按 PT_LOAD 映射
userfs.lg 由 build.py 生成
```

## 编译 && 运行

需要 `lgc`、`gcc` 与 `qemu-system-x86_64`。

```
LGC_SRC=/path/to/自举版/lgc.lg python ./build.py
```

## 磁盘布局

| LBA | 内容 |
|----|----|
| 0 | 引导扇区（BIOS 载入内核） |
| 1 - 127 | 内核（lgc `@boot` 输出） |
| 256 起 | 各文件按 512 字节对齐依次排布 |

## 内存布局（16MB）

| 物理地址 | 用途 |
|----|----|
| 0x000000 - 0x180000 | 内核代码/数据/页表 |
| 0x180000 - 0x200000 | ring3 用户代码窗口（RWX，4KB 页） |
| 0x200000 - 0x400000 | 空闲 |
| 0x400000 - 0x600000 | C 程序镜像（glibc 静态链接默认基址） |
| 0x600000 向下增长 | 用户初始栈（argc/argv/envp/auxv） |
| 0x800000 - 0xA00000 | RAMFS 预载文件（程序 + 源码，紧凑排布） |
| 0xA00000 - 0xC00000 | RAMFS 运行时新建的文件（编译器输出等） |
| 0xC00000 - 0x1000000 | mmap bump 区 |

## 运行 C 程序

内核没有动态链接器，因此只支持静态、非 PIE的 ELF：

```
gcc -static -no-pie -O2 -o usr/hello_c usr/hello_c.c
```

## 系统调用

主路径走 `syscall`/`sysret` 指令，兼容 Linux x86-64 ABI

| nr | 名称 | 参数 | 返回 |
|----|------|------|------|
| 0  | read | rdi = fd, rsi = buf, rdx = count | 读取字节数 |
| 1  | write | rdi = fd, rsi = buf, rdx = count | 写入字节数 |
| 2  | open | rdi = path, rsi = flags, rdx = mode | fd |
| 3  | close | rdi = fd | 0 |
| 5  | fstat | rdi = fd, rsi = statbuf | 0 |
| 9  | mmap | rsi = len, r10 = flags（仅匿名） | 地址 |
| 10 | mprotect | — | 0（占位） |
| 11 | munmap | — | 0（占位） |
| 12 | brk | rdi = 新末尾 | 当前末尾 |
| 16 | ioctl | — | -25 (ENOTTY) |
| 60 / 231 | exit / exit_group | rdi = 退出码 | 不返回 |
| 158 | arch_prctl | rdi = code, rsi = addr | 0 |
| 218 | set_tid_address | rdi = tidptr | 1 |
| 262 | newfstatat | rsi = statbuf | 0 |
| 267 | readlinkat | — | -2 (ENOENT) |
| 273 | set_robust_list | — | 0 |
| 302 | prlimit64 | rdx = old_limit | 0 |
| 318 | getrandom | rdi = buf, rsi = len | 写入字节数 |

- 出错返回负 errno：`-2` ENOENT、`-12` ENOMEM、`-22` EINVAL、`-25` ENOTTY、`-28` ENOSPC
- 未实现的编号返回 `-38` (ENOSYS)

## 自举测试

```
python build.py          
tools/selfhost_test.sh    
```

## 待办

- [x] ELF 文件放进 RAMFS，loader 经 VFS 读取加载
- [x] 用户态 ring3 + 系统调用（int 0x80）
- [x] syscall/sysret 系统调用，兼容 Linux x86-64 ABI（read/write/exit）
- [x] 各 demo 合并成单一 @import 内核
- [x] 加载真实 ELF 文件（usr/hello.elf 嵌进镜像，不是运行时现算）
- [x] ring0 命令 shell（内建命令 + exec 跑 ELF）
- [x] 输出改到 VGA 画面 + PS/2 键盘输入（串口降级做测试回退）
- [x] exec 后进程 exit 返回 shell
- [x] 在 lgc-os 内运行自举版 lgc 编译器并编译源码
- [x] 运行静态链接的 glibc C 程序（auxv/envp 初始栈、brk/mmap、SSE）
- [x] 自包含镜像
- [x] 自举往返
- [ ] 调度策略（时间片/优先级）
- [ ] 动态链接（PT_INTERP / ld.so）
