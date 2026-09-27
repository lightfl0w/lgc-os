# lgc-os

用 [lgc](https://github.com/lightfl0w/lgc) 编译器写的 64 位微内核，设计上参考了《操作系统真相还原》。

## 结构

```
os.lg     @boot 入口
shell.lg  一个微shell
vga.lg    VGA 文本模式输出、滚动
core.lg   GDT/TSS、页表、IDT、PIC/PIT IRQ0、ring3 + syscall/sysret (Linux ABI) 与 int 0x80 系统调用
io.lg     COM1 串口和读写字节的助手
heap.lg   内核堆
fs.lg     一个简易 RAMFS
elf.lg    ELF64 加载器，按 PT_LOAD 映射
userfs.lg 由 build.py 生成，声明预加载到固定物理地址的 RAMFS 槽位
```

## 编译 && 运行

```
python ./build.py
```

## 系统调用

主路径走 `syscall`/`sysret` 指令，兼容Linux x86-64 ABI

| nr | 名称 | 参数 | 返回 |
|----|------|------|------|
| 0  | read | rdi = fd, rsi = buf, rdx = count | 读取字节数 |
| 1  | write | rdi = fd, rsi = buf, rdx = count | 写入字节数 |
| 2  | open | rdi = path, rsi = flags, rdx = mode | fd |
| 3  | close | rdi = fd | 0 |
| 60 / 231 | exit / exit_group | rdi = 退出码 | 不返回 |

- 出错返回负 errno：`-2` ENOENT、`-9` EBADF、`-28` ENOSPC

未知编号返回 `-38` (ENOSYS)。

| nr | 名称 | 参数 | 返回 |
|----|------|------|------|
| 0  | putc | rdi = 字符 | 0 |
| 1  | exit | rdi = 退出码 | 不返回 |
| 2  | puts | rdi = 字符串指针 | 0 |

未知编号返回 -1

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
- [ ] 调度策略（时间片/优先级）