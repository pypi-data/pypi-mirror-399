# fastreactpy

Fast, lightweight reactive state library for Python.

## Example

```python
from fastreactpy import signal, effect

count = signal(0)

@effect
def print_count():
    print("Count changed:", count())

count(5)
count(10)

```
