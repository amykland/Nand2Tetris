#!/usr/bin/python
import os, sys

class JackTokenizer:
	KEYWORD = {"class","method","function","constructor","int","boolean","char","void","var","static","field","let","do","if","else","while","return","true","false","null","this"}
	SYMBOL = {"{","}","(",")","[","]",".",",",";","+","-","*","/","&","|","<",">","=","~","<",">","&","&amp;","&lt;","&gt;"}
	def __init__(self, file):
		self.inFile = file
		self.hasMoreTokens = True
		self.tok=None
		self.tok2=None
		self.tokens = []
	def advance(self):
		token=""
		tokChar = self.inFile.read(1)
		while tokChar.isspace() or (tokChar == "*" or tokChar == "/"):
			if tokChar.isspace():
				tokChar = self.inFile.read(1)
			elif (tokChar == "*" or tokChar == "/"):
				prev = self.inFile.tell()
				tokChars = self.inFile.read(2)
				comment = tokChars[0]=="*" and tokChars[1]=="*" and tokChar == "/"
				if not (tokChars[0]=="/") and not comment:
					self.inFile.seek(prev)
					break
				comment = False
				self.inFile.readline()
				tokChar = self.inFile.read(1)
			continue
		if tokChar.isalnum():
			while (tokChar=="_" or tokChar.isalnum()):
				token+=tokChar
				prev = self.inFile.tell()
				tokChar=self.inFile.read(1)
			self.inFile.seek(prev)
		elif tokChar == "\"":
			token+=tokChar
			tokChar=self.inFile.read(1)
			while tokChar != "\"":
				token+=tokChar
				tokChar=self.inFile.read(1)
			token+=tokChar
		else:
			if tokChar=="&":
				token="&amp;"
			elif tokChar=="<":
				token="&lt;"
			elif tokChar==">":
				token="&gt;"
			else:
				token = tokChar
		if self.tok:
			self.tokens.append(token)
			self.tok=self.tok2
			self.tok2=token
		else:
			self.tok = token
			self.tok2=token
			self.advance()
		if not len(self.tok2)>0:
			self.hasMoreTokens=False
	def tokenType(self):
		if self.tok in self.SYMBOL:
			return "SYMBOL"
		elif self.tok in self.KEYWORD:
			return "KEYWORD"
		elif self.tok.isdigit():
			return "INT_CONST"
		elif self.tok.isalnum():
			return "IDENTIFIER"
		else:
			return "STRING_CONST"
	def expression(self):
		if self.tokens[len(self.tokens)-4]=="." and len(self.tokens)>=3:
			return True
		else:
			return False

	def keyWord(self):
		if self.tokenType() == "KEYWORD":
			return self.tok
	def symbol(self):
		if self.tokenType()=="SYMBOL":
			return self.tok
	def identifier(self):
		if self.tokenType()=="IDENTIFIER":
			self.tok
	def intVal(self):
		if self.tokenType()=="INT_CONST":
			return self.tok
	def stringVal(self):
		if self.tokenType()=="STRING_CONST":
			return self.tok

class SymbolTable:
	def __init__(self):
		self.classST={}
		self.methodST={}
		self.ST={"static": self.classST,"field":self.classST,"arg":self.methodST,"var":self.methodST}
		self.kIndex={"static": 0,"field":0,"arg":0,"var":0}
	def startSubroutine(self):
		self.methodST.clear()
		self.kIndex["arg"]=0
		self.kIndex["var"]=0
	def define(self,name,stype,kind):
		if kind in["static","field","arg","var"]:
			self.ST[kind][name]=(stype,kind,self.varCount(kind))
			self.kIndex[kind]+=1
	def varCount(self,kind):
		i=0
		if kind in["static","field","arg","var"]:
			for (typee,kind1,index) in self.ST[kind]:
				if kind1==kind:
					i+=1
		return i
	def kindOf(self,name):
		if name in self.methodST:
			return self.methodST[name][1]
		elif name in self.classST:
			return self.classST[name][1]
		else:
			return -1
	def typeOf(self,name):
		if name in self.methodST:
			return self.methodST[name][0]
		elif name in self.classST:
			return self.classST[name][0]
		else:
			return -1
	def indexOf(self,name):
		if name in self.methodST:
			return self.methodST[name][2]
		elif name in self.classST:
			return self.classST[name][2]
		else:
			return -1

