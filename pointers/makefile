all: okk_exe

okk_exe: okk.o
    gcc -no-pie -fno-pie okk.o -o okk_exe

okk.o: okk.asm
    nasm -f elf64 okk.asm

#executer `$ ./okk_exe <args>`