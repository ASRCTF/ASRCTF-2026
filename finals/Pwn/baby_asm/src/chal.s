section .data
intro : db "This is my first ASM course, time to learn IO! What is your name?", 0xA, ">", 0
intro_len equ $ - intro
sec_line : db "Hey I heard you can also store stuff in registers! Let's give it a try", 0xA, ">", 0
sec_line_len equ $ - sec_line
outro : db "Ok bye!"
outro_len equ $ - outro


section .bss
buf : resb 20

section .text
global _start

_start:
call _main

_exit:
mov rax, 0x3c
xor rdi, rdi
syscall

_incRax:
xor rax, rax
inc al
ret

_zeroRax:
xor rax, rax
ret

_main:
mov rax, 1
mov rdi, 1
mov rsi, intro
mov rdx, intro_len
syscall

call _zeroRax
xor rdi, rdi
mov rsi, buf
mov rdx, 30
syscall

call _incRax
mov rdi, 1
mov rsi, sec_line
mov rdx, sec_line_len
syscall

sub rsp, 32
call _zeroRax
xor rdi, rdi
mov rsi, rsp
mov rdx, 0x200
syscall

call _incRax
mov rdi, 1
mov rsi, outro
mov rdx, outro_len
syscall

add rsp, 32
ret

section .note.GNU-stack noalloc noexec nowrite progbits

