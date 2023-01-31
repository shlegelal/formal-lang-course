# Cинтаксиса языка запросов к графам

## Абстрактный синтаксис

```
prog = List<stmt>

stmt =
    bind of var * expr
  | print of expr

val =
    String of string
  | Int of int
  | Bool of bool
  | Regex of srting
  | Cfg of string

expr =
    Var of var                   // переменные
  | Val of val                   // константы
  | Set_start of expr * expr     // задать множество стартовых состояний
  | Set_final of expr * expr     // задать множество финальных состояний
  | Add_start of expr * expr     // добавить состояния в множество стартовых
  | Add_final of expr * expr     // добавить состояния в множество финальных
  | Get_start of expr            // получить множество стартовых состояний
  | Get_final of expr            // получить множество финальных состояний
  | Get_reachable of expr        // получить все пары достижимых вершин
  | Get_vertices of expr         // получить все вершины
  | Get_edges of expr            // получить все рёбра
  | Get_labels of expr           // получить все метки
  | Map of lambda * expr         // классический map
  | Filter of lambda * expr      // классический filter
  | Load_dot of path             // загрузка графа из дот файла
  | Load_graph of string         // загрузка графа из базы данных
  | Intersect of expr * expr     // пересечение языков
  | Concat of expr * expr        // конкатенация языков
  | Union of expr * expr         // объединение языков
  | Star of expr                 // замыкание языков (звезда Клини)
  | Contains of expr * expr
  | Set of List<expr>
  | Not of expr
  | And of expr * expr
  | Or expr * expr
  | Range of int * int

lambda = Lambda of pattern * expr

pattern =
    Wildcard                                 // отбрасывание значения
  | Name of string                           // именование значения
  | Unpair of pattern * pattern              // раскрытие пары
  | Untriple of pattern * pattern * pattern  // раскрытие тройки
```

## Конкретный синтаксис

```
prog -> EOL* ((COMMENT EOL+ )* stmt (WS COMMENT)? EOL+ (COMMENT EOL+ )* )*

stmt ->
      var WS '=' WS expr
    | 'print' '(' expr ')'

expr ->
      var
    | val
    | bool
    | graph
    | set
    | '(' expr ',' WS expr ')'                   // Pair
    | '(' expr ',' WS expr ',' WS expr ')'       // Triple
    | '(' expr ')'

graph ->
      var | REGEX | CFG
    | graph '.' 'set_starts' '(' set ')'
    | graph '.' 'set_finals' '(' set ')'
    | graph '.' 'add_starts' '(' set ')'
    | graph '.' 'add_finals' '(' set ')'
    | 'load_dot' '(' (var | STR) ')'
    | 'load_graph' '(' (var | STR) ')'
    | graph WS '&' WS graph                      // Intersect
    | graph WS '^' WS graph                      // Concat
    | graph WS '|' WS graph                      // Union
    | graph '*'                                  // Star
    | '(' graph ')'

bool ->
      var
    | 'true' | 'false'
    | expr WS 'in' WS expr                       // Contains
    | 'not' WS bool
    | '(' bool ')'

set ->
      var
    | '{' INT WS '..' WS INT '}'                 // Range
    | '{' (expr (',' WS expr)* )? '}'            // Set
    | graph '.' 'starts'
    | graph '.' 'finals'
    | graph '.' 'reachable'
    | graph '.' 'nodes'
    | graph '.' 'edges'
    | graph '.' 'labels'
    | 'map' '(' '{' pattern WS '->' WS expr '}' ',' WS set ')'
    | 'filter' '(' '{' pattern WS '->' WS bool '}' ',' WS set ')'
    | '(' set ')'

pattern ->
    '_'
  | var
  | '(' pattern ',' pattern ')'
  | '(' pattern ',' pattern ',' pattern ')'

var -> [a-zA-Z_][a-zA-Z_0-9]*
val -> STR | INT

STR -> '"' ~[\n]* '"'
INT -> '-'? [1-9][0-9]*
REGEX -> 'r' STR
CFG -> 'c' STR

COMMENT -> '//' ~[\n]*
EOL -> [\n]+
WS -> [ \t]+
```

## Примеры

Получение достижимых вершин из данного множетсва
```
g = load_graph("skos").set_starts({0 .. 10})

res = map({(_, f) -> f}, g.reachable)
```

Получение пар вершин, между которыми существует путь, удовлетворяющий КС-ограничению
```
g = c"S -> a S b | a b"
r = r"a b"

res = map({((u, _), (v, _)) -> (u, v)}, (g & r).reachable)

print(res)
```

Получение множества общих меток графов "wine" и "pizza"
```
g_w = load_graph("wine")
g_p = load_graph("pizza")

common_labels = filter({l -> l in g_w.labels}, g_p.labels)

print(common_labels)
```
