#!/usr/bin/env python3
"""Synthesizes every sound effect and music track of Santadoku.

Pure standard library (no numpy, no third-party asset): bells, music-box
melodies of public-domain carols (Jingle Bells, We Wish You a Merry
Christmas, Silent Night) and a few sleigh-bell effects. Nothing to attribute.

Run from the project root:  python scripts/generate-audio.py
Writes 16-bit mono WAV files to assets/sounds and assets/music.
"""
import math
import os
import random
import struct
import wave

SR = 22050
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
random.seed(7)


def write_wav(path, samples):
    peak = max(1e-9, max(abs(s) for s in samples))
    scale = min(1.0, 0.89 / peak)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b''.join(struct.pack('<h', int(max(-1, min(1, s * scale)) * 32767)) for s in samples))


def mix_into(buf, start, tone):
    i0 = int(start * SR)
    need = i0 + len(tone)
    if need > len(buf):
        buf.extend([0.0] * (need - len(buf)))
    for i, v in enumerate(tone):
        buf[i0 + i] += v


def bell(freq, dur=1.2, vol=0.5):
    """Struck-bell tone: inharmonic partials with different decay speeds."""
    partials = [(1.0, 1.0, 3.0), (2.0, 0.6, 4.5), (2.76, 0.45, 6.0), (5.4, 0.25, 9.0), (8.93, 0.12, 14.0)]
    n = int(dur * SR)
    out = []
    for i in range(n):
        t = i / SR
        v = 0.0
        for ratio, amp, decay in partials:
            v += amp * math.exp(-decay * t) * math.sin(2 * math.pi * freq * ratio * t)
        attack = min(1.0, t / 0.004)
        out.append(v * vol * attack)
    return out


def musicbox(freq, dur=0.5, vol=0.5):
    """Soft music-box / celesta note."""
    n = int(dur * SR)
    out = []
    for i in range(n):
        t = i / SR
        env = math.exp(-5.0 * t) * min(1.0, t / 0.003)
        v = math.sin(2 * math.pi * freq * t) + 0.35 * math.sin(2 * math.pi * freq * 2 * t) * math.exp(-8 * t) + 0.12 * math.sin(2 * math.pi * freq * 3 * t) * math.exp(-12 * t)
        out.append(v * env * vol)
    return out


def pad(freq, dur, vol=0.18):
    """Warm low note for the accompaniment."""
    n = int(dur * SR)
    out = []
    for i in range(n):
        t = i / SR
        env = min(1.0, t / 0.02) * math.exp(-1.6 * t) * min(1.0, (dur - t) / 0.05)
        out.append((math.sin(2 * math.pi * freq * t) + 0.3 * math.sin(2 * math.pi * freq * 2 * t)) * env * vol)
    return out


def sleigh_bells(dur=0.6, vol=0.5, shakes=7):
    buf = [0.0] * int(dur * SR)
    for k in range(shakes):
        start = k * dur / shakes + random.uniform(0, 0.01)
        for f in (3300, 4100, 5200):
            tone = [math.sin(2 * math.pi * f * (i / SR) + random.random()) * math.exp(-38 * (i / SR)) * vol * 0.4 for i in range(int(0.12 * SR))]
            mix_into(buf, start, tone)
    return buf


NOTE = {'C': 0, 'D': 2, 'E': 4, 'F': 5, 'G': 7, 'A': 9, 'B': 11}


def freq_of(name):
    """'C4', "G#3" style names plus a trailing ' for the octave above (C5)."""
    letter = name[0]
    octave = 4
    semi = NOTE[letter]
    rest = name[1:]
    if rest.startswith('#'):
        semi += 1
        rest = rest[1:]
    if rest.isdigit():
        octave = int(rest)
    midi = 12 * (octave + 1) + semi
    return 440.0 * 2 ** ((midi - 69) / 12)


