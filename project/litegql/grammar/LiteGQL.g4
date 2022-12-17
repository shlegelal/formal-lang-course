grammar LiteGQL;

prog : (COMMENT? SEMI)* (stmt ((COMMENT? SEMI)+ stmt)*)? (COMMENT? SEMI)* EOF ;

stmt :
    PRINT LPAREN expr RPAREN
  | ID EQUALS expr
  ;

expr :
    SET_STARTS LPAREN expr COMMA expr RPAREN
  | SET_FINALS LPAREN expr COMMA expr RPAREN
  | ADD_STARTS LPAREN expr COMMA expr RPAREN
  | ADD_FINALS LPAREN expr COMMA expr RPAREN
  | GET_STARTS LPAREN expr RPAREN
  | GET_FINALS LPAREN expr RPAREN
  | GET_REACHABLES LPAREN expr RPAREN
  | GET_VERTICES LPAREN expr RPAREN
  | GET_EDGES LPAREN expr RPAREN
  | GET_LABELS LPAREN expr RPAREN
  | MAP LPAREN lambda COMMA expr RPAREN
  | FILTER LPAREN lambda COMMA expr RPAREN
  | LOAD LPAREN expr RPAREN
  | INT | BOOL | STR | REG | CFG              // val
  | ID                                        // var
  | LCURLY (expr (COMMA expr)*)? RCURLY       // Set
  | LPAREN expr COMMA expr RPAREN             // Pair
  | LPAREN expr COMMA expr COMMA expr RPAREN  // Edge
  | expr ASTER                                // Star
  | expr DOT expr                             // Concat
  | expr AMPER expr                           // Intersect
  | expr VLINE expr                           // Union
  | expr IN expr                              // Contains
  | LPAREN expr RPAREN                        // вложенное выражение
  ;

lambda : LCURLY pattern RARROW expr RCURLY ;

pattern :
    UNDER
  | ID
  | LPAREN pattern COMMA pattern RPAREN
  | LPAREN pattern COMMA pattern COMMA pattern RPAREN
  ;

SEMI : ';' ;

LPAREN : '(' ;
RPAREN : ')' ;
LCURLY : '{' ;
RCURLY : '}' ;

EQUALS : '=' ;
COMMA : ',' ;
RARROW : '->' ;
UNDER : '_' ;

ASTER : '*' ;
DOT : '.' ;
AMPER : '&' ;
VLINE : '|' ;
IN : 'in' ;

PRINT : 'print' ;

SET_STARTS : 'set_starts' ;
SET_FINALS : 'set_finals' ;
ADD_STARTS : 'add_starts' ;
ADD_FINALS : 'add_finals' ;
GET_STARTS : 'get_starts' ;
GET_FINALS : 'get_finals' ;
GET_REACHABLES : 'get_reachables' ;
GET_VERTICES : 'get_vertices' ;
GET_EDGES : 'get_edges' ;
GET_LABELS : 'get_labels' ;
MAP : 'map' ;
FILTER : 'filter' ;
LOAD : 'load' ;

ID : [_a-zA-Z][_a-zA-Z0-9]* ;

INT : '0' | '-'? [1-9][0-9]* ;
BOOL : 'true' | 'false' ;
STR : '"' .*? '"' ;
REG : 'r' STR ;
CFG : 'c' STR ;

COMMENT : '//' ~[\r\n]* -> skip ;
WS : [ \n\r\t\f]+ -> skip ;
