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
statement: statement ADD statement #SumStatement
    | statement SUB statement #SubStatement
    | statement MULT statement #MultStatement
    | statement DIV statement #DivStatement
    | function_call #FunctionCallStatement
    | '(' statement ')' #ParenthesisStatement
    | value #valueStatement
    ;
param: ID #idParameter
    | NUM #numParameter
    | ID ',' param #idParametersForMultipleIDs
    | NUM ',' param #numParametersForMultipleNums
    | #emptySpaceParameter
    ;
value: NUM #numValue
    | ID #idValue
    ;
arg: NUM
    | ID #idArgument
    | NUM ',' arg #numArguments
    | ID ',' arg #idArguments
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
