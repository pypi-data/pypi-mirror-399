
from dataclasses import dataclass, field
from typing import Any, List, Optional

@dataclass
class Node:
    line: int = field(default=0, init=False)

@dataclass
class Number(Node):
    value: int

@dataclass
class String(Node):
    value: str

@dataclass
class Regex(Node):
    pattern: str

@dataclass
class VarAccess(Node):
    name: str

@dataclass
class Assign(Node):
    name: str # variable name
    value: Node

@dataclass
class PropertyAssign(Node):
    instance_name: str
    property_name: str
    value: Node

@dataclass
class UnaryOp(Node):
    op: str
    right: Node

@dataclass
class BinOp(Node):
    left: Node
    op: str
    right: Node

@dataclass
class Print(Node):
    expression: Node
    style: Optional[str] = None
    color: Optional[str] = None

@dataclass
class If(Node):
    condition: Node
    body: List[Node]
    else_body: Optional[List[Node]] = None

@dataclass
class While(Node):
    condition: Node
    body: List[Node]

@dataclass
class For(Node):
    count: Node
    body: List[Node]

@dataclass
class ListVal(Node):
    elements: List[Node]

@dataclass
class Dictionary(Node):
    pairs: List[tuple[Node, Node]]

@dataclass
class SetVal(Node):
    elements: List[Node]

@dataclass
class Boolean(Node):
    value: bool

@dataclass
class Input(Node):
    prompt: Optional[str] = None

@dataclass
class FunctionDef(Node):
    name: str
    args: List[tuple[str, Optional[Node], Optional[str]]] # [(name, default_node, type_hint), ...]
    body: List[Node]
    return_type: Optional[str] = None

@dataclass
class Call(Node):
    name: str
    args: List[Node]
    body: Optional[List[Node]] = None # For WebDSL (e.g. div ... \n ...block)

@dataclass
class Return(Node):
    value: Node

@dataclass
class ClassDef(Node):
    name: str
    properties: List[str]
    methods: List[FunctionDef]
    parent: Optional[str] = None

@dataclass
class Instantiation(Node):
    var_name: str
    class_name: str
    args: List[Node]

@dataclass
class MethodCall(Node):
    instance_name: str
    method_name: str
    args: List[Node]

@dataclass
class PropertyAccess(Node):
    instance_name: str
    property_name: str

@dataclass
class Import(Node):
    path: str

@dataclass
class Try(Node):
    try_body: List[Node]
    catch_var: str
    catch_body: List[Node]

@dataclass
class Lambda(Node):
    params: List[str]
    body: Node  # Single expression

@dataclass
class Ternary(Node):
    condition: Node
    true_expr: Node
    false_expr: Node

@dataclass
class ListComprehension(Node):
    expr: Node
    var_name: str
    iterable: Node
    condition: Optional[Node] = None

@dataclass
class Spread(Node):
    value: Node

@dataclass
class ConstAssign(Node):
    name: str
    value: Node

@dataclass
class ForIn(Node):
    var_name: str
    iterable: Node
    body: List[Node]

@dataclass
class IndexAccess(Node):
    obj: Node
    index: Node

@dataclass
class Stop(Node):
    """Break out of loop"""
    pass

@dataclass
class Skip(Node):
    """Continue to next iteration"""
    pass

@dataclass
class When(Node):
    """Pattern matching - when x is value1 => ... otherwise => ..."""
    value: Node
    cases: List[tuple[Node, List[Node]]]  # [(match_value, body), ...]
    otherwise: Optional[List[Node]] = None

@dataclass
class Throw(Node):
    """Throw an error - error 'message'"""
    message: Node

@dataclass
class TryAlways(Node):
    """Try with always block - try ... catch ... always ..."""
    try_body: List[Node]
    catch_var: str
    catch_body: List[Node]
    always_body: List[Node]

@dataclass
class Unless(Node):
    """Negative if - unless condition"""
    condition: Node
    body: List[Node]
    else_body: Optional[List[Node]] = None

@dataclass
class Execute(Node):
    """Execute code from string - execute 'say hello'"""
    code: Node

@dataclass
class Repeat(Node):
    """Simple repeat loop - repeat 5 times"""
    count: Node
    body: List[Node]

@dataclass
class ImportAs(Node):
    """Import with alias - use 'math' as m"""
    path: str
    alias: str

@dataclass
class Until(Node):
    """Loop until condition - until done"""
    condition: Node
    body: List[Node]

@dataclass
class Forever(Node):
    """Infinite loop - forever"""
    body: List[Node]

@dataclass
class Exit(Node):
    """Exit program - exit or exit 1"""
    code: Optional[Node] = None

@dataclass  
class Make(Node):
    """Create object - make Robot or new Robot"""
    class_name: str
    args: List[Node]

@dataclass
class FileWatcher(Node):
    """File watcher - on file_change 'path' ..."""
    path: Node
    body: List[Node]

# --- New GUI Nodes ---
@dataclass
class Alert(Node):
    message: Node

@dataclass
class Prompt(Node):
    prompt: Node

@dataclass
class Confirm(Node):
    prompt: Node

# --- Async Nodes ---
@dataclass
class Spawn(Node):
    call: Node

@dataclass
class Await(Node):
    task: Node

@dataclass
class ProgressLoop(Node):
    """show progress for i in ..."""
    loop_node: Node # The underlying loop (For or ForIn or Repeat)
    
@dataclass
class Convert(Node):
    """convert x to json"""
    expression: Node
    target_format: str

@dataclass
class Listen(Node):
    """listen on port 8000"""
    port: Node

@dataclass
class OnRequest(Node):
    """on request to "/path" ..."""
    path: Node # or pattern
    body: List[Node]

@dataclass
class Every(Node):
    """every 5 minutes ..."""
    interval: Node
    unit: str # 'seconds', 'minutes'
    body: List[Node]

@dataclass
class After(Node):
    """in 5 minutes ..."""
    delay: Node
    unit: str
    body: List[Node]

@dataclass
class ServeStatic(Node):
    folder: Node
    url: Node

@dataclass
class Download(Node):
    url: Node

@dataclass
class ArchiveOp(Node):
    op: str # 'compress' or 'extract'
    source: Node
    target: Node

@dataclass
class CsvOp(Node):
    op: str # 'load' or 'save'
    data: Optional[Node]
    path: Node

@dataclass
class ClipboardOp(Node):
    op: str # 'copy' or 'paste'
    content: Optional[Node] # for copy

@dataclass
class AutomationOp(Node):
    action: str # 'press', 'type', 'click', 'notify'
    args: List[Node]

@dataclass
class DateOp(Node):
    expr: str # "next friday"

@dataclass
class FileWrite(Node):
    """write 'text' to file 'path' (mode='w') or append (mode='a')"""
    path: Node 
    content: Node 
    mode: str # 'w' or 'a'

@dataclass
class FileRead(Node):
    """read file 'path'"""
    path: Node

@dataclass
class DatabaseOp(Node):
    """db open 'path', db query 'sql', etc."""
    op: str
    args: List[Node]
