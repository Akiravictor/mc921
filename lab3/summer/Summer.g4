grammar Summer;

root : expr;
expr: var_decl #expressionVariableDeclaration
    | func_decl #expressionFunctionDeclaration
    | expr ';' expr #expressionSameLineExpressions
    | #emptyExpression
    ;
var_decl: VAR ID '=' statement;
func_decl: FUNC ID '(' param ')' statement;
function_call: ID '(' arg ')';
statement: statement ADD statement
    | statement SUB statement
    | statement MULT statement
    | statement DIV statement
    | function_call
    | '(' statement ')'
    | value
    ;
param: ID
    | NUM
    | ID ',' param 
    | NUM ',' param
    | 
    ;
value: NUM
    | ID
    ;
arg: NUM
    | ID
    | NUM ',' arg
    | ID ',' arg
    | 
    ;
VAR: 'var';
FUNC: 'func';
ID: [_A-Za-z0-9]+;
MULT: '*';
DIV: '/';
ADD : '+';
SUB: '-';
NUM : [0-9]+;
WS: [ \t\r\n]+ -> skip;