# ---------------------------------------------------------------- effects
def sfx():
    out = os.path.join(ROOT, 'assets', 'sounds')

    # correct: bright two-note bell
    b = []
    mix_into(b, 0.0, bell(freq_of('G5'), 0.7, 0.5))
    mix_into(b, 0.11, bell(freq_of('C6'), 0.9, 0.5))
    write_wav(os.path.join(out, 'correct.wav'), b)

    # wrong: muted low wooden thud + flat bell
    b = []
    mix_into(b, 0.0, [math.sin(2 * math.pi * (150 - 60 * (i / SR)) * (i / SR)) * math.exp(-14 * (i / SR)) * 0.9 for i in range(int(0.35 * SR))])
    mix_into(b, 0.0, bell(freq_of('E3'), 0.5, 0.25))
    write_wav(os.path.join(out, 'wrong.wav'), b)

    # win: ascending jingle arpeggio
    b = []
    for k, n in enumerate(['C5', 'E5', 'G5', 'C6', 'G5', 'C6', 'E6']):
        mix_into(b, k * 0.14, bell(freq_of(n), 1.1, 0.45))
    mix_into(b, 0.5, sleigh_bells(0.9, 0.5, 9))
    write_wav(os.path.join(out, 'win.wav'), b)

    # lose: slow descending bells
    b = []
    for k, n in enumerate(['G4', 'E4', 'C4', 'A3']):
        mix_into(b, k * 0.3, bell(freq_of(n), 1.2, 0.45))
    write_wav(os.path.join(out, 'lose.wav'), b)

    # mark: tiny soft tick
    write_wav(os.path.join(out, 'mark.wav'), [math.sin(2 * math.pi * 520 * (i / SR)) * math.exp(-60 * (i / SR)) * 0.7 for i in range(int(0.09 * SR))])

    # hint: gentle rising chime
    b = []
    mix_into(b, 0.0, bell(freq_of('E5'), 0.8, 0.4))
    mix_into(b, 0.15, bell(freq_of('A5'), 0.8, 0.4))
    mix_into(b, 0.30, bell(freq_of('E6'), 1.0, 0.4))
    write_wav(os.path.join(out, 'hint.wav'), b)

    # bonus: sparkle
    b = []
    for k, n in enumerate(['C6', 'E6', 'G6', 'C7', 'E6', 'G6', 'C7']):
        mix_into(b, k * 0.07, bell(freq_of(n), 0.6, 0.35))
    write_wav(os.path.join(out, 'bonus.wav'), b)

    # bat (reindeer): sleigh bells shake
    write_wav(os.path.join(out, 'bat.wav'), sleigh_bells(0.55, 0.7, 6))

    # swoosh: filtered noise sweep
    n = int(0.32 * SR)
    sw = []
    lp = 0.0
    for i in range(n):
        t = i / n
        a = 0.05 + 0.5 * math.sin(math.pi * t)
        lp += a * (random.uniform(-1, 1) - lp)
        sw.append(lp * math.sin(math.pi * t) * 1.4)
    write_wav(os.path.join(out, 'swoosh.wav'), sw)


