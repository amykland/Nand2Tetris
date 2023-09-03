#!/usr/bin/python
import sys, os

comp = {
	"0": "0101010",
	"1": "0111111",
	"-1": "0111010",
	"D": "0001100",
	"A": "0110000",
	"!D": "0001101",
	"!A": "0110001",
	"-D": "0001111",
	"-A": "0110011",
	"D+1": "0011111",
	"A+1": "0110111",
	"D-1": "0001110",
	"A-1": "0110010",
	"D+A": "0000010",
	"D-A": "0010011",
	"A-D": "0000111",
	"D&A": "0000000",
	"D|A": "0010101",
	"M": "1110000",
	"!M": "1110001",
	"-M": "1110011",
	"M+1": "1110111",
	"M-1": "1110010",
	"D+M": "1000010",
	"D-M": "1010011",
	"M-D": "1000111",
	"D&M": "1000000",
	"D|M": "1010101"
}

dest = {
	"null": "000",
	"M": "001",
	"D": "010",
	"MD": "011",
	"A": "100",
	"AM": "101",
	"AD": "110",
	"AMD": "111"
}

jump = {
	"null": "000",
	"JGT": "001",
	"JEQ": "010",
	"JGE": "011",
	"JLT": "100",
	"JNE": "101",
	"JLE": "110",
	"JMP": "111"
}

symbol = {
    "SP": 0,
    "LCL": 1,
    "ARG": 2,
    "THIS": 3,
    "THAT": 4,
    "R0":0,
    "R1":1,
    "R2":2,
    "R3":3,
    "R4":4,
    "R5":5,
    "R6":6,
    "R7":7,
    "R8":8,
    "R9":9,
    "R10":10,
    "R11":11,
    "R12":12,
    "R13":13,
    "R14":14,
    "R15":15,
    "SCREEN": 16384,
    "KBD": 24576,
}

#Opens and reads input file
pointer = 16


def removeBlanks(lines):
	outLines=""
	for line in lines:
		line=line.split("//",1)[0]	# Removes comments
		line=line.strip()	# Strips white spaces
		if not len(line)==0:	# Removes blank lines
			outLines=outLines+line+"\n"
	return outLines

def addlbl(lbl):
	global pointer
	symbol[lbl] = pointer
	pointer += 1
	return symbol[lbl];

def Ainstruct(line):
	if line[1].isdigit():
		a=int(line[1:])
	else:
		lbl=line[1:-1]
		a=symbol.get(lbl,-1)
		if a==-1:
			a=addlbl(lbl)
	a1=bin(a)[2:].zfill(16)
	return a1

def Cinstruct(line):
    if not ';' in line:
        line=line+';null'
    if not '=' in line:
        line='null='+line
    linesplit=line.split("=")
    destline=dest.get(linesplit[0].strip())
    linesplit=linesplit[1].split(";")
    compline=comp.get(linesplit[0].strip());
    jumpline=jump.get(linesplit[1].strip());
    return '111' + str(compline) + str(destline) + str(jumpline)

def AandCinstruct(line):
    if line[0]=="@":
        return Ainstruct(line)
    else:
        return Cinstruct(line)


def assemble1():
	file=open(sys.argv[1] + ".asm","r")
	lines=file.readlines()
	outFile=open(sys.argv[1] + ".tmp","w")
	outFile.writelines(removeBlanks(lines))
	file=open(sys.argv[1] + ".tmp","r")
	outFile=open(sys.argv[1] + "1" + ".tmp","w")
	lines=file.readlines()
	count=0
	for line in lines:
		if line[0]=="(":
			lbl=line.strip()[1:-1]
			symbol[lbl]=count
			line=""
		else:
			count+=1
			outFile.writelines(line)

def assemble2():
	file=open(sys.argv[1] + "1"+".tmp","r")
	lines=file.readlines()
	outFile=open(sys.argv[1] + ".hack","w")
	for line in lines:
		aandcline=AandCinstruct(line)
		outFile.writelines(aandcline+"\n")
	os.remove(sys.argv[1] + ".tmp")
	os.remove(sys.argv[1] +"1"+ ".tmp")

assemble1()
assemble2()