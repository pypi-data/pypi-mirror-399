from .basics import core
# metaclass
class Generator:
    '''
    # Generator
    Metaclass for code generation.
    '''
    def __init__(self):
        self._code = [] # main code
        self._pre = [] # pre-code
        self._end = [] # post-code
        self._log = [] # raw code
        self.tabs = 0 # current tabs counter
    
    def _line(self, code: str):
        '''
        Add code (to _code)
        '''
        # add line to code with tabs
        self._code.append('    ' * self.tabs + code) 
    
    @property
    def code(self):
        '''
        Returning all builded code in format:

        - core code
        - raw code   (_log)
        - pre code   (_pre)
        - main code  (_code)
        - pos code   (_end)
        '''
        code = f'''
# =============================
#         core code
# =============================
{'\n'.join(core)}



# =============================
#          raw code
# =============================
RAW = """
{'\n'.join(self._log)}
"""


# =============================
#      compiled code: pre
# =============================
{'\n'.join(self._pre)}


# =============================
#     compiled code: main
# =============================
{'\n'.join(self._code)}



# =============================
#     compiled code: post
# =============================
{'\n'.join(self._end)}
        '''
        return code.split('\n')