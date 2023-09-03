#!/usr/bin/python
import os, sys

class Parser:
  def __init__(self, file):
    self.inFile = open(file)
    self.done = False
    self.cmd = ""
    self.file=file

    self.cmdType = {
        "add" : "math",
        "sub" : "math",
        "neg" : "math",
        "eq"  : "math",
        "gt"  : "math",
        "lt"  : "math",
        "and" : "math",
        "or"  : "math",
        "not" : "math",
        "push" : "push",
        "pop"  : "pop",
        "label" : "C_LABEL",
        "goto" : "C_GOTO",
        "if-goto" : "C_IF",
        "function" : "C_FUNCTION",
        "return" : "C_RETURN",
        "call" : "C_CALL",
        }

  def hasMoreCommands(self):
    currentpos = self.inFile.tell()
    self.advance()
    self.inFile.seek(currentpos)
    return not self.done

  def advance(self):
    line = self.inFile.readline()
    if not len(line)==0:
      line = line.split("//",1)[0].strip()
      if not len(line)==0:
        self.cmd = line.split()
      else:
        self.advance()
    else:
      self.done = True

  def commandType(self):
    return self.cmdType.get(self.cmd[0])

  def arg1(self):
    return self.cmd[1]

  def arg2(self):
    return self.cmd[2]