class CompilationEngine():
	def __init__(self, jackTokenizer, file):
		self.outFile=file
		self.jackTokenizer=jackTokenizer
		self.className=""
		self.methodList=[]
		self.SymbolTable=SymbolTable()
		self.VMWriter=VMWriter(self.outFile)
		self.ebool=False
		self.rbool=False
		self.rCount=0
		self.lbool=False
		self.lCount=0
		self.wCount=0
		self.iCount=0
	def wToken(self):
		if self.jackTokenizer.tokenType()=="INT_CONST":
			self.outFile.write("<integerConstant> "+self.jackTokenizer.tok+" </integerConstant>\n")
		elif self.jackTokenizer.tokenType()=="STRING_CONST":
			self.outFile.write("<stringConstant> "+self.jackTokenizer.tok.replace("\"", "")+" </stringConstant>\n")
		else:
			self.outFile.write("<"+self.jackTokenizer.tokenType().lower()+"> "+self.jackTokenizer.tok+" </"+self.jackTokenizer.tokenType().lower()+">\n")
	def compileClass(self):
		self.jackTokenizer.advance()
		self.className+=self.jackTokenizer.tok
		while self.jackTokenizer.hasMoreTokens:
			self.jackTokenizer.advance()
			if self.jackTokenizer.tok in ["static","field"]:
				self.compileClassVarDec()
			elif self.jackTokenizer.tok in ["method","function","constructor"]:
				self.compileSubroutine()
	def compileClassVarDec(self):
		kind=self.jackTokenizer.keyWord()
		self.jackTokenizer.advance()
		typee=self.jackTokenizer.keyWord()
		self.jackTokenizer.advance()
		self.compileVar(typee,kind,True)

	def compileSubroutine(self):
		method=self.jackTokenizer.tok=="method"
		constructor=self.jackTokenizer.tok=="constructor"
		self.SymbolTable.startSubroutine()
		if method:
			self.SymbolTable.define("this",self.className,"arg")			
		self.jackTokenizer.advance()
		if not constructor:
			self.jackTokenizer.advance()
		name=self.jackTokenizer.tok
		self.jackTokenizer.advance()
		self.jackTokenizer.advance()
		if constructor:
			self.jackTokenizer.advance()
		while(self.jackTokenizer.tok!=")"):
			self.SymbolTable.define(self.jackTokenizer.tok2,self.jackTokenizer.tok,"arg")
			self.jackTokenizer.advance() 
			self.jackTokenizer.advance()
		self.jackTokenizer.advance()
		self.jackTokenizer.advance()
		if self.jackTokenizer.tok=="var":
			self.jackTokenizer.advance()
			self.compileVar(self.jackTokenizer.tok,"var",False)
			self.jackTokenizer.advance()
		self.VMWriter.writeFunction(self.className+"."+name, self.SymbolTable.kIndex["var"])
		if method:
			self.VMWriter.writePush("argument",0)
			self.VMWriter.writePop("pointer",0)
		if constructor:
			self.outFile.write("push constant"+str(self.SymbolTable.kIndex["field"])+"\n")
			self.outFile.write("call Memory.alloc 1\n")
			self.outFile.write("pop pointer 0\n")
		self.compileStatements()
		self.jackTokenizer.advance()

	def compileVar(self,typee,kind,isClass):
		self.SymbolTable.define(self.jackTokenizer.tok,typee,kind)
		self.jackTokenizer.advance()
		if self.jackTokenizer.tok==";":
			self.jackTokenizer.advance()
			if isClass:
				self.compileClassVarDec()
			else:
				self.compileSubroutine()
		elif self.jackTokenizer.tok==",":
			self.jackTokenizer.advance()
			self.compileVar(type1,kind1,isClass)

	def compileParameterList(self,args):
		if self.jackTokenizer.tok!=")":
			args+=1
			self.compileTerm()
			while self.jackTokenizer.tok in ["+","-","*","/","|","&amp","&lt","&gt"]:
				op=self.jackTokenizer.tok
				self.jackTokenizer.advance()
				self.compileTerm()
				self.VMWriter.writeArithmetic(op)
			if self.jackTokenizer.tok==",":
				self.jackTokenizer.advance()
				args=self.compileParameterList(args)
		return args		
	def compileStatements(self):
		while self.jackTokenizer.tok!="}": 
			if self.jackTokenizer.tok=="let":
				self.compileLet()		
			elif self.jackTokenizer.tok=="do":
				self.compileDo()
			elif self.jackTokenizer.tok=="if":
				self.compileIf()
			elif self.jackTokenizer.tok=="while":
				self.compileWhile()
			else:
				self.compileReturn()
			self.jackTokenizer.advance()	
	def compileDo(self):
		self.jackTokenizer.advance()
		if self.jackTokenizer.tok2==".":
			name=self.jackTokenizer.tok
			if self.SymbolTable.kindOf(self.jackTokenizer.tok)!=-1:
				self.VMWriter.writePush(self.SymbolTable.kindOf(self.jackTokenizer.tok),self.SymbolTable.indexOf(self.jackTokenizer.tok))
				name=self.SymbolTable.typeOf(self.jackTokenizer.tok)
			self.jackTokenizer.advance()
			self.jackTokenizer.advance()
			fName=name+"."+self.jackTokenizer.tok
			self.jackTokenizer.advance()
			self.jackTokenizer.advance()
			args=self.compileParameterList(0)
			if self.SymbolTable.kindOf(name)==-1:
				self.VMWriter.writeCall(fName,args)
			else:
				self.VMWriter.writeCall(fName,args+1)
			self.jackTokenizer.advance()
		elif self.jackTokenizer.tok2=="(":
			token=self.jackTokenizer.tok
			i=0
			if self.jackTokenizer.tok in self.methodList:
				self.VMWriter.writePush("pointer",0)
				i+=1
			self.jackTokenizer.advance()
			self.jackTokenizer.advance()
			i=self.compileParameterList(i)
			self.VMWriter.writeCall(self.className+"."+token,i)
			self.jackTokenizer.advance()
		self.jackTokenizer.advance()
		self.VMWriter.writePop("temp",0)
	def compileLet(self):
		self.jackTokenizer.advance()
		if self.jackTokenizer.tok2=="[":
			self.lCount+=1
			self.lbool=True
			self.compileArray(self.jackTokenizer.tok)
		else:
			self.jackTokenizer.advance()
		self.ebool=True
		if self.lbool==False:
			self.VMWriter.writePop(self.SymbolTable.kindOf(self.jackTokenizer.tok),self.SymbolTable.indexOf(self.jackTokenizer.tok))
		else:
			if self.lCount==1:      #could be an issue
				self.lCount-=1
				self.VMWriter.writePop("temp",0)
				self.VMWriter.writePop("pointer",1)
				self.VMWriter.writePush("temp",0)
				self.VMWriter.writePop("that",0)
		self.ebool=False
		self.lbool=False
		self.jackTokenizer.advance()
	def compileWhile(self):
		self.wCount+=1
		count=self.wCount-1
		self.jackTokenizer.advance()
		self.jackTokenizer.advance()
		self.VMWriter.writeLabel(str(count)+"STARTWHILE") 
		self.compileExpression()
		self.jackTokenizer.advance()
		self.jackTokenizer.advance()
		self.VMWriter.writeArithmetic("not")
		self.VMWriter.writeIf(str(count)+"ENDWHILE")
		self.compileStatements()
		self.jackTokenizer.advance()
		self.VMWriter.writeGoto(str(count)+"STARTWHILE")
		self.VMWriter.writeLabel(str(count)+"ENDWHILE")
	def compileReturn(self):
		self.jackTokenizer.advance()
		if self.jackTokenizer.tok!=";":
			self.compileExpression()
		else:
			self.VMWriter.writePush("constant",0)
		self.jackTokenizer.advance()
		self.VMWriter.writeReturn()
	def compileIf(self):
		self.iCount+=1
		count=self.iCount-1
		self.jackTokenizer.advance()
		self.jackTokenizer.advance()
		self.compileExpression()
		self.jackTokenizer.advance()
		self.jackTokenizer.advance()
		self.VMWriter.writeIf(str(count)+"IFT")
		self.VMWriter.writeGoto(str(count)+"IFF")
		self.VMWriter.writeLabel(str(count)+"IFT")
		self.compileStatements()
		self.jackTokenizer.advance()
		self.VMWriter.writeGoto(str(count)+"ENDIF")	
		if self.jackTokenizer.tok=="else":
			self.jackTokenizer.advance()
			self.jackTokenizer.advance()
			self.VMWriter.writeLabel(str(count)+"IFF")
			self.compileStatements()
			self.jackTokenizer.advance()
			self.VMWriter.writeLabel(str(count)+"ENDIF")
		else:
			self.VMWriter.writeLabel(str(count)+"IFF")
			self.VMWriter.writeLabel(str(count)+"ENDIF")	
	def methodList(self):
		for i in self.jackTokenizer.tokens:
			if self.jackTokenizer.tokens[i]=="method":
				self.methodList.append(self.jackTokenizer.tokens[i+2])		
	def compileExpression(self):
		self.compileTerm()
		while self.jackTokenizer.tok in ["+","-","*","/","|","=","&amp","&lt","&gt"]:
			x=self.jackTokenizer.tok
			self.jackTokenizer.advance()
			self.compileTerm()
			self.VMWriter.writeArithmetic(x)
	def compileTerm(self):
		if self.jackTokenizer.tokenType()=="KEYWORD":
			if self.jackTokenizer.tok=="this":
				self.VMWriter.writePush("pointer",0)
			elif self.jackTokenizer.tok=="true" or self.jackTokenizer.tok=="false" or self.jackTokenizer.tok=="null":
				self.VMWriter.writePush("constant",0)
				if self.jackTokenizer.tok=="true":
					self.VMWriter.writeArithmetic("not")
			self.jackTokenizer.advance()
		elif self.jackTokenizer.tokenType()=="IDENTIFIER":
			if self.jackTokenizer.tok2=="(":
				token=self.jackTokenizer.tok
				i=0
				if self.jackTokenizer.tok in self.methodList:
					self.VMWriter.writePush("pointer",0)
					i+=1
				self.jackTokenizer.advance()
				self.jackTokenizer.advance()
				i=self.compileParameterList(i)
				self.VMWriter.writeCall(self.className+"."+token,i)
				self.jackTokenizer.advance()
			elif self.jackTokenizer.tok2=="[":
				if self.ebool:
					self.rCount+=1
					self.rbool=True
				else:
					self.lCount+=1
					self.lbool=True
				self.compileArray(self.jackTokenizer.tok)
			elif self.jackTokenizer.tok2==".":
				name=self.jackTokenizer.tok
				if self.SymbolTable.kindOf(self.jackTokenizer.tok)!=-1:
					self.VMWriter.writePush(self.SymbolTable.kindOf(self.jackTokenizer.tok),self.SymbolTable.indexOf(self.jackTokenizer.tok))
					name=self.SymbolTable.typeOf(self.jackTokenizer.tok)
				self.jackTokenizer.advance()
				self.jackTokenizer.advance()
				fName=name+"."+self.jackTokenizer.tok
				self.jackTokenizer.advance()
				self.jackTokenizer.advance()
				args=self.compileParameterList(0)
				if self.SymbolTable.kindOf(name)==-1:
					self.VMWriter.writeCall(fName,args)
				else:
					self.VMWriter.writeCall(fName,args+1)
				self.jackTokenizer.advance()
			else:
				self.VMWriter.writePush(self.SymbolTable.kindOf(self.jackTokenizer.tok),self.SymbolTable.indexOf(self.jackTokenizer.tok))
		elif self.jackTokenizer.tokenType()=="STRING_CONST":
			string_const=self.jackTokenizer.tok[1:-1]
			self.VMWriter.writePush("constant",len(self.jackTokenizer.tok)-2)
			self.VMWriter.writeCall("String.new",1)
			for i in self.jackTokenizer.tok[1:-1]: 
				self.VMWriter.writePush("constant",ord(i))
				self.VMWriter.writeCall("String.appendChar", 2)
			self.jackTokenizer.advance()
		elif self.jackTokenizer.tokenType()=="INT_CONST":
			self.VMWriter.writePush("constant",self.jackTokenizer.tok)
			self.jackTokenizer.advance()
		elif self.jackTokenizer.tok=="-":
			self.jackTokenizer.advance()
			self.compileTerm()
			self.VMWriter.writeArithmetic("neg")
		elif self.jackTokenizer.tok=="~":
			self.jackTokenizer.advance()
			self.compileTerm()
			self.VMWriter.writeArithmetic("not")
		elif self.jackTokenizer.tok=="(":
			self.jackTokenizer.advance()
			self.compileExpression()
			self.jackTokenizer.advance()

	def compileArray(self,name):
		self.VMWriter.writePush(self.SymbolTable.kindOf(name),self.SymbolTable.indexOf(name))
		self.jackTokenizer.advance()
		self.jackTokenizer.advance()
		self.compileExpression()
		self.VMWriter.writeArithmetic("+")
		self.VMWriter.writePop("pointer",1)
		self.VMWriter.writePush("that",0)
		if self.lbool and self.lCount>1:
			self.lCount-=1
		elif self.rbool and self.rCount>0:
			self.rCount-=1
		self.compileTerm()
		self.jackTokenizer.advance()
		while self.jackTokenizer.tok in ["+","-","*","/","|","&amp","&lt","&gt"]:
			op=self.jackTokenizer.tok
			self.jackTokenizer.advance()
			self.compileTerm()
			self.VMWriter.writeArithmetic(op)		

