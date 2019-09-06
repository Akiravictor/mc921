#!/bin/bash

fix_c_code(){
	input=$1
	output=${2}_corrected.c

	printf "\tBEGIN: Code Cleanup\n"
	printf "\t\tINPUT: "${input}"\n"
	
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
	
	printf "\t\tOUTPUT: "${output}"\n"	
	printf "\tEND: Code Cleanup\n\n"
}

exec_scanner(){
	input=$1
	output=${2}_tokens.txt
	
	printf "\tBEGIN: Token extraction\n"
	printf "\t\tINPUT: "${input}"\n"
	
	./scanner < $input > $output
	
	printf "\t\tOUTPUT: "${output}"\n"	
	printf "\tEND: Token extraction\n\n"

}

exec_select(){
	input=$1
	output=${2}_selected.txt
	
	printf "\tBEGIN: Select tokens\n"
	printf "\t\tINPUT: "${input}"\n"
	
	sed -E -n "/\bT_ID\b|\bT_NUM\b|\bT_STR\b/p" $input > $output

	printf "\t\tOUTPUT: "${output}"\n"	
	printf "\tEND: Select tokens\n\n"
}

exec_diff(){
	input_1=$1
	input_2=$2
	output=${1}_diff.txt

	printf "\tBEGIN: Compare with results\n"
	printf "\t\tINPUT_1: "${input_1}"\n"
	printf "\t\tINPUT_2: "${input_2}"\n"
	
	diff $input_1 $input_2 > $output
	
	printf "\t\tOUTPUT: "${output}"\n"
	printf "\tEND: Compare with results\n\n"
}

### MAIN ###

main(){
	
	if [ ! -z $1 ]; then
		if [ $1 = "clean" ]; then
			printf "Remove generated files\n";
			
			rm *_selected.txt
			rm *_tokens.txt
			rm *_corrected.c
			rm *_diff.txt
		
		else
			printf ${1}" is not recognized\n"
		fi
	
	else
	
		printf "BEGIN: Main\n"
		printf "\tBEGIN: Compile scanner\n"
		
		flex -i -o scan.c scan.l
		gcc -g -o scanner scanner.c scan.c
		
		printf "\tEND: Compile scanner\n\n"
		
		for f in code*.c; do
			fix_c_code $f ${f:0:5};
		done
		
		for f in code*_corrected.c; do
			exec_scanner $f ${f:0:5};
		done
		
		for f in code*_tokens.txt; do
			exec_select $f ${f:0:5};
		done
		
		for f in code*_corrected.c; do
			exec_diff $f results/${f};
		done
		
		for f in code*_tokens.txt; do
			exec_diff $f results/${f};
		done
		
		for f in code*_selected.txt; do
			exec_diff $f results/${f};
		done
		
		printf "END: Main\n"
	
	fi
	
}

### MAIN ###

main $1

