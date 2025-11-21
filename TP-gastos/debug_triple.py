import sys
p = 'modules/ui_manager.py'
with open(p, 'r', encoding='utf-8') as f:
    s = f.read()

indices = [i for i in range(len(s)-2) if s[i:i+3] == '"""']
print('Found', len(indices), 'triple-quote positions')
for idx in indices:
    print('pos', idx)

try:
    import ast
    ast.parse(s)
    print('AST OK')
except Exception as e:
    print('AST error:', e)
    raise
