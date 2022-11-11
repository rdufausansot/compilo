from logging.config import IDENTIFIER
import lark

grammaire = lark.Lark(r"""
exp : SIGNED_NUMBER                                                          -> exp_nombre
| IDENTIFIER                                                                 -> exp_variable
| exp OPBIN exp                                                              -> exp_opbin
| "(" exp ")"                                                                -> exp_par
| "*" IDENTIFIER                                                          -> ptr_dereference
| "*" "*" IDENTIFIER                                                      -> ptr_to_ptr_deref
| "*" "("IDENTIFIER /[+-]/ SIGNED_NUMBER ")"                              -> ptr_deref_op
| "&" IDENTIFIER                                                          -> value_adress
com : IDENTIFIER "=" exp ";"                                                 -> assignation
| "*" IDENTIFIER "=" exp ";"                                              -> assign_value_at_ptr
| "*""*" IDENTIFIER "=" exp ";"                                           -> ptr_to_ptr_assign
| "*" "("IDENTIFIER /[+-]/ SIGNED_NUMBER ")" "=" exp ";"                  -> ptr_deref_op_assign
| IDENTIFIER "=" "malloc" "(" SIGNED_NUMBER ")" ";"                       -> malloc
| "if" "(" exp ")" "{" bcom "}"                                              -> if
| "while" "(" exp ")" "{" bcom "}"                                           -> while
| "print" "(" ")"                                                            -> print
bcom : (com)*                                                                -> command_block
prg : "main" "(" var_list ")" "{" bcom "return" "(" exp ")" ";" "}"          -> program
var_list :                                                                   -> vide
| IDENTIFIER ("," IDENTIFIER)*                                               -> aumoinsune
IDENTIFIER : /[a-zA-Z][a-zA-Z0-9]*/
OPBIN : /[+\-*>]/
%import common.WS
%import common.SIGNED_NUMBER
%ignore WS
""", 
start="prg")

###expressions
op = {'+' : 'add', '-' : 'sub'}

def asm_exp(e):
    if e.data == "exp_nombre":
        return f"mov rax, {e.children[0].value}"
    elif e.data == "exp_variable":
        return f"mov rax, [{e.children[0].value}]"
    elif e.data == "exp_par":
        return asm_exp(e.children[0])
    elif e.data == "value_adress":
        return f"mov rax, {e.children[0].value}"
    elif e.data == "ptr_dereference":
        return f"""mov rax, [{e.children[0].value}]
        push rax
        pop rbx
        mov rax, [rbx]
        """
    elif e.data == "ptr_deref_op":
        P = e.children[0].value
        OPBIN = op[e.children[1].value]
        nb = int(e.children[2])*8
        return f"""
        mov rax, {nb}
        push rax
        mov rax, [{P}]
        pop rbx
        {OPBIN} rax, rbx
        mov rbx, rax

        mov rax, [rbx]
        """
    elif e.data == "ptr_to_ptr_deref":
        P = e.children[0].value
        return f"""
        mov rbx, [{P}]
        mov rax, [rbx]
        push rax
        pop rbx
        mov rax, [rbx]
        """
    else:
        E1 = asm_exp(e.children[0])
        E2 = asm_exp(e.children[2])
        return f"""
        {E2}
        push rax
        {E1}
        pop rbx
        {op[e.children[1].value]} rax, rbx 
        """

def pp_exp(e):
    if e.data == "exp_nombre":
        return e.children[0].value
    elif e.data == "exp_variable":
        return e.children[0].value
    elif e.data == "exp_par":
        return f"({pp_exp(e.children[0])})"
    elif e.data == "ptr_dereference":
        return f"*{e.children[0].value}"
    elif e.data == "ptr_deref_op":
        return f"*({e.children[0].value} {e.children[1].value} {e.children[2].value})"
    elif e.data == "ptr_to_ptr_deref":
            return f"**{e.children[0].value}"
    elif e.data == "value_adress":
        return f"&{e.children[0].value}"
    else:
        return f"{pp_exp(e.children[0])} {e.children[1].value} {pp_exp(e.children[2])}"

def vars_exp(e):
    if e.data == "exp_nombre":
        return set()
    elif e.data == "exp_variable":
        return {e.children[0].value}
    elif e.data == "exp_par":
        return vars_exp(e.children[0])
    elif e.data == "value_adress":
        return {e.children[0].value}
    elif e.data == "ptr_dereference":
        return {e.children[0].value}
    elif e.data == "ptr_deref_op":
        return {e.children[0].value}
    elif e.data == "ptr_to_ptr_deref":
        return {e.children[0].value}
    else:
        L = vars_exp(e.children[0])
        R = vars_exp(e.children[2])
        return L | R #union
####################

###commandes
cpt = 0
def next():
    global cpt
    cpt += 1
    return cpt

