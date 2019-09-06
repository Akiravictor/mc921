#!/bin/bash

fix_c_code(){
	input=$1
	output="corrected.c"

	#printf "\tBEGIN: Code Cleanup\n"
	#printf "\t\tINPUT: "${input}"\n"
	
	sed "/TEST/d" < $input > $output

	sed -i "s/\bVOID\b/void/g" $output
	sed -i "s/\bINT\b/int/g" $output
	sed -i "s/\bFLOAT\b/float/g" $output
	sed -i "s/\bCHAR\b/char/g" $output
	sed -i "s/\bLONG\b/long/g" $output
	sed -i "s/\bDOUBLE\b/double/g" $output
	sed -i "s/\bENUM\b/enum/g" $output
	
	sed -i "s/\bSIGNED\b/signed/g" $output
	sed -i "s/\bUNSIGNED\b/unsigned/g" $output
	
	sed -i "s/\bSTRUCT\b/struct/g" $output
	sed -i "s/\bTYPEDEF\b/typedef/g" $output
	
	sed -i "s/\bIF\b/if/g" $output
	sed -i "s/\bELSE\b/else/g" $output
	sed -i "s/\bFOR\b/for/g" $output
	sed -i "s/\bDO\b/do/g" $output
	sed -i "s/\bWHILE\b/while/g" $output
	sed -i "s/\bSWITCH\b/switch/g" $output
	sed -i "s/\bCASE\b/case/g" $output
	sed -i "s/\bBREAK\b/break/g" $output
	sed -i "s/\bCONTINUE\b/continue/g" $output
	sed -i "s/\bDEFAULT\b/default/g" $output
	
	sed -i "s/\bUNION\b/union/g" $output
	sed -i "s/\bSTATIC\b/static/g" $output
	sed -i "s/\bVOLATILE\b/volatile/g" $output
	sed -i "s/\bSIZEOF\b/sizeof/g" $output
	sed -i "s/\bRETURN\b/return/g" $output
	
	#printf "\t\tOUTPUT: "${output}"\n"	
	#printf "\tEND: Code Cleanup\n\n"
}

exec_scanner(){
	input="corrected.c"
	output="tokens.txt"
	
	#printf "\tBEGIN: Token extraction\n"
	#printf "\t\tINPUT: "${input}"\n"
	
	./scanner < $input > $output
	
	#printf "\t\tOUTPUT: "${output}"\n"	
	#printf "\tEND: Token extraction\n\n"

}

exec_select(){
	input="tokens.txt"
	output="selected.txt"
	
	#printf "\tBEGIN: Select tokens\n"
	#printf "\t\tINPUT: "${input}"\n"
	
	sed -E -n "/\bT_ID\b|\bT_NUM\b|\bT_STR\b/p" $input > $output

	#printf "\t\tOUTPUT: "${output}"\n"	
	#printf "\tEND: Select tokens\n\n"
}

main(){
	
	
	#printf "BEGIN: Main\n"
	#printf "\tBEGIN: Compile scanner\n"
	
	flex -i -o scan.c scan.l
	gcc -g -o scanner scanner.c scan.c
	
	#printf "\tEND: Compile scanner\n\n"
	
	fix_c_code $1
	exec_scanner
	exec_select

	#printf "END: Main\n"	
}

### MAIN ###

main $1

