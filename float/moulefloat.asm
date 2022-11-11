extern printf, atoi,atof, sqrt
section .data
fmt : db "%d", 10, 0
fmtf : db "%lf", 10, 0
double_0 : db 0.0
argc : dq 0
argv : dq 0
DECL_VARS

section .text
global main
main :
	push rbp
	mov [argc], rdi
	mov [argv], rsi
	INIT_VARS
	BODY
	RETURN
