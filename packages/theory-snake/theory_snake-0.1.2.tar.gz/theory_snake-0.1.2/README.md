
# theory_snake 🐍🎶

A lightweight Python library for music theory. Easily generate scales, build chords, and handle note transformations with a simple, intuitive API.

---

## 🚀 Installation

Install **theory_snake** via pip:

```bash
pip install theory_snake
```


## 🎹 Features & Usage

### 1. Scales

Generate full scales by providing a root note and the scale type.

**Python**

```
from theory_snake.scale_builder import build_scale

# Generate a C Major Scale
c_major = build_scale("C", "major")
print(c_major)
# Output: ['C', 'D', 'E', 'F', 'G', 'A', 'B']

# Generate an A Minor Scale
a_minor = build_scale("A", "minor")
print(a_minor)
```

### 2. Chords

Construct triads quickly using the chord builder.

**Python**

```
from theory_snake.chord_builder import build_chord

# Build a G Major triad
g_major = build_chord("G", "major")
print(g_major)
# Output: ['G', 'B', 'D']

# Build a D Minor triad
d_minor = build_chord("D", "minor")
print(d_minor)
```

### 3. Note Utilities

Handle accidentals and note naming conventions efficiently.

**Python**

```
from theory_snake.note_utils import get_sharp, get_flat

print(get_sharp("C")) # "C#"
print(get_flat("B"))  # "Bb"
```

### 4. Constants

Access raw music theory data like intervals and formulas.
*Note: These must be imported explicitly from the `consts` module.*

**Python**

```
from theory_snake import consts

# Access raw semitone formulas
print(consts.CHORD_FORMULAS['major']) # [0, 4, 7]
```

---

## 🏗 Project Structure

The library is organized for modularity and easy extension:

**Plaintext**

```
theory_snake/
├── src/
│   └── theory_snake/
│       ├── __init__.py      # Shortcuts for builders & utils
│       ├── note_utils.py    # Accidental handling
│       ├── chord_builder.py # Triad logic
│       ├── scale_builder.py # Scale logic
│       └── consts.py        # Intervals and formulas
```
