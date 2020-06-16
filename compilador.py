import re
import sys
import ply.lex as lex
import ply.yacc as yacc

tokens = (
    'NOME','NOME_FUNC', 'NUMERO','BOLLEAN','ABRE','FECHA','BINARYOP','LPARENT','RPARENT',\
        'IGUAL','IGUAL_IGUAL','MAIOR','MENOR','OR','NOT',\
            'ECHO','WHILE','IF','ELSE','AND','DIVIDE','MULT',\
                'PONTOEVIRGULA','SPACE','MAIS','MENOS', 'SUFIXVAR',\
                    'VIRGULA','FUNCTION','RETURN','PONTO','READLINE','STRING'

)

literals = ['=', '+', '-', '*', '/', '(', ')','{','}',';']

token=[]

# Tokens
# Ascii binary of normal elements

def t_READLINE(t):
    r'0111001001100101011000010110010001101100011010010110111001100101' # readline
    return t
def t_NOME_FUNC(t):
    r'01000000(.*?)01000000' # prefix and sufix : ex -> @soma123_dasd@
    t.value = t.value[8:-8]
    return t
def t_STRING(t):
    r'00100111(.*?)00100111' # prefix and sufix : ex -> 'essa é minha string 123 __ -'
    t.value = t.value[8:-8]
    return t
def t_PONTO(t):
    r'00101110' # .
    return t
def t_MULT(t):
    r'00101010'
    return t
def t_DIVIDE(t):
    r'00101111'
    return t
def t_NOT(t):
    r'00100001'
    return t
def t_MAIS(t):
    r'00101011'
    return t
def t_MENOS(t):
    r'00101101'
    return t
def t_LPARENT(t):
    r'00101000' # (
    return t
def t_RPARENT(t):
    r'00101001' # )
    return t
def t_IGUAL_IGUAL(t):
    r'0011110100111101'
    return t
def t_IGUAL(t):
    r'00111101'
    return t
def t_MAIOR(t):
    r'00111110'
    return t
def t_MENOR(t):
    r'00111100'
    return t
def t_ABRE(t):
    r'01111011' # {
    return t
def t_FECHA(t):
    r'01111101' # }
    return t
def t_PONTOEVIRGULA(t):
    r'00111011'
    return t
def t_BOLLEAN(t):
    r'(01110100011100100111010101100101|0110011001100001011011000111001101100101)'
    return t
def t_RETURN(t):
    r'011100100110010101110100011101010111001001101110' #return
    return t
def t_FUNCTION(t):
    r'0110011001110101011011100110001101110100011010010110111101101110' # function
    return t
def t_VIRGULA(t):
    r'00101100' # , 
    return t
def t_ECHO(t):
    r'01100101011000110110100001101111' #echo
    return t
def t_WHILE(t):
    r'0111011101101000011010010110110001100101' #while
    return t
def t_IF(t):
    r'0110100101100110' #if
    return t
def t_ELSE(t):
    r'01100101011011000111001101100101' #else
    return t
# variaveis somente uma letra maiuscula ou minuscula ex-> $A...$Z or $a...$z
def t_NOME(t):
    r'00100100(010[0-1]{5})|00100100(011[0-1]{5})' #prefix $ in ascii
    t.value=t.value[8:]
    return t
# or -> |
def t_OR(t):
    r'01111100'
    return t
# and -> &&
def t_AND(t):
    r'0010011000100110'
    return t
# prefix and sufix : ex -> :20:
def t_NUMERO(t):
    r'00111010(.*?)00111010'
    t.value = t.value[8:-8]
    return t
# ignore space
def t_SPACE(t):
    r'00100000'
    pass
t_ignore = " \t | '"
    
# new line in ascii
def t_newline(t):
    r'00001010'
    t.lexer.lineno += t.value.count("\n")


def t_error(t):
    print("Illegal character '%s'" % t.value[0])
    t.lexer.skip(8)


def p_error(p):
    if p:
        print("Syntax error at '%s'" % p.value)
    else:
        print("Syntax error at EOF")



