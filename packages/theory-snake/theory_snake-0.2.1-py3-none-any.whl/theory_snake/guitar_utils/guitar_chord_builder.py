def make_guitar_chord(fret_board, chord_notes):
    guitar_chord = {}
    for string in fret_board:
        note_list = fret_board[string]
        for note in note_list:
            if note in chord_notes:
                guitar_chord[string] = note_list.index(note)
                break
    return guitar_chord
