from typing import List, Optional
from .lexer import Token, Lexer
from .ast_nodes import *
import re

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset: int = 0) -> Token:
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return self.tokens[-1]

    def consume(self, expected_type: str = None) -> Token:
        token = self.peek()
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type} but got {token.type} on line {token.line}")
        self.pos += 1
        return token

    def check(self, token_type: str) -> bool:
        return self.peek().type == token_type

    def parse(self) -> List[Node]:
        statements = []
        while not self.check('EOF'):
            # Skip newlines at the top level between statements
            while self.check('NEWLINE'):
                self.consume()
                if self.check('EOF'): break
            
            if self.check('EOF'): break
            
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return statements


    def parse_statement(self) -> Node:
        if self.check('USE'):
            return self.parse_import()
        elif self.check('ON'):
            return self.parse_on()
        elif self.check('CONST'):
            return self.parse_const()
        elif self.check('PRINT') or self.check('SAY'):
            return self.parse_print()
        elif self.check('ALERT'):
            return self.parse_alert()
        elif self.check('IF'):
            return self.parse_if()
        elif self.check('UNLESS'):
            return self.parse_unless()
        elif self.check('WHILE'):
            return self.parse_while()
        elif self.check('UNTIL'):
            return self.parse_until()
        elif self.check('FOREVER'):
            return self.parse_forever()
        elif self.check('TRY'):
            return self.parse_try()
        elif self.check('FOR') or self.check('LOOP'):
            return self.parse_for()
        elif self.check('REPEAT'):
            return self.parse_repeat()
        elif self.check('WHEN'):
            return self.parse_when()
        elif self.check('TO'):
            return self.parse_function_def()
        elif self.check('STRUCTURE'):
            return self.parse_class_def()
        elif self.check('RETURN'):
            return self.parse_return()
        elif self.check('STOP'):
            return self.parse_stop()
        elif self.check('SKIP'):
            return self.parse_skip()
        elif self.check('EXIT'):
            return self.parse_exit()
        elif self.check('ERROR'):
            return self.parse_error()
        elif self.check('EXECUTE'):
            return self.parse_execute()
        elif self.check('MAKE'):
            return self.parse_make()
        elif self.check('INPUT'):
            # Check if this is 'input type="..."' i.e. HTML tag
            next_t = self.peek(1)
            if next_t.type in ('ID', 'TYPE', 'STRING', 'NAME', 'VALUE', 'CLASS', 'STYLE', 'ONCLICK', 'SRC', 'HREF', 'ACTION', 'METHOD'):
                # Treat as HTML tag function call - use parse_id_start_statement with token passed
                input_token = self.consume()
                return self.parse_id_start_statement(passed_name_token=input_token)
            # Else fallthrough to expression
            return self.parse_expression_stmt()
        elif self.check('ID'):
            return self.parse_id_start_statement()
        elif self.check('SPAWN'):
             # Support spawn as a statement (ignore return value)
             # e.g. spawn my_func()
             expr = self.parse_expression()
             self.consume('NEWLINE')
             return Print(expr) # Hack: Wrap in Print to execute? No, just expression stmt
             # Actually parse_expression_stmt handles this if we fall through
             # But here we caught check('SPAWN'), so we must handle it or let fallthrough?
             # check('ID') is above. SPAWN is a keyword.
             # So we must handle it explicitly or remove this block and let 'else' handle parse_expression_stmt.
             # BUT parse_expression_stmt calls parse_expression.
             # Does parse_expression handle SPAWN at top level?
             # Yes if added to parse_factor/parse_expression.
             # So we can remove this block if SPAWN starts an expression.
             pass
        elif self.check('WAIT'):
            return self.parse_wait()
        elif self.check('EVERY'):
            return self.parse_every()
        elif self.check('IN'):
             # "In 10 minutes" - Check if it looks like a time duration start
             # If just 'IN' and we are at statement level, likely 'After'
             return self.parse_after()
        elif self.check('LISTEN'):
            return self.parse_listen()
        elif self.check('SERVE'):
            return self.parse_serve()
        elif self.check('DOWNLOAD'):
             return self.parse_download()
        elif self.check('COMPRESS') or self.check('EXTRACT'):
             return self.parse_archive()
        elif self.check('LOAD') or self.check('SAVE'):
             # Check if it's CSV? "load csv" or "save x to csv"
             if self.check('LOAD') and self.peek(1).type == 'CSV':
                 return self.parse_csv_load()
             if self.check('SAVE'):
                 return self.parse_csv_save() # We'll need to check "to csv" inside
             return self.parse_expression_stmt() # Fallback
        elif self.check('COPY') or self.check('PASTE'):
             return self.parse_clipboard()
        elif self.check('WRITE'):
             return self.parse_write()
        elif self.check('APPEND'):
             return self.parse_append()
        elif self.check('DB'):
             return self.parse_db_op()
        elif self.check('PRESS') or self.check('TYPE') or self.check('CLICK') or self.check('NOTIFY'):
             return self.parse_automation()
        elif self.check('BEFORE'):
             return self.parse_middleware()
        # === NATURAL ENGLISH WEB DSL ===
        elif self.check('DEFINE'):
            return self.parse_define_page()
        elif self.check('ADD'):
            return self.parse_add_to()
        elif self.check('START'):
            return self.parse_start_server()
        elif self.check('HEADING'):
            return self.parse_heading()
        elif self.check('PARAGRAPH'):
            return self.parse_paragraph()
        else:
            return self.parse_expression_stmt()

    def parse_alert(self) -> Alert:
        token = self.consume('ALERT')
        message = self.parse_expression()
        self.consume('NEWLINE')
        node = Alert(message)
        node.line = token.line
        return node
        



    def parse_const(self) -> ConstAssign:
        token = self.consume('CONST')
        name = self.consume('ID').value
        self.consume('ASSIGN')
        value = self.parse_expression()
        self.consume('NEWLINE')
        node = ConstAssign(name, value)
        node.line = token.line
        return node

    
    def parse_on(self) -> Node:
        """Parse: on file_change "path" ... OR on request to "/path" ..."""
        token = self.consume('ON')
        
        if self.check('REQUEST') or (self.check('ID') and self.peek().value == 'request'):
            # on request to "/path"
            self.consume()
            if self.check('TO'): self.consume('TO')
            
            path = self.parse_expression() # path pattern
            
            self.consume('NEWLINE')
            self.consume('INDENT')
            
            body = []
            while not self.check('DEDENT') and not self.check('EOF'):
                while self.check('NEWLINE'): self.consume()
                if self.check('DEDENT'): break
                body.append(self.parse_statement())
            self.consume('DEDENT')
            
            node = OnRequest(path, body)
            node.line = token.line
            return node
            
        event_type = self.consume('ID').value
        path = self.parse_expression()
        
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        body = []
        while not self.check('DEDENT') and not self.check('EOF'):
            while self.check('NEWLINE'): self.consume()
            if self.check('DEDENT'): break
            body.append(self.parse_statement())
            
        self.consume('DEDENT')
        return FileWatcher(path, body)

    def _parse_natural_list(self) -> ListVal:
        """Parse: a list of x, y, z"""
        self.consume('ID') # a
        self.consume('LIST')
        self.consume('OF')
        
        elements = []
        if not self.check('NEWLINE') and not self.check('EOF'):
            elements.append(self.parse_expression())
            while self.check('COMMA'):
                self.consume('COMMA')
                if self.check('NEWLINE'): break 
                elements.append(self.parse_expression())
                
        node = ListVal(elements)
        return node

    def _parse_natural_set(self) -> Node:
        """Parse: a unique set of x, y, z -> Set([x,y,z])"""
        self.consume('ID') # a
        self.consume('UNIQUE')
        self.consume('SET')
        self.consume('OF')
        
        elements = []
        if not self.check('NEWLINE') and not self.check('EOF'):
            elements.append(self.parse_expression())
            while self.check('COMMA'):
                self.consume('COMMA')
                if self.check('NEWLINE'): break
                elements.append(self.parse_expression())
        
        list_node = ListVal(elements)
        return Call('Set', [list_node])

    def parse_wait(self) -> Node:
        """Parse: wait for 2 seconds (or just wait 2)"""
        token = self.consume('WAIT')
        
        # Optional 'for'
        # 'for' is a keyword FOR
        if self.check('FOR'):
            self.consume('FOR')
            
        time_expr = self.parse_expression()
        
        # Optional 'seconds' or 'second' filler
        if self.check('SECOND'):
            self.consume()
        
        self.consume('NEWLINE')
        
        # Return as a Call to 'wait' builtin
        # Standard Call node: Call(func_name, args)
        return Call('wait', [time_expr])

    # --- New English-like statement parsers ---
    
    def parse_stop(self) -> Stop:
        """Parse: stop"""
        token = self.consume('STOP')
        self.consume('NEWLINE')
        node = Stop()
        node.line = token.line
        return node

    def parse_skip(self) -> Skip:
        """Parse: skip"""
        token = self.consume('SKIP')
        self.consume('NEWLINE')
        node = Skip()
        node.line = token.line
        return node

    def parse_error(self) -> Throw:
        """Parse: error 'message'"""
        token = self.consume('ERROR')
        message = self.parse_expression()
        self.consume('NEWLINE')
        node = Throw(message)
        node.line = token.line
        return node

    def parse_execute(self) -> Execute:
        """Parse: execute 'code string'"""
        token = self.consume('EXECUTE')
        code = self.parse_expression()
        self.consume('NEWLINE')
        node = Execute(code)
        node.line = token.line
        return node

    def parse_unless(self) -> Unless:
        """Parse: unless condition (body)"""
        token = self.consume('UNLESS')
        condition = self.parse_expression()
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        body = []
        while not self.check('DEDENT') and not self.check('EOF'):
            while self.check('NEWLINE'): self.consume()
            if self.check('DEDENT'): break
            body.append(self.parse_statement())
        
        self.consume('DEDENT')
        
        else_body = None
        if self.check('ELSE'):
            self.consume('ELSE')
            self.consume('NEWLINE')
            self.consume('INDENT')
            else_body = []
            while not self.check('DEDENT') and not self.check('EOF'):
                while self.check('NEWLINE'): self.consume()
                if self.check('DEDENT'): break
                else_body.append(self.parse_statement())
            self.consume('DEDENT')
        
        node = Unless(condition, body, else_body)
        node.line = token.line
        return node

    def parse_until(self) -> Until:
        """Parse: until condition (body)"""
        token = self.consume('UNTIL')
        condition = self.parse_expression()
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        body = []
        while not self.check('DEDENT') and not self.check('EOF'):
            while self.check('NEWLINE'): self.consume()
            if self.check('DEDENT'): break
            body.append(self.parse_statement())
        
        self.consume('DEDENT')
        node = Until(condition, body)
        node.line = token.line
        return node

    def parse_forever(self) -> Forever:
        """Parse: forever (body) - infinite loop"""
        token = self.consume('FOREVER')
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        body = []
        while not self.check('DEDENT') and not self.check('EOF'):
            while self.check('NEWLINE'): self.consume()
            if self.check('DEDENT'): break
            body.append(self.parse_statement())
        
        self.consume('DEDENT')
        node = Forever(body)
        node.line = token.line
        return node

    def parse_exit(self) -> Exit:
        """Parse: exit or exit 1"""
        token = self.consume('EXIT')
        code = None
        if not self.check('NEWLINE'):
            code = self.parse_expression()
        self.consume('NEWLINE')
        node = Exit(code)
        node.line = token.line
        return node

    def parse_make(self) -> Node:
        """Parse: make Robot 'name' 100  or  new Robot 'name' 100"""
        token = self.consume('MAKE')
        class_name = self.consume('ID').value
        
        args = []
        while not self.check('NEWLINE') and not self.check('EOF'):
            args.append(self.parse_expression())
        
        self.consume('NEWLINE')
        node = Make(class_name, args)
        node.line = token.line
        return node

    def parse_repeat(self) -> Repeat:
        """Parse: repeat 5 times (body) or repeat (body)"""
        token = self.consume('REPEAT')
        
        # Check if there's a count
        if self.check('NEWLINE'):
            # Infinite loop style - but we'll require a count
            raise SyntaxError(f"repeat requires a count on line {token.line}")
        
        count = self.parse_expression()
        
        # Optional 'times' keyword
        if self.check('TIMES'):
            self.consume('TIMES')
        
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        body = []
        while not self.check('DEDENT') and not self.check('EOF'):
            while self.check('NEWLINE'): self.consume()
            if self.check('DEDENT'): break
            body.append(self.parse_statement())
        
        self.consume('DEDENT')
        node = Repeat(count, body)
        node.line = token.line
        return node

        return node

    def parse_db_op(self) -> DatabaseOp:
        """Parse: db open "path", db query "sql", db close, db exec "sql" """
        token = self.consume('DB')
        
        op = 'open' # default? no
        if self.check('OPEN'): op = 'open'; self.consume()
        elif self.check('QUERY'): op = 'query'; self.consume()
        elif self.check('EXEC'): op = 'exec'; self.consume()
        elif self.check('CLOSE'): op = 'close'; self.consume()
        else:
             # Maybe db "path" -> open?
             if self.check('STRING'):
                 op = 'open'
             else:
                 raise SyntaxError(f"Unknown db operation at line {token.line}")
        
        args = []
        if op != 'close' and not self.check('NEWLINE'):
             args.append(self.parse_expression())
             # Support multiple args? e.g. db exec "sql" [params]
             while not self.check('NEWLINE'):
                 args.append(self.parse_expression())
                 
        # self.consume('NEWLINE') # Don't consume newline, let caller do it
        node = DatabaseOp(op, args)
        node.line = token.line
        return node

    def parse_middleware(self) -> Node:
        """Parse: before request ..."""
        # We reuse OnRequest node? No, usually distinct.
        # But for now, let's treat it as a special OnRequest with pattern "*"
        # NO, user wants 'before request' syntax.
        # Let's add Middleware AST? Or reuse OnRequest?
        # Reusing OnRequest with path="MIDDLEWARE" might be confusing.
        # But 'before request' is essentially 'on request' that runs first.
        # Let's map it to OnRequest(path='__middleware__', body)
        token = self.consume('BEFORE')
        self.consume('REQUEST')
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        body = []
        while not self.check('DEDENT') and not self.check('EOF'):
            while self.check('NEWLINE'): self.consume()
            if self.check('DEDENT'): break
            body.append(self.parse_statement())
        self.consume('DEDENT')
        
        return OnRequest(String('__middleware__'), body)

    def parse_when(self) -> Node:
        """Parse: when value is x => (body) ... OR when condition (body) OR when someone visits/submits"""
        token = self.consume('WHEN')
        
        # Check for natural routing: when someone visits/submits "path"
        if self.check('SOMEONE'):
            self.consume('SOMEONE')
            if self.check('VISITS'):
                self.consume('VISITS')
                path = String(self.consume('STRING').value)
                self.consume('NEWLINE')
                self.consume('INDENT')
                body = []
                while not self.check('DEDENT') and not self.check('EOF'):
                    while self.check('NEWLINE'): self.consume()
                    if self.check('DEDENT'): break
                    body.append(self.parse_statement())
                self.consume('DEDENT')
                node = OnRequest(path, body)
                node.line = token.line
                return node
            elif self.check('SUBMITS'):
                self.consume('SUBMITS')
                if self.check('TO'):
                    self.consume('TO')
                path = String(self.consume('STRING').value)
                self.consume('NEWLINE')
                self.consume('INDENT')
                body = []
                while not self.check('DEDENT') and not self.check('EOF'):
                    while self.check('NEWLINE'): self.consume()
                    if self.check('DEDENT'): break
                    body.append(self.parse_statement())
                self.consume('DEDENT')
                node = OnRequest(path, body)
                node.line = token.line
                return node
        
        condition_or_value = self.parse_expression()
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        # Check first statement in block to decide if Switch or If
        if self.check('IS'):
             # It's a Switch Statement
            cases = []
            otherwise = None
            
            # Loop for Switch cases
            while not self.check('DEDENT') and not self.check('EOF'):
                if self.check('IS'):
                    self.consume('IS')
                    match_val = self.parse_expression()
                    self.consume('NEWLINE')
                    self.consume('INDENT')
                    
                    case_body = []
                    while not self.check('DEDENT') and not self.check('EOF'):
                        while self.check('NEWLINE'): self.consume()
                        if self.check('DEDENT'): break
                        case_body.append(self.parse_statement())
                    self.consume('DEDENT')
                    
                    cases.append((match_val, case_body))
                    
                elif self.check('OTHERWISE'):
                    self.consume('OTHERWISE')
                    self.consume('NEWLINE')
                    self.consume('INDENT')
                    
                    otherwise = []
                    while not self.check('DEDENT') and not self.check('EOF'):
                        while self.check('NEWLINE'): self.consume()
                        if self.check('DEDENT'): break
                        otherwise.append(self.parse_statement())
                    self.consume('DEDENT')
                elif self.check('NEWLINE'):
                    self.consume('NEWLINE')
                else:
                    break
            
            self.consume('DEDENT')
            node = When(condition_or_value, cases, otherwise)
            node.line = token.line
            return node
            
        else:
            # It's an IF statement (when condition -> body)
            body = []
            while not self.check('DEDENT') and not self.check('EOF'):
                while self.check('NEWLINE'): self.consume()
                if self.check('DEDENT'): break
                body.append(self.parse_statement())
            
            self.consume('DEDENT')
            
            # Allow else/elif for 'when' too?
            else_body = None
            if self.check('ELSE'):
                self.consume('ELSE')
                self.consume('NEWLINE')
                self.consume('INDENT')
                else_body = []
                while not self.check('DEDENT') and not self.check('EOF'):
                    while self.check('NEWLINE'): self.consume()
                    if self.check('DEDENT'): break
                    else_body.append(self.parse_statement())
                self.consume('DEDENT')
                
            node = If(condition_or_value, body, else_body)
            node.line = token.line
            return node

    def parse_return(self) -> Return:
        token = self.consume('RETURN')
        expr = self.parse_expression()
        self.consume('NEWLINE')
        node = Return(expr)
        node.line = token.line
        return node

    def parse_function_def(self) -> FunctionDef:
        start_token = self.consume('TO')
        name = self.consume('ID').value
        
        args = []
        # Syntax: to greet name OR to greet name:string
        while self.check('ID'):
            arg_name = self.consume('ID').value
            type_hint = None
            
            # Check for Type Hint or Trailing Colon
            if self.check('COLON'):
                # If next is newline, it's a trailing colon (end of def)
                if self.peek(1).type == 'NEWLINE':
                    pass 
                else:
                    self.consume('COLON')
                    if self.check('ID'):
                        type_hint = self.consume('ID').value
                    elif self.check('STRING'): 
                        type_hint = "str"
                        self.consume()
                    else: 
                         type_hint = self.consume().value 
            
            default_val = None
            if self.check('ASSIGN'):
                self.consume('ASSIGN')
                default_val = self.parse_expression()
            args.append((arg_name, default_val, type_hint))
            
        if self.check('COLON'):
            self.consume('COLON')
            
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        body = []
        while not self.check('DEDENT') and not self.check('EOF'):
            while self.check('NEWLINE'): self.consume()
            if self.check('DEDENT'): break
            body.append(self.parse_statement())
            
        self.consume('DEDENT')
        node = FunctionDef(name, args, body)
        node.line = start_token.line
        return node

    def parse_class_def(self) -> ClassDef:
        start_token = self.consume('STRUCTURE')
        name = self.consume('ID').value
        
        parent = None
        if self.check('LPAREN'):
            self.consume('LPAREN')
            parent = self.consume('ID').value
            self.consume('RPAREN')
            
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        properties = []
        methods = []
        
        while not self.check('DEDENT') and not self.check('EOF'):
            if self.check('HAS'):
                self.consume()
                properties.append(self.consume('ID').value)
                self.consume('NEWLINE')
            elif self.check('TO'):
                methods.append(self.parse_function_def())
            elif self.check('NEWLINE'):
                self.consume()
            else:
                self.consume('DEDENT') # break out if unexpected
                break

        self.consume('DEDENT')
        node = ClassDef(name, properties, methods, parent)
        node.line = start_token.line
        return node
    
    def parse_id_start_statement(self, passed_name_token=None) -> Node:
        """
        Handles statements starting with ID.
        1. Assignment: name = expr
        2. Instantiation: name is Model arg1 arg2
        3. Function Call: name arg1 arg2
        4. Method Call: name.method
        5. Property Access (Expression stmt): name.prop
        """
        if passed_name_token:
            name_token = passed_name_token
        else:
            name_token = self.consume('ID')
        name = name_token.value
        
        if self.check('ASSIGN'):
            self.consume('ASSIGN')
            value = self.parse_expression()
            self.consume('NEWLINE')
            node = Assign(name, value)
            node.line = name_token.line
            return node
            
        elif self.check('PLUSEQ'):
            self.consume('PLUSEQ')
            value = self.parse_expression()
            self.consume('NEWLINE')
            # Desugar a += 1 to a = a + 1
            node = Assign(name, BinOp(VarAccess(name), '+', value))
            node.line = name_token.line
            return node
            
        elif self.check('MINUSEQ'):
            self.consume('MINUSEQ')
            value = self.parse_expression()
            self.consume('NEWLINE')
            node = Assign(name, BinOp(VarAccess(name), '-', value))
            node.line = name_token.line
            return node
            
        elif self.check('MULEQ'):
            self.consume('MULEQ')
            value = self.parse_expression()
            self.consume('NEWLINE')
            node = Assign(name, BinOp(VarAccess(name), '*', value))
            node.line = name_token.line
            return node
            
        elif self.check('DIVEQ'):
            self.consume('DIVEQ')
            value = self.parse_expression()
            self.consume('NEWLINE')
            node = Assign(name, BinOp(VarAccess(name), '/', value))
            node.line = name_token.line
            return node
        
        elif self.check('IS'):
            token_is = self.consume('IS')
            
            # Natural English initialization: tasks is a list
            if self.check('ID') and self.peek().value == 'a':
                self.consume()
                
            if self.check('LIST'):
                self.consume('LIST')
                self.consume('NEWLINE')
                node = Assign(name, ListVal([]))
                node.line = token_is.line
                return node
                
            if self.check('ID') and self.peek().value in ('dictionary', 'map', 'dict'):
                self.consume()
                self.consume('NEWLINE')
                node = Assign(name, Dictionary([]))
                node.line = token_is.line
                return node
            
            if self.check('ID') and not self.peek().value in ('{', '['): # sanity check or just check ID
                class_name = self.consume('ID').value
                args = []
                while not self.check('NEWLINE') and not self.check('EOF'):
                    args.append(self.parse_expression()) 
                
                self.consume('NEWLINE')
                node = Instantiation(name, class_name, args)
                node.line = token_is.line
                return node
            else:
                # Support: name is "Alice" or data is {"x": 1}
                value = self.parse_expression()
                self.consume('NEWLINE')
                node = Assign(name, value)
                node.line = token_is.line
                return node
            
        elif self.check('DOT'):
            # Method call or property access (or assignment)
            self.consume('DOT')
            member_token = self.consume()
            member = member_token.value
            # Warning: we accept ANY token as member if it follows DOT to allow keywords like 'json', 'open' etc.
            
            if self.check('ASSIGN'):
                self.consume('ASSIGN')
                value = self.parse_expression()
                self.consume('NEWLINE')
                return PropertyAssign(name, member, value)
                
            args = []
            while not self.check('NEWLINE') and not self.check('EOF'):
                args.append(self.parse_expression())
            
            self.consume('NEWLINE')
            node = MethodCall(name, member, args)
            node.line = name_token.line
            return node

        else:
            if not self.check('NEWLINE') and not self.check('EOF') and not self.check('EQ') and not self.check('IS'):
                args = []
                while not self.check('NEWLINE') and not self.check('EOF') and not self.check('IS'): 
                     # Check for named arg: KEYWORD/ID = Expr
                     # Support HTML attributes like class=..., type=..., for=...
                     is_named_arg = False
                     if self.peek(1).type == 'ASSIGN':
                         # Acceptable keys
                         t_type = self.peek().type
                         if t_type in ('ID', 'STRUCTURE', 'TYPE', 'FOR', 'IN', 'WHILE', 'IF', 'ELSE', 'FROM', 'TO', 'STRING', 'EXTENDS', 'WITH', 'PLACEHOLDER', 'NAME', 'VALUE', 'ACTION', 'METHOD', 'HREF', 'SRC', 'CLASS', 'STYLE'):
                             is_named_arg = True
                     
                     if is_named_arg:
                         key_token = self.consume()
                         key = key_token.value
                         self.consume('ASSIGN')
                         val = self.parse_expression()
                         # Pass as a dictionary node {key: val}
                         # Since Interpreter _make_tag_fn handles dicts as attrs
                         args.append(Dictionary([ (String(key), val) ]))
                     else:
                         if self.check('USING'):
                             self.consume('USING')
                         args.append(self.parse_expression())
                         
                if self.check('NEWLINE'):
                    self.consume('NEWLINE')
                elif self.check('INDENT'):
                    pass
                else:
                    self.consume('NEWLINE')
                
                # Check for Block Call (WebDSL style)
                # div class="x"
                #     p "hello"
                body = None
                if self.check('INDENT'):
                    self.consume('INDENT')
                    body = []
                    while not self.check('DEDENT') and not self.check('EOF'):
                        while self.check('NEWLINE'): self.consume()
                        if self.check('DEDENT'): break
                        body.append(self.parse_statement())
                    self.consume('DEDENT')

                node = Call(name, args, body)
                node.line = name_token.line
                return node

                node = Call(name, args, body)
                node.line = name_token.line
                return node

            if self.check('NEWLINE'):
                self.consume('NEWLINE')
            elif self.check('INDENT'):
                pass
            else:
                 self.consume('NEWLINE')

            # Standalone variable/identifier -> Just access it (via Call with 0 args to check for Block)
            # OR could be VarAccess.
            # But if it has a BLOCK, it MUST be a call (e.g. div \n ...)
            
            if self.check('INDENT'):
                self.consume('INDENT')
                body = []
                while not self.check('DEDENT') and not self.check('EOF'):
                    while self.check('NEWLINE'): self.consume()
                    if self.check('DEDENT'): break
                    body.append(self.parse_statement())
                self.consume('DEDENT')
                
                # Treat as Call(name, [], body)
                node = Call(name, [], body)
                node.line = name_token.line
                return node
            
            # Just access
            node = VarAccess(name)
            node.line = name_token.line
            return node
    def parse_print(self) -> Node:
        if self.check('PRINT'):
            token = self.consume('PRINT')
        else:
            token = self.consume('SAY')
            
        # Check for 'show progress'
        if self.check('PROGRESS'):
            return self.parse_progress_loop(token)
            
        style = None
        color = None
        
        # Handle 'say in red "..."'
        if self.check('IN'):
            self.consume('IN')
            if self.peek().type in ('RED', 'GREEN', 'BLUE', 'YELLOW', 'CYAN', 'MAGENTA'):
                color = self.consume().value
        
        # Handle 'say bold green "..."'
        if self.check('BOLD'):
            self.consume('BOLD')
            style = 'bold'
            
        if self.peek().type in ('RED', 'GREEN', 'BLUE', 'YELLOW', 'CYAN', 'MAGENTA'):
            color = self.consume().value
            
        expr = self.parse_expression()
        self.consume('NEWLINE')
        node = Print(expression=expr, style=style, color=color)
        node.line = token.line
        return node
        
    def parse_progress_loop(self, start_token: Token) -> ProgressLoop:
        """Parse: show progress for i in ..."""
        self.consume('PROGRESS')
        
        # Expect a loop like 'for ...' or 'repeat ...'
        # But 'for' parser expects to be called when current token is 'FOR'
        if not (self.check('FOR') or self.check('REPEAT') or self.check('LOOP')):
             raise SyntaxError(f"Expected loop after 'show progress' on line {start_token.line}")
             
        if self.check('FOR') or self.check('LOOP'):
            loop_node = self.parse_for()
        else:
            loop_node = self.parse_repeat()
            
        node = ProgressLoop(loop_node)
        node.line = start_token.line
        return node
    
    def parse_serve(self) -> ServeStatic:
        """Parse: serve static 'folder' at 'url' OR serve files from 'folder'"""
        token = self.consume('SERVE')
        
        # Natural syntax: serve files from "public"
        if self.check('FILES'):
            self.consume('FILES')
            if self.check('FROM'):
                self.consume('FROM')
            folder = self.parse_expression()
            # Default URL is /static
            url = String('/static')
            if self.check('AT'):
                self.consume('AT')
                url = self.parse_expression()
            if self.check('FOLDER'):
                self.consume('FOLDER')
            self.consume('NEWLINE')
            node = ServeStatic(folder, url)
            node.line = token.line
            return node
        
        # Original syntax: serve static "folder" at "/url"
        self.consume('STATIC')
        folder = self.parse_expression()
        self.consume('AT')
        url = self.parse_expression()
        self.consume('NEWLINE')
        node = ServeStatic(folder, url)
        node.line = token.line
        return node

    def parse_listen(self) -> Listen:
        """Parse: listen on port 8000"""
        token = self.consume('LISTEN')
        
        if self.check('ON'): self.consume('ON')
        if self.check('PORT'): self.consume('PORT')
        
        port_num = self.parse_expression()
        self.consume('NEWLINE')
        
        node = Listen(port_num)
        node.line = token.line
        return node
        
    def parse_every(self) -> Every:
        """Parse: every 5 minutes (body)"""
        token = self.consume('EVERY')
        interval = self.parse_expression()
        
        unit = 'seconds'
        if self.check('MINUTE'): 
            self.consume()
            unit = 'minutes'
        elif self.check('SECOND'):
            self.consume()
            unit = 'seconds'
            
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        body = []
        while not self.check('DEDENT') and not self.check('EOF'):
            while self.check('NEWLINE'): self.consume()
            if self.check('DEDENT'): break
            body.append(self.parse_statement())
            
        self.consume('DEDENT')
        node = Every(interval, unit, body)
        node.line = token.line
        return node
        
    def parse_after(self) -> After:
        """Parse: in 5 minutes (body)"""
        token = self.consume('IN')
        delay = self.parse_expression()
        
        unit = 'seconds'
        if self.check('MINUTE'):
            self.consume()
            unit = 'minutes'
        elif self.check('SECOND'):
            self.consume()
            unit = 'seconds'
            
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        body = []
        while not self.check('DEDENT') and not self.check('EOF'):
            while self.check('NEWLINE'): self.consume()
            if self.check('DEDENT'): break
            body.append(self.parse_statement())
            
        self.consume('DEDENT')
        node = After(delay, unit, body)
        node.line = token.line
        return node

    # === NATURAL ENGLISH WEB DSL PARSERS ===
    
    def parse_define_page(self) -> Node:
        """Parse: define page Name (using args) = body"""
        token = self.consume('DEFINE')
        if self.check('PAGE'):
            self.consume('PAGE')
        
        name = self.consume('ID').value
        
        # Check for arguments: define page TaskList using items
        args = []
        if self.check('USING'):
            self.consume('USING')
            args.append((self.consume('ID').value, None, None))
            while self.check('COMMA'):
                self.consume('COMMA')
                args.append((self.consume('ID').value, None, None))
        
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        body = []
        while not self.check('DEDENT') and not self.check('EOF'):
            while self.check('NEWLINE'): self.consume()
            if self.check('DEDENT'): break
            body.append(self.parse_statement())
        self.consume('DEDENT')
        
        # Create a FunctionDef node (reuse existing infrastructure)
        node = FunctionDef(name, args, body)
        node.line = token.line
        return node
    
    def parse_add_to(self) -> Node:
        """Parse: add item to list"""
        token = self.consume('ADD')
        item_expr = self.parse_factor_simple()
        
        if self.check('TO') or self.check('INTO'):
            self.consume()
        
        list_name = self.consume('ID').value
        self.consume('NEWLINE')
        
        # Generate: list = list + [item]
        list_access = VarAccess(list_name)
        item_list = ListVal([item_expr])
        concat = BinOp(list_access, '+', item_list)
        node = Assign(list_name, concat)
        node.line = token.line
        return node
    
    def parse_start_server(self) -> Node:
        """Parse: start server (on port X)"""
        token = self.consume('START')
        if self.check('SERVER'):
            self.consume('SERVER')
        
        # Default port 8080
        port = Number(8080)
        
        if self.check('ON'):
            self.consume('ON')
            if self.check('PORT'):
                self.consume('PORT')
            port = self.parse_expression()
        
        self.consume('NEWLINE')
        
        node = Listen(port)
        node.line = token.line
        return node
    
    def parse_heading(self) -> Node:
        """Parse: heading 'text' -> h1"""
        token = self.consume('HEADING')
        text = self.parse_expression()
        self.consume('NEWLINE')
        
        # Create a Call node for 'h1' builtin
        node = Call('h1', [text])
        node.line = token.line
        return node
    
    def parse_paragraph(self) -> Node:
        """Parse: paragraph 'text' -> p"""
        token = self.consume('PARAGRAPH')
        text = self.parse_expression()
        self.consume('NEWLINE')
        
        # Create a Call node for 'p' builtin
        node = Call('p', [text])
        node.line = token.line
        return node

    def parse_assign(self) -> Assign:
        name = self.consume('ID').value
        self.consume('ASSIGN')
        value = self.parse_expression()
        self.consume('NEWLINE')
        return Assign(name, value)

    def parse_import(self) -> Node:
        token = self.consume('USE')
        path = self.consume('STRING').value
        
        if self.check('AS'):
            self.consume('AS')
            alias = self.consume('ID').value
            self.consume('NEWLINE')
            node = ImportAs(path, alias)
        else:
            self.consume('NEWLINE')
            node = Import(path)
            
        node.line = token.line
        return node

    def parse_if(self) -> If:
        self.consume('IF')
        condition = self.parse_expression()
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        body = []
        while not self.check('DEDENT') and not self.check('EOF'):
            while self.check('NEWLINE'): self.consume()
            if self.check('DEDENT'): break
            body.append(self.parse_statement())
        
        self.consume('DEDENT')
        
        else_body = None
        
        # Handle ELIF (as recursive If in else_body? Or flat? Let's use recursive for simplicity with AST)
        # AST is If(cond, body, else_body).
        # ELIF cond body -> else_body = [If(cond, body, ...)]
        
        if self.check('ELIF'):
            # This 'elif' becomes the 'if' of the else_body
            # But wait, 'elif' token needs to be consumed inside the recursive call?
            # Or we recursively call parse_if but trick it?
            # Better: Rewrite parse_if to NOT consume IF if called recursively?
            # No, standard way:
            else_body = [self.parse_elif()]
            
        elif self.check('ELSE'):
            self.consume('ELSE')
            self.consume('NEWLINE')
            self.consume('INDENT')
            else_body = []
            while not self.check('DEDENT') and not self.check('EOF'):
                while self.check('NEWLINE'): self.consume()
                if self.check('DEDENT'): break
                else_body.append(self.parse_statement())
            self.consume('DEDENT')

        return If(condition, body, else_body)

    def parse_elif(self) -> If:
        # Similar to parse_if but consumes ELIF
        token = self.consume('ELIF')
        condition = self.parse_expression()
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        body = []
        while not self.check('DEDENT') and not self.check('EOF'):
            while self.check('NEWLINE'): self.consume()
            if self.check('DEDENT'): break
            body.append(self.parse_statement())
        self.consume('DEDENT')
        
        else_body = None
        if self.check('ELIF'):
            else_body = [self.parse_elif()]
        elif self.check('ELSE'):
            self.consume('ELSE')
            self.consume('NEWLINE')
            self.consume('INDENT')
            else_body = []
            while not self.check('DEDENT') and not self.check('EOF'):
                while self.check('NEWLINE'): self.consume()
                if self.check('DEDENT'): break
                else_body.append(self.parse_statement())
            self.consume('DEDENT')
            
        node = If(condition, body, else_body)
        node.line = token.line
        node = If(condition, body, else_body)
        node.line = token.line
        return node

    def parse_while(self) -> While:
        start_token = self.consume('WHILE')
        condition = self.parse_expression()
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        body = []
        while not self.check('DEDENT') and not self.check('EOF'):
            while self.check('NEWLINE'): self.consume()
            if self.check('DEDENT'): break
            body.append(self.parse_statement())
            
        self.consume('DEDENT')
        node = While(condition, body)
        node.line = start_token.line
        return node
        
    def parse_try(self) -> Try:
        start_token = self.consume('TRY')
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        try_body = []
        while not self.check('DEDENT') and not self.check('EOF'):
            while self.check('NEWLINE'): self.consume()
            if self.check('DEDENT'): break
            try_body.append(self.parse_statement())
        self.consume('DEDENT')
        
        self.consume('CATCH')
        catch_var = self.consume('ID').value
        self.consume('NEWLINE')
        self.consume('INDENT')
        
        catch_body = []
        while not self.check('DEDENT') and not self.check('EOF'):
            while self.check('NEWLINE'): self.consume()
            if self.check('DEDENT'): break
            catch_body.append(self.parse_statement())
        self.consume('DEDENT')
        
        # Check for always block (finally)
        always_body = []
        if self.check('ALWAYS'):
            self.consume('ALWAYS')
            self.consume('NEWLINE')
            self.consume('INDENT')
            while not self.check('DEDENT') and not self.check('EOF'):
                while self.check('NEWLINE'): self.consume()
                if self.check('DEDENT'): break
                always_body.append(self.parse_statement())
            self.consume('DEDENT')
        
        if always_body:
            node = TryAlways(try_body, catch_var, catch_body, always_body)
        else:
            node = Try(try_body, catch_var, catch_body)
        node.line = start_token.line
        return node

    def parse_list(self) -> Node:
        token = self.consume('LBRACKET')
        
        def skip_formatted():
            while self.check('NEWLINE') or self.check('INDENT') or self.check('DEDENT'):
                self.consume()
        skip_formatted()
        # Empty list
        if self.check('RBRACKET'):
            self.consume('RBRACKET')
            node = ListVal([])
            node.line = token.line
            return node
        
        # Check for spread operator
        if self.check('DOTDOTDOT'):
             node = self._parse_list_with_spread(token)
             skip_formatted()
             return node
        
        # Parse first expression
        first_expr = self.parse_expression()
        skip_formatted()
        
        # Check for list comprehension: [expr for var in iterable]
        if self.check('FOR'):
            self.consume('FOR')
            var_name = self.consume('ID').value
            self.consume('IN')
            iterable = self.parse_expression()
            
            # Optional condition: [x for x in list if x > 0]
            condition = None
            if self.check('IF'):
                self.consume('IF')
                condition = self.parse_expression()
            
            self.consume('RBRACKET')
            node = ListComprehension(first_expr, var_name, iterable, condition)
            node.line = token.line
            return node
        
        # Regular list
        elements = [first_expr]
        while self.check('COMMA'):
            self.consume('COMMA')
            skip_formatted()
            if self.check('RBRACKET'):
                break  # Trailing comma support
            if self.check('DOTDOTDOT'):
                self.consume('DOTDOTDOT')
                spread_val = self.parse_expression()
                spread_node = Spread(spread_val)
                spread_node.line = token.line
                elements.append(spread_node)
            else:
                elements.append(self.parse_expression())
            skip_formatted()
        
        skip_formatted()
        self.consume('RBRACKET')
        node = ListVal(elements)
        node.line = token.line
        return node

    def _parse_list_with_spread(self, token: Token) -> ListVal:
        """Parse list starting with spread operator"""
        elements = []
        self.consume('DOTDOTDOT')
        spread_val = self.parse_expression()
        spread_node = Spread(spread_val)
        spread_node.line = token.line
        elements.append(spread_node)
        
        while self.check('COMMA'):
            self.consume('COMMA')
            if self.check('RBRACKET'):
                break
            if self.check('DOTDOTDOT'):
                self.consume('DOTDOTDOT')
                spread_val = self.parse_expression()
                spread_node = Spread(spread_val)
                spread_node.line = token.line
                elements.append(spread_node)
            else:
                elements.append(self.parse_expression())
        
        self.consume('RBRACKET')
        node = ListVal(elements)
        node.line = token.line
        return node

    def parse_dict(self) -> Dictionary:
        token = self.consume('LBRACE')
        
        def skip_formatted():
            while self.check('NEWLINE') or self.check('INDENT') or self.check('DEDENT'):
                self.consume()
        
        skip_formatted()
        pairs = []
        if not self.check('RBRACE'):
            # Support { key: value } or { "key": value } or { expr: value }
            if self.check('ID') and self.peek(1).type == 'COLON':
                key_token = self.consume('ID')
                key = String(key_token.value)
                key.line = key_token.line
            else:
                key = self.parse_expression()
                
            self.consume('COLON')
            skip_formatted()
            value = self.parse_expression()
            pairs.append((key, value))
            skip_formatted()
            
            while self.check('COMMA'):
                self.consume('COMMA')
                skip_formatted()
                if self.check('RBRACE'): break
                
                if self.check('ID') and self.peek(1).type == 'COLON':
                    key_token = self.consume('ID')
                    key = String(key_token.value)
                    key.line = key_token.line
                else:
                    key = self.parse_expression()
                    
                self.consume('COLON')
                skip_formatted()
                value = self.parse_expression()
                pairs.append((key, value))
                skip_formatted()
        
        skip_formatted()
        self.consume('RBRACE')
        node = Dictionary(pairs)
        node.line = token.line
        return node

    def parse_factor_simple(self) -> Node:
        """Parse a simple factor (atomic) to be used as an argument."""
        token = self.peek()
        if token.type == 'NUMBER':
            self.consume()
            val = token.value
            if '.' in val:
                node = Number(float(val))
            else:
                node = Number(int(val))
            node.line = token.line
            return node
        elif token.type == 'STRING':
            self.consume()
            val = token.value
            if '{' in val and '}' in val:
                parts = re.split(r'\{([^}]+)\}', val)
                if len(parts) == 1:
                     node = String(val)
                     node.line = token.line
                     return node
                current_node = None
                for i, part in enumerate(parts):
                    if i % 2 == 0:
                        if not part: continue 
                        expr = String(part)
                        expr.line = token.line
                    else:
                        # Full expression support via re-parsing
                        snippet = part.strip()
                        if snippet:
                            sub_lexer = Lexer(snippet)
                            # Remove comments/indent processing if any? Expressions are usually simple.
                            sub_tokens = sub_lexer.tokenize() 
                            # Tokenize adds EOF. Parser expects list of tokens.
                            
                            sub_parser = Parser(sub_tokens)
                            # We want a single expression.
                            # But parse_expression might fail if tokens are empty/weird.
                            try:
                                expr = sub_parser.parse_expression()
                                expr.line = token.line
                            except Exception as e:
                                # Fallback or error?
                                raise SyntaxError(f"Invalid interpolation expression: '{snippet}' on line {token.line}")
                        else:
                            continue
                            
                    if current_node is None:
                        current_node = expr
                    else:
                        current_node = BinOp(current_node, '+', expr)
                        current_node.line = token.line
                return current_node if current_node else String("")
            node = String(token.value)
            node.line = token.line
            return node
        elif token.type == 'YES':
            self.consume()
            node = Boolean(True)
            node.line = token.line
            return node
        elif token.type == 'NO':
            self.consume()
            node = Boolean(False)
            node.line = token.line
            return node
        elif token.type == 'LBRACKET':
            return self.parse_list()
        elif token.type == 'LBRACE':
            return self.parse_dict()
        elif token.type == 'ID':
            self.consume()
            # Dont check for args here, just VarAccess or Dot
            if self.check('DOT'):
                self.consume('DOT')
                prop_token = self.consume()
                prop = prop_token.value
                node = PropertyAccess(token.value, prop)
                node.line = token.line
                return node
            node = VarAccess(token.value)
            node.line = token.line
            return node
        elif token.type == 'LPAREN':
            self.consume()
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr
        elif token.type == 'INPUT' or token.type == 'ASK':
            # Check if this is 'input type="..."' i.e. HTML tag
            is_tag = False
            next_t = self.peek(1)
            if next_t.type in ('ID', 'TYPE', 'STRING', 'NAME', 'VALUE', 'CLASS', 'STYLE', 'ONCLICK', 'SRC', 'HREF', 'ACTION', 'METHOD'):
                is_tag = True
            if is_tag:
                 return self.parse_id_start_statement(passed_name_token=token)
            self.consume()
            prompt = None
            if self.check('STRING'):
                prompt = self.consume('STRING').value
            node = Input(prompt)
            node.line = token.line
            return node
        
        raise SyntaxError(f"Unexpected argument token {token.type} at line {token.line}")

    def parse_factor(self) -> Node:
        token = self.peek()
        
        if token.type == 'NOT':
            op = self.consume()
            right = self.parse_factor() 
            node = UnaryOp(op.value, right)
            node.line = op.line
            return node
        elif token.type == 'DB':
            return self.parse_db_op()
        elif token.type == 'SPAWN':
            op = self.consume()
            right = self.parse_factor()
            node = Spawn(right)
            node.line = op.line
            return node
        elif token.type == 'EXECUTE':
            op = self.consume()
            # run "cmd" -> convert to function call run("cmd")
            # Argument is parse_factor or parse_expression? 
            # run "cmd". parse_expression catches "cmd".
            right = self.parse_expression()
            node = Call('run', [right])
            node.line = op.line
            return node
        elif token.type == 'COUNT' or token.type == 'HOW':
            # count of x, how many x
            token = self.consume()
            if token.type == 'HOW':
                self.consume('MANY')
            if self.check('OF'):
                self.consume('OF')
            expr = self.parse_expression()
            node = Call('len', [expr])
            node.line = token.line
            return node
        elif token.type == 'AWAIT':
            op = self.consume()
            right = self.parse_factor()
            node = Await(right)
            node.line = op.line
            return node
        elif token.type == 'CONVERT':
            return self.parse_convert()
        elif token.type == 'LOAD' and self.peek(1).type == 'CSV':
             # Handle load csv as expression
             self.consume('LOAD')
             self.consume('CSV')
             path = self.parse_factor() # argument
             node = CsvOp('load', None, path)
             node.line = token.line
             return node
        elif token.type == 'PASTE':
             token = self.consume('PASTE')
             self.consume('FROM')
             self.consume('CLIPBOARD')
             node = ClipboardOp('paste', None)
             node.line = token.line
             return node
        elif token.type == 'READ':
             token = self.consume('READ')
             self.consume('FILE')
             path = self.parse_factor()
             node = FileRead(path)
             node.line = token.line
             return node
        elif token.type == 'DATE':
             token = self.consume('DATE')
             s = self.consume('STRING').value
             node = DateOp(s)
             node.line = token.line
             return node
        elif token.type == 'TODAY':
             token = self.consume('TODAY')
             node = DateOp('today')
             node.line = token.line
             return node
            
        if token.type == 'NUMBER':
            self.consume()
            val = token.value
            if '.' in val:
                node = Number(float(val))
            else:
                node = Number(int(val))
            node.line = token.line
            return node
        elif token.type == 'REGEX':
            self.consume()
            node = Regex(token.value)
            node.line = token.line
            return node
        elif token.type == 'STRING':
            self.consume()
            node = String(token.value)
            node.line = token.line
            return node
        elif token.type == 'YES':
            self.consume()
            node = Boolean(True)
            node.line = token.line
            return node
        elif token.type == 'NO':
            self.consume()
            node = Boolean(False)
            node.line = token.line
            return node
        elif token.type == 'LBRACKET':
            return self.parse_list()
        elif token.type == 'LBRACE':
            return self.parse_dict()
        elif token.type == 'ID':
            # Check for Natural Collection Syntax: a list of / a unique set of
            if token.value == 'a':
                if self.peek(1).type == 'LIST' and self.peek(2).type == 'OF':
                    # a list of ...
                    return self._parse_natural_list()
                elif self.peek(1).type == 'UNIQUE' and self.peek(2).type == 'SET' and self.peek(3).type == 'OF':
                    # a unique set of ...
                    return self._parse_natural_set()
            
            self.consume()
            instance_name = token.value
            method_name = None
            
            # Check for dot access in expression
            if self.check('DOT'):
                self.consume('DOT')
                method_name = self.consume().value
            
            args = []
            force_call = False
            
            while True:
                next_t = self.peek()
                
                if next_t.type == 'LPAREN' and self.peek(1).type == 'RPAREN':
                    self.consume('LPAREN')
                    self.consume('RPAREN')
                    force_call = True
                    continue

                if next_t.type in ('NUMBER', 'STRING', 'REGEX', 'ID', 'LPAREN', 'INPUT', 'ASK', 'YES', 'NO', 'LBRACKET', 'LBRACE'):
                     args.append(self.parse_factor_simple())
                else:
                    break
                    
            if method_name:
                if args or force_call:
                    node = MethodCall(instance_name, method_name, args)
                else:
                    node = PropertyAccess(instance_name, method_name)
                node.line = token.line
                return node
            
            if args or force_call:
                node = Call(instance_name, args)
                node.line = token.line
                return node
                
            node = VarAccess(instance_name)
            node.line = token.line
            return node
        elif token.type == 'LPAREN':
            self.consume()
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr
        elif token.type == 'INPUT' or token.type == 'ASK':
            # Check if this is 'input type="..."' i.e. HTML tag
            next_t = self.peek(1)
            if next_t.type in ('ID', 'TYPE', 'STRING', 'NAME', 'VALUE', 'CLASS', 'STYLE', 'ONCLICK', 'SRC', 'HREF', 'ACTION', 'METHOD'):
                # Treat as HTML tag function call
                self.consume() # Consume INPUT token
                return self.parse_id_start_statement(passed_name_token=token)
            self.consume()
            prompt = None
            if self.check('STRING'):
                prompt = self.consume('STRING').value
            node = Input(prompt)
            node.line = token.line
            return node
        elif token.type == 'PROMPT':
            self.consume()
            prompt_expr = self.parse_factor() # argument
            node = Prompt(prompt_expr)
            node.line = token.line
            return node
        elif token.type == 'CONFIRM':
            self.consume()
            prompt_expr = self.parse_factor()
            node = Confirm(prompt_expr)
            node.line = token.line
            return node
        
        raise SyntaxError(f"Unexpected token {token.type} at line {token.line}")

    def parse_for(self) -> Node:
        # Support:
        # 1. for x in list       -> ForIn loop
        # 2. for i in range 1 10 -> For loop with range
        # 3. for 20 in range     -> For loop (old style)
        # 4. loop 20 times       -> For loop
        
        if self.check('LOOP'):
            # loop N times
            start_token = self.consume('LOOP')
            count_expr = self.parse_expression()
            self.consume('TIMES')
            
            self.consume('NEWLINE')
            self.consume('INDENT')
            
            body = []
            while not self.check('DEDENT') and not self.check('EOF'):
                while self.check('NEWLINE'): self.consume()
                if self.check('DEDENT'): break
                body.append(self.parse_statement())

            self.consume('DEDENT')
            node = For(count_expr, body)
            node.line = start_token.line
            return node
        
        # for ...
        start_token = self.consume('FOR')
        
        # Check if it's: for VAR in ITERABLE (where VAR is an ID followed by IN)
        if self.check('ID') and self.peek(1).type == 'IN':
            var_name = self.consume('ID').value
            self.consume('IN')
            
            # Check if it's range syntax: for i in range 1 10
            if self.check('RANGE'):
                self.consume('RANGE')
                start_val = self.parse_expression()
                end_val = self.parse_expression()
                
                self.consume('NEWLINE')
                self.consume('INDENT')
                
                body = []
                while not self.check('DEDENT') and not self.check('EOF'):
                    while self.check('NEWLINE'): self.consume()
                    if self.check('DEDENT'): break
                    body.append(self.parse_statement())
                
                self.consume('DEDENT')
                
                # Create ForIn with a range call
                iterable = Call('range', [start_val, end_val])
                node = ForIn(var_name, iterable, body)
                node.line = start_token.line
                return node
            else:
                # for x in iterable
                iterable = self.parse_expression()
                
                self.consume('NEWLINE')
                self.consume('INDENT')
                
                body = []
                while not self.check('DEDENT') and not self.check('EOF'):
                    while self.check('NEWLINE'): self.consume()
                    if self.check('DEDENT'): break
                    body.append(self.parse_statement())
                
                self.consume('DEDENT')
                node = ForIn(var_name, iterable, body)
                node.line = start_token.line
                return node
        else:
            # Old style: for 20 in range (count-based)
            count_expr = self.parse_expression()
            self.consume('IN')
            self.consume('RANGE')
            
            self.consume('NEWLINE')
            self.consume('INDENT')
            
            body = []
            while not self.check('DEDENT') and not self.check('EOF'):
                while self.check('NEWLINE'): self.consume()
                if self.check('DEDENT'): break
                body.append(self.parse_statement())

            self.consume('DEDENT')
            node = For(count_expr, body)
            node.line = start_token.line
            return node

    def parse_expression_stmt(self) -> Node:
        # Implicit print for top-level expressions
        expr = self.parse_expression()
        self.consume('NEWLINE')
        # Wrap in Print node for implicit output behavior
        node = Print(expression=expr)
        node.line = expr.line
        return node

    def parse_expression(self) -> Node:
        # Check for lambda: fn x => expr or fn x y => expr
        if self.check('FN'):
            return self.parse_lambda()
        
        return self.parse_ternary()

    def parse_lambda(self) -> Lambda:
        token = self.consume('FN')
        params = []
        
        # Parse parameters until =>
        while self.check('ID'):
            params.append(self.consume('ID').value)
        
        self.consume('ARROW')
        body = self.parse_expression()
        
        node = Lambda(params, body)
        node.line = token.line
        return node

    def parse_ternary(self) -> Node:
        # condition ? true_expr : false_expr
        condition = self.parse_logic_or()
        
        if self.check('QUESTION'):
            self.consume('QUESTION')
            true_expr = self.parse_expression()
            self.consume('COLON')
            false_expr = self.parse_expression()
            node = Ternary(condition, true_expr, false_expr)
            node.line = condition.line
            return node
        
        return condition

    def parse_logic_or(self) -> Node:
        left = self.parse_logic_and()
        
        while self.check('OR'):
            op_token = self.consume()
            right = self.parse_logic_and()
            new_node = BinOp(left, op_token.value, right)
            new_node.line = op_token.line
            left = new_node
            
        return left

    def parse_logic_and(self) -> Node:
        left = self.parse_comparison()
        
        while self.check('AND'):
            op_token = self.consume()
            right = self.parse_comparison()
            new_node = BinOp(left, op_token.value, right)
            new_node.line = op_token.line
            left = new_node
            
        return left

    def parse_comparison(self) -> Node:
        # Simple binary operators handling
        # precedence: ==, !=, <, >, <=, >=, is, matches
        left = self.parse_arithmetic()
        
        if self.peek().type in ('EQ', 'NEQ', 'GT', 'LT', 'GE', 'LE', 'IS', 'MATCHES'):
            op_token = self.consume()
            op_val = op_token.value
            if op_token.type == 'IS':
                op_val = '==' # Treat 'is' as equality
            # matches is kept as matches
                
            right = self.parse_arithmetic()
            node = BinOp(left, op_val, right)
            node.line = op_token.line
            return node
            
        return left

    def parse_arithmetic(self) -> Node:
        # precedence: +, -
        left = self.parse_term()
        
        while self.peek().type in ('PLUS', 'MINUS'):
            op_token = self.consume()
            right = self.parse_term()
            new_node = BinOp(left, op_token.value, right)
            new_node.line = op_token.line
            left = new_node
            
        return left

    def parse_term(self) -> Node:
        # precedence: *, /, %
        left = self.parse_factor()
        
        while self.peek().type in ('MUL', 'DIV', 'MOD'):
            op_token = self.consume()
            right = self.parse_factor()
            new_node = BinOp(left, op_token.value, right)
            new_node.line = op_token.line
            left = new_node
            
        return left


    def parse_convert(self) -> Convert:
        """Parse: convert expr to json"""
        token = self.consume('CONVERT')
        expr = self.parse_factor() # parse simple factor or expression? 'convert data' - data is factor.
        
        self.consume('TO')
        
        target_format = 'json'
        if self.check('JSON'):
             self.consume('JSON')
        elif self.check('ID'):
             target_format = self.consume('ID').value
             
        node = Convert(expr, target_format)
        node.line = token.line
        return node

    def parse_download(self) -> Download:
        """Parse: download 'url'"""
        token = self.consume('DOWNLOAD')
        url = self.parse_expression()
        self.consume('NEWLINE')
        node = Download(url)
        node.line = token.line
        return node

    def parse_archive(self) -> ArchiveOp:
        """Parse: compress folder 'x' to 'y' / extract 'x' to 'y'"""
        op = None
        token = None
        if self.check('COMPRESS'):
            token = self.consume('COMPRESS')
            op = 'compress'
            if self.check('FOLDER'): self.consume('FOLDER')
        else:
            token = self.consume('EXTRACT')
            op = 'extract'
            
        source = self.parse_expression()
        self.consume('TO')
        target = self.parse_expression()
        self.consume('NEWLINE')
        
        node = ArchiveOp(op, source, target)
        node.line = token.line
        return node

    def parse_csv_load(self) -> CsvOp:
        """Parse: load csv 'path'"""
        token = self.consume('LOAD')
        self.consume('CSV')
        path = self.parse_expression()
        # Should we allow assignment here? usually 'users = load csv ...'
        # Which is an Assign statement.
        # But parse_assign handles ID = ...
        # If we have 'users = load csv ...', parse_statement sees ID, goes to parse_id_start...
        # -> checks ASSIGN -> parse_expression.
        # So 'load csv' must be parsed as an EXPRESSION if used in assignment.
        # But here we added it to parse_statement.
        # If used as statement: `load csv "file"` -> implicitly prints result due to display logic?
        # We need to add `load` to parse_expression / parse_factor to be usable in assignment.
        self.consume('NEWLINE')
        node = CsvOp('load', None, path)
        node.line = token.line
        return node
        
    def parse_csv_save(self) -> CsvOp:
         """Parse: save expr to csv 'path'"""
         token = self.consume('SAVE')
         data = self.parse_expression()
         self.consume('TO')
         self.consume('CSV')
         path = self.parse_expression()
         self.consume('NEWLINE')
         node = CsvOp('save', data, path)
         node.line = token.line
         return node

    def parse_clipboard(self) -> Node:
        """Parse: copy expr to clipboard OR paste from clipboard"""
        if self.check('COPY'):
            token = self.consume('COPY')
            content = self.parse_expression()
            self.consume('TO')
            self.consume('CLIPBOARD')
            self.consume('NEWLINE')
            node = ClipboardOp('copy', content)
            node.line = token.line
            return node
        else:
             # Paste is usually an expression: text = paste from clipboard
             # If statement: paste from clipboard (useless unless implicit print?)
             # Let's support statement
             token = self.consume('PASTE')
             self.consume('FROM')
             self.consume('CLIPBOARD')
             self.consume('NEWLINE')
             node = ClipboardOp('paste', None)
             node.line = token.line
             return node

    def parse_automation(self) -> AutomationOp:
         """Parse: press 'x', type 'x', click at x, y, notify 't' 'b'"""
         if self.check('PRESS'):
             token = self.consume('PRESS')
             keys = self.parse_expression()
             self.consume('NEWLINE')
             return AutomationOp('press', [keys])
         elif self.check('TYPE'):
             token = self.consume('TYPE')
             text = self.parse_expression()
             self.consume('NEWLINE')
             return AutomationOp('type', [text])
         elif self.check('CLICK'):
             token = self.consume('CLICK')
             self.consume('AT')
             x = self.parse_expression()
             if self.check('COMMA'): self.consume('COMMA') # optional
             y = self.parse_expression()
             self.consume('NEWLINE')
             return AutomationOp('click', [x, y])
         elif self.check('NOTIFY'):
             token = self.consume('NOTIFY')
             title = self.parse_expression()
             msg = self.parse_expression()
             self.consume('NEWLINE')
             return AutomationOp('notify', [title, msg])

    def parse_write(self) -> FileWrite:
        """Parse: write 'text' to file 'path'"""
        token = self.consume('WRITE')
        content = self.parse_expression()
        self.consume('TO')
        self.consume('FILE')
        path = self.parse_expression()
        self.consume('NEWLINE')
        node = FileWrite(path, content, 'w')
        node.line = token.line
        return node

    def parse_append(self) -> FileWrite:
        """Parse: append 'text' to file 'path'"""
        token = self.consume('APPEND')
        content = self.parse_expression()
        self.consume('TO')
        self.consume('FILE')
        path = self.parse_expression()
        self.consume('NEWLINE')
        node = FileWrite(path, content, 'a')
        node.line = token.line
        return node

