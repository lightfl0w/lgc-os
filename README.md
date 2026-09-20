# lgc-os

用 lgc 编译器编写的微操作系统内核，
借鉴《操作系统真相还原》的设计，但目标是 64 位。

## 结构

```
kernel/kernel.lg  
build.sh          
lgc-os.img         产物
```

## 运行

```
qemu-system-x86_64 -drive format=raw,file=lgc-os.img -display none -serial stdio -no-reboot
```

## 已实现能力

- 串口 `outb/inb` 输出、VGA 文本写。
- IDT：软件中断 `int 0x20` 进 handler、`iretq` 返回、全局 `ticks` 跨中断累加。

## 现状 / 待办

- [x] 长模式裸金属内核、编译为可引导镜像
- [x] 串口字符/字符串输出、VGA 文本输出
- [x] IDT + 软件中断 ISR（addr/naked 支持）
- [ ] 硬件中断：8253 timer (IRQ0)、8042 键盘（需重映射 PIC + 完整寄存器保存）
- [ ] 修复 naked 中 15 寄存器保存导致全局写丢失的 bug
- [ ] 页表与开启分页、内核堆
- [ ] 多任务（TSS / 上下文切换）
