#askdhgha
#!/usr/bin/python

import os,sys,glob,errno,shlex,re
import xml.etree.ElementTree as xml
class jackTokenizer:
  #regex for lexical elements
    re_integer = '\d+'
    re_symbol = '\{|\}|\(|\)|\[|\]|\.|\,|\;|\+|-|\*|/|&|\||\<|\>|=|_|~'
    re_string = '"[^"]*"'
    re_identifier = '[A-Z_]|[a-z]'

    
    #keywords
    keyword = {
            'class' : 'CLASS',
            'constructor' : 'CONSTRUCTOR',
            'function': 'FUNCTION',
            'method' : 'METHOD',
            'field' : 'FIELD',
            'static' : 'STATIC',
            'var' : 'VAR',
            'int' : 'INT',
            'char' : 'CHAR',
            'boolean' : 'BOOLEAN',
            'void' : 'VOID',
            'true' : 'TRUE',
            'false' : 'FALSE',
            'null' : 'NULL',
            'this' : 'THIS',
            'let' : 'LET',
            'do' : 'DO',
            'if' : 'IF',
            'else' : 'ELSE',
            'while' : 'WHILE',
            'return' : 'RETURN'
        }
    
    def __init__(self, inpfile):
        self.infile = open(inpfile)        
        self.tokens = self.infile.read()
        self.token = ""
        
        self.removeComments(self.tokens)
        self.tokenize(self.tokens)


        
    
    def advance(self):
        if self.hasMoreTokens():
            self.token =self.tokens[0]                
            print("token: " + str(self.token)+" type: " + self.tokenType())
            print( self.token)
            
            self.tokens = self.tokens[1:]

        
        return self.token
            
        
    def removeComments(self, lines):
        
        uncommented = re.sub('//.*?\n', '\n', lines)
        uncommented = re.sub('/\*.*?\*/', '', uncommented, flags=re.DOTALL)
        self.tokens = uncommented
        #print uncommented

    def tokenize(self,l):
        
        reg = '('+'|'.join(exp for exp in[self.re_symbol,self.re_string]) + ')|\s+'
        split_codes = re.split(reg,l)

        split_codes = filter(None, split_codes)

        self.tokens = list(split_codes)
        
    def nextToken(self):
        if self.hasMoreTokens():
            return self.tokens[0]
        else:
            return ("ERROR!!!")
    #returns the type of the next token

    def nextValue(self):
        element = self.nextToken()
        if element in self.keyword.keys():
            return 'keyword'
        elif re.match(self.re_integer,element):
            return 'integerConstant'
        elif re.match(self.re_symbol, element):
            return 'symbol'
        elif re.match(self.re_identifier, element):
            return 'identifier'
        elif re.match(self.re_string, element):
            return 'stringConstant'
        else:
            return 'NONE'
    
    #-- API Routines Begin

    def tokenType(self):
        if self.token in self.keyword.keys():
            return 'keyword'
        elif re.match(self.re_integer,self.token):
            return 'integerConstant'
        elif re.match(self.re_symbol,self.token):
            return 'symbol'
        elif re.match(self.re_identifier,self.token):
            return 'identifier'
        elif re.match(self.re_string,self.token):
            return 'stringConstant'
        else:
            return 'NONE'
                
    #def keyWord(self):
        






