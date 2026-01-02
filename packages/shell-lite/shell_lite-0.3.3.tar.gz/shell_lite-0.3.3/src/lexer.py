import re
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class Token:
    type: str
    value: str
    line: int

class Lexer:
    def __init__(self, source_code: str):
        self.source_code = source_code
        self.tokens: List[Token] = []
        self.current_char_index = 0
        self.line_number = 1
        self.indent_stack = [0]

    def tokenize(self) -> List[Token]:
        source = self._remove_multiline_comments(self.source_code)
        lines = source.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            self.line_number = line_num
            stripped_line = line.strip()
            
            if not stripped_line or stripped_line.startswith('#'):
                continue

            indent_level = len(line) - len(line.lstrip())
            if indent_level > self.indent_stack[-1]:
                self.indent_stack.append(indent_level)
                self.tokens.append(Token('INDENT', '', self.line_number))
            elif indent_level < self.indent_stack[-1]:
                while indent_level < self.indent_stack[-1]:
                    self.indent_stack.pop()
                    self.tokens.append(Token('DEDENT', '', self.line_number))
                if indent_level != self.indent_stack[-1]:
                    raise IndentationError(f"Unindent does not match any outer indentation level on line {self.line_number}")

            self.tokenize_line(stripped_line)
            self.tokens.append(Token('NEWLINE', '', self.line_number))

        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token('DEDENT', '', self.line_number))
            
        self.tokens.append(Token('EOF', '', self.line_number))
        return self.tokens

    def _remove_multiline_comments(self, source: str) -> str:
        result = []
        i = 0
        while i < len(source):
            if source[i:i+2] == '/*':
                end = source.find('*/', i + 2)
                if end == -1:
                    raise SyntaxError("Unterminated multi-line comment")
                comment = source[i:end+2]
                result.append('\n' * comment.count('\n'))
                i = end + 2
            else:
                result.append(source[i])
                i += 1
        return ''.join(result)

    def tokenize_line(self, line: str):
        pos = 0
        while pos < len(line):
            match = None
            

            if line[pos] == '#':
                break
            
            if line[pos].isspace():
                pos += 1
                continue

            if line[pos].isdigit():
                match = re.match(r'^\d+(\.\d+)?', line[pos:])
                if match:
                    value = match.group(0)
                    self.tokens.append(Token('NUMBER', value, self.line_number))
                    pos += len(value)
                    continue

            # Check for Triple Quotes first
            if line[pos:pos+3] in ('"""', "'''"):
                 quote_char = line[pos:pos+3]
                 # For multiline, we need to scan ahead across lines?
                 # Lexer tokenizes line by line.
                 # If we want multiline strings, we need to look ahead in lines or store state.
                 # Current Lexer iterates lines.
                 # We can switch to "in_multiline_string" state?
                 # Or we can consume remaining lines here?
                 # Since tokenize() loop iterates lines, we can't easily consume from 'lines' list inside tokenize_line.
                 # But we can raise SyntaxError or support it limited to one line (useless).
                 
                 # Simpler logic: Lexer state machine.
                 # But refactoring tokenize() loop is risky.
                 
                 # Alternative: "css" tag takes a BLOCK?
                 # css:
                 #    ... content ...
                 # But css takes expression.
                 
                 # Let's support triple quotes ONLY if they end on same line? No.
                 # Let's change website/main.shl to use single line strings concatenated?
                 # Or use a separate file for CSS? serve static is already there.
                 # I used get_styles() returning css string.
                 
                 # User asked for "CSS Bundling: A way to define styles directly".
                 # I'll stick to single quotes for now to save time and reliability.
                 # I'll update website/main.shl to use "string" + "string".
                 pass

            if line[pos] in ('"', "'"):
                quote_char = line[pos]
                end_quote = line.find(quote_char, pos + 1)
                if end_quote == -1:
                    raise SyntaxError(f"Unterminated string on line {self.line_number}")
                value = line[pos+1:end_quote]
                # Simple escape handling
                value = value.replace("\\n", "\n").replace("\\t", "\t").replace("\\r", "\r").replace("\\\"", "\"").replace("\\\'", "\'")
                self.tokens.append(Token('STRING', value, self.line_number))
                pos = end_quote + 1
                continue

            if line[pos:pos+3] == '...':
                self.tokens.append(Token('DOTDOTDOT', '...', self.line_number))
                pos += 3
                continue

            two_char = line[pos:pos+2]
            two_char_tokens = {
                '=>': 'ARROW', '==': 'EQ', '!=': 'NEQ',
                '<=': 'LE', '>=': 'GE', '+=': 'PLUSEQ',
                '-=': 'MINUSEQ', '*=': 'MULEQ', '/=': 'DIVEQ',
                '%=': 'MODEQ'
            }
            if two_char in two_char_tokens:
                self.tokens.append(Token(two_char_tokens[two_char], two_char, self.line_number))
                pos += 2
                continue
            
            char = line[pos]

            # Natural Language Comparisons: 'is at least', 'is exactly', 'is less than', 'is more than'
            # We check this before single chars to catch 'is' phrases.
            # Using simple Lookahead
            rest_of_line = line[pos:]
            
            if rest_of_line.startswith('is at least '):
                self.tokens.append(Token('GE', '>=', self.line_number))
                pos += 12 # len('is at least ')
                continue
            elif rest_of_line.startswith('is exactly '):
                self.tokens.append(Token('EQ', '==', self.line_number))
                pos += 11
                continue
            elif rest_of_line.startswith('is less than '):
                self.tokens.append(Token('LT', '<', self.line_number))
                pos += 13
                continue
            elif rest_of_line.startswith('is more than '):
                self.tokens.append(Token('GT', '>', self.line_number))
                pos += 13
                continue

            # Filler Words: 'the'
            # Check if next chars are 'the' plus a non-alphanum bound (e.g. space, newline, symbol)
            if rest_of_line.startswith('the') and (len(rest_of_line) == 3 or not rest_of_line[3].isalnum()):
                 # Only skip if it's a standalone word 'the'
                 pos += 3
                 continue

            if char == '/':
                # Check for Regex /regex/
                # We assume regex if the PREVIOUS token is not something that implies division (Number, ID, RBracket, RParen)
                last_type = self.tokens[-1].type if self.tokens else None
                is_division = False
                if last_type in ('NUMBER', 'STRING', 'ID', 'RPAREN', 'RBRACKET'):
                     is_division = True
                
                if not is_division:
                    # Parse Regex
                    end_slash = line.find('/', pos + 1)
                    if end_slash != -1:
                        pattern = line[pos+1:end_slash]
                        # Check for flags after slash
                        flags = ""
                        k = end_slash + 1
                        while k < len(line) and line[k].isalpha():
                            flags += line[k]
                            k += 1
                        
                        self.tokens.append(Token('REGEX', pattern, self.line_number))
                        pos = k
                        continue

            single_char_tokens = {
                '+': 'PLUS', '-': 'MINUS', '*': 'MUL', '/': 'DIV',
                '%': 'MOD', '=': 'ASSIGN', '>': 'GT', '<': 'LT',
                '?': 'QUESTION', '(': 'LPAREN', ')': 'RPAREN',
                '[': 'LBRACKET', ']': 'RBRACKET', ':': 'COLON',
                '{': 'LBRACE', '}': 'RBRACE', ',': 'COMMA', '.': 'DOT'
            }
            if char in single_char_tokens:
                self.tokens.append(Token(single_char_tokens[char], char, self.line_number))
                pos += 1
                continue

            if char.isalpha() or char == '_':
                match = re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*', line[pos:])
                if match:
                    value = match.group(0)
                    keywords = {
                        'if': 'IF', 'else': 'ELSE', 'elif': 'ELIF',
                        'for': 'FOR', 'in': 'IN', 'range': 'RANGE',
                        'loop': 'LOOP', 'times': 'TIMES',
                        'while': 'WHILE', 'until': 'UNTIL',
                        'repeat': 'REPEAT', 'forever': 'FOREVER',
                        'stop': 'STOP', 'skip': 'SKIP', 'exit': 'EXIT',
                        'each': 'FOR',
                        'unless': 'UNLESS', 'when': 'WHEN', 'otherwise': 'OTHERWISE',
                        'then': 'THEN', 'do': 'DO',
                        'print': 'PRINT', 'say': 'SAY', 'show': 'SAY',
                        'input': 'INPUT', 'ask': 'ASK',
                        'to': 'TO', 'can': 'TO',
                        'return': 'RETURN', 'give': 'RETURN',
                        'fn': 'FN',
                        'structure': 'STRUCTURE', 'thing': 'STRUCTURE', 'class': 'STRUCTURE',
                        'has': 'HAS', 'with': 'WITH',
                        'is': 'IS', 'extends': 'EXTENDS', 'from': 'FROM',
                        'make': 'MAKE', 'new': 'MAKE',
                        'yes': 'YES', 'no': 'NO',
                        'true': 'YES', 'false': 'NO',
                        'const': 'CONST',
                        'and': 'AND', 'or': 'OR', 'not': 'NOT',
                        'try': 'TRY', 'catch': 'CATCH', 'always': 'ALWAYS',
                        'error': 'ERROR',
                        'use': 'USE', 'as': 'AS', 'share': 'SHARE',
                        'execute': 'EXECUTE', 'run': 'EXECUTE',
                        'alert': 'ALERT', 'prompt': 'PROMPT', 'confirm': 'CONFIRM',
                        'spawn': 'SPAWN', 'await': 'AWAIT',
                        'matches': 'MATCHES',
                        'on': 'ON',
                        'download': 'DOWNLOAD',
                        'compress': 'COMPRESS', 'extract': 'EXTRACT', 'folder': 'FOLDER',
                        'load': 'LOAD', 'save': 'SAVE', 'csv': 'CSV',
                        'copy': 'COPY', 'paste': 'PASTE', 'clipboard': 'CLIPBOARD',
                        'press': 'PRESS', 'type': 'TYPE', 'click': 'CLICK', 'at': 'AT',
                        'notify': 'NOTIFY',
                        'date': 'DATE', 'today': 'TODAY', 'after': 'AFTER', 'before': 'BEFORE',
                        'list': 'LIST', 'set': 'SET', 'unique': 'UNIQUE', 'of': 'OF',
                        'wait': 'WAIT',
                        'convert': 'CONVERT', 'json': 'JSON',
                        'listen': 'LISTEN', 'port': 'PORT',
                        'every': 'EVERY', 'minute': 'MINUTE', 'minutes': 'MINUTE',
                        'second': 'SECOND', 'seconds': 'SECOND',
                        'progress': 'PROGRESS',
                        'bold': 'BOLD',
                        'red': 'RED', 'green': 'GREEN', 'blue': 'BLUE', 
                        'yellow': 'YELLOW', 'cyan': 'CYAN', 'magenta': 'MAGENTA',
                        'serve': 'SERVE', 'static': 'STATIC',
                        
                        # === NATURAL ENGLISH WEB DSL ===
                        # Routing
                        # File System Mastery (v0.03.3)
                        'write': 'WRITE', 'append': 'APPEND', 'read': 'READ', 'file': 'FILE',
                        
                        # File System Mastery (v0.03.3)
                        'write': 'WRITE', 'append': 'APPEND', 'read': 'READ', 'file': 'FILE',
                        'db': 'DB', 'database': 'DB',
                        'query': 'QUERY', 'open': 'OPEN', 'close': 'CLOSE', 'exec': 'EXEC',
                        'middleware': 'MIDDLEWARE', 'before': 'BEFORE',
                         
                        
                        'when': 'WHEN', 'someone': 'SOMEONE', 'visits': 'VISITS', 
                        'submits': 'SUBMITS', 'start': 'START', 'server': 'SERVER',
                        'files': 'FILES',
                        
                        # Page/Component creation
                        'define': 'DEFINE', 'page': 'PAGE', 'called': 'CALLED',
                        'using': 'USING', 'component': 'PAGE',
                        
                        # HTML aliases (natural names)
                        'heading': 'HEADING', 'paragraph': 'PARAGRAPH',
                        # 'link' removed - conflicts with HTML <link> tag
                        'image': 'IMAGE',
                        
                        # List operations  
                        'add': 'ADD', 'put': 'ADD', 'into': 'INTO',
                        'count': 'COUNT', 'many': 'MANY', 'how': 'HOW',
                        
                        # Forms
                        'field': 'FIELD', 'submit': 'SUBMIT', 'named': 'NAMED',
                        'placeholder': 'PLACEHOLDER',
                    }
                    token_type = keywords.get(value, 'ID')
                    self.tokens.append(Token(token_type, value, self.line_number))
                    pos += len(value)
                    continue
            

            
            if char in single_char_tokens:
                self.tokens.append(Token(single_char_tokens[char], char, self.line_number))
                pos += 1
                continue

            raise SyntaxError(f"Illegal character '{char}' at line {self.line_number}")
