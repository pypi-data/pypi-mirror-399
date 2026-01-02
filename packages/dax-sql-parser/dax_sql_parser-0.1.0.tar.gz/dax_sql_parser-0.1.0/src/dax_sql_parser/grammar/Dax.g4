grammar Dax;

/*
 * DAX Grammar for Python Target
 * Supports DAX functions including AND(), OR(), NOT() as both functions and operators
 */

// Entry point
query
    : EVALUATE tableExpression (orderClause)? EOF
    ;

orderClause
    : ORDER BY orderExpression (COMMA orderExpression)*
    ;

orderExpression
    : expression (ASC | DESC)?
    ;

// Expressions
expression
    : varExpression
    | logicalOr
    ;

varExpression
    : VAR IDENTIFIER EQ expression (varExpression | RETURN expression)
    ;

logicalOr
    : logicalAnd (OR_OP logicalAnd)*
    ;

logicalAnd
    : equality (AND_OP equality)*
    ;

equality
    : relational ((EQ | NEQ) relational)*
    ;

relational
    : additive ((LT | LTE | GT | GTE | IN) additive)*
    ;

additive
    : multiplicative ((PLUS | MINUS | AMPERSAND) multiplicative)*
    ;

multiplicative
    : unary ((ASTERISK | SLASH) unary)*
    ;

unary
    : (PLUS | MINUS | NOT_OP) unary
    | primaryExpression
    ;

primaryExpression
    : literal
    | columnReference
    | tableReference
    | functionCall
    | constructor  // Allow { ... } as primary expression for IN logic
    | OPEN_PAREN expression CLOSE_PAREN
    ;

// Table Expressions
tableExpression
    : expression
    ;

// Functions - now supports AND, OR, NOT as function names
functionCall
    : functionName OPEN_PAREN (argumentList)? CLOSE_PAREN
    ;

// Function names can be regular identifiers OR logical keywords (for AND(), OR(), NOT())
functionName
    : IDENTIFIER
    | AND_KW
    | OR_KW
    | NOT_KW
    ;

argumentList
    : expression (COMMA expression)*
    ;

// References
columnReference
    : (tableReference)? BRACKET_ID
    ;

tableReference
    : IDENTIFIER
    | SINGLE_QUOTE_ID
    ;

// Literals
literal
    : STRING_LITERAL
    | NUMBER
    | TRUE
    | FALSE
    | BLANK OPEN_PAREN CLOSE_PAREN
    | ASC   // Used as argument in TOPN etc
    | DESC  // Used as argument in TOPN etc
    ;
    
constructor
    : OPEN_CURLY constructorRow (COMMA constructorRow)* CLOSE_CURLY
    ;

constructorRow
    : OPEN_PAREN expression (COMMA expression)* CLOSE_PAREN
    | expression
    ;


// Lexer Rules

EVALUATE: 'EVALUATE';
ORDER: 'ORDER';
BY: 'BY';
ASC: 'ASC';
DESC: 'DESC';
TRUE: 'TRUE';
FALSE: 'FALSE';
BLANK: 'BLANK';
VAR: 'VAR';
RETURN: 'RETURN';

// Logical keywords (can be used as functions)
AND_KW: [Aa][Nn][Dd];
OR_KW: [Oo][Rr];
NOT_KW: [Nn][Oo][Tt];

// Logical operators (symbols only)
AND_OP: '&&';
OR_OP: '||';
NOT_OP: '!';

EQ: '==' | '=';
NEQ: '<>';
LT: '<';
LTE: '<=';
GT: '>';
GTE: '>=';
IN: 'IN';
PLUS: '+';
MINUS: '-';
ASTERISK: '*';
SLASH: '/';
AMPERSAND: '&';

OPEN_PAREN: '(';
CLOSE_PAREN: ')';
OPEN_CURLY: '{';
CLOSE_CURLY: '}';
COMMA: ',';

STRING_LITERAL
    : '"' (~'"' | '""')* '"' // Support double quotes via escaping ""
    ;

// 'Table Name'
SINGLE_QUOTE_ID
    : '\'' (~'\'' | '\'\'')* '\''
    ;

// [Column Name]
BRACKET_ID
    : '[' (~']')* ']'
    ;

NUMBER
    : [0-9]+ ('.' [0-9]+)?
    ;

IDENTIFIER
    : [a-zA-Z_] [a-zA-Z0-9_.]*
    ;

WS
    : [ \t\r\n]+ -> skip
    ;

KEYWORD: [a-zA-Z]+;