class Variaveis:
    funcs={}
    def __init__(self):
        self.dict = {"RETURN":None}

    def getter(self,value):
        return self.dict[value]

    def setter(self,name,value):
        self.dict[name] = value
    @staticmethod
    def f_getter(name):
        if not (name in Variaveis.funcs):
            raise TypeError("ERRO: Funcão chamada inesistente")
        return Variaveis.funcs[name]
    @staticmethod
    def f_setter(node):
        if(node.value in Variaveis.funcs):
            raise TypeError(f'ERRO: Função {node.value} já foi declarada')
        Variaveis.funcs[node.value] = node.children


class Node:
        def __init__(self):
            self.value = None
            self.children = []
        def evaluate(self,simbol_table):
            raise NotImplementedError    
class BinOP(Node):
    def evaluate(self,simbol_table):
        value1=self.children[0].evaluate(simbol_table)
        value2=self.children[1].evaluate(simbol_table)
        if(value1[1]=="string" or value2[1]=="string"):
            raise TypeError("ERRO: Tentativa de operação com str")
        if (self.value=="+"):
            return (int(value1[0]) + int(value2[0]),"int")
        if (self.value=="-"):
            return (int(value1[0]) - int(value2[0]),"int")
        if (self.value=="*"):
            return (int(value1[0]) * int(value2[0]),"int")
        if (self.value=="/"):
            return (int(value1[0]) // int(value2[0]),"int")
        if (self.value=="and"):
            return ((bool(value1[0]) and bool(value2[0])),"bool")
        if (self.value=="or"):
            return ((bool(value1[0]) or bool(value2[0])),"bool")
            
class RelacionalOP(Node):
    def evaluate(self,simbol_table):
        value1=self.children[0].evaluate(simbol_table)
        value2=self.children[1].evaluate(simbol_table)
        if (self.value=="=="):
            # check types
            if((value1[1]==value2[1]) or ((value1[1] =="bool" and value2[1] =="int") or value2[1] == "bool" and value1 == "int")):
                return ((value1[0] == value2[0]),"bool")
            else:
                raise TypeError("ERRO: tentativa de == com tipos não permitidos")
        if (self.value==">"):
            return ((value1[0] > value2[0]),"bool")
        if (self.value=="<"):
            return ((value1[0] < value2[0]),"bool")
        if (self.value=="."):
            if(value1[1] == "bool"):
                value1=(int(value1[0]),"int")
            if(value2[1] == "bool"):
                 value2=(int(value2[0]),"int")
            return (str(value1[0])+str(value2[0]),"str")
class UnOP(Node):
    def evaluate(self,simbol_table):
        value=self.children[0].evaluate(simbol_table)
        if (self.value=="+"):
            return (int(value[0]),"int")
        elif (self.value=="-"):
            return (-int(value[0]),"int")
        elif (self.value=="!" and value[1]!="string"):    
            return (not(value[0]),'bool')
        else:
            raise TypeError("ERRO: Trying to not a string")
class IntVAL(Node):
    def evaluate(self,simbol_table):
        return self.value
class NoOP(Node):
    def evaluate(self,simbol_table):
        return super().evaluate(simbol_table)
class Identifier(Node):
    def evaluate(self,simbol_table):
        return simbol_table.getter(self.value)
class Assign(Node):
    def evaluate(self,simbol_table):
        var=self.children[1].evaluate(simbol_table)
        simbol_table.setter(name=self.children[0].value,value=var)
class Echo(Node):
    def evaluate(self,simbol_table):
        print(self.children[0].evaluate(simbol_table)[0])
class While(Node):
    def evaluate(self,simbol_table):
        while (self.children[0].evaluate(simbol_table)[0]):
            self.children[1].evaluate(simbol_table)
class If(Node):
    def evaluate(self,simbol_table):
        if(self.children[0].evaluate(simbol_table)[0]):
            return self.children[1].evaluate(simbol_table)
        if(len(self.children)==3):  
            return self.children[2].evaluate(simbol_table)
        return

class ReadLine(Node):
    def evaluate(self,simbol_table):
       return (int(input()),"int")
class Commands(Node):
    def evaluate(self, simbol_table):
        for i in self.children:
            i.evaluate(simbol_table)
            if(simbol_table.getter("RETURN")!=None):
                return
        
class BoolVal(Node):
    def evaluate(self, simbol_table):
        return self.value
class StringVal(Node):
    def evaluate(self, simbol_table):
        return (self.value)

class FuncDec(Node):
    def evaluate(self, simbol_table):
        Variaveis.f_setter(self)

class FuncCall(Node):
    def evaluate(self, simbol_table):
        func = Variaveis.f_getter(self.value) 
        args = func[:-1]
        command = func[-1]
        local_vars = Variaveis()
        if(len(args)!=len(self.children)):
            raise TypeError("ERRO: Numero de argumentos invalido")
        for i in range(len(args)):
            local_vars.setter(args[i].value,self.children[i].evaluate(simbol_table))
        command.evaluate(local_vars)
        if(local_vars.getter("RETURN")!=None):
            return local_vars.getter("RETURN")
        
class Return(Node):
    def evaluate(self, simbol_table):
        simbol_table.setter(name="RETURN",value=self.children[0].evaluate(simbol_table))

class Token(object):
    def __init__(self, type_="", value=""):
        self.type_ = type_
        self.value = value


def get_type(str):
    if(str == "MAIS"):
        return "+"
    elif(str == "MENOS"):
        return "-"
    elif(str == " " or str == '\n'):
        return "espaço"
    elif(str.isdigit()):
        return "int"
    elif(str == "DIVIDE"):
        return "/"
    elif(str == "MULT"):
        return "*"
    elif(str == "IGUAL_IGUAL"):
        return "=="
    elif(str == "MAIOR"):
        return ">"
    elif(str == "MENOR"):
        return "<"
    elif(str == "AND"):
        return "and" 
    elif(str == "OR"):
        return "or"
    elif(str == "PONTO"):
        return "."
    elif(str == "NOT"):
        return "!"    
    else:
        return "Não identificado"

class Preprocess():
    def remove_comments(code):
        return re.sub(re.compile("[a-zA-Z s \D]+",re.DOTALL),"",code)


class Tokenizer(object):
    def __init__(self, origin, position, actual):
        self.origin = origin
        self.position = 0

    def selectNext(self):
        self.position +=1


class Parser(object):
    @staticmethod
    def block(tokenizador):
        if(token[tokenizador.position].type == "ABRE"):
            tokenizador.selectNext()
            node = Commands()
            node.children.append(Parser.command(tokenizador))
            while (token[tokenizador.position].type != "FECHA"):
                node.children.append(Parser.command(tokenizador))
            tokenizador.selectNext()
            return node
        else:
            raise TypeError("ERRO : CODIGO INVALIDO")

    @staticmethod
    def command(tokenizador):
        if(token[tokenizador.position].type == "NOME"):
            filho_esquerda = Identifier()
            filho_esquerda.value = token[tokenizador.position].value
            tokenizador.selectNext()
            if(token[tokenizador.position].type == "IGUAL"):
                node = Assign()
                node.children.append(filho_esquerda)
                node.value=token[tokenizador.position].value
                tokenizador.selectNext()
                node.children.append(Parser.relexpr(tokenizador))
                if(token[tokenizador.position].type == "PONTOEVIRGULA"):
                    tokenizador.selectNext()
                    return node
        elif(token[tokenizador.position].type == "ECHO"):
            node = Echo()
            tokenizador.selectNext()
            node.children.append(Parser.relexpr(tokenizador))
            if(token[tokenizador.position].type == "PONTOEVIRGULA"):
                tokenizador.selectNext()
                return node
        elif(token[tokenizador.position].type == "WHILE"):
            node = While()
            node.value=token[tokenizador.position].type
            tokenizador.selectNext()
            if(token[tokenizador.position].type == "LPARENT"):
                node.children.append(Parser.relexpr(tokenizador))
                node.children.append(Parser.command(tokenizador))
                return node
            return TypeError("ERRO: NA formatação do While")
        elif(token[tokenizador.position].type == "IF"):
            node = If()
            node.value=token[tokenizador.position].type
            tokenizador.selectNext()
            if(token[tokenizador.position].type == "LPARENT"):
                node.children.append(Parser.relexpr(tokenizador))
                node.children.append(Parser.command(tokenizador))
                # tokenizador.selectNext()
                if(token[tokenizador.position].type == "ELSE"):
                    tokenizador.selectNext()
                    node.children.append(Parser.command(tokenizador))
                    return node
                else:
                    return node
            return TypeError("ERRO: NA formatação do If")
            
            
        elif(token[tokenizador.position].type == "ABRE"):
            commands = Parser.block(tokenizador)
            return commands
        elif(token[tokenizador.position].type == "PONTOEVIRGULA"):
            return
        elif(token[tokenizador.position].type == "FUNCTION"):
            node = FuncDec()
            tokenizador.selectNext()
            if(token[tokenizador.position].type == "NOME_FUNC"):
                node.value=token[tokenizador.position].value
                tokenizador.selectNext()
                if(token[tokenizador.position].type == "LPARENT"):
                    tokenizador.selectNext()
                    while(token[tokenizador.position].type!="RPARENT"):
                        if(token[tokenizador.position].type == "NOME" and token[tokenizador.position].type!="VIRGULA"):
                            node.children.append(Parser.relexpr(tokenizador))
                        if(token[tokenizador.position].type!="RPARENT"):
                            tokenizador.selectNext()
                    tokenizador.selectNext()
                    node.children.append(Parser.block(tokenizador))
                    return node
        elif(token[tokenizador.position].type == "RETURN"):
            node = Return()
            tokenizador.selectNext()
            node.children.append(Parser.relexpr(tokenizador))
            if(token[tokenizador.position].type !="PONTOEVIRGULA"):
                raise TypeError("ERRO: falta de ;")
            tokenizador.selectNext()
            while token[tokenizador.position].type!="FECHA":
                tokenizador.selectNext()
            return node
        elif(token[tokenizador.position].type == "NOME_FUNC"):
            node = FuncCall()
            node.value=token[tokenizador.position].value
            tokenizador.selectNext()
            if(token[tokenizador.position].type == "LPARENT"):
                tokenizador.selectNext()
                while(token[tokenizador.position].type!="RPARENT"):
                    if(token[tokenizador.position].type=="VIRGULA"):
                        tokenizador.selectNext()
                    if(token[tokenizador.position].type!="VIRGULA"):
                        node.children.append(Parser.relexpr(tokenizador))
                        # if(tokenizador.actual.value!="," and tokenizador.actual.value!=")"):
                        #     raise TypeError("ERRO: na chamada da funcao")
                tokenizador.selectNext()
                if(token[tokenizador.position].type == "PONTOEVIRGULA"):
                    tokenizador.selectNext()
                    return node
                else:
                    raise TypeError("ERRO: ; não encontrado")
        else:
            raise TypeError(f"ERRO: COMMAND NOT FOUND {token[tokenizador.position].type} ")
        
    @staticmethod
    def relexpr(tokenizador):
        node2 = Parser.parseExpression2(tokenizador)
        while(token[tokenizador.position].type == "IGUAL_IGUAL" or token[tokenizador.position].type == "MAIOR"\
             or token[tokenizador.position].type == "MENOR" or token[tokenizador.position].type == "PONTO"):
            node = RelacionalOP()
            node.value=get_type(token[tokenizador.position].type)
            node.children.append(node2)
            node2=node
            tokenizador.selectNext()
            node.children.append(Parser.parseExpression2(tokenizador))
        return node2
    @staticmethod
    def factor(tokenizador):
        resultado = 0
        string=""
        if(token[tokenizador.position].type == "NUMERO"):
            node = IntVAL()
            if(len(token[tokenizador.position].value)>8):
                numbers=[token[tokenizador.position].value[i:i+8] for i in range(0, len(token[tokenizador.position].value), 8)]
                for name in numbers:
                    string+=chr(int(name,2))
            else:
                string=chr(int(token[tokenizador.position].value,2))
            node.value=(int(string),'int')
            tokenizador.selectNext()
            return node
        if(token[tokenizador.position].type=="BOLLEAN"):
            node = BoolVal()
            if token[tokenizador.position].value=="01110100011100100111010101100101":
                node.value=(True,'bool')
            else:
                node.value=(False,'bool')
            # node.value=(token[tokenizador.position].value,'bool')
            tokenizador.selectNext()
            return node
        if(token[tokenizador.position].type=="STRING"):
            node = StringVal()
            binary_int=int(token[tokenizador.position].value,2)
            byte_number = binary_int.bit_length() + 7 // 8
            binary_array = binary_int.to_bytes(byte_number, "big")
            node.value=(binary_array.decode(),'string')
            tokenizador.selectNext()
            return node
        if(token[tokenizador.position].type == "NOME"):
            node = Identifier()
            node.value=token[tokenizador.position].value
            tokenizador.selectNext()
            return node
        if(token[tokenizador.position].type == "MAIS" or token[tokenizador.position].type == "MENOS" or token[tokenizador.position].type == "NOT" ):
            node = UnOP()
            node.value = get_type(token[tokenizador.position].type)
            tokenizador.selectNext()
            node.children.append(Parser.factor(tokenizador))
            return node
        if(token[tokenizador.position].type == "READLINE"):
            node = ReadLine()
            node.value = token[tokenizador.position].type
            tokenizador.selectNext()
            if(token[tokenizador.position].type == "LPARENT"):
                tokenizador.selectNext()
                if(token[tokenizador.position].type == "RPARENT"):
                    tokenizador.selectNext()
                    return node
            return TypeError("ERRO: Formatação do readline")
        elif(token[tokenizador.position].type == "LPARENT"):
            tokenizador.selectNext()
            resultado = Parser.relexpr(tokenizador)
            if(token[tokenizador.position].type == "RPARENT"):
                tokenizador.selectNext()
                return resultado
            else:
                raise TypeError("ERRO: NO {token[tokenizador.position].value}")
        elif(token[tokenizador.position].type == "NOME_FUNC"):
            node = FuncCall()
            node.value=token[tokenizador.position].value
            tokenizador.selectNext()
            if(token[tokenizador.position].type == "LPARENT"):
                tokenizador.selectNext()
                while(token[tokenizador.position].type!="RPARENT"):
                    if(token[tokenizador.position].type=="VIRGULA"):
                        tokenizador.selectNext()
                    if(token[tokenizador.position].type!="VIRGULA"):
                        node.children.append(Parser.relexpr(tokenizador))
                        # if(tokenizador.actual.value!="," and tokenizador.actual.value!=")"):
                        #     raise TypeError("ERRO: na chamada da funcao")
                tokenizador.selectNext()
                return node
        # elif(tokenizador.actual.value == "$"):
        else:
            raise TypeError("ERRO: factor cant consume token")
        return resultado

    

    @staticmethod
    def parseTerm(tokenizador):
        node2 = Parser.factor(tokenizador)
        while(token[tokenizador.position].type == "MULT" or token[tokenizador.position].type == "DIVIDE" or token[tokenizador.position].type == "AND"):
            node = BinOP()
            node.value=get_type(token[tokenizador.position].type)
            tokenizador.selectNext()
            node.children.append(node2)
            node2=node
            node.children.append((Parser.factor(tokenizador)))
        return node2

    @staticmethod
    def parseExpression2(tokenizador):
        # tokenizador.selectNext() 
        node2 = Parser.parseTerm(tokenizador)
        while(token[tokenizador.position].type == "MAIS" or token[tokenizador.position].type == "MENOS" or token[tokenizador.position].type == "OR"):
            node = BinOP()
            node.value=get_type(token[tokenizador.position].type)
            node.children.append(node2)
            node2=node
            tokenizador.selectNext()
            node.children.append(Parser.parseTerm(tokenizador))
            # resultado = Parser.parseTerm(tokenizador)
        return node2
   

    @staticmethod
    def run(code):
        tokenizador = Tokenizer("", 0, 0)
        tokenizador.origin = Preprocess.remove_comments(code)
        lexer = lex.lex()
        lexer.input(tokenizador.origin)
        while True:
            tok = lexer.token()
            if not tok: 
                break      # No more input
            token.append(tok)
            print(tok)
        tokenizador.origin = tokenizador.origin.replace('\\n','\n')
        resultado = Parser.block(tokenizador)
        if(len(token)!=tokenizador.position):
            raise TypeError("EOF not found")
        return resultado

def main():
    import sys
    parser = Parser()
    f = open("teste_simpler.php", "r")
    data=f.read()
        # Lexica
    resultado = parser.run(data)
    simpletable = Variaveis()
    f.close() 
    return resultado.evaluate(simbol_table=simpletable)


if __name__ == "__main__":
    main()