def asm_com(c):
    if c.data == "assignation":
        E = asm_exp(c.children[1])
        return f"""
        {E}
        mov [{c.children[0].value}], rax
        """
    elif c.data == "if":
        E = asm_exp(c.children[0])
        C  = asm_bcom(c.children[1])
        n = next()
        return f"""
        {E}
        cmp rax, 0
        jz fin{n}
        {C}
fin{n} : nop
"""
    elif c.data == "while":
        E = asm_exp(c.children[0])
        C = asm_bcom(c.children[1])
        n = next()
        return f"""
debut{n} : {E}
        cmp rax, 0
        jz fin{n}
        {C}
        jmp debut{n}
fin{n} : nop
"""
    elif c.data == "print":
        E = asm_exp(c.children[0])
        return f"""
        {E}
        mov rdi, fmt
        mov rsi, rax
        call printf
        """
    elif c.data == "assign_value_at_ptr":
        P = c.children[0].value
        E = asm_exp(c.children[1])
        return f"""
        {E}
        push rax
        mov rax, [{P}]
        pop rbx
        mov [rax], rbx
        """
    elif c.data == "malloc":
        P = c.children[0].value
        E = int(c.children[1].value)*8
        return f"""
        mov rax, {E}
        mov rdi, rax
        extern malloc
        call malloc
        mov [{P}], rax
        """
    elif c.data == "ptr_deref_op_assign":
        P = c.children[0].value
        OPBIN = c.children[1].value
        nb = int(c.children[2])*8
        E = asm_exp(c.children[3])
        return f"""
        {E}
        push rax

        mov rax, {nb}
        push rax
        mov rax, [{P}]
        pop rbx
        {op[OPBIN]} rax, rbx
        
        pop rbx
        mov [rax], rbx
        """
    elif c.data == "ptr_to_ptr_assign":
        P = c.children[0].value
        E = asm_exp(c.children[1])
        return f"""
        {E}
        push rax
        mov rbx, [{P}]
        mov rax, [rbx]
        pop rbx
        mov [rax], rbx
        """

def pp_com(c):
    if c.data == "assignation":
        return f"{c.children[0]} = {pp_exp(c.children[1])};"
    elif c.data == "if":
        x = f"\n    {pp_bcom(c.children[1], 1)}\n"
        return f"if ({pp_exp(c.children[0])}) {{{x}}}" #{{{ triple accolade pour afficher des accolades en formatage}}}
    elif c.data == "while":
        x = f"\n    {pp_bcom(c.children[1], 1)}\n"
        return f"while ({pp_exp(c.children[0])}) {{{x}}}" #{{{ triple accolade pour afficher des accolades en formatage}}}
    elif c.data == "print":
        return f"print({pp_exp(c.children[0])})"
    elif c.data == "assign_value_at_ptr":
        return f"*{c.children[0].value} = {pp_exp(c.children[1])};"
    elif c.data == "malloc":
        return f"{c.children[0].value} = malloc({c.children[1].value});"
    elif c.data == "ptr_deref_op_assign":
        return f"*({c.children[0].value} {c.children[1].value} {c.children[2].value}) = {pp_exp(c.children[3])} ;"
    elif c.data == "ptr_to_ptr_assign":
        return f"**{c.children[0].value} = {pp_exp(c.children[1])};"

def vars_com(c):
    if c.data == "assignation":
        R = vars_exp(c.children[1])
        return {c.children[0].value} | R
    elif c.data in {"if", "while"}:
        B = vars_bcom(c.children[1])
        E = vars_exp(c.children[0])
        return E | B
    elif c.data == "print":
        return vars_exp(c.children[0])
    elif c.data == "assign_value_at_ptr":
        R = vars_exp(c.children[1])
        return {c.children[0].value} | R
    elif c.data == "malloc":
        return {c.children[0].value}
    elif c.data == "ptr_deref_op_assign":
        R = vars_exp(c.children[3])
        return {c.children[0].value} | R
    elif c.data == "ptr_to_ptr_assign":
        R = vars_exp(c.children[1])
        return {c.children[0].value} | R
####################

###blocs de commandes
def asm_bcom(bc):
    return "\n" + "".join([asm_com(c) for c in bc.children]) + "\n"

def pp_bcom(bc, in_com= 0):
    if in_com == 1:
        return "\n    ".join([pp_com(c) for c in bc.children])
    else:
        return "\n".join([pp_com(c) for c in bc.children])

def vars_bcom(bc):
    S = set()
    for c in bc.children:
        S = S | vars_com(c)
    return S
####################

def pp_var_list(vl):
    return ", ".join([t.value for t in vl.children])

###programme
def asm_prg(p):
    f = open("moule.asm")
    moule = f.read()
    C = asm_bcom(p.children[1])
    moule = moule.replace("BODY", C)
    R = asm_exp(p.children[2])
    moule = moule.replace("RETURN", R)
    D = "\n".join([f"{v} : dq 0" for v in vars_prg(p)])
    moule = moule.replace("DECL_VARS", D)
    s = ""
    for i in range(len(p.children[0].children)):
        v = p.children[0].children[i].value
        e = f"""
        mov rbx, [argv]
        mov rdi, [rbx + {8*(i+1)}]
        xor rax, rax
        call atoi
        mov [{v}], rax
        """
        s = s + e
    moule = moule.replace("INIT_VARS", s)
    return moule

def pp_prg(p):
    L = pp_var_list(p.children[0])
    C = pp_bcom(p.children[1])
    R = pp_exp(p.children[2])
    return "main (%s) {\n%s \n\nreturn (%s);\n}" % (L, C, R)

def vars_prg(p):
    L = set([t.value for t in p.children[0].children])
    C = vars_bcom(p.children[1])
    R = vars_exp(p.children[2])
    return L | C | R
####################



ast = grammaire.parse(
    """
main(x, y){
    x = 5;
    y = 9;

    p = malloc(4);
    *p = 1;
    *(p+1) = 2;
    *(p+2) = y;    

    return(*(p+2));
}
""")

print(ast)
print(pp_prg(ast))

asm = asm_prg(ast)
f = open("okk.asm", "w")
f.write(asm)
f.close()