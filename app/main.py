import sys

class Literal:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        if self.value is True:
            return "true"
        elif self.value is False:
            return "false"
        elif self.value is None:
            return "nil"
        return str(self.value)

class Token:
    def __init__(self, type, lexeme, literal, line):
        self.type = type
        self.lexeme = lexeme
        self.literal = literal
        self.line = line
    def __str__(self):
        literal_str = "null" if self.literal is None else str(self.literal)
        return f"{self.type} {self.lexeme} {literal_str}"

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current = 0

    def parse(self):
        return self.expression()

    def expression(self):
        return self.primary()

    def primary(self):
        token = self.advance()

        if token.type == "TRUE":
            return Literal(True)
        if token.type == "FALSE":
            return Literal(False)
        if token.type == "NIL":
            return Literal(None)
        if token.type == "NUMBER":
            return Literal(token.literal) # Literal value of the NUMBER token
        if token.type == "STRING":
            return Literal(token.literal) # Literal value of the STRING token
        if token.type == "LEFT_PAREN":
            expr = self.expression()
            if not self.match("RIGHT_PAREN"):
                raise Exception("Expected ')' after expression.")
            return f"(group {expr})" # The expected output
        elif token.type == "IDENTIFIER":
            return token.lexeme # Identifier name
        else:
            raise Exception(f"Unexpected token: {token.type}")
    def match(self, expected_type):
        if self.is_at_end() or self.tokens[self.current].type != expected_type:
            return False
        self.current += 1
        return True
    def advance(self):
        if not self.is_at_end():
            self.current += 1
        return self.previous()
    def previous(self):
        return self.tokens[self.current - 1]
    def is_at_end(self):
        return self.current >= len(self.tokens) or self.tokens[self.current].type == "EOF"

class Scanner:
    def __init__(self, source):
        self.source = source
        self.tokens = []
        self.start = 0
        self.current = 0
        self.line = 1
        self.errors = []


    def scan_tokens(self):
        while not self.is_at_end():
            self.start = self.current
            self.scan_token()
        self.tokens.append(Token("EOF", "", None, self.line))
        return self.tokens, self.errors
    def is_at_end(self):
        return self.current >= len(self.source)

    def scan_token(self):
        char = self.advance()
        if char == "(":
            self.add_token("LEFT_PAREN")
        elif char == ")":
            self.add_token("RIGHT_PAREN")
        elif char == "{":
            self.add_token("LEFT_BRACE")
        elif char == "}":
            self.add_token("RIGHT_BRACE")
        elif char == ",":
            self.add_token("COMMA")
        elif char == ".":
            self.add_token("DOT")
        elif char == "-":
            self.add_token("MINUS")
        elif char == "+":
            self.add_token("PLUS")
        elif char == ";":
            self.add_token("SEMICOLON")
        elif char == "*":
            self.add_token("STAR")
        elif char == "/":
            if self.match("/"):
                # Consume the rest of the line for a comment
                while not self.is_at_end() and self.source[self.current] != "\n":
                    self.advance()
            else:
                self.add_token("SLASH")
        elif char == "!":
            if self.match("="):
                self.add_token("BANG_EQUAL")
            else:
                self.add_token("BANG")
        elif char == "=":
            if self.match("="):
                self.add_token("EQUAL_EQUAL")
            else:
                self.add_token("EQUAL")
        elif char == "<":
            if self.match("="):
                self.add_token("LESS_EQUAL")
            else:
                self.add_token("LESS")
        elif char == ">":
            if self.match("="):
                self.add_token("GREATER_EQUAL")
            else:
                self.add_token("GREATER")
        elif char in (" ", "\r", "\t", "\n"):
            # Ignore whitespace
            if char == "\n":
                self.line += 1
        elif char == "\"":
            self.scan_string()
        elif char.isdigit():
            self.scan_number()
        elif self.is_alpha(char):
            self.scan_identifier()
        else:
            # If the character doesn't match any recognized tokens, log an error
            self.error(f"Unexpected character: {char}")

    def scan_string(self):
        # Start scanning after the opening quote
        while not self.is_at_end() and self.peek() != "\"":
            if self.peek() == "\n":
                self.line += 1  # Track line numbers if there's a newline within the string
            self.advance()

        # If we reached the end of the file without a closing quote, raise an error
        if self.is_at_end():
            self.error("Unterminated string.")
            return

        # Consume the closing quote
        self.advance()

        # Extract the actual string contents without the surrounding quotes
        value = self.source[self.start + 1: self.current - 1]

        # Add a STRING token with the lexeme being the full string and literal being the value
        self.add_token("STRING", value)
    def scan_number(self):
        while not self.is_at_end() and self.source[self.current].isdigit():
            self.advance()
        if not self.is_at_end() and self.source[self.current] == '.' and self.peek_next().isdigit():
            self.advance()
            while not self.is_at_end() and self.source[self.current].isdigit():
                self.advance()
        lexeme = self.source[self.start : self.current]
        literal = float(lexeme)
        self.add_token("NUMBER", literal)

    def scan_identifier(self):
        keywords = {
            "and": "AND",
            "class": "CLASS",
            "else": "ELSE",
            "false": "FALSE",
            "for": "FOR",
            "fun": "FUN",
            "if": "IF",
            "nil": "NIL",
            "or": "OR",
            "print": "PRINT",
            "return": "RETURN",
            "super": "SUPER",
            "this": "THIS",
            "true": "TRUE",
            "var": "VAR",
            "while": "WHILE"
        }
        while self.is_alpha_num(self.peek()):
            self.advance()

        text = self.source[self.start : self.current]
        token_type = keywords.get(text, "IDENTIFIER")
        self.add_token(token_type, None)

    def is_alpha(self, c):
        return c.isalpha() or c == '_'
    def is_alpha_num(self, c):
        return c.isalnum() or c == '_'


    def peek(self):
        if self.is_at_end():
            return '\0'
        return self.source[self.current]

    def peek_next(self):
        if self.current + 1 >= len(self.source):
            return '\0'
        return self.source[self.current + 1]

    def match(self, expected):
        if self.is_at_end():
            return False
        if self.source[self.current] != expected:
            return False
        self.current += 1
        return True
    def advance(self):
        self.current += 1
        return self.source[self.current - 1]
    def add_token(self, type, literal=None):
        text = self.source[self.start: self.current]
        self.tokens.append(Token(type, text, literal, self.line))

    def error(self, message):
        self.errors.append(f"[line {self.line}] Error: {message}")
def main():
    if len(sys.argv) < 3:
        print("Usage: ./your_program.sh tokenize <filename>", file=sys.stderr)
        exit(1)
    command = sys.argv[1]
    filename = sys.argv[2]
    if command not in ["tokenize", "parse"]:
        print(f"Unknown command: {command}", file=sys.stderr)
        exit(1)
    with open(filename) as file:
        file_contents = file.read()

    if command == "tokenize":
        scanner = Scanner(file_contents)
        tokens, errors = scanner.scan_tokens()
        for token in tokens:
            print(token)
        for error in errors:
            print(error, file=sys.stderr)

    elif command == "parse":
        scanner = Scanner(file_contents)
        tokens, errors = scanner.scan_tokens()
        parser = Parser(tokens)
        ast = parser.parse()
        print(ast)

    if errors:
        exit(65)  # Exit with code 65 for lexical errors


if __name__ == "__main__":
    main()