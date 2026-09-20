# lgc-os

用 [lgc](../compiler) 编译器编写的最小裸金属操作系统内核（x86-64 长模式），
借鉴《操作系统真相还原》(`/root/k`) 的设计，但目标是 64 位（`/root/k` 是 32 位，lgc 只生成 64 位码，无法直接移植）。

## 结构

```
kernel/kernel.lg   内核：串口(COM1) + VGA文本输出 + 算术验证
build.sh           用 lgc 把 kernel.lg 编成可引导磁盘镜像 lgc-os.img
lgc-os.img         产物：512B 引导扇区 + N 个内核扇区
```

## 引导流程（复用 lgc 的 @boot）

lgc 的 `@boot` 模式把内置 stage1(`main.c` 里的 `BOOT_SEC`) 与内核拼成一个磁盘镜像：
1. stage1 实模式读盘 → 保护模式 → 长模式；
2. 内核加载到 `0x100000`，stage1 `jmp` 到入口 `main`；
3. stage1 读盘扇区数按内核实际大小自动计算（见 lgc `write_bin`）。

## 运行

需要 qemu：
```
qemu-system-x86_64 -drive format=raw,file=lgc-os.img -serial stdio -nographic
```
预期串口输出：`lgc-os boot: serial ok`、`sum(0..9)=5`。

## 现状 / 待办

- [x] 长模式裸金属内核、编译为可引导镜像
- [x] 串口字符/字符串输出、VGA 文本输出
- [ ] GDT/IDT 与中断/异常 ISR（需确认 lgc 里如何取函数地址填 IDT）
- [ ] 8253 timer (IRQ0)、8042 键盘
- [ ] 页表与开启分页、内核堆
- [ ] 多任务（TSS / 上下文切换）
- [ ] 若要让自举版 `build/lgc` 也能编译内核：需把 for/switch/struct/enum/print 移植进 `src/lgc.lg`

注意：本环境无 qemu，镜像仅通过编译与字节布局校验，未实机启动验证。