class compilationEngine:

    

    spl_char = { '<':'&lt;', '>':'&gt;', '"':'&quot;','&':'&amp;'}
    
    def __init__(self, infile, outfile):
        self.tokenizer = jackTokenizer(infile)
        self.op = outfile
        self.indent = ""
        self.mStack =[] #a stack to store all non terminal blocks opened which have to be closed
        self.keywordConsts = {'true', 'false','null','this'}
        self.binaryOp = {'+','-','*','|','<','>','=','/','&'}
        self.unaryOp = {'-','~'}

        
    def addIndent(self):
        self.indent +="    "

    def removeIndent(self):
        self.indent = self.indent[:-4]
    

    def writeTerm(self, token, Ttype):
        self.op.write(self.indent+"<"+Ttype+">"+ token + "</"+Ttype+">\n")


    def startNonTerm(self, rule):
        self.op.write(self.indent+"<"+rule+">\n")
        self.addIndent()
        self.mStack.append(rule)


    def endNonTerm(self):
        rule = self.mStack.pop()
        self.removeIndent()
        self.op.write(self.indent+"</"+rule+">\n")
        
    
    def advance(self):
        token = self.tokenizer.advance()
        Ttype = self.tokenizer.tokenType()
        #handle string constant
        if Ttype == "stringConstant":
            token = token[1:-1]

        if token in self.spl_char.keys():
            token = self.spl_char[token]
        self.writeTerm(token, Ttype)

    def nextValue(self):
        value = self.tokenizer.nextValue()
        return value
        
    def nextToken(self):
        return self.tokenizer.nextToken()

    def writeArrayIndex(self):
        self.advance()  #get "["
        self.compileExpression() # compile the expression in the indexholder
        self.advance() # get "]"

    def existExpression(self):
        return self.existTerm()

    def existTerm(self):
        token = self.nextToken()
        Ttype = self.nextValue()

        return (Ttype == "integerConstant" or Ttype == "stringConstant" \
            or Ttype == "identifier" or token in self.unaryOp \
            or token in self.keywordConsts or token == "(")
            

    def existStatement(self):
        return (self.nextToken() == "do") \
               or (self.nextToken() == "let") \
               or (self.nextToken() == "if") \
               or (self.nextToken() == "while") \
               or (self.nextToken() == "return") \

    
    def existVarDec(self):
        return (self.nextToken() == "var")

    def existClassVarDec(self):
        return (self.nextToken() == "static" or self.nextToken() == "field")

    def existSubroutineDec(self):
        return (self.nextToken() == "constructor" or self.nextToken() == "function" or self.nextToken() == "method")

    def existParameter(self):
        return not (self.nextValue() == "symbol")

    def writeParameter(self):
        self.advance() # get type
        self.advance() # get var name
        if (self.nextToken() == ","):
            self.advance() # get ","

    def  eat(self,string):   # check for expected elements in the grammar
        nextToken= self.nextToken()
        print("!!"+nextToken+"!")
        if nextToken == string:
            self.advance()
        else:
            print("ERROR!! expected " + string+"got: "   + nextToken)
            exit()

    #API BEGINS

    #compile parameter list

    def compileParameterList(self):
        self.startNonTerm("parameterList")
        while self.existParameter():
            self.writeParameter()
        self.endNonTerm()


