import sys
from psana import DataSource

exp = sys.argv[1]
run = eval(sys.argv[2])

ds = DataSource(exp=exp, run=run)
myrun = next(ds.runs())
step_value = myrun.Detector("step_value")
step_docstring = myrun.Detector("step_docstring")
for step in myrun.steps():
    print(step_value(step), step_docstring(step))
    for evt in step.events():
        pass
