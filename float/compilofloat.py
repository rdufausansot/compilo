import lark
grammaire = lark.Lark(r"""
exp : SIGNED_NUMBER  -> exp_nombre
|IDENTIFIER_INT          -> exp_variable_int
|IDENTIFIER_FLOAT          -> exp_variable_float
|exp OPBIN exp       -> exp_opbin
|"(" exp ")"         -> exp_par
|SIGN SIGNED_NUMBER SEP (SIGNED_NUMBER)* -> exp_float
|"sqrt("exp")"  ->sqrt

com : IDENTIFIER_INT "=" exp ";"      -> assignation_int
|IDENTIFIER_FLOAT "=" exp ";"         -> assignation_float
|"if" "(" exp ")" "{" bcom "}"    -> if
|"while" "(" exp ")" "{" bcom "}" ->  while
|"print" "(" exp ")" ";"              -> print

bcom : (com)*
prg : "main" "(" var_list ")" "{" bcom  "return"  exp"}"

var_list :                      -> vide
| IDENTIFIER_FLOAT ("," IDENTIFIER_INT)* ("," IDENTIFIER_FLOAT)* -> aumoinsunevariable_float
| IDENTIFIER_INT ("," IDENTIFIER_INT)* ("," IDENTIFIER_FLOAT)* -> aumoinsvariable_int


IDENTIFIER_FLOAT : /[f][a-zA-Z0-9]*/
IDENTIFIER_INT : /[i][a-zA-Z0-9]*/

SIGN : /[+\-]/

SEP : /[.]/

OPBIN : /[+\-*>]/

%import common.WS
%ignore WS
%import common.SIGNED_NUMBER
""",
start="prg")

op_int = {'+' : 'add' , '-' : 'sub', '*' : 'imul', '>' : 'cmp'}
op_float = {'+' : 'addsd' , '-' : 'subsd' , '*' : 'mulsd', '>' : 'ucomisd'}

list_float = ""


def pp_exp(e):
	if e.data == "exp_nombre":
		return e.children[0].value

	elif e.data == "exp_variable_float":
		return e.children[0].value

	elif e.data == "exp_variable_int":
		return e.children[0].value

	elif e.data == "exp_par":
		return f"({pp_exp(e.children[0])})"
	elif e.data == "sqrt":
		return f"sqrt({pp_exp(e.children[0])})"

	elif e.data == "exp_opbin":
		return f"{pp_exp(e.children[0])} {e.children[1].value} {pp_exp(e.children[2])}"
	elif e.data == "exp_float":
		nbrc = len(e.children)
		n = "".join(e.children[i].value for i in range(3,nbrc))
		if e.children[0].value == "+":
			return f"{e.children[1].value}{e.children[2].value}{n}"
		else:
			return f"{e.children[0]}{e.children[1].value}{e.children[2].value}{n}"


def vars_exp(e):
	if e.data == "exp_nombre":
		return set()
	elif e.data == "exp_float":
		return set()
	elif e.data == "exp_variable_float":
		return  {e.children[0].value}
	elif e.data == "exp_variable_int":
		return {e.children[0].value}
	elif e.data == "exp_par":
		return vars_exp(e.children[0])
	elif e.data == "sqrt":
		return vars_exp(e.children[0])
	else:
		L = vars_exp(e.children[0])
		R = vars_exp(e.children[2])
		return L | R


