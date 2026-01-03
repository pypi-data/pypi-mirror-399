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

### 5. Guitar Utils (module)

The `guitar_utils` module provides helpers for working with guitar-specific abstractions like tunings, strings, fretboards and finding chord shapes on a fretboard.

Quick examples

```python
from theory_snake.guitar_utils.tuning_utils import select_tuning
from theory_snake.guitar_utils.fretboard_builder import build_fretboard
from theory_snake.guitar_utils.string_builder import build_guitar_string
from theory_snake.guitar_utils.guitar_chord_builder import make_guitar_chord
from theory_snake.chord_builder import build_chord

# Get a standard 6-string tuning (or pass a custom tuning like "E A D G B E" or "E,A,D,G,B,E")
tuning = select_tuning("Standard")

# Build a full fretboard (each open string -> list of fretted notes)
fretboard = build_fretboard(tuning)

# Build a single guitar string from its open note
e_string = build_guitar_string("E")

# Build chord notes (uses the chord builder in the main package)
g_major_notes = build_chord("G", "major")

# Find a simple fingering on the fretboard for the chord notes
guitar_chord_shape = make_guitar_chord(fretboard, g_major_notes)
print(guitar_chord_shape)
# Example output: {'E': 3, 'A': 2, 'D': 0, 'G': 0, 'B': 0}
```

Notes

- `select_tuning(tuning)` accepts a key from the library's common tunings (e.g. `"Standard"`) or a custom comma/space-separated list of open-string notes.
- `build_guitar_string(open_note)` returns a list of notes across frets for that string.
- `build_fretboard(tuning)` returns a mapping of each open string -> its fretted-note list.
- `make_guitar_chord(fret_board, chord_notes)` returns a mapping from string (open-note key used in the fretboard) to the fret index for the first matching chord tone found on that string.
