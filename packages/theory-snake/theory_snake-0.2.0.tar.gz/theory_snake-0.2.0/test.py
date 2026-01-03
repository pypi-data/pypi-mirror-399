import theory_snake as ts

from theory_snake.guitar_utils.tuning_utils import select_tuning
from theory_snake.guitar_utils.fretboard_builder import build_fretboard
from theory_snake.guitar_utils.guitar_chord_builder import make_guitar_chord


chord = ts.build_chord("B","major")
print(chord)
fretboard = build_fretboard(select_tuning())

guitar_chord = make_guitar_chord(fretboard, chord)

print(guitar_chord)

