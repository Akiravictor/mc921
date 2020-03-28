grammar Summer;

root : stmt;
stmt : line ';'					#SingleLine
     | line ';' stmt			#MoreLine
     ;

line : 'var' ID '=' expr				#DeclareVar
     | 'func' ID '(' args ')' expr		#DeclareFunc
     ;

args : ID					#ArgId
     | ID ',' args			#MultArg
     ;

expr : expr '+' expr		#SumExpr
     | expr '-' expr		#MinExpr
     | expr '*' expr		#MulExpr
     | expr '/' expr		#DivExpr
     | ePar					#ExprParentesis
     | fUse					#CallFunc
     | NUM					#NUMExpr
     | ID					#IDExpr
     ;
	 
ePar : '(' expr ')' ;

fUse : ID '(' prmt ')' 		#FuncUse
     ;

prmt : fUse					#ParamFunc
     | ID ',' prmt			#IDParameter
     | NUM ',' prmt			#NUMParameter
     | ID					#IDOnly
     | NUM					#NUMOnly
     ;
	 
NUM : [0-9]+;
ID : [_a-zA-Z][_a-zA-Z0-9]*;
WS : [ \t\r\n]+ -> skip;

