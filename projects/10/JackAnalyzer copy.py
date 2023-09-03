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

class CompilationEngine():
	def __init__(self, jackTokenizer, file):
		self.outFile=file
		self.jackTokenizer=jackTokenizer
	def wToken(self):
		if self.jackTokenizer.tokenType()=="INT_CONST":
			self.outFile.write("<integerConstant> "+self.jackTokenizer.tok+" </integerConstant>\n")
		elif self.jackTokenizer.tokenType()=="STRING_CONST":
			self.outFile.write("<stringConstant> "+self.jackTokenizer.tok.replace("\"", "")+" </stringConstant>\n")
		else:
			self.outFile.write("<"+self.jackTokenizer.tokenType().lower()+"> "+self.jackTokenizer.tok+" </"+self.jackTokenizer.tokenType().lower()+">\n")
	def compileClass(self):
		self.outFile.write("<class>\n")
		while self.jackTokenizer.hasMoreTokens:
			self.jackTokenizer.advance()
			if self.jackTokenizer.tok in ["static","field"]:
				self.compileClassVarDec()
			elif self.jackTokenizer.tok in ["method","function","constructor"]:
				self.compileSubroutine()
			elif self.jackTokenizer.tok in ["class","int","boolean","void"] or self.jackTokenizer.tokenType() in ["SYMBOL","INT_CONST","IDENTIFIER","STRING_CONST"]:
				self.wToken()
		self.outFile.write("</class>\n")
	def compileClassVarDec(self):
		self.outFile.write("<classVarDec>\n")
		self.wToken()
		while self.jackTokenizer.tok != ";":
			self.jackTokenizer.advance()
			self.wToken()
		self.outFile.write("</classVarDec>\n")
	def compileSubroutine(self):
		self.outFile.write("<subroutineDec>\n")
		self.wToken()
		while self.jackTokenizer.tok != "}":
			self.jackTokenizer.advance()
			if self.jackTokenizer.tok=="{":
				self.outFile.write("<subroutineBody>\n")
				self.wToken()
				while self.jackTokenizer.tok != "}":
					self.jackTokenizer.advance()
					if self.jackTokenizer.tok in ["let","do","if","while","return"]:
						self.compileStatements()
					elif self.jackTokenizer.tok=="var":
						self.compileVarDec()
					else:
						self.wToken()
				self.wToken()
				self.outFile.write("</subroutineBody>\n")
			elif self.jackTokenizer.tok=="(":
				self.compileParameterList()
			else:
				self.wToken()
		self.outFile.write("</subroutineDec>\n")
	def compileParameterList(self):
		self.wToken()
		self.outFile.write("<parameterList>\n")
		while self.jackTokenizer.tok2 != ")":
			self.jackTokenizer.advance()
			self.wToken()
		self.outFile.write("</parameterList>\n")
		self.jackTokenizer.advance()
		self.wToken()
	def compileVarDec(self):
		self.outFile.write("<varDec>\n")
		self.wToken()
		while self.jackTokenizer.tok!=";":
			self.jackTokenizer.advance()
			self.wToken()
		self.outFile.write("</varDec>\n")		
	def compileStatements(self):
		self.outFile.write("<statements>\n")
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
		self.outFile.write("</statements>\n")		
	def compileDo(self):
		self.outFile.write("<doStatement>\n")
		self.wToken()
		while self.jackTokenizer.tok!=";":
			self.jackTokenizer.advance()
			if self.jackTokenizer.tok=="(":
				self.compileExpressionList()
			else:
				self.wToken()
		self.outFile.write("</doStatement>\n")		
	def compileLet(self):
		self.outFile.write("<letStatement>\n")
		self.wToken()
		while self.jackTokenizer.tok!=";":
			self.jackTokenizer.advance()
			if self.jackTokenizer.tok in ["(","[","="]:
				self.wToken()
				self.compileExpression()
			else:
				self.wToken()
		self.outFile.write("</letStatement>\n")		
	def compileWhile(self):
		self.outFile.write("<whileStatement>\n")
		self.wToken()
		self.jackTokenizer.advance()
		self.wToken()
		self.compileExpression()
		while self.jackTokenizer.tok!="}":
			self.jackTokenizer.advance()
			if self.jackTokenizer.tok in ["let","do","if","while","return",";","}"]:
				self.compileStatements()
			else:
				self.wToken()
		self.wToken()
		self.outFile.write("</whileStatement>\n")			
	def compileReturn(self):
		self.outFile.write("<returnStatement>\n")
		self.wToken()
		if self.jackTokenizer.tok2!=";":
			self.compileExpression()
		else:
			self.jackTokenizer.advance()
			self.wToken()
		self.outFile.write("</returnStatement>\n")		
	def compileIf(self):
		self.outFile.write("<ifStatement>\n")
		self.wToken()
		self.jackTokenizer.advance()
		self.wToken()
		self.compileExpression()
		def ifandelse(self):
			while self.jackTokenizer.tok!="}":
				self.jackTokenizer.advance()
				if self.jackTokenizer.tok in ["let","do","if","while","return",";","}"]:
					self.compileStatements()
				else:
					self.wToken()
		ifandelse(self)
		if self.jackTokenizer.tok2=="else":
			self.wToken()
			self.jackTokenizer.advance()
			self.wToken()
			ifandelse(self)
		self.wToken()
		self.outFile.write("</ifStatement>\n")
	def compileExpression(self):
		neg = self.jackTokenizer.tok2=="-" and self.jackTokenizer.tok=="("
		self.outFile.write("<expression>\n")
		self.jackTokenizer.advance()
		while self.jackTokenizer.tok not in [")","]",",",";"]:
			if  not neg and self.jackTokenizer.tok in ["+","-","*","/","|","=","&amp;","&lt;","&gt;"]:
				self.wToken()
				self.jackTokenizer.advance()
			else:
				self.compileTerm()
		self.outFile.write("</expression>\n")
		self.wToken()
	def compileTerm(self):
		self.outFile.write("<term>\n")
		while self.jackTokenizer.tok not in [")","]",",",";"]:
			if self.jackTokenizer.tok=="[" or self.jackTokenizer.tok=="=":
				self.wToken()
				self.compileExpression()
			elif self.jackTokenizer.expression() and self.jackTokenizer.tok=="(":
				self.compileExpressionList()
			elif not self.jackTokenizer.expression() and self.jackTokenizer.tok=="(":
				self.wToken()
				self.compileExpression()
			elif self.jackTokenizer.tok=="~" or self.jackTokenizer.tok=="-":
				self.wToken()
				if self.jackTokenizer.tok2 in ["(","[","="]:
					self.jackTokenizer.advance()
					self.compileTerm()
				else:
					self.jackTokenizer.advance()
					self.outFile.write("<term>\n")
					self.wToken()
					self.outFile.write("</term>\n")			
			else:
				self.wToken()
			if self.jackTokenizer.tok!="(" and self.jackTokenizer.tok2 in ["+","-","*","/","|","=","&amp;","&lt;","&gt;"]:
				self.jackTokenizer.advance()
				break
			self.jackTokenizer.advance()
		self.outFile.write("</term>\n")

	def compileExpressionList(self):
		self.wToken()
		self.outFile.write("<expressionList>\n")
		self.jackTokenizer.advance()
		while self.jackTokenizer.tok!=")":
			self.outFile.write("<expression>\n")
			while self.jackTokenizer.tok not in ["]",",",";",")"]:
				if self.jackTokenizer.tok in ["+","-","*","/","|","=","&amp;","&lt;","&gt;"]:
					self.wToken()
					self.jackTokenizer.advance()
				else:
					self.compileTerm()
			self.outFile.write("</expression>\n")
		self.outFile.write("</expressionList>\n")
		self.wToken()

def JackAnalyzer():
	inFile=open(sys.argv[1]+".jack","r")
	outFile=open(sys.argv[1]+"generated.xml","w")
	jackTokenizer=JackTokenizer(inFile)
	compilationEngine=CompilationEngine(jackTokenizer,outFile)
	compilationEngine.compileClass()

JackAnalyzer()
