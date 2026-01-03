import os
from setuptools import setup, Extension, find_packages
from pathlib import Path
import sys

print('==== Creating libs dir ====')
LIBS = Path.home() / 'BTXLIBS'
LIBS.mkdir(exist_ok=True)

setuplib = '''metadata by pt, description = lib for install bytex2 modules

#pymodule pathlib os




stdfunc setup \'\'\'
# Setup
Function for setup bytex2 modules.

Args:
- name : str - name of module
- code : str - code of module
- pymodule : bool - install module like python code if true
    \'\'\' name: str, code: str, pymodule: bool = False
    # creating path in libs
    var _path '/'.join(str(name).split('.')[:-1])

    # creating full path
    var path LIBS/_path

    # creating path for file
    var name LIBS/(str(name).replace('.', '/')+".btx")
    # check for path exist
    var :bool cond not os.path.exists(path)

    # if not exist - create dir
    start mkdir; do os.mkdir path; end
    if cond 
        goto mkdir
    end

    # if pymodule - replace tabs and add [python] blocks
    var :bool pymodule pymodule
    if pymodule
        var code 'python \\n' + code.replace('	', '\\\\tab|').replace('    ' , '\\\\tab| ' ) + '\\npython'
    end

    # write lib to file
    system openfile name 'w' file
        src file.write(code)
    end
endf'''




descriptions = '''metadata by pt, description = lib for get documentation of functions

stdfunc getdocs \'\'\'
# Getdocs
Get documentation of standart function

Args:
- need_name: str - name of function to get docs

Return: 
- Str - documentaton of function
    \'\'\' need_name: str
    var :str _ver '2.0'
    var parser Bytex(ver).stdbtx2.parse_btx2
    var tokens parser(RAW)
    var :str docs 'Function has no docs or function is not found'
    src for token in tokens:; @addtabs
        var :bool cond token[0] in ('stdfunc', 'sfunc', 'func')
        if cond
            var :bool cond len(token) >= 3
            if cond
                var :bool cond token[2].startswith("\'\'\'")
                end
            if cond; 
                var name token[1]
                var docs token[2][3:-3]
                end
            else; 
                var name token[1]
                var docs 'Function has no docs'
                end
            var :bool cond name == need_name
            if cond
                return docs
            end
        end
    return docs

#SLANGMOD __docs__
    python 
        def handler(ctx, line):
        \\tab|  args = line[1:]
        \\tab|  ctx.main_edit(
            [
            f'for func in {args}:',
            """    print(f"====== {func} documentation =====\\\\n", getdocs(func), f"\\\\n====== {func} documentation =====")"""
            ])
    python
    src CTX.plugin('command')('getdocs', handler)
#ELANGMOD __docs__
#LANGMOD __docs__'''

libs = {'setup': setuplib, 'docs': descriptions}

for lib in libs.keys():
    with open(LIBS/f'{lib}.btx', 'w') as file:
        file.write(libs[lib])
print('==== Creating libs dir Success ====')


__bx_version__ = '2.0'
__framework_verion__ = '1.2'

match __bx_version__:
    case '1.0':
        path = 'src/C-CORES/bx1/'
        bytex = Extension(
            name='untvgdev.core.bx1.UnitBytexCore',
            sources=[path + 'UnitBytexCore.c'],
        )
        config = Extension(
            name='untvgdev.core.bx1.UnitBytexDevConfig', 
            sources=[path + 'UnitBytexDevConfig.c'],
        )
        c_mod = [bytex, config]
    
    case '2.0':
        path = 'src/UnitVerge/Bytex/bx2/'
        basemem = Extension(
            name='BYTEX2_back',
            sources=[path + 'machine/BYTEX2_back.c'],
        )
        c_mod = [basemem]


setup(
    name='unitverge',
    author='Pt',
    author_email='kvantorium73.int@gmail.com',
    version=__framework_verion__,
    ext_modules=c_mod,
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.10',
    install_requires=[],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Software Development :: Compilers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
    ],
    description='A metaprogramming framework for code generation and DSL creation',
    url='https://github.com/pt-main/unitverge',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'btx2=btx_tool.btx2:main',
            'bytex=btx_tool.bytex:main'
        ]
    },
    options={
        'bdist_wheel': {
            'python_tag': 'cp314',
            'plat_name': 'manylinux2014_x86_64',
        }
    }
)
