import inspect
import importlib
import sys
import os

# Ensure project root is on sys.path so we can import local packages
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

mod = importlib.import_module('ToolAgents.Storytelling_tool')
print('Module:', mod)
fn = getattr(mod, 'storytelling_tool_node')
print('Function object (tool wrapper):', fn)
print('Annotations:', fn.__annotations__)
print('Doc:', (fn.__doc__ or '')[:120])
print('args_schema:', getattr(fn, 'args_schema', None))
args_schema = getattr(fn, 'args_schema', None)
if args_schema is not None:
    try:
        print('args_schema fields:')
        for k, v in args_schema.model_fields.items():
            print(' -', k, 'required=' , getattr(v, 'required', None), 'annotation=', getattr(v, 'annotation', None))
    except Exception as e:
        print('Could not introspect args_schema fields:', e)
print('Attrs (first 50):', [a for a in dir(fn) if not a.startswith('_')][:50])

# If the decorator created a tool object, it might be accessible as fn.__wrapped__ or fn.tool
wrapped = getattr(fn, '__wrapped__', None)
print('__wrapped__:', wrapped)
if wrapped:
    print('Wrapped signature:', inspect.signature(wrapped))

# Print module-level imports that may matter
print('\nModule imports check:')
for name in ['ToolMessage','ToolRuntime','Command']:
    print(name, getattr(mod, name, 'NOT FOUND'))

print('\nDone')

print('\n--- Humor tool inspection ---')
mod_h = importlib.import_module('ToolAgents.Humor_tool')
fn_h = getattr(mod_h, 'humor_tool_node')
print('Humor object:', fn_h)
print('Humor args_schema:', getattr(fn_h, 'args_schema', None))
sch = getattr(fn_h, 'args_schema', None)
if sch is not None:
    try:
        print('Humor args_schema fields:')
        for k, v in sch.model_fields.items():
            print(' -', k, 'required=' , getattr(v, 'required', None), 'annotation=', getattr(v, 'annotation', None))
    except Exception as e:
        print('Could not introspect humor args_schema fields:', e)
