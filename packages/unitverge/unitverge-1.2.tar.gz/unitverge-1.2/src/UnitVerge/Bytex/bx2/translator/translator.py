'''
# BYTEX2
Main file of bytex translator.

## Extend:
    parse(code: str) -> list[list[str]]

        : Simple language parser and splitter.
    
    Generator : metaclass

        : Metaclass for code generation.
    
    GenerateContex : metaclass

        : Metaclass with fast functions and context for translator
    
    Translator : class

        : Main class for translation bytex to python instructions.
'''



try: import cloudpickle as pickle
except: import pickle
from .exceptions import *
from .generator import Generator
from pathlib import Path

LIBS = Path.home() / 'BTXLIBS' # path for libs



class GenerateContext(Generator):
    def __init__(self, safemode: bool = False):
        super().__init__()
        self.user_structs = { # user commands
            'COMMAND':{'PARSER': lambda context, line: 0 } # EXAMPLE
            # context - [Translator] object
            # line - full line ([0] - is command)
        }
        self.in_struct = 0 # structures "stack"
        self._in_code = False # in code block
        self.included = [] # included libs
        self.safe = safemode # safemode
        self._last_funcs = [] # functions stack
        self._constants = [] # constants name
        self._variables = [] # variables name
        self._var_val = {} # variables values 
        self._macroses = {} # macroses (bytex2 code)
        self.allowed = ['all'] # white list
        self.not_allowed = [None] # black list
        self.writepython = False # add raw pyhthon code if true
        # ADD WILL BE WITHOUT CHECKS! (not allowed in safemode)
        self._macros = None # current macros name (without stack)
        if safemode: # replace builtins if safemode
            code = '''
# ======================
# =  !!! SAFEMODE !!!  =
# ======================

def not_available(what: str):
    def inner(*args, **kwargs): raise SystemError('Exec is not available in safemode')
    return inner

__builtins__.exec = not_available('Exec')
__builtins__.eval = not_available('Eval')'''.split('\n')
            self.main_edit(code)
    
    def block_command(self, command: str):
        'Add comand to blacklist'
        self.not_allowed.append(command)
    
    def command(self, command: str, parser: object):
        '''
        Add command to language.
        
        Args:
            - command : str 
                - command to parse
            
            - parser : object - function (context: Translator, line: list[str])
                - object to parse command
        '''
        self.user_structs[command] = {'PARSER': parser}
        return self
    
    def pre_edit(self, code: list[str]):
        for line in code: 
            self._pre.append(line)
        return self

    def post_edit(self, code: list[str]):
        for line in code: 
            self._end.append(line)
        return self

    def main_edit(self, code: list[str]):
        for line in code: 
            self._line(line)
        return self
    
    def _paste_macros(self, args):
        name = args[0]
        args = ' '.join(args[1:]).split(', ')
        if name in self._macroses.keys():
            macro = []
            for line in self._macroses[name]:
                to_append = []
                for i in line:
                    if str(i).strip().startswith('$'):
                        _i = str(i).strip()[1:]
                        for arg in args:
                            _arg = arg.split('=')
                            if str(_arg[0]).strip().replace(' ', '') in _i.replace(' ', ''):
                                _i = '='.join(_arg[1:])
                                _i = _i.replace('//.', ',')
                                _i = _i.replace('//:', ';')
                                i = _i.strip()
                        i = i.strip()
                    to_append.append(i)
                macro.append(to_append)
            for line in macro:
                self.translate(' '.join(line))
        else:
            raise ValueError(f'Try to paste unknown macros: {name}\n(has: {", ".join(self._macroses.keys())})')
        
    def _include(self, args):
        if self.safe: # not allowed in safemode
            raise Bytex2Error("Include error', 'Include is not available in safemode. Turn off safemode or use '#append'.")
        name = args[0]
        libs = [name] if len(args) == 1 else args[1:] # libs list
        append = f'{name}{libs}' # for debug
        if append in self.included: return
        else: self.included.append(append)
        try:
            # open file and get raw bytex code for translate
            with open(f"{name}.btx", 'r') as f: 
                content = f.read()
        except FileNotFoundError: # parse exception
            raise Bytex2Error('Include error', 
                    f"Module {name} is not found.")
        # translate and execute code
        # translated code will be contains -
        # - _is_lib : bool : file is library if true
        # - in_lib : bool : true if lib is not compleated
        # - LIB[name] : str : parameters with raw python code of libs
        localscope = locals()
        trs = Translator()
        code = trs.translate(content)
        self._log += trs._log
        code = '\n'.join(code)
        exec(code, localscope, localscope)
        # if file is library
        if not localscope['_is_lib']:
            raise Bytex2Error('Include error', "File has no lib. Did you mean '#append'?")
        if localscope['in_lib']:
            raise Bytex2Error('Include error', 
                "Lib is not finished or unknown syntax. Did you forget add '#ELIB' block?")
        for lib in libs: # add libs to code
            try: # try to get library raw code from code
                self.pre_edit([f'{lib} = """{localscope[f"LIB{lib}"]}"""'])
            except KeyError:
                raise Bytex2Error('Include error', 
                    f"Lib {lib} is not found in file.")
            # add executor to code
            self.pre_edit([f'exec({lib})'])
            self.pre_edit([f'libs.append("{lib}")'])
            # create lib object
            self.work(['create', 'lib_' + lib, lib])
            
    


    def _append(self, args):
        try:
            # open and read bytex file
            with open(f"{args[0]}.btx", 'r') as f:
                content = f.read()
        except FileNotFoundError:
            raise Bytex2Error('Include error', 
                    f"Module {args[0]} is not found.")
        trs = Translator()
        compiled = trs.translate(content)
        self._pre.append(f'# APPEND: {args[0]}')
        self._log += trs._log
        # add code from file to current code
        [self._pre.append(str(i))
        for i in compiled]
    
    def _sys_check(self, args):
        arg = args[0]
        match arg:
            case 'unsafe':
                if not self.safe: # raise exception if not in safemode
                    self._line('raise SystemError("\nCode execution must be in safemode.")')
            case 'safe': # raise exceprion if in safemode
                if self.safe:
                    self._line('raise SystemError("\nCode execution must be without safemode.")')
            case 'lib': # raise exception if lib
                self.main_edit([
                    'if _is_lib:'
                    '    raise SystemError("\nCode must be not lib.")'
                ])
            case 'notlib': # raise exception if not lib
                self.main_edit([
                    'if not _is_lib:'
                    '    raise SystemError("\nCode must be not lib.")'
                ])
            case _: # raise exception if condition is true
                cond = " ".join(args[0:])
                self._line(f'if {cond}:')
                self._line(f'    raise SystemError("\\nSystem check failed ({cond}).")') 










