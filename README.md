# lgc-os

用 [lgc](https://github.com/lightfl0w/lgc) 编译器写的 64 位微内核，设计上参考了《操作系统真相还原》。

## 结构

```
os.lg     @boot 入口，初始化完进 shell
shell.lg  ring0 命令 shell（REPL + 几个内建命令）
vga.lg    VGA 文本模式(0xB8000)输出、滚动、光标，外加 PS/2 键盘轮询
core.lg   GDT/TSS、页表、IDT、PIC/PIT IRQ0、ring3 + int 0x80 系统调用
io.lg     COM1 串口和读写字节的助手
heap.lg   内核堆，bump + first-fit，相邻块合并
fs.lg     一个简易 RAMFS
elf.lg    ELF64 加载器，按 PT_LOAD 映射
usrelf.lg 由 tools/mkelf.py 从 usr/hello.elf 生成
```

## 运行

```
qemu-system-x86_64 -drive format=raw,file=lgc-os.img -no-reboot
```

## 系统调用

`int 0x80`：`rax` = 编号，`rdi` / `rsi` / `rdx` = 参数，返回值回写 `rax`。

| nr | 名称 | 参数 | 返回 |
|----|------|------|------|
| 0  | putc | rdi = 字符 | 0 |
| 1  | exit | rdi = 退出码 | 不返回，回 shell |
| 2  | puts | rdi = 字符串指针 | 0 |

未知编号返回 -1。`exit` 从 ring3 切回 ring0 的 `exec_resume`，恢复内核栈顶

## 待办

- [x] ELF 文件放进 RAMFS，loader 经 VFS 读取加载
- [x] 用户态 ring3 + 系统调用（int 0x80）
- [x] 各 demo 合并成单一 @import 内核
- [x] 加载真实 ELF 文件（usr/hello.elf 嵌进镜像，不是运行时现算）
- [x] ring0 命令 shell（内建命令 + exec 跑 ELF）
- [x] 输出改到 VGA 画面 + PS/2 键盘输入（串口降级做测试回退）
- [x] exec 后进程 exit 返回 shell
- [ ] 调度策略（时间片/优先级）