class CodeWriter:
  def __init__(self, file):
    self.input = file[:-4].split('/')[-1]
    self.outFile = open(file, "w")
    self.count = 0
    self.ret=0
    self.fileName=""

  def setFileName(self, file):
    self.fileName = file.split("/")[-1].replace(".vm","")

  def writeArithmetic(self, command):
    lines=""
    if command=="add":
      lines+="@SP\n"
      lines+="AM=M-1\n"
      lines+="D=M\n"
      lines+="A=A-1\n"
      lines+="M=D+M\n" 
    elif command=="sub":
      lines+="@SP\n"
      lines+="AM=M-1\n"
      lines+="D=M\n"
      lines+="A=A-1\n"
      lines+="M=M-D\n"
    elif command=="neg":
      lines+="@SP\n"
      lines+="A=M-1\n" 
      lines+="M=-M\n"
    elif command=="eq":
      num=str(self.count)
      self.count += 1
      lines+="@SP\n"
      lines+="AM=M-1\n"
      lines+="D=M\n" 
      lines+="A=A-1\n"
      lines+="D=M-D\n"
      lines+="M=-1\n"
      lines+="@eqEND" + num + "\n"
      lines+="D;JEQ\n"
      lines+="@SP\n"
      lines+="A=M-1\n"
      lines+="M=0\n" 
      lines+="(eqEND" + num + ")\n"
    elif command=="gt":
      num=str(self.count)
      self.count+=1
      lines+="@SP\n"
      lines+="AM=M-1\n"
      lines+="D=M\n" 
      lines+="A=A-1\n"
      lines+="D=M-D\n"
      lines+="M=-1\n"
      lines+="@gtEND" + num + "\n"
      lines+="D;JGT\n"
      lines+="@SP\n"
      lines+="A=M-1\n"
      lines+="M=0\n" 
      lines+="(gtEND" + num + ")\n"
    elif command=="lt":
      num=str(self.count)
      self.count+=1
      lines+="@SP\n"
      lines+="AM=M-1\n"
      lines+="D=M\n" 
      lines+="@SP\n"
      lines+="A=M-1\n"
      lines+="D=M-D\n"
      lines+="M=-1\n"
      lines+="@ltEND"+num+"\n"
      lines+="D;JLT\n"
      lines+="@SP\n"
      lines+="A=M-1\n"
      lines+="M=0\n" 
      lines+="(ltEND"+num+")\n"
    elif command=="and":
      lines+="@SP\n"
      lines+="AM=M-1\n"
      lines+="D=M\n" 
      lines+="A=A-1\n"
      lines+="M=D&M\n"
    elif command=="or":
      lines+="@SP\n"
      lines+="AM=M-1\n"
      lines+="D=M\n" 
      lines+="A=A-1\n"
      lines+="M=D|M\n"
    elif command=="not":
      lines+="@SP\n"
      lines+="A=M-1\n" 
      lines+="M=!M\n"
    self.outFile.write(lines)

  def writePushPop(self, command, segment, index):
    lines=""
    if command=="push":
      if segment=="argument":
        lines+="@" + index + "\n"
        lines+="D=A\n"
        lines+="@ARG\n"
        lines+="A=M+D\n" 
        lines+="D=M\n"
        lines+="@SP\n"
        lines+="M=M+1\n"
        lines+="A=M-1\n"
        lines+="M=D\n"
      elif segment=="local":
        lines+="@LCL\n"
        lines+="D=M\n"
        lines+="@" + index + "\n"
        lines+="A=D+A\n"
        lines+="D=M\n" 
        lines+="@SP\n"
        lines+="M=M+1\n"
        lines+="A=M-1\n"
        lines+="M=D\n"
      elif segment=="static":
        lines+= "@" + self.fileName + "." + index + "\n"
        lines+= "D=M\n"
        lines+= "@SP\n" 
        lines+= "M=M+1\n"
        lines+= "A=M-1\n" 
        lines+= "M=D\n"
      elif segment=="constant":
        lines+="@" + index + "\n"
        lines+="D=A\n"
        lines+="@SP\n"
        lines+="M=M+1\n"
        lines+="A=M-1\n"
        lines+="M=D\n"
      elif segment == "this":
        lines+= "@" + index + "\n"
        lines+= "D=A\n"
        lines+= "@THIS\n"
        lines+= "A=M+D\n" 
        lines+= "D=M\n"
        lines+= "@SP\n"
        lines += "M=M+1\n"
        lines += "A=M-1\n"
        lines += "M=D\n"
      elif segment == "that":
        lines += "@" + index + "\n"
        lines += "D=A\n"
        lines += "@THAT\n"
        lines += "A=M+D\n" 
        lines += "D=M\n"
        lines += "@SP\n"
        lines += "M=M+1\n"
        lines += "A=M-1\n"
        lines += "M=D\n"
      elif segment=="pointer":
        lines += "@" + index + "\n"
        lines += "D=A\n"
        lines += "@3\n"
        lines += "A=A+D\n" 
        lines += "D=M\n"
        lines += "@SP\n"
        lines += "M=M+1\n"
        lines += "A=M-1\n"
        lines += "M=D\n"
      elif segment=="temp":
        lines += "@" + index + "\n"
        lines += "D=A\n"
        lines += "@5\n"
        lines += "A=A+D\n" 
        lines += "D=M\n"
        lines += "@SP\n"
        lines += "M=M+1\n"
        lines += "A=M-1\n"
        lines += "M=D\n"
    elif command=="pop":
      if segment=="argument":
        lines+="@" + index + "\n"
        lines += "D=A\n"
        lines += "@ARG\n"
        lines += "D=M+D\n" 
        lines += "@R13\n"
        lines += "M=D\n"
        lines += "@SP\n"
        lines += "AM=M-1\n"
        lines += "D=M\n"
        lines += "@R13\n"
        lines += "A=M\n"
        lines += "M=D\n"
      elif segment == "local":
        lines += "@LCL\n"
        lines += "D=M\n"
        lines += "@" + index + "\n"
        lines += "D=D+A\n" 
        lines += "@R13\n"
        lines += "M=D\n"
        lines += "@SP\n"
        lines += "AM=M-1\n"
        lines += "D=M\n"
        lines += "@R13\n"
        lines += "A=M\n"
        lines += "M=D\n"
      elif segment == "static":
        lines += "@SP\n"
        lines += "AM=M-1\n"
        lines += "D=M\n"
        lines += "@" + self.fileName + "." + index + "\n"
        lines += "M=D\n"
      elif segment == "this":
        lines += "@" + index + "\n"
        lines += "D=A\n"
        lines += "@THIS\n"
        lines += "D=M+D\n" 
        lines += "@R13\n"
        lines += "M=D\n"
        lines += "@SP\n"
        lines += "AM=M-1\n"
        lines += "D=M\n"
        lines += "@R13\n"
        lines += "A=M\n"
        lines += "M=D\n"
      elif segment == "that":
        lines += "@" + index + "\n"
        lines += "D=A\n"
        lines += "@THAT\n"
        lines += "D=M+D\n" 
        lines += "@R13\n"
        lines += "M=D\n"
        lines += "@SP\n"
        lines += "AM=M-1\n"
        lines += "D=M\n"
        lines += "@R13\n"
        lines += "A=M\n"
        lines += "M=D\n"
      elif segment == "pointer":
        lines += "@" + index + "\n"
        lines += "D=A\n"
        lines += "@3\n"
        lines += "D=A+D\n" 
        lines += "@R13\n"
        lines += "M=D\n"
        lines += "@SP\n"
        lines += "AM=M-1\n"
        lines += "D=M\n"
        lines += "@R13\n"
        lines += "A=M\n"
        lines += "M=D\n"
      elif segment == "temp":
        lines+="@" + index + "\n"
        lines+="D=A\n"
        lines+="@5\n"
        lines+="D=A+D\n" 
        lines+="@R13\n"
        lines+="M=D\n"
        lines+="@SP\n"
        lines+="AM=M-1\n"
        lines+="D=M\n"
        lines+="@R13\n"
        lines+="A=M\n"
        lines+="M=D\n"
    self.outFile.write(lines)
  def writeInit(self):
    lines=""
    lines+="@256\n"
    lines+="D=A\n"
    lines+="@SP\n"
    lines+="M=D\n"
    self.outFile.write(lines)
    self.writeCall("Sys.init",0)
  def writeLabel(self,label):
    self.outFile.write("("+label+")\n")
  def writeGoto(self,label):
    lines=""
    lines+="@"+label+"\n"
    lines+="0;JMP\n"
    self.outFile.write(lines)
  def writeIf(self,label):
    lines=""
    lines+="@SP\n"
    lines+="AM=M-1\n"
    lines+="D=M\n"
    lines+="@"+label+"\n"
    lines+="D;JNE\n"
    self.outFile.write(lines)
  def writeCall(self,functionName,numArgs):
    lines=""
    lines+="@"+functionName+"RETURN"+str(self.ret)+"\n"
    lines+="D=A\n"
    lines+="@SP\n"
    lines+="A=M\n"
    lines+="M=D\n"
    lines+="@SP\n"
    lines+="M=M+1\n"
    lines+="@LCL\n"
    lines+="D=M\n"
    lines+="@SP\n"
    lines+="A=M\n"
    lines+="M=D\n"
    lines+="@SP\n"
    lines+="M=M+1\n"
    lines+="@ARG\n"
    lines+="D=M\n"
    lines+="@SP\n"
    lines+="A=M\n"
    lines+="M=D\n"
    lines+="@SP\n"
    lines+="M=M+1\n"
    lines+="@THIS\n"
    lines+="D=M\n"
    lines+="@SP\n"
    lines+="A=M\n"
    lines+="M=D\n"
    lines+="@SP\n"
    lines+="M=M+1\n"
    lines+="@THAT\n"
    lines+="D=M\n"
    lines+="@SP\n"
    lines+="A=M\n"
    lines+="M=D\n"
    lines+="@SP\n"
    lines+="M=M+1\n"
    lines+="@SP\n"
    lines+="D=M\n"
    lines+="@"+str(numArgs)+"\n"
    lines+="D=D-A\n"
    lines+="@5\n"
    lines+="D=D-A\n"
    lines+="@ARG\n"
    lines+="M=D\n"
    lines+="@SP\n"
    lines+="D=M\n"
    lines+="@LCL\n"
    lines+="M=D\n"
    lines+="@"+functionName+"\n"
    lines+="0;JMP\n"
    lines+="("+functionName+"RETURN"+str(self.ret)+")\n"
    self.ret+=1
    self.outFile.write(lines)
  def writeReturn(self):
    lines=""
    lines+="@LCL\n"
    lines+="D=M\n"
    lines+="@R13\n"
    lines+="M=D\n"
    lines+="@R13\n"
    lines+="D=M\n"
    lines+="@5\n"
    lines+="AD=D-A\n"
    lines+="D=M\n"
    lines+="@R14\n"
    lines+="M=D\n"
    lines+="@SP\n"
    lines+="M=M-1\n"
    lines+="A=M\n"
    lines+="D=M\n"
    lines+="@ARG\n"
    lines+="A=M\n"
    lines+="M=D\n"
    lines+="@ARG\n"
    lines+="M=M+1\n"
    lines+="D=M\n"
    lines+="@SP\n"
    lines+="M=D\n"
    lines+="@R13\n"
    lines+="D=M\n" 
    lines+="@1\n"
    lines+="AD=D-A\n"
    lines+="D=M\n" 
    lines+="@THAT\n"
    lines+="M=D\n"#here
    lines+="@R13\n"
    lines+="D=M\n"
    lines+="@2\n"
    lines+="AD=D-A\n"
    lines+="D=M\n"
    lines+="@THIS\n"
    lines+="M=D\n"
    lines+="@R13\n"
    lines+="D=M\n" 
    lines+="@3\n"
    lines+="AD=D-A\n"
    lines+="D=M\n"
    lines+="@ARG\n"
    lines+="M=D\n"
    lines+="@R13\n"
    lines+="D=M\n"
    lines+="@4\n"
    lines+="AD=D-A\n"
    lines+="D=M\n"
    lines+="@LCL\n" 
    lines+="M=D\n"
    lines+="@R14\n"
    lines+="A=M\n"
    lines+="0;JMP\n"
    self.outFile.write(lines)
  def writeFunction(self,functionName,numLocals):
    lines=""
    lines+="("+functionName+")\n"
    for i in range(int(numLocals)):
      lines+="D=0\n"
      lines+="@SP\n"
      lines+="A=M\n"
      lines+="M=D\n"
      lines+="@SP\n"
      lines+="M=M+1\n"
    self.outFile.write(lines)
def VM2():
  input = sys.argv[1]
  files=[]
  for x,y,allFiles in os.walk(input):
    for file in allFiles:
      if file.find(".vm")!=-1:
        files.append(input+"/"+file)
  outFile=input+"/"+input.split("/")[-1]+".asm"
  w=CodeWriter(outFile)
  w.writeInit()
  for file in files:
    w.setFileName(file)
    p = Parser(file)
    while p.hasMoreCommands():
      p.advance()
      cmdType = p.commandType()
      if cmdType == "math":
        w.writeArithmetic(p.cmd[0])
      elif cmdType == "push" or cmdType == "pop":
        w.writePushPop(cmdType, p.arg1(), p.arg2())
      elif cmdType == "C_LABEL":
        w.writeLabel(p.arg1())
      elif cmdType=="C_GOTO":
        w.writeGoto(p.arg1())
      elif cmdType=="C_IF":
        w.writeIf(p.arg1())
      elif cmdType=="C_FUNCTION":
        w.writeFunction(p.arg1(), p.arg2())
      elif cmdType=="C_RETURN":
        w.writeReturn()
      elif cmdType=="C_CALL":
        w.writeCall(p.arg1(), p.arg2())
VM2()