def asm_exp(e):
	global list_float
	if e.data == "exp_nombre":
		return f"mov rax, {e.children[0].value}\n"

	elif e.data == "exp_float":
		nbrc = len(e.children)
		n = "".join(e.children[i].value for i in range(3,nbrc))
		if e.children[0].value == "+":
			list_float = list_float + f"double_{e.children[1].value}{e.children[2].value}{n} : dq {e.children[1].value}{e.children[2].value}{n}\n"
			return f"movsd xmm0, qword [double_{e.children[1].value}{e.children[2].value}{n}]\n"
		else:
			list_float = list_float + f"double__{e.children[1].value}{e.children[2].value}{n} : dq {e.children[0]}{e.children[1].value}{e.children[2].value}{n}\n"
			return f"movsd xmm0, qword [double__{e.children[1].value}{e.children[2].value}{n}]\n"

	elif e.data == "exp_variable_int":
		return f"mov rax, [{e.children[0].value}]\n"

	elif e.data == "exp_variable_float":
		return f"movsd xmm0, qword [{e.children[0].value}]\n"

	elif e.data == "exp_par":
		return asm_exp(e.children[0])

	elif e.data == "sqrt":
		if is_float(e.children[0]):
			E = asm_exp(e.children[0])
			return f"""
			{E}
			call sqrt
			"""
		else:
			E = asm_exp(e.children[0])
			return f"""
			{E}
			cvtsi2sd xmm0, rax
			call sqrt
			"""
	elif e.data == "exp_opbin":
		E1 = asm_exp(e.children[0])
		E2 = asm_exp(e.children[2])
		if is_float(e) :
			if (is_float(e.children[0]) and is_float(e.children[2])):
				return f"""
				{E2}
				movsd xmm1, xmm0
				{E1}
				{op_float[e.children[1].value]} xmm0, xmm1
				"""
			elif is_float(e.children[0]):
				return f"""
				{E2}
				cvtsi2sd xmm1, rax
				{E1}
				{op_float[e.children[1].value]} xmm0, xmm1
				"""
			elif is_float(e.children[2]):
				return f"""
				{E2}
				{E1}
				cvtsi2sd xmm1, rax
				{op_float[e.children[1].value]} xmm0, xmm1
				"""
		else:
			if e.children[1].value == "*":
				return f"""
				{E2}
				push rax
				{E1}
				pop rbx
				imul rax, rax, rbx
				"""
			else:
				return f"""
				{E2}
				push rax
				{E1}
				pop rbx
				{op_int[e.children[1].value]} rax, rbx
				"""





def is_float(e):
	if e.data == "exp_nombre":
		return False
	elif e.data == "exp_float":
		return True
	elif e.data == "exp_variable_int":
		return False
	elif e.data == "exp_variable_float":
		return True
	elif e.data == "sqrt":
		return  True
	elif e.data == "exp_par":
		return is_float(e.children[0])
	elif e.data == "exp_opbin":
		return (is_float(e.children[0]) or is_float(e.children[2]))

def pp_float_to_int(e):
		if e.data == "exp_float":
			if e.children[0].value == '+':
				return f"{e.children[1].value}"
			else:
				return f"{e.children[0]}{e.children[1].value}"
		elif e.data == "exp_variable_float":
			return pp_exp(e)
		elif e.data == "exp_par":
			return f"({pp_float_to_int(e.children[0])})"
		elif e.data == "sqrt":
			return f"sqrt({pp_float_to_int(e.children[0])})"
		elif e.data == "exp_opbin":
			return f"{pp_float_to_int(e.children[0])} {e.children[1].value} {pp_float_to_int(e.children[2])}"

def pp_int_to_float(e):
	if e.data == "exp_nombre":
			return f"{e.children[0].value} .0"
	elif e.data == "exp_variable_int":
		return pp_exp(e)
	elif e.data  == "exp_par":
		return f"({pp_int_to_float(e.children[0])})"
	elif e.data == "sqrt":
		return f"sqrt({pp_int_to_float(e.children[0])})"
	elif e.data == "exp_opbin":
		return f"{pp_int_to_float(e.children[0])} {e.children[1].value} {pp_int_to_float(e.children[2])}"

def pp_com(c):
	if c.data == "assignation_int":
		if is_float(c.children[1]):
			return f"{c.children[0].value} = {pp_float_to_int(c.children[1])};"
		else:
			return f"{c.children[0].value} = {pp_exp(c.children[1])};"
	if c.data == "assignation_float":
		if is_float(c.children[1]):
			return f"{c.children[0].value} = {pp_exp(c.children[1])};"
		else:
			return f"{c.children[0].value} = {pp_int_to_float(c.children[1])};"

	elif c.data == "if":
		x = f"\n{pp_bcom(c.children[1])}"
		return f"if ({pp_exp(c.children[0])}) {{{x}}}"
	elif c.data == "while":
		x = f"\n{pp_bcom(c.children[1])}\n"
		return f"while ({pp_exp(c.children[0])}) {{{x}}}"
	elif c.data == "print":
		return f"print({pp_exp(c.children[0])})"
cpt = 0
def next():
	global cpt
	cpt += 1
	return cpt

