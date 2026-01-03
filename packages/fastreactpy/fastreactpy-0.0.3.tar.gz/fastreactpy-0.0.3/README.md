
 # fastreactpy ⚡

Fast, lightweight reactive state library for Python.

`fastreactpy` brings **React-like reactive state** to Python with **zero dependencies**, minimal overhead, and a clean API.

---

## 🚀 Installation

```bash
pip install fastreactpy
```

---

## 🧠 Core Concepts

### Signal

A **signal** is a reactive container for state.

```python
from fastreactpy import signal

count = signal(0)
```

* `count()` → get value
* `count(10)` → set value and notify subscribers

---

### Effect

An **effect** automatically re-runs when the signals it uses change.

```python
from fastreactpy import effect

@effect
def logger():
    print("Count:", count())
```

---

## ✨ Basic Example

```python
from fastreactpy import signal, effect

count = signal(0)

@effect
def print_count():
    print("Count changed:", count())

count(5)
count(10)
```

Output:

```
Count changed: 0
Count changed: 5
Count changed: 10
```

---

## 📁 Sharing State Between Multiple Files

This is the most common real-world usage.

---

### store.py (Shared State)

```python
from fastreactpy import signal

count = signal(0)
user = signal("Guest")
```

---

### logger.py (Reactions / Effects)

```python
from fastreactpy import effect
from store import count, user

@effect
def log_count():
    print("[logger] Count:", count())

@effect
def log_user():
    print("[logger] User:", user())
```

---

### main.py (Mutating State)

```python
import logger  # IMPORTANT: registers effects
from store import count, user

count(1)
user("Malahim")

count(5)
user("Alice")
```

Output:

```
[logger] Count: 0
[logger] User: Guest
[logger] Count: 1
[logger] User: Malahim
[logger] Count: 5
[logger] User: Alice
```

---

## 🧩 Multiple Effects on One Signal

```python
from fastreactpy import effect
from store import count

@effect
def double():
    print("Double:", count() * 2)

@effect
def square():
    print("Square:", count() ** 2)
```

---

## ⚡ Why fastreactpy?

* Zero dependencies
* Extremely lightweight
* React-style mental model
* Automatic dependency tracking
* Works across files
* Ideal for CLIs, tools, and services

---

## ⚠️ Best Practices

* Keep shared signals in a single module (e.g. `store.py`)
* Always import modules that define effects
* Avoid heavy logic inside effects
* Use effects for side-effects only


---

## 🌐 Contact

Website: [https://malahim.dev](https://malahim.dev)

Phone: +92 328 4671797

---

## 📄 License

MIT License © 2025 Malahim Haseeb

