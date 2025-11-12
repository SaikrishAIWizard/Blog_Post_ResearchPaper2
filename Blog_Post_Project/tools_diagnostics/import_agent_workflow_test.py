import sys, os
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

print('Importing Agent_workflow...')
try:
    import Agent_workflow as aw
    print('Imported Agent_workflow module:', aw)
    print('Graph object:', getattr(aw, 'graph', None))
    print('Workflow compiled successfully.')
except Exception as e:
    print('Error importing Agent_workflow:', type(e), e)
    raise
