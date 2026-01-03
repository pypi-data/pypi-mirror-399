from consts import MAJOR_CHORD, MINOR_CHORD
from scale_builder import build_scale
from note_utils import get_flat, get_sharp


def build_chord(root_note, chord_type):
    match chord_type:
        case 'major':
            chord_intervals = MAJOR_CHORD
            scale = build_scale(root_note, 'major')
        case 'minor':
            chord_intervals = MINOR_CHORD
            scale = build_scale(root_note, 'major')
        case _:
            return ValueError("Unsupported chord type")

    chord = []
    for interval in chord_intervals:
        if interval.isnumeric():
            chord.append(scale[int(interval) - 1])
        elif "b" in interval:
            base_note = scale[int(interval[0]) - 1]
            chord.append(get_flat(base_note))
        elif "#" in interval:
            base_note = scale[int(interval[0]) - 1]
            chord.append(get_sharp(base_note))
    return chord

if __name__ == "__main__":
    print(build_chord("G", "minor"))  # Expected output: ['C', 'E', 'G']
    print(build_chord("A", "minor"))  # Expected output: ['A', 'C', 'E']