class VMWriter:
	def __init__(self,outFile):
		self.outFile=outFile
	def writePush(self,segment,index):
		if segment=="field":
			self.outFile.write("push this "+str(index)+"\n")
		else:
			self.outFile.write("push "+str(segment)+" "+str(index)+"\n")
	def writePop(self,segment,index):
		if segment=="field":
			self.outFile.write("pop this "+str(index)+"\n")
		else:
			self.outFile.write("pop "+str(segment)+" "+str(index)+"\n")	
	def writeArithmetic(self,command): 
		if command=="+":
			self.outFile.write("add\n")
		elif command=="-":
			self.outFile.write("sub\n")
		elif command=="|":
			self.outFile.write("or\n")
		elif command=="&amp":
			self.outFile.write("and\n")
		elif command=="&lt":
			self.outFile.write("lt\n")
		elif command=="&gt":
			self.outFile.write("gt\n")
		elif command=="neg":
			self.outFile.write("neg\n")
		elif command=="not":
			self.outFile.write("not\n")
		elif command=="=":
			self.outFile.write("eq\n")
	def writeLabel(self,label):
		self.outFile.write("label "+label+"\n")
	def writeGoto(self,label):
		self.outFile.write("goto "+label+"\n")
	def writeIf(self,label):
		self.outFile.write("if-goto "+label+"\n")
	def writeCall(self,name,nArgs):
		self.outFile.write("call "+name+" "+str(nArgs)+"\n")
	def writeFunction(self,name,nLocals):
		self.outFile.write("function "+name+" "+str(nLocals)+"\n")
	def writeReturn(self):
		self.outFile.write("return\n")

def JackCompiler():
	inFile=open(sys.argv[1]+".jack","r")
	outFile=open(sys.argv[1]+".vm","w")
	jackTokenizer=JackTokenizer(inFile)
	compilationEngine=CompilationEngine(jackTokenizer,outFile)
	compilationEngine.compileClass()

JackCompiler()
