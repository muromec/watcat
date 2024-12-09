module: statement ARG_SPACE*

DOT: "."
UNDER: "_"
DIGIT: /[0-9]/

name : (LCASE_LETTER | UCASE_LETTER) ( UNDER | DOT | LCASE_LETTER | UCASE_LETTER| DIGIT )*

var_name : (UNDER | LCASE_LETTER | UCASE_LETTER) ( DOT | UNDER | LCASE_LETTER | UCASE_LETTER | DIGIT)*

COMMENT: /;;[^\n]*/

value: number | string | variable | name | statement

HEX_DIGIT: /[a-fA-F0-9]/

hex_number: ("0x" (HEX_DIGIT|UNDER)+)
dec_number: (DIGIT | UNDER)+

MINUS : "-"
number : MINUS? dec_number | hex_number

string: ESCAPED_STRING
variable: "$" var_name

ARG_SPACE: WS+
statement: "(" name ((ARG_SPACE value) | ARG_SPACE)* ")"



%ignore COMMENT

%import common.ESCAPED_STRING
%import common.SIGNED_NUMBER
%import common.WS
%import common.LCASE_LETTER
%import common.UCASE_LETTER
%ignore WS
