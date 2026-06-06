.text
.global __x86_return_thunk
.type __x86_return_thunk, @function
__x86_return_thunk:
    pop %r11
    jmp *%r11
.size __x86_return_thunk, .-__x86_return_thunk