def parse(code: str) -> list[list[str]]:
    lines = []
    current_line = []
    in_string = False
    string_char = ''
    current_token = ''
    triple_quote = False
    
    i = 0
    while i < len(code):
        char = code[i]
        if char in '\'"' and i + 2 < len(code) and code[i:i+3] in ('"""', "'''"):
            if not in_string:
                in_string = True
                triple_quote = True
                string_char = code[i:i+3]
                current_token += string_char
                i += 2 
            elif string_char == code[i:i+3]:
                in_string = False
                triple_quote = False
                string_char = ''
                current_token += code[i:i+3]
                current_line.append(current_token)
                current_token = ''
                i += 2
            else:
                current_token += char
        elif char in '\'"' and (i == 0 or code[i-1] != '\\'):
            if not in_string:
                in_string = True
                string_char = char
                current_token += char
            elif char == string_char and not triple_quote:
                in_string = False
                string_char = ''
                current_token += char
                current_line.append(current_token)
                current_token = ''
            else:
                current_token += char
        elif in_string:
            current_token += char
        elif char == ';':
            if current_token:
                current_line.append(current_token)
                current_token = ''
            if current_line:
                lines.append(current_line)
                current_line = []
        elif char == ' ' or char == '\t':
            if current_token:
                current_line.append(current_token)
                current_token = ''
        elif char == '\n':
            if current_token:
                current_line.append(current_token)
                current_token = ''
            if current_line:
                lines.append(current_line)
                current_line = []
        else:
            current_token += char
        i += 1
    if current_token:
        current_line.append(current_token)
    if current_line:
        lines.append(current_line)
    return lines































































