grammar gramatica;

root : codigo;
codigo : linha ';'                              #PrimeiraLin
       | linha ';' codigo                       #ExpandeCod
       ;
linha: 'var' ID '=' expressao                   #Declara
     | 'func' ID '(' argumentos ')' expressao   #Define
     ;
argumentos: ID                                  #PrimeiroArg
          | ID ',' argumentos                   #ExpandeArg
          ;
expressao: comeco                               #Gambiarra
         | produto                              #Multiplica
         | soma                                 #Adiciona
         | resto                                #Subtrai
         | razao                                #Divide
         ;
comeco: chamada                                 #ChamaFunc
      | parenteses                              #Agrupa
      | fixo                                    #Invariavel
      ;
chamada:    ID '(' parametros ')';
parametros: fixo                                #PrimeiroParam
          | fixo ',' parametros                 #ExpandeParam
          ;
fixo: NUM                                       #ConstanteNum                                      
    | ID                                        #ConstanteId
    ;
produto:    comeco '*' expressao;
soma:       comeco '+' expressao;
resto:      comeco '-' expressao;
razao:      comeco '/' expressao;
parenteses: '(' expressao ')';
NUM :       [0-9]+;
ID :        [_a-zA-Z][_a-zA-Z0-9]*;
PATAVINA: (' ' | '\t' | '\n')+ -> channel(HIDDEN);

