// This file is part of www.nand2tetris.org
// and the book "The Elements of Computing Systems"
// by Nisan and Schocken, MIT Press.
// File name: projects/04/Fill.asm

// Runs an infinite loop that listens to the keyboard input.
// When a key is pressed (any key), the program blackens the screen,
// i.e. writes "black" in every pixel;
// the screen should remain fully black as long as the key is pressed. 
// When no key is pressed, the program clears the screen, i.e. writes
// "white" in every pixel;
// the screen should remain fully clear as long as no key is pressed.

// Put your code here.

(RESET)    //sets i to 8192
	@8192
	D=A
	@i
	M=D

(COUNTER)
	@i
	M=M-1
	D=M    //i counts down from 8192 to 0, since there are 8192 pixels on the screen
	@RESET
	D;JLT
	@KBD
	D=M
	@WHITE
	D;JEQ  //jumps to WHITE if nothing is pressed
	@BLACK
	D;JGT  //othewise jumps to BLACK

(WHITE)
	@SCREEN
	D=A
	@i
	A=D+M   //sets address to i greater than the first screeen pixel
	M=0     //sets pixel white
	@COUNTER
	0;JMP

(BLACK)
	@SCREEN
	D=A
	@i
	A=D+M     //sets address to i greater than the first screeen pixel
	M=-1     //sets pixel black
	@COUNTER
	0;JMP