class Translator(GenerateContext):
    '''
    # Translator
    Bytex2 code interpreter. 

    Translate Bytex2 code to python interactive with bytex2-vm.

    ## Args:
    - safemode : bool : add more check and block unsafe operations if true.

    ## Methods:
    - translate (code: str) 
        -> list[str] (python code) 
        : interprete your code 
    
    - plugin (type: str) 
        -> object 
        : add extension to language
    
    - @add_command_handler (command: str)
        -> decorator
        : add command to language
    
    ## Examples: 
    >>> code = '+; cns; ns; cnr; >; out.'
    >>> final = Translator().translate(code = code)
    >>> exec(final) # out: 1
    '''
    def __init__(self, safemode: bool = False, preload = None):
        super().__init__(safemode)
        if preload is not None:
            self = preload
        
    def translate(self, code: str):
        '''
        # Translate
        Bytex2 code interpreter.

        ## Args:
        - code: str : code to interprete

        # Return
        -> list[str] : compiled python code
        '''
        code = parse(code)
        self.parse(code)
        return self.code
    
    def plugin(self, type: str = 'command'):
        '''
        Add Plugin to language. 
        
        types: 
            - command 
                -> function (command: str, parser: object)
                : add command to language
            - main
                -> function (code: list[str])
                : edit main code
            - pre 
                -> function (code: list[str])
                : edit code preprocess
            - post
                -> function (code: list[str])
                : edit finalization code
            - block
                -> function (command: str)
                : add command to black list
        '''
        if type == 'command':
            return self.command
        elif type == 'pre':
            return self.pre_edit
        elif type == 'post':
            return self.post_edit
        elif type == 'main':
            return self.main_edit
        elif type == 'block':
            return self.block_command
        else:
            raise Bytex2Error('Plugin error', f'Unknown type of plugin: {type}')
    
    def add_command_handler(self, command: str):
        """
        Add command decorator.
        
        Example:
            >>> @translator.add_command_handler('mycmd')
            >>> def handle_mycmd(context, line):
            >>>     context.main_edit(['# comment'])
        """
        def decorator(handler_func):
            self.command(command=command, parser=handler_func)
            return handler_func
        return decorator
        
    def parse(self, code: list[list[str]]):
        for line in code:
            if self.allowed != ['all']:
                if line[0] not in self.allowed:
                    raise SyntaxError(f'Command [{line[0]}] is not in allowed list.')
            if self.not_allowed != [None]:
                if line[0] in self.not_allowed:
                    raise SyntaxError(f'Command [{line[0]}] is not allowed.')
            try:
                if self.writepython and line[0] != 'python': # append raw python
                    if not self.safe:
                        self._line(" ".join(line).replace('\\tab|', '    '))
                    else:
                        raise RuntimeError('Safemode error', 'Turn off safe mode.')
                elif self._macros != None and not line[0].startswith('#'): # work in macros
                    # Store line in macro without adding to output or log
                    curr = self._macroses[self._macros]
                    if isinstance(curr, list):
                        res = curr + [line]
                    else:
                        res = [line]
                    self._macroses[self._macros] = res
                else:
                    # Only add to log and process lines that are not inside macros
                    self._log.append(('    ' * self.tabs) + ' '.join(line))
                    self._line(f'# RAW {repr(line)}')
                    self.work(line)
            except Exception as e: 
                raise TranslationError(f'Interprete error - {e.__class__.__name__}', str(e), line, code, 1)
                
    
    
    
    def work(self, line: list[str]):
        
        command = line[0]
        self._line(f'# line: {repr(" ".join(line))}')
        if command.startswith('#') and command != '#':
            self._preprocess(line)
            return
        elif command.startswith('@'):
            self._system(line)
            return
        elif command.startswith('!'):
            self._param(line)
            return
        elif command in self.user_structs.keys():
            try: self.user_structs[command]['PARSER'](self, line)
            except Exception as e:
                raise Bytex2Error(f'Plugin exception', str(e))
        else:
            self._main(line)
            return
    
    
    
    
    
    def _preprocess(self, line):
        command = line[0]
        args = line[1:]
        def basicargscheck(args):
            if ';' in args or ' ' in args:
                raise ValueError(f'Bad input value: {args}')
        def checklen(length: int = 0, operator: str = "!="):
            if not eval(f'len(args) {operator} length'):
                raise SyntaxError(f"Invalid argument length: {len(args)} (must be {length})")
        match command:
            case '#append':
                checklen(1, '==')
                basicargscheck(args[0])
                self._append(args)
            
            case '#include':
                checklen(1, '>=')
                basicargscheck(args[0])
                self._include(args)
           
            case '#pymodule':
                checklen(1, '>=')
                libs = args[0:]
                for lib in libs:
                    basicargscheck(lib)
                    try:
                        __import__(str(lib))
                    except ImportError:
                        raise Bytex2Error('Import error', f"Lib {lib} is not found.")
                    self._pre.append(f'import {lib}')
                
            case '#import':
                checklen(1, '==')
                basicargscheck(args[0])
                try:
                    with open(LIBS / (args[0].replace('.', '/') + '.btx'), 'r') as lib:
                        content = lib.read()
                    trs = Translator()
                    trs.translate(content)
                    code = trs._pre + trs._code + trs._end
                    self._log += trs._log
                    # sync macroses
                    newmacroses = self._macroses
                    for key in trs._macroses.keys():
                        newmacroses[key] = trs._macroses[key]
                    self._macroses = newmacroses
                    # sync variables
                    newvars = self._var_val
                    for key in trs._var_val.keys():
                        newvars[key] = trs._var_val[key]
                    self._var_val = newvars
                    # sync commands
                    newuserstructs = self.user_structs
                    for key in trs.user_structs.keys():
                        newuserstructs[key] = trs.user_structs[key]
                    self.user_structs = newuserstructs
                    # sync variables namess
                    self._variables += trs._variables
                    self.main_edit(code)
                except Exception as e:
                    raise SystemError(f"Import error:\n\t{e}")       
            
            case '#SLIB': # start LIB
                checklen(1, '==')
                basicargscheck(args[0])
                self._line('in_lib = True')
                self.work(['#SCODE', f'LIB{args[0]}'])
                self.work(['struct', "lib_" + args[0]])
            
            case '#ELIB': # end LIB
                checklen(0, '==')
                self.work(['endstruct'])
                self.work(['#ECODE'])
                self._line('in_lib = False')
            
            case '#SCODE': # start raw code block
                checklen(1, '==')
                basicargscheck(args[0])
                if not self._in_code: 
                    self._line(f'{args[0]} = """\n')
                    self._in_code = True
            
            case '#ECODE': # end raw code block
                checklen(0, '==')
                if self._in_code: self._line('"""')

            case '#SMACRO': # macros start
                checklen(1, '==')
                basicargscheck(args[0])
                name = args[0]
                self._line(f'# start of macros {name}')
                self._macroses[name] = []
                self._macros = name

            case '#EMACRO': # macros ens
                checklen(1, '==')
                basicargscheck(args[0])
                name = args[0]
                if self._macros == name:
                    self._macros = None
                    self._line(f'# end of macros {name}')
                else:
                    raise ValueError(f'Try to final unknown macros (current: {self._macros}): {name}')
                
            case '#PMACRO': # paste macros
                checklen(1, '>=')
                basicargscheck(args[0])
                self._paste_macros(args)
            
            case '#SLANGMOD': # start language modification
                checklen(1, '==')
                self._preprocess(['#SMACRO', f'__TMP{args[0]}__'])
                self.parse([[f'stdfunc', f'edit{args[0]}', 'CTX']])
            
            case '#ELANGMOD':
                checklen(1, '==')
                self._preprocess(['#EMACRO', f'__TMP{args[0]}__'])

            case '#LANGMOD':
                if self.safe:
                    raise SystemError('Language dit is not available in safemode.')
                checklen(1, '==')
                name = args[0]
                trs = Translator()
                trs._macros = self._macros
                trs._macroses = self._macroses
                trs._paste_macros([f"__TMP{name}__"])
                code = trs._pre + trs._code + trs._end
                localscope = locals()
                exec('\n'.join(code), localscope, localscope)
                func = localscope[f"edit{name}"]
                func(self)
            
            case _:
                raise SyntaxError('Unknown preprocess command')
    
    
    
    
    
    def _system(self, line):
        command = line[0]
        args = line[1:]
        def checklen(length: int = 0, operator: str = "!="):
            if not eval(f'len(args) {operator} length'):
                raise SyntaxError(f"Invalid argument length: {len(args)} (must be {length})")
        match command:
            case '@islib':
                checklen(0, '==')
                self._pre.append(f'_is_lib = True')
            
            case '@vm-nochecks':
                checklen(0, '==')
                self._line('MEM.CHECK = False')
            
            case '@vm-checks':
                checklen(0, '==')
                self._line('MEM.CHECK = True')
            
            case '@check':
                self._sys_check(args)
                
            case '@jit':
                self._line(f'@jit({" ".join(args)})')
            
            case '@cache':
                try:self._line(f'@functools.lru_cache(maxsize={int(args[0])})')
                except TypeError:
                    raise TypeError(f'Bad input: {args[0]}')
            
            case '@require':
                self._line(f'if not LANG.haslib({repr(str(args[0]))}):')
                self._line(f'''    raise ImportError("Lib {args[0]} is not included. Did you forgot wtite '#include [module] {args[0]}'?")''')
            
            case '@addtabs':
                checklen(0, '==')
                self.tabs += 1

            case '@subtabs':
                checklen(0, '==')
                self.tabs -= 1
            
            case '@int-lim':
                checklen(1, '==')
                try:self._line(f"sys.set_int_max_str_digits({int(args[0])})")
                except TypeError:
                    raise TypeError(f'Bad input: {args[0]}')
            
            case _:
                raise SyntaxError('Unknown system command')
    
    
    
    
    def _param(self, line):
        command = line[0]
        args = line[1:]
        def checklen(length: int = 0, operator: str = "!="):
            if not eval(f'len(args) {operator} length'):
                raise SyntaxError(f"Invalid argument length: {len(args)} (must be {length})")
        match command:
            case '!ldtp': # load data to parameter
                checklen(2, '==')
                try:addr = int(args[0])
                except TypeError:
                    raise TypeError(f'Bad input: {args[0]}')
                self._line(f'MEM.setto_p({args[1]}, {addr})')
            
            case '!lctp': # load current to parameter
                checklen(1, '==')
                try: self._line(f'MEM.setto_p({int(args[0])}, MEM.getdata())')
                except TypeError:
                    raise TypeError(f'Bad input: {args[0]}')
            
            case '!ldfp': # load data from parameter
                checklen(1, '==')
                try: 
                    self._line(f'MEM.setdata(\n{"    " * (self.tabs + 1)}MEM.getfrom_p({int(args[0])})\n{"    " * self.tabs})')
                except TypeError:
                    raise TypeError(f'Bad input: {args[0]}')
            
            case '!gdfp': # get data from parameter
                checklen(2, '==')
                try: addr = int(args[0])
                except TypeError:
                    raise TypeError(f'Bad input: {args[0]}')
                self._main(['var', args[1], f'MEM.getfrom_p({addr})'])
            
            case _:
                raise SyntaxError('Unknown parameter command')
    
    
    
    def _main(self, line: list[str], addcoments: bool = True):
        command = line[0]
        args = line[1:]
        def operation(a, b, op):
            if addcoments: self._line(f'# operation {a} {op} {b}')
            self._line(f'__res = MEM.getdata({a}) {op} MEM.getdata({b})')
            self._line(f'MEM.setdatato({a}, __res)')
        def operationreg(rega, regb, a, b, op):
            if addcoments:self._line(f'# register operation')
            if addcoments:self._line(f'# {rega}:{a} {op} {regb}:{b}')
            self._line(f'__res = MEM.getreg({rega})[{a}] {op} MEM.getreg({regb})[{b}]')
            self._line(f'MEM.regs[{rega}][{a}] = __res')
        def checklen(length: int = 0, operator: str = "!="):
            if not eval(f'len(args) {operator} length'):
                raise SyntaxError(f"Invalid argument length: {len(args)} (must be {length})")

        if command.startswith('e-'): # end and
            self.work(['end'])
            command = command[2:]
            self.work([command]+args)
            return
                
        match command:
            case 'start': # declarate point
                checklen(1, '==')
                if addcoments:self._line(f'# start of point {args[0]}')
                self._last_funcs.append(args[0])
                self._pre.append(f'points.append("{args[0]}")')
                self._line(f'def {args[0]}():')
                self.tabs += 1
                self._line('pass')
            
            case 'return':
                if len(args) == 1:
                    what = args[0]
                    if what in self._variables:
                        self.main_edit([f'return {what}'])
                        self.work(['endf'])
                    else:
                        raise SystemError('Functions can return only variables.')
                elif len(args) == 0:
                    self.main_edit([f'return None'])
                    self.work(['endf'])
                else:
                    raise SystemError('Bad return arguments: can be only variable or empty.')
            
            case 'python':
                self.writepython = not self.writepython
            
            case 'func': # declarate function
                checklen(1, ">=")
                if addcoments:self._line(f'# start of method {args[0]}')
                if self.in_struct:
                    name = args[0]
                    self._last_funcs.append(name)
                    docs = 'pass'
                    if len(args) >= 2:
                        if args[1].startswith(("'''")) and args[1].endswith(("'''")):
                            docs = args[1]
                            args = args[1:]
                    func_args = "self, " + " ".join(args[1:])
                    self._line(f'def {name}({func_args}):')
                    self.tabs += 1
                    self._line(docs)
                else:
                    raise SyntaxError('Must be in struct')
        
            case 'sfunc': # declarate static function
                checklen(1, ">=")
                if addcoments:self._line(f'# start of static method {args[0]}')
                name = args[0]
                self._last_funcs.append(name)
                docs = 'pass'
                if len(args) >= 2:
                        if args[1].startswith(("'''")) and args[1].endswith(("'''")):
                            docs = args[1]
                            args = args[1:]
                func_args = " ".join(args[1:])
                self._line("@staticmethod")
                self._line(f'def {name}({func_args}):')
                self.tabs += 1
                self._line(docs)
            
            case 'stdfunc': # declarate standart function
                checklen(1, ">=")
                if addcoments:self._line(f'# start of standart function {args[0]}')
                name = args[0]
                self._last_funcs.append(name)
                docs = 'pass'
                if len(args) >= 2:
                        if args[1].startswith(("'''")) and args[1].endswith(("'''")):
                            docs = args[1]
                            args = args[1:]
                func_args = " ".join(args[1:])
                self._line(f'def {name}({func_args}):')
                self.tabs += 1
                self._line(docs)
            
            case 'struct':
                checklen(1, "==")
                if addcoments:self._line(f'# start of structure {args[0]}')
                self._line(f'class {args[0]}:')
                self.in_struct += 1
                self.tabs += 1
                self._line('_ = None')
            
            case 'async':
                checklen(1, ">=")
                if args[0] in ("stdfunc", "sfunc", "func"):
                    if addcoments: self.main_edit(["# new async use"])
                    self.main_edit(['async \\'])
                    self._main(args[0:], addcoments=False)
                elif args[0] == 'run':
                    checklen(2, ">=")
                    self.main_edit([f'asyncio.run({args[1]}({", ".join(args[2:])}))'])
            
            case 'await':
                checklen(2, "==")
                self._line(f'{args[1]} = await {args[0]}')
            
            case 'exloc': # exec in locals
                checklen(1, ">=")
                if self.safe:
                    raise SystemError('Exec is not available in sfemode.')
                code = " ".join(args[0:-1])
                if code.startswith(('\"', "\'")) and code.startswith(('\"', "\'")):
                    code = code[1:-1]
                    trs = Translator()
                    trs.translate(code)
                    compiled = trs._pre + trs._code + trs._end
                    self._log += trs._log
                    self.main_edit(compiled)
                else:
                    code = self._var_val.get(args[0], 
                        f'''"src raise SystemError("Invalid code for execute (line: {repr(" ".join([command] + args))})")"''')
                    self._main(['exec', code])
            
            case 'excode': # execute code
                checklen(1, ">=")
                if self.safe:
                    raise SystemError('Exec is not available in sfemode.')
                self.main_edit(['__code__ = ', args[0]])
                self.main_edit([
                    '__trs__ = Bytex("2.0").translator()',
                    '__compiled__ = __trs__.translate(__code__)',
                    'RAW += "\n".join(__trs__._log)'
                ])
                self.main_edit('localscope = loacls()')
                self.main_edit(['exec(__compiled__, localscope, localscope)'])

            case 'metadata': # add metadata to code
                checklen(1, ">=")
                args = ' '.join(args).split(', ')
                metaid = id(self)
                self.pre_edit(['metadata_'+str(metaid)+'='+repr(args)])

            case 'VM':
                checklen(1, ">=")
                self._line(f'MEM.{args[0]} {" ".join(args[1:])}')
            
            case 'self':
                checklen(1, ">=")
                if self.in_struct:
                    self._line(f'self.{args[0]} {" ".join(args[1:])}')
                else:
                    raise SyntaxError('Must be in struct')
            
            case 'create':
                checklen(2, ">=")
                if addcoments:self._line(f'# creating object')
                class_name = args[0]
                obj_name = args[1]
                constr_args = args[2:] if len(args) > 2 else []
                self._line(f'{obj_name} = {class_name}({" ".join(constr_args)})')
            
            case 'do':
                checklen(1, ">=")
                func_name = args[0]
                func_args = args[1:] if len(args) > 1 else []
                self._line(f'{func_name}({" ".join(func_args)})')

            case 'loop':
                checklen(0, "==")
                if addcoments:self._line(f'# loop')
                self._line(f'while True:')
                self.tabs += 1
                self._line('None')

            case 'repeat':
                checklen(1, "==")
                if addcoments:self._line(f'# repeat loop')
                try: self._line(f'for i in range(int({args[0]})):')
                except TypeError:
                    raise TypeError(f'Bad input: {args[0]}')
                self.tabs += 1
                self._line('None')
            
            case 'iters':
                checklen(2, "==")
                self._line(f"if {repr(args[0])} in points: MEM.repeat({args[0]}, {args[1]})")
            
            case 'delay':
                checklen(1, "==")
                self._line(f'time.sleep({args[0]} * 0.001)')
                
            case 'break':
                if addcoments:self._line(f'# break loop')
                if len(args) > 0:
                    if args[0] == 'if':
                        operator = args[1]
                        value = args[2]
                        self._line(f'if MEM.getdata() {operator} {value}:break')
                else: self._line('break')
            
            case 'end': # end of block
                checklen(0, "==")
                if self.tabs >= 1: self.tabs -= 1
                else: raise Bytex2Error('[end] Error', 'Try to finalize not stared block')
            
            case 'endf': # end of function block
                checklen(0, "==")
                if self.tabs >= 1: self.tabs -= 1
                else: raise Bytex2Error('[end] Error', 'Function is not started')
                try: self._last_funcs.pop()
                except: pass
            
            case 'endstruct': # end of structure
                checklen(0, "==")
                if self.tabs >= 1: 
                    self.tabs -= 1; 
                    self.in_struct -= 1
                
            case 'try':
                checklen(0, "==")
                self._line('try:')
                self.tabs += 1
                self._line('None')

            case 'err':
                checklen(0, "==")
                self._line('except Exception as e:')
                self.tabs += 1
                self._line('None')
            
            case 'handle':
                checklen(0, "==")
                self._line('except Exception as e: print(e)')
                
            case 'debug':
                checklen(0, "==")
                self._line('print(f"DEBUG: CURSOR={MEM.CURSOR}, ' \
                    'POINTER={MEM.POINTER}, DATA={MEM.getdata()}, HAND={MEM.hand}")')
                
            case 'goto':
                checklen(1, "==")
                self._line(f'if "{args[0]}" in points:')
                self.tabs += 1
                self._line(f'{args[0]}()')
                self.tabs -= 1
                self._line(f'else:')
                self.tabs += 1
                self._line(f'raise EXECUTIONERROR("Unknown point: {args[0]}")')
                self.tabs -= 1
            
            case 'save':
                checklen(1, "==")
                name = args[0]
                self._line(f'with open({name}, "wb") as f:')
                self._line(f'    pickle.dump(MEM, f)')
                
            case 'open':
                checklen(1, "==")
                if self.safe:
                    raise Bytex2Error('[safemode] Error', 'Open is not available in safemode.')
                name = args[0]
                self._line(f'with open({name}, "rb") as f:')
                self._line(f'    content = pickle.load(f)')
                self._line(f'MEM = content')
            
            case 'if':
                checklen(1, "==")
                cond = args[0]
                if cond in self._variables:
                    self._line(f'if {cond}:')
                    self.tabs += 1
                else:
                    raise SystemError('If block works only with variables. Format [if <variable name>]')
            
            case 'else':
                if len(args) == 1:
                    checklen(2, "==")
                    if args[0] != 'if':
                        raise SyntaxError('Unknow syntzx in else block')
                    args = args[1:]
                    cond = args[0]
                    if cond in self._variables:
                        self._line(f'elif {cond}:')
                        self.tabs += 1
                    else:
                        raise SystemError('Else if block works only with variables. Format [if <variable name>]')
                else:
                    checklen(0, "==")
                    self._line(f'else:')
                    self.tabs += 1
                
            case 'copy':
                checklen(1, "==")
                spl = args[0].split(':')
                self._line(f'MEM.setdataraw({spl[0]}, {spl[1]}, MEM.getdata())')
            
            case 'cns': # copy next section
                checklen(0, "==")
                self._line(f'MEM.setdataraw(MEM.CURSOR, MEM.POINTER+1, MEM.getdata())')
            
            case 'cnr': # copy next register
                checklen(0, "==")
                self._line(f'MEM.setdataraw(MEM.CURSOR+1, MEM.POINTER, MEM.getdata())')
            
            case 'cps': # copy prev section
                checklen(0, "==")
                self._line(f'MEM.setdataraw(MEM.CURSOR, MEM.POINTER-1, MEM.getdata())')
            
            case 'cpr': # copy prev register
                checklen(0, "==")
                self._line(f'MEM.setdataraw(MEM.CURSOR-1, MEM.POINTER, MEM.getdata())')

            case 'move':
                checklen(2, "==")
                self._line(f'MEM.setdatato({args[0]}, MEM.getdata())')
            
            case 'moveto':
                checklen(1, "==")
                self._line(f'MEM.CURSOR = int({args[0]})')
                
            case 'spawn':
                checklen(1, "==")
                point = args[0]
                self._line(f'threading.Thread(target={point}).start()')
                
            case 'error':
                checklen(1, "==")
                name = f'Error{args[0]}'
                self._line(f'class {name}(Exception):pass')
                self._line(f'raise {name}')
                
            case 'jump':
                checklen(1, "==")
                self._line(f'MEM.POINTER = int({args[0]})')
                
            case 'load':
                checklen(1, "==")
                self._line(f'MEM.setdata({args[0]})')
                
            case 'src':
                checklen(1, ">=")
                if not self.safe:
                    self._line(' '.join(args))
                else:
                    raise SyntaxError (f"Source code command is not available in safemode")
            
            case 'ewin': # end, work iters and next
                checklen(1, "==")
                if len(self._last_funcs) > 0:
                    func = self._last_funcs[-1]
                    self.translate('end')
                    self._line(f'MEM.repeat({func}, int({args[0]}))')
                    self.translate('>')
                else:
                    raise Bytex2Error('[ewin] Error', 'Function is not started')
            
            case 'ewip': # end, work iters and prev
                checklen(1, "==")
                if len(self._last_funcs) > 0:
                    func = self._last_funcs[-1]
                    self.translate('end')
                    self._line(f'MEM.repeat({func}, int({args[0]}))')
                    self.translate('<')
                else:
                    raise Bytex2Error('[ewip] Error', 'Function is not started')
            
            case 'ewni': # end, work iters with next
                checklen(1, "==")
                if len(self._last_funcs) > 0:
                    self.translate('>')
                    func = self._last_funcs[-1]
                    self.translate('end')
                    self._line(f'MEM.repeat({func}, int({args[0]}))')
                else:
                    raise Bytex2Error('[ewni] Error', 'Function is not started')
                
            case 'ewpi': # end, work iters with prev
                checklen(1, "==")
                if len(self._last_funcs) > 0:
                    self.translate('<')
                    func = self._last_funcs[-1]
                    self.translate('end')
                    self._line(f'MEM.repeat({func}, int({args[0]}))')
                else:
                    raise Bytex2Error('[ewpi] Error', 'Function is not started')

            case 'ns': # next section
                checklen(0, "==")
                self._line('MEM.POINTER += 1')
            
            case 'ps': # prev section
                checklen(0, "==")
                self._line('MEM.POINTER -= 1')
            
            case '>':
                checklen(0, "==")
                self._line('MEM.CURSOR += 1')
            
            case '<':
                checklen(0, "==")
                self._line('MEM.CURSOR -= 1')
            
            case '+':
                checklen(0, "==")
                self._line(f'MEM.setdatato(MEM.POINTER, MEM.getdata() + 1)')
            
            case '-':
                checklen(0, "==")
                self._line(f'MEM.setdatato(MEM.POINTER, MEM.getdata() - 1)')
            
            case 'in':
                checklen(0, "==")
                self._line('MEM.setdata(int(input()))')
            
            case 'sum':
                checklen(2, "==")
                reg = args[0]
                name = args[1]
                self._line(f'{name} = MEM.getsum({reg})')
            
            case 'var':
                checklen(2, ">=")
                type = ''
                if args[0].startswith(':'):
                    checklen(3, ">=")
                    type = args[0][1:]
                    args = args[1:]
                self._variables.append(args[0])
                self._line(f'{args[0]} = {type}({" ".join(args[1:])})')
                self._var_val[args[0]] = " ".join(args[1:])
            
            case 'const':
                checklen(2, ">=")
                type = ''
                if args[0].startswith(':'):
                    checklen(3, ">=")
                    type = args[0][1:]
                    args = args[1:]
                if str(args[0]) == str(args[0]).upper():
                    self.work(['var', f":{type}"] + args)
                    self._constants.append(args[0])
                else:
                    raise ValueError('Constant must be uppercased.')
                self._var_val[args[0]] = " ".join(args[1:])
            
            case 'varset':
                checklen(2, ">=")
                in_constants = str(args[0]) in self._constants
                in_varivables = str(args[0]) in self._variables
                if not in_varivables:
                    raise ValueError('Try to edit unknown variable.')
                if in_constants:
                    raise ValueError('Try to edit constant.')
                self.work(['var'] + args)
                self._var_val[args[0]] = " ".join(args[1:])

            case 'add':
                checklen(2, "==")
                a = args[0]
                b = args[1]
                operation(a, b, '+')
            
            case 'sub':
                checklen(2, "==")
                a = args[0]
                b = args[1]
                operation(a, b, '-')
                
            case 'mul':
                checklen(2, "==")
                a = args[0]
                b = args[1]
                operation(a, b, '*')
                
            case 'div':
                checklen(2, "==")
                a = args[0]
                b = args[1]
                operation(a, b, '/')
                
            case 'pow':
                checklen(2, "==")
                a = args[0]
                b = args[1]
                operation(a, b, '**')
                
            case 'addreg':
                checklen(2, "==")
                a_spl = args[0].split(':')
                b_spl = args[1].split(':')
                operationreg(a_spl[0], b_spl[0], a_spl[1], b_spl[1], '+')
            
            case 'subreg':
                checklen(2, "==")
                a_spl = args[0].split(':')
                b_spl = args[1].split(':')
                operationreg(a_spl[0], b_spl[0], a_spl[1], b_spl[1], '-')
                
            case 'divreg':
                checklen(2, "==")
                a_spl = args[0].split(':')
                b_spl = args[1].split(':')
                operationreg(a_spl[0], b_spl[0], a_spl[1], b_spl[1], '/')
                
            case 'mulreg':
                checklen(2, "==")
                a_spl = args[0].split(':')
                b_spl = args[1].split(':')
                operationreg(a_spl[0], b_spl[0], a_spl[1], b_spl[1], '*')
                
            case 'powreg':
                checklen(2, "==")
                a_spl = args[0].split(':')
                b_spl = args[1].split(':')
                operationreg(a_spl[0], b_spl[0], a_spl[1], b_spl[1], '**')
                
            case 'switch':
                checklen(1, "==")
                self._line(f'MEM.set_hand("{args[0]}")')
                
            case 'new':
                checklen(1, "==")
                self._line(f'MEM.new_hand("{args[0]}")')
                
            case 'reg':
                checklen(1, "==")
                self._line(f'MEM._create_reg({args[0]})')
                
            case 'workif':
                checklen(3, "==")
                operator = args[0]
                value = args[1]
                call = args[2]
                self._line(f'if MEM.getdata() {operator} {value}:{call}()')
                
            case 'out.':
                checklen(0, "==")
                self._line('print(MEM.getdata(), end = "")')
                
            case 'outch':
                checklen(0, "==")
                self._line('print(chr(MEM.getdata()), end = "")')
                
            case 'echo':
                self._line(f'print({" ".join(args)}, end = "")')
            
            case 'echoln':
                self._line(f'print({" ".join(args)})')
            
            case 'system':
                checklen(1, '>=')
                parameter = args[0]
                match parameter:
                    case 'save':
                        checklen(2, '>=')
                        with open(args[1], 'wb') as file:
                            pickle.dump(self, file)
                    case 'load':
                        if self.safe:
                            raise Bytex2Error('[safemode] Error', 'System [load] is not available in safemode.')
                        checklen(2, '>=')
                        with open(args[1], 'rb') as file:
                            content = pickle.load(file)
                        self.__init__(content.safe, preload=content)
                    case 'openfile':
                        if self.safe:
                            raise Bytex2Error('[safemode] Error', 'Open file is not available in safemode.')
                        checklen(4, '>=')
                        self._line(f'with open({args[1]}, {args[2]}) as {args[3]}:')
                        self.tabs += 1
                    case 'readfile':
                        checklen(2, '>=')
                        file = args[0]
                        out = args[1]
                        self._main(['system', 'openfile', file, '"r"', '__tmpfile'])
                        self._main(['const', out, "__tmpfile.read()"])
                        self._main(['end'])
                
            case '#': self._line(f'# {" ".join(args)}')
            
            case _:
                raise SyntaxError(f"Unknown syntax: {' '.join(line)}")