def asm_com(c):
	if c.data == "assignation_int":
		E = asm_exp(c.children[1])
		if not(is_float(c.children[1])):
			return f"""
			{E}
			mov [{c.children[0].value}],rax
			"""
		else:
			return f"""
			{E}
			cvttsd2si rax, xmm0
			mov [{c.children[0].value}],rax
			"""
	elif c.data == "assignation_float":
		E = asm_exp(c.children[1])
		if is_float(c.children[1]):
			return f"""
			{E}
			movsd [{c.children[0].value}],xmm0
			"""
		else:
			return f"""
			{E}
			cvtsi2sd xmm0, rax
			movsd [{c.children[0].value}],xmm0
			"""
	elif c.data == "if":
		E = asm_exp(c.children[0])
		C = asm_bcom(c.children[1])
		if is_float(c.children[0]):
			n = next()
			return f"""
			{E}
			jbe fin{n}
			{C}
	fin{n} : nop
	"""
		else:
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
		if is_float(c.children[0]):
			n = next()
			return f"""
			debut{n}: {E}
			jbe fin{n}
			{C}
			jmp debut{n}
	fin{n} : nop
	"""
		else:
			n = next()
			return f"""
			debut{n}: {E}
			cmp rax, 0
			jz fin{n}
			{C}
			jmp debut{n}
	fin{n} : nop
	"""
	elif c.data == "print":
		E = asm_exp(c.children[0])
		if is_float(c.children[0]):
			return f"""
			mov rdi, fmtf
			{E}
			mov rax, 1
			call printf
			"""
		else:
			return f"""
			mov rdi, fmt
			{E}
			mov rsi, rax
			call printf
			"""

def vars_com(c):
	if c.data in {"assignation_float", "assignation_int"}:
		R = vars_exp(c.children[1])
		return {c.children[0].value} | R
	elif c.data in {"if" , "while"}:
		B = vars_bcom(c.children[1])
		E = vars_exp(c.children[0])
		return E | B
	elif c.data == "print":
		return vars_exp(c.children[0])




def asm_bcom(bc):
	return "".join([asm_com(c) for c in bc.children])

def pp_bcom(bc):
	return "\n".join([pp_com(c) for c in bc.children])

def vars_bcom(bc):
	S = set()
	for c in bc.children:
		S = S | vars_com(c)
	return S




def pp_prg(p):
	var = f"{pp_var_list(p.children[0])}"
	bloc =  f"\n{pp_bcom(p.children[1])}"
	res = f"{pp_exp(p.children[2])}"
	return f"main( {var} ) {bloc} \nreturn {res} "

def asm_prg(p):
	f = open("moulefloat.asm")
	moule = f.read()
	C = asm_bcom(p.children[1])
	moule = moule.replace("BODY",C)
	E = asm_exp(p.children[2])
	if is_float(p.children[2]):
		R = f"""
		mov rdi, fmtf
		{E}
		mov rax,1
		call printf
		pop rbp
		ret
		"""
		moule = moule.replace("RETURN",R)
	else:
		R = f"""
		mov rdi, fmt
		{E}
		mov rsi, rax
		call printf
		pop rbp
		ret
		"""
		moule = moule.replace("RETURN",R)
	D ="\n".join([f"{v} : dq 0" for v in vars_prg(p)])
	global list_float
	moule = moule.replace("DECL_VARS",D + "\n" + list_float)
	s = ""
	for i in range(len(p.children[0].children)):
		v = p.children[0].children[i].value
		if p.children[0].children[i][0] == "i":
			e = f"""
			mov rbx, [argv]
			mov rdi, [rbx + {8 * (i +1)}]
			xor rax, rax
			call atoi
			mov [{v}], rax
			"""
			s = s  + e
		else:
			e=f"""
			mov rbx, [argv]
			mov rdi, [rbx + {8 * (i+1)}]
			xorps xmm0, xmm0
			call atof
			movsd [{v}], xmm0
			"""
			s = s + e
	moule = moule.replace("INIT_VARS", s)
	return moule

def vars_prg(p):
	L = set([t.value for t in p.children[0].children])
	C = vars_bcom(p.children[1])
	R = vars_exp(p.children[2])
	return L | C |R


def pp_var_list(vl):
	return ", ".join([v.value for v in vl.children])

ast = grammaire.parse("""main(fx){
	if(fx > 10){
		print(fx);
	}
	if(fx > 20){
		print(fx);
	}
	return fx
}
""")

#test = grammaire.parse("-3")

print(pp_prg(ast))
asm = asm_prg(ast)
f = open("ouf.asm" , "w")
f.write(asm)
f.close()
