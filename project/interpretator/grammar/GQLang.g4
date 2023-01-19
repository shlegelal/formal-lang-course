grammar GQLang;

prog : EOL* (stmt EOL+)* (stmt COMMENT?)? EOF;

stmt :
      PRINT LP expr RP # print
    | VAR EQUALS expr # bind
    ;

expr :
      expr DOT SET_STARTS LP expr RP # setStarts
    | expr DOT SET_FINALS LP expr RP # setFinals
    | expr DOT ADD_STARTS LP expr RP # addStarts
    | expr DOT ADD_FINALS LP expr RP # addFinals
    | expr DOT STARTS # getStarts
    | expr DOT FINALS # getFinals
    | expr DOT REACHABLE # getReachable
    | expr DOT NODES # getNodes
    | expr DOT EDGES # getEdges
    | expr DOT LABELS # getLabels
    | MAP LP lambda COMMA expr RP # map
    | FILTER LP lambda COMMA expr RP # filter
    | LOAD_DOT LP (VAR | STR) RP # load_dot
    | LOAD_GRAPH LP (VAR | STR) RP # load_graph
    | LP expr COMMA expr RP # pair
    | LP expr COMMA expr  COMMA expr RP # triple
    | LC INT DOTS INT RC # range
    | expr AMPER expr # intersect
    | expr CARET expr # concat
    | expr PIPE expr # union
    | expr ASTER # star
    | LC (expr ( COMMA expr)* )? RC # set
    | expr IN expr # contains
    | REGEX # reg
    | CFG # cfg
    | STR # string
    | INT # int
    | BOOL # bool
    | NOT expr # not
    | VAR # var
    | LP expr RP # parens
    ;

lambda : LC pattern ARROW expr RC;

pattern :
    UNDER # wildcard
  | VAR # name
  | LP pattern  COMMA pattern RP # unpair
  | LP pattern  COMMA pattern  COMMA pattern RP # untriple
  ;

PRINT : 'print';
SET_STARTS : 'set_starts';
SET_FINALS : 'set_finals';
ADD_STARTS : 'add_starts';
ADD_FINALS : 'add_finals';
STARTS : 'starts';
FINALS : 'finals';
REACHABLE : 'reachable';
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