#compile class variable declarations
    def compileClassVarDec(self):
        self.startNonTerm("classVarDec")
        if self.nextToken() == "static":
            self.eat("static")
        else:
            self.eat("field")

        self.advance() #get varName type
        self.advance() #get varName
        while self.nextToken() == ",":
            self.eat(",")
            self.advance() #get var Name

        self.eat(";")

        self.endNonTerm()

        
    
    #compiles class declaration
            
    def compileClass(self):
        self.startNonTerm("class")
        self.eat("class") # get "class"
        self.advance() #get class name
        self.eat("{")
        while (self.existClassVarDec()):
            self.compileClassVarDec()

        while (self.existSubroutineDec()):
            self.compileSubroutineDec()

        self.eat("}")
        self.endNonTerm()


   #compile variable declaration     
    def compileVarDec(self):
        self.startNonTerm("varDec")
        self.eat("var")
        self.advance() #get var-type
        self.advance() #get varName
        while (self.nextToken() == ","):
            self.eat(",")
            self.advance()
        self.eat(";")
        self.endNonTerm()

        
        
    #compile subroutine declaration
    def compileSubroutineDec(self):
        self.startNonTerm("subroutineDec")
        if self.nextToken() == "constructor" or self.nextToken() == "function" or self.nextToken() == "method":
            self.advance() # get constructor | method | function
        else:
            print("ERROR!!! keyword expected")
            return
        self.advance() # get type | void
        self.advance() # get subroutine name
        self.eat("(")
        self.compileParameterList()
        self.eat(")")
        self.compileSubroutineBody()
        self.endNonTerm()

    #compiles subroutine body

    def compileSubroutineBody(self):
        self.startNonTerm("subroutineBody")
        self.eat("{")
        while(self.existVarDec()):
            self.compileVarDec()
        
        self.compileStatements()
        self.eat("}")
        self.endNonTerm()


    #

    
    #compile Statements
    def compileStatements(self):
        self.startNonTerm("statements")
        while self.existStatement():
            if self.nextToken() == "do":
                self.compileDo()
            elif self.nextToken() == "let":
                self.compileLet()
            elif self.nextToken() == "while":
                self.compileWhile()
            elif self.nextToken() == "if":
                self.compileIf()
            elif self.nextToken() == "return":
                self.compileReturn()
        self.endNonTerm()    

    
    #compiles let statement
    
    def compileLet(self):
        self.startNonTerm('letStatement')
        self.eat("let") # get 'let' keyword
        self.advance() # get varName
        if self.nextToken() == '[':
            self.writeArrayIndex()
        self.eat("=") # get '=' symbol
        self.compileExpression()
        self.eat(";") # get ';' symbol
        self.endNonTerm()


    #compiles if statement
    def compileIf(self):
        self.startNonTerm('ifStatement')
        
        self.eat("if") # get 'if' keyword
        self.eat("(") # get '(' symbol
        self.compileExpression()
        self.eat(")") # get ')' symbol
        
        self.eat("{")

        self.compileStatements()
        self.eat("}")        

        if self.nextToken() == "else":
            self.eat("else")
            self.eat("{")

            self.compileStatements()
            self.eat("}")

        self.endNonTerm()


    # compiles while statement(loop)

    def compileWhile(self):
        self.startNonTerm("whileStatement")

        self.eat("while")
        self.eat("(")
        self.compileExpression()
        self.eat(")")
        self.eat("{")
        self.compileStatements()
        self.eat("}")

        self.endNonTerm()


    #compiles do statements (subroutine call
    def compileDo(self):
        self.startNonTerm("doStatement")
        self.eat("do")
        self.advance()
        if self.nextToken() == ".":
            self.eat(".")
            self.advance()
        self.eat("(")
        self.compileExpressionList();
        self.eat(")")
        self.eat(";")
        self.endNonTerm()


    #compiles return satement
    def compileReturn(self):
        self.startNonTerm("returnStatement")

        self.eat("return")
        if self.nextToken() != ";":
            self.compileExpression()

        self.eat(";")

        self.endNonTerm()


    
    

        
    #compiles expression list
    def compileExpressionList(self):
        self.startNonTerm('expressionList')
        if self.existExpression():
            self.compileExpression()
        while self.nextToken() == ",":
            self.eat(",") #get the symbol ","
            if self.existExpression():
                self.compileExpression()
        
        self.endNonTerm()
        

    #compiles expressions
    def compileExpression(self):
        self.startNonTerm('expression')
        self.compileTerm()
        while (self.nextToken() in self.binaryOp):
            self.advance() # get the  binary op
            self.compileTerm()

        self.endNonTerm()

    # compile subRoutine calls
    def compileSubroutinecall(self):
        self.startNonTerm("subroutineCall")
        self.advance() # get subroutine name  |  class name
        if self.nextToken() == ".": # if the above token is a class name
            self.eat(".")
            self.advance() # get subroutine name
        self.eat("(")
        self.compileExpressionList()
        self.eat(")")

        self.endNonTerm()

        
    #compiles term

    def compileTerm(self):
        #Grammar : varname | constant
        self.startNonTerm("term")# to start the new non terminal block

        print("compiling term"+self.nextValue())
        if self.nextValue() == "integerConstant" or self.nextValue() == "stringConstant" or (self.nextToken() in self.keywordConsts):
            self.advance() # to get the const
        elif self.nextValue() == "identifier":
            self.advance() # get varName or ClassName
            
            if self.nextToken() == "[":
                self.writeArrayIndex()

            if self.nextToken() == "(":
                self.eat("(") # get "("
                self.compileExpressionList()
                self.eat(")") # get ")"

            if self.nextToken() == ".": # handles with subroutine call
                self.eat(".") # get "."
                self.advance() # get subRoutine name
                self.eat("(") # get "("
                self.compileExpressionList()
                self.eat(")") # get ")"

        elif (self.nextToken() in self.unaryOp):
            self.advance()# get op
            self.compileTerm()

        elif self.nextToken() == "(":
            self.eat("(") # get "("
            self.compileExpression()
            self.eat(")") # get ")"

        self.endNonTerm()

    
        



    
        
        











        
        
def main(): 
    
    inFile = sys.argv[1]
    

    def Parser(inputFile):
        source = inputFile
        out_file = open(inputFile[:-5] + "_Test.xml","w+")
        cwrite = compilationEngine(source, out_file)
        cwrite.compileClass()
        
        out_file.close()

        
    #If the  given argument is a file.
        
    if os.path.isfile(inFile):
        Parser(inFile)



    elif os.path.isdir(inFile):
        path = "./"+inFile+"/*.jack"
        files = glob.glob(path)
        for name in files:
            try:
                Parser(name)

            
            except IOError as e:
                if e.errno != errno.EISDIR:
                    raise

    

              
if __name__ == "__main__":
    main()
