grammar GQLang;

prog : EOL* (stmt EOL+)* (stmt COMMENT?)? EOF;

stmt :
      PRINT LP expr RP
    | VAR EQUALS expr
    ;

expr :
      expr DOT SET_STARTS LP expr RP
    | expr DOT SET_FINALS LP expr RP
    | expr DOT ADD_STARTS LP expr RP
    | expr DOT ADD_FINALS LP expr RP
    | expr DOT STARTS
    | expr DOT FINALS
    | expr DOT REACHABLES
    | expr DOT NODES
    | expr DOT EDGES
    | expr DOT LABELS
    | MAP LP LC pattern ARROW expr RC  COMMA expr RP
    | FILTER LP LC pattern ARROW expr RC  COMMA expr RP
    | LOAD_DOT LP (VAR | STR) RP
    | LOAD_GRAPH LP (VAR | STR) RP
    | LP expr  COMMA expr RP                        // Pair
    | LP expr  COMMA expr  COMMA expr RP            // Triple
    | LC INT DOTS INT RC                            // Range
    | expr AMPER expr                               // Intersect
    | expr CARET expr                               // Concat
    | expr PIPE expr                                // Union
    | expr ASTER                                    // Star
    | LC (expr ( COMMA expr)* )? RC                 // Set
    | expr IN expr                                  // Contains
    | REGEX | CFG | STR | INT | BOOL
    | NOT expr
    | VAR
    | LP expr RP
    ;


pattern :
    UNDER
  | VAR
  | LP pattern  COMMA pattern RP
  | LP pattern  COMMA pattern  COMMA pattern RP
  ;

PRINT : 'print';
SET_STARTS : 'set_starts';
SET_FINALS : 'set_finals';
ADD_STARTS : 'add_starts';
ADD_FINALS : 'add_finals';
STARTS : 'starts';
FINALS : 'finals';
REACHABLES : 'reachables';
VERTICES : 'vertices';
NODES : 'nodes';
EDGES : 'edges' ;
LABELS : 'labels';
MAP : 'map';
FILTER : 'filter';
LOAD_DOT : 'load_dot';
LOAD_GRAPH : 'load_graph';

EQUALS : '=';
ARROW : '->';
COMMA : ',';
DOT : '.';
DOTS : '..';
ASTER : '*';
NOT : 'not';
AMPER : '&';
PIPE : '|';
CARET : '^';
UNDER : '_';
IN : 'in';
AND : '&&';
OR : '||';
LP : '(';
RP : ')';
LC : '{';
RC : '}';

STR : '"' ~[\n]* '"';
INT : '-'? [1-9][0-9]* | '0';
BOOL : 'true' | 'false';
REGEX : 'r' STR;
CFG : 'c' STR;
VAR : [a-zA-Z_][a-zA-Z0-9_]*;

EOL : '\n';

COMMENT : '#' ~[\n]* -> skip;
FULL_COMMENT : COMMENT '\n' -> skip;
WS : [ \t]+ -> skip;