# ------------------------------------------------------------------ music
# Each song: (tempo in seconds per unit, accompaniment pattern,
#             melody as list of (note, units) where note None = rest)
JINGLE = (
    0.24,
    [('C3', 'E3', 'G3'), ('C3', 'E3', 'G3'), ('F3', 'A3', 'C4'), ('C3', 'E3', 'G3'), ('D3', 'F3', 'A3'), ('G3', 'B3', 'D4'), ('C3', 'E3', 'G3'), ('G3', 'B3', 'D4')],
    [
        ('E4', 2), ('E4', 2), ('E4', 4), ('E4', 2), ('E4', 2), ('E4', 4),
        ('E4', 2), ('G4', 2), ('C4', 3), ('D4', 1), ('E4', 8),
        ('F4', 2), ('F4', 2), ('F4', 3), ('F4', 1), ('F4', 2), ('E4', 2), ('E4', 2), ('E4', 1), ('E4', 1),
        ('E4', 2), ('D4', 2), ('D4', 2), ('E4', 2), ('D4', 4), ('G4', 4),
        ('E4', 2), ('E4', 2), ('E4', 4), ('E4', 2), ('E4', 2), ('E4', 4),
        ('E4', 2), ('G4', 2), ('C4', 3), ('D4', 1), ('E4', 8),
        ('F4', 2), ('F4', 2), ('F4', 3), ('F4', 1), ('F4', 2), ('E4', 2), ('E4', 2), ('E4', 1), ('E4', 1),
        ('G4', 2), ('G4', 2), ('F4', 2), ('D4', 2), ('C4', 8),
    ],
    4,
)
WISH = (
    0.3,
    [('C3', 'E3', 'G3'), ('F3', 'A3', 'C4'), ('G3', 'B3', 'D4'), ('C3', 'E3', 'G3')],
    [
        ('D4', 2),
        ('G4', 2), ('G4', 1), ('A4', 1), ('G4', 1), ('F#4', 1), ('E4', 2), ('E4', 2), ('E4', 2),
        ('A4', 2), ('A4', 1), ('B4', 1), ('A4', 1), ('G4', 1), ('F#4', 2), ('D4', 2), ('D4', 2),
        ('B4', 2), ('B4', 1), ('C5', 1), ('B4', 1), ('A4', 1), ('G4', 2), ('E4', 2), ('D4', 1), ('D4', 1),
        ('E4', 2), ('A4', 2), ('F#4', 2), ('G4', 4), ('D4', 2),
        ('G4', 2), ('G4', 2), ('G4', 2), ('F#4', 4), ('F#4', 2),
        ('G4', 2), ('F#4', 2), ('E4', 2), ('D4', 4), ('A4', 2),
        ('B4', 2), ('A4', 2), ('D5', 2), ('G4', 6), ('', 0),
    ],
    3,
)
SILENT = (
    0.28,
    [('C3', 'G3', 'E4'), ('C3', 'G3', 'E4'), ('G3', 'B3', 'D4'), ('C3', 'G3', 'E4'), ('F3', 'A3', 'C4'), ('C3', 'G3', 'E4'), ('G3', 'B3', 'D4'), ('C3', 'G3', 'E4')],
    [
        ('G4', 3), ('A4', 1), ('G4', 2), ('E4', 6),
        ('G4', 3), ('A4', 1), ('G4', 2), ('E4', 6),
        ('D5', 4), ('D5', 2), ('B4', 6),
        ('C5', 4), ('C5', 2), ('G4', 6),
        ('A4', 4), ('A4', 2), ('C5', 3), ('B4', 1), ('A4', 2),
        ('G4', 3), ('A4', 1), ('G4', 2), ('E4', 6),
        ('A4', 4), ('A4', 2), ('C5', 3), ('B4', 1), ('A4', 2),
        ('G4', 3), ('A4', 1), ('G4', 2), ('E4', 6),
        ('D5', 4), ('D5', 2), ('F5', 3), ('D5', 1), ('B4', 2),
        ('C5', 6), ('E5', 6),
        ('C5', 2), ('G4', 2), ('E4', 2), ('G4', 3), ('F4', 1), ('D4', 2),
        ('C4', 12),
    ],
    1,
)


def render_song(song, filename, target_seconds=48):
    unit, chords, melody, _ = song
    total_units = sum(u for _, u in melody)
    one_pass = total_units * unit
    passes = max(1, round(target_seconds / one_pass))
    buf = []
    t = 0.0
    for _ in range(passes):
        for note, u in melody:
            if note:
                mix_into(buf, t, musicbox(freq_of(note), min(1.6, u * unit * 1.6), 0.55))
            t += u * unit
    # accompaniment: one chord per group of units, arpeggiated
    t = 0.0
    per_chord = total_units * unit / len(chords)
    for _ in range(passes):
        for chord in chords:
            for k, n in enumerate(chord * 2):
                step = per_chord / (len(chord) * 2)
                mix_into(buf, t + k * step, pad(freq_of(n), step * 1.8, 0.16))
            t += per_chord
    # a touch of sleigh bells on the beat for the lively tunes
    if song is JINGLE:
        bt = 0.0
        while bt < len(buf) / SR - 0.5:
            mix_into(buf, bt, sleigh_bells(0.12, 0.18, 1))
            bt += unit * 2
    # tiny fade at both ends so the loop crossfade is clean
    fade = int(0.05 * SR)
    for i in range(fade):
        buf[i] *= i / fade
        buf[-1 - i] *= i / fade
    write_wav(os.path.join(ROOT, 'assets', 'music', filename), buf)


def music():
    render_song(JINGLE, 'jingle-bells.wav')
    render_song(WISH, 'merry-christmas.wav')
    render_song(SILENT, 'silent-night.wav', 52)


if __name__ == '__main__':
    sfx()
    music()
    print('done')
