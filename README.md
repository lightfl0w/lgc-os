# lgc-os

用 lgc 编译器编写的微操作系统内核，
借鉴《操作系统真相还原》的设计，但目标是 64 位。

## 结构

```
kernel/kernel.lg   IDT + PIT/PIC IRQ0 定时器
kernel/apic.lg     本地 APIC 定时器（自建页表映射 MMIO）
kernel/high.lg     高半区内核（双映射 + 高位入口跳板）
build.sh
lgc-os.img         产物
```

## 运行

```
qemu-system-x86_64 -drive format=raw,file=lgc-os.img -display none -serial stdio -no-reboot
```

## 已实现能力

- 串口 `outb/inb` 输出、VGA 文本写。
- IDT + 中断：软件中断 `int 0x20` 进 handler、`iretq` 返回。
- **8253 PIT + 8259 PIC 的 IRQ0 硬件定时中断**（`kernel/kernel.lg`）：`sti` 后 tick 自动走表，实测每秒 +1000。
- **本地 APIC 定时器**（`kernel/apic.lg`）：内核自建页表映射 `0xFEE00000`、`wrmsr` 使能 LAPIC、LVT 周期模式，tick 经 vector 自增。
- **高半区内核 / 双映射**（`kernel/high.lg`）：`map_high()` 在保留恒等低映射（`PML4[0]`）的同时，把 `0xFFFFFFFF80000000` 经 `PML4[511]→PDPT_HI[510]→PD_HI[0]`（2MB 大页映射物理 `0x0`）映到内核物理基址

## 现状 / 待办

- [x] 长模式裸金属内核、编译为可引导镜像
- [x] 串口/VGA 输出
- [x] IDT + 软件中断 ISR（addr/naked 支持）
- [x] 8253 PIT + PIC IRQ0 硬件定时中断（tick 走表，qemu 实测）
- [x] 本地 APIC 定时器（内核自建页表映射 APIC MMIO，qemu 实测走表）
- [x] 修复 freestanding 下寄存器常驻全局导致 ISR 写丢失
- [x] 高半区内核（双映射 + 高位入口跳板，qemu 实测在 `0xFFFFFFFF801005xx` 运行）
- [ ] IO-APIC（把 IRQ 经 IO-APIC 重定向，配合本地 APIC）
- [ ] 8042 键盘（IRQ1）
- [ ] 内核堆、多任务（TSS/上下文切换）