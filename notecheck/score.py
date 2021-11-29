import json
import math
import re

from django.db import models
from django.utils.translation import gettext_lazy as _

class Clefs(models.TextChoices):
    TREBLE = 'treble', _('Treble')
    BASS = 'bass', _('Bass')

class DiatonicPitch:
    pitch: int # 0 is sub-contra octave
    accs: int # 1 sharp, -1 flat

    def __init__(self, pitch: int, accs: int):
        self.pitch = pitch
        self.accs = accs

    def __repr__(self):
        return "({}, {})".format(self.pitch, self.accs)

    def __eq__(self, other):
        if other is None:
            return False
        return self.pitch == other.pitch and self.accs == other.accs

    def __add__(self, i: 'Interval') -> 'DiatonicPitch':
        dp = DiatonicPitch(self.pitch, self.accs)

        # Only use positive intervals in up direction. If interval is negative, inverse it.
        if (i.quantity < 0):
            if (i.quantity != -1):
                # First lower the pitch for i octaves + 1,
                dp.pitch += math.floor((i.quantity+1)/7)*7
            else:
                # The exception is the negative prime (which is illegal in musical terms, but we still need to handle it).
                dp.pitch -= 7
            # Then inverse the interval (NB: negative prime becomes octave). Below, the positive interval is now added to the lowered note.
            i = -i

        dp.pitch += i.quantity - 1
        deltaAccs = 0
        relP = self.pitch % 7
        relQnt = ((i.quantity - 1) % 7) + 1

        if relQnt==Interval.PRIME:
            deltaAccs = 0
        elif relQnt==Interval.SECOND:
            if relP == 2 or relP == 6:
                deltaAccs = 1
            else:
                deltaAccs = 0
        elif relQnt==Interval.THIRD:
            if relP == 0 or relP == 3 or relP == 4:
                deltaAccs = 0
            else:
                deltaAccs = 1
        elif relQnt==Interval.FOURTH:
            if relP == 3:
                deltaAccs = -1
            else:
                deltaAccs = 0
        elif relQnt==Interval.FIFTH:
            if relP == 6:
                deltaAccs = 1
            else:
                deltaAccs = 0
        elif relQnt==Interval.SIXTH:
            if relP == 2 or relP == 5 or relP == 6:
                deltaAccs = 1
            else:
                deltaAccs = 0
        elif relQnt==Interval.SEVENTH:
            if relP == 0 or relP == 3:
                deltaAccs = 0
            else:
                deltaAccs = 1

        if relQnt == 4 or relQnt == 5 or relQnt == 1:
            if i.quality < 0:
                dp.accs += deltaAccs + i.quality + 1
            elif i.quality > 0:
                dp.accs = deltaAccs + i.quality - 1
            else:
                dp.accs += deltaAccs
        else:
            if i.quality < 0:
                dp.accs += deltaAccs + i.quality
            elif i.quality > 0:
                dp.accs += deltaAccs + i.quality - 1

        return dp

    def toJSON(self):
        return json.dumps(self, default=lambda o: o.__dict__)

    def to_name(self, lang: str = 'en', relative = False) -> str:
        """converts pitch to note name. e.g. (0,0) -> C2, (9, 1) -> Eis1, (28, 0) -> c1

        If relative is set, it returns the lower-case note name only without the octave.
        """
        name = chr(ord('C')+(self.pitch%7))

        if name=='H':
            name = 'A'
        if name=='I':
            if lang in ['sl', 'de']:
                name = 'H'
            else:
                name = 'B'

        if self.pitch >= 21 or relative:
            name = name.lower()

        name += 'is'*self.accs
        name += 'es'*-self.accs
        if name.startswith('ee'): # es
            name = name[1:]
        if name.startswith('aes'): # as
            name = name.replace('es','as')
            name = name[1:]

        if not relative:
            if self.pitch < 7:
                name += '2'
            elif self.pitch < 14:
                name += '1'
            elif self.pitch >= 28:
                name += str((self.pitch-28) // 7 + 1)

        return name

    def __sub__(self, i: 'Interval') -> 'DiatonicPitch':
        return self.__add__(Interval(i.quality, -i.quantity))

    def from_name(name: str, lang: str = 'en') -> 'DiatonicPitch':
        """converts note name to pitch. Returns None, if pitch is invalid"""
        if not name:
            return None

        pitch = ord(name.upper()[0])-ord('C')
        if pitch < 0: # A, B
            pitch += 7
        elif pitch == 5: # H
            pitch = 6

        accs = 0
        if name.count('is'): # sharps
            accs = name.count('is')
        elif name.count('s'): # flats
            accs = -name.count('s')

        if lang in ['sl', 'de']:
            # In Slovenian (and German) language B also means Hes, and BB means Heses
            accs -= name.upper().count('B')

        pitch += 14
        if name[0].islower():
            pitch += 7
            if name[-1].isdigit():
                pitch += 7*int(name[-1])
        if name[0].isupper() and name[-1].isdigit():
            pitch -= 7*int(name[-1])

        return DiatonicPitch(pitch,accs)

    def to_lilypond(self) -> str:
        name = chr(ord('c')+(self.pitch%7))

        if name=='h':
            name = 'a'
        if name=='i':
            name = 'b'

        name += 'is'*self.accs
        name += 'es'*-self.accs
        if name.startswith('ee'): # es
            name = name[1:]
        if name.startswith('aes'): # as
            name = name.replace('es','as')
            name = name[1:]

        name += "'"*((self.pitch-21)//7)
        name += ","*-((self.pitch-21)//7)

        return name

class DiatonicPitchDecoder(json.JSONDecoder):
    def __init__(self, *args, **kwargs):
        json.JSONDecoder.__init__(self, object_hook=self.object_hook, *args, **kwargs)

    def object_hook(self, obj):
        if "pitch" in obj and "accs" in obj:
            return DiatonicPitch(pitch=obj["pitch"], accs=obj["accs"])
        return None

class DiatonicPitchEncoder(json.JSONEncoder):
        def default(self, obj):
            return obj.__dict__

class Interval:
    quality: int # 0 perfect, 1 major, -1 minor, 2 augmented, -2 diminished
    quantity: int # 1 prime, 2 second, 3 third etc. Can be negative, if direction is important

    PERFECT = 0
    MAJOR = 1
    MINOR = -1
    AUGMENTED = 2
    DIMINISHED = -2

    PRIME = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5
    SIXTH = 6
    SEVENTH = 7
    OCTAVE = 8

    def __init__(self, quality: int, quantity: int):
        self.quality = quality
        self.quantity = quantity

    def __repr__(self):
        return "({}, {})".format(self.quality, self.quantity)

    def __eq__(self, other):
        if other is None:
            return False
        return self.quantity == other.quantity and self.quality == other.quality

    def __neg__(self):
        """Inverse interval. e.g. Major second -> Minor seventh, Perfect fourth -> perfect fifth"""
        return Interval(-self.quality, 8-(abs(self.quantity)-1) )

    @staticmethod
    def from_diatonic_pitches( pitch_pair: (DiatonicPitch, DiatonicPitch), absolute: bool = True) -> 'Interval':
        """
        Construct an interval between given pitches.

        :param pitch1: The first note pitch
        :param pitch2: The second note pitch
        :param absolute: If True, the order of note pitches will be ignored; If False, the quantity of the resulting
        interval will be positive if the second pitch is higher than the first one, or negative if the second pitch is
        lower than the first one (default True)
        :return: Interval between the given pitches
        """
        pitch1 = pitch_pair[0]
        pitch2 = pitch_pair[1]
        interval = Interval(0, 0)
        pLow: DiatonicPitch
        pHigh: DiatonicPitch
        if pitch1.pitch < pitch2.pitch or (pitch1.pitch == pitch2.pitch and pitch1.accs <= pitch2.accs):
            pLow = pitch1
            pHigh = pitch2
        else:
            pLow = pitch2
            pHigh = pitch1

        interval.quantity = pHigh.pitch - pLow.pitch + 1
        relQnt = ((interval.quantity - 1) % 7) + 1
        relPLow = (pLow.pitch % 7)
        deltaQlt = 0
        # TODO: Rewrite using match statement introduced in Python 3.10
        if relQnt == Interval.PRIME:
            deltaQlt = 0
        elif relQnt == Interval.SECOND:
            if relPLow == 2 or relPLow == 6:
                deltaQlt = -1
            else:
                deltaQlt = 1
        elif relQnt == Interval.THIRD:
            if relPLow == 0 or relPLow == 3 or relPLow == 4:
                deltaQlt = 1
            else:
                deltaQlt = -1
        elif relQnt == Interval.FOURTH:
            if relPLow == 3:
                deltaQlt = 2
            else:
                deltaQlt = 0
        elif relQnt == Interval.FIFTH:
            if relPLow == 6:
                deltaQlt = -2
            else:
                deltaQlt = 0
        elif relQnt == Interval.SIXTH:
            if relPLow == 2 or relPLow == 5 or relPLow == 6:
                deltaQlt = -1
            else:
                deltaQlt = 1
        elif relQnt == Interval.SEVENTH:
            if relPLow == 0 or relPLow == 3:
                deltaQlt = 1
            else:
                deltaQlt = -1

        if relQnt == Interval.PRIME or relQnt == Interval.FOURTH or relQnt == Interval.FIFTH:
            # prime, fourth, fifth are perfect, diminished or augmented
            if (deltaQlt == 2 and pHigh.accs - pLow.accs == -1) or (deltaQlt == 0 and pHigh.accs - pLow.accs <= -1):
                interval.quality = deltaQlt + pHigh.accs - pLow.accs - 1
            elif deltaQlt == 2 and pHigh.accs - pLow.accs < -1:
                interval.quality = deltaQlt + pHigh.accs - pLow.accs - 2
            elif (deltaQlt == -2 and pHigh.accs - pLow.accs == 1) or (deltaQlt == 0 and pHigh.accs - pLow.accs >= 1):
                interval.quality = deltaQlt + pHigh.accs - pLow.accs + 1
            elif deltaQlt == -2 and pHigh.accs - pLow.accs > 1:
                interval.quality = deltaQlt + pHigh.accs - pLow.accs + 2
            else:
                interval.quality = deltaQlt + pHigh.accs - pLow.accs
        elif deltaQlt == Interval.MAJOR and pHigh.accs - pLow.accs < 0: # second, third, sixth and seventh cannot be perfect
            interval.quality = deltaQlt + pHigh.accs - pLow.accs - 1
        elif deltaQlt == Interval.MINOR and pHigh.accs - pLow.accs > 0:
            interval.quality = deltaQlt + pHigh.accs - pLow.accs + 1
        else:
            interval.quality = deltaQlt + pHigh.accs - pLow.accs

        if not absolute and (pitch1.pitch > pitch2.pitch or (pitch1.pitch == pitch2.pitch and pitch1.accs > pitch2.accs)):
            interval.quantity *= -1

        return interval

    def semitones(self) -> int:
        """
        Return the number of semitones in the interval.

        The return value is always positive.
        This mapping is surjective.

        :return: Number of semitones in the interval
        """

        semitones = 0
        absQuantity = ((abs(self.quantity) - 1) % 7) + 1

        # Use Major and Perfect intervals as a base.
        # TODO: Rewrite using match statement introduced in Python 3.10
        if absQuantity == Interval.PRIME:
            semitones = 0
        elif absQuantity == Interval.SECOND:
            semitones = 2
        elif absQuantity == Interval.THIRD:
            semitones = 4
        elif absQuantity == Interval.FOURTH:
            semitones = 5
        elif absQuantity == Interval.FIFTH:
            semitones = 7
        elif absQuantity == Interval.SIXTH:
            semitones = 9
        elif absQuantity == Interval.SEVENTH:
            semitones = 11

        # Handle Diminished, Minor, and Augmented.
        if self.quality <= Interval.DIMINISHED:
            if absQuantity == Interval.FOURTH or absQuantity == Interval.FIFTH:
                semitones += self.quality+1
            else:
                # Diminished intervals of Second, Third, Sixth, Seventh are reduced for 2 semitones.
                semitones += self.quality
        elif self.quality == Interval.MINOR:
            semitones -= 1
        elif self.quality >= Interval.AUGMENTED:
            semitones += self.quality-1

        # Octaves.
        semitones += 12 * ((abs(self.quantity) - 1) // 7)

        # Always return positive value.
        return abs(semitones)

    def to_name(self, lang: str = 'en') -> str:
        """converts interval to human readable. e.g. (2, 4) -> aug4, (0, 5) -> p5, (1, 2) -> maj2, (-1, 2) -> min2, (-1, -2) -> -min2"""
        quality_name: str
        if lang=='sl':
            if self.quality == Interval.PERFECT:
                quality_name = 'č'
            elif self.quality == Interval.MAJOR:
                quality_name = 'v'
            elif self.quality == Interval.MINOR:
                quality_name = 'm'
            elif self.quality >= Interval.AUGMENTED:
                quality_name = 'zv'*(self.quality-1)
            elif self.quality <= Interval.DIMINISHED:
                quality_name = 'zm'*(abs(self.quality)-1)
        else:
            if self.quality == Interval.PERFECT:
                quality_name = 'p'
            elif self.quality == Interval.MAJOR:
                quality_name = 'maj'
            elif self.quality == Interval.MINOR:
                quality_name = 'min'
            elif self.quality >= Interval.AUGMENTED:
                quality_name = 'aug'*(self.quality-1)
            elif self.quality <= Interval.DIMINISHED:
                quality_name = 'dim'*(abs(self.quality)-1)

        name = ''
        if self.quantity < 0:
            name += '-'
        name += quality_name
        name += str(abs(self.quantity))

        return name

    def from_name(name: str, lang: str) -> 'Interval':
        """converts human-readable interval to interval. Returns None, if interval is invalid"""
        if not name:
            return None

        negative = False
        if name[0] == '-':
            negative = True
            name = name[1:]

        quality: int
        if name.startswith('p') or name.startswith('č'):
            quality = 0
        elif name.startswith('maj') or name.startswith('v'):
            quality = 1
        elif name.startswith('min') or name.startswith('m'):
            quality = -1
        elif name.startswith('aug') or name.startswith('zv'):
            quality = 1 + name.count('aug') + name.count('zv')
        elif name.startswith('dim') or name.startswith('zm'):
            quality = -1 - name.count('dim') - name.count('zm')
        else:
            return None

        name_parts = re.split(r'(\d+)', name)
        if len(name_parts)<2:
            return None

        quantity = int(name_parts[1])

        if negative:
            quantity *= -1

        return Interval(quality, quantity)

class ScaleGender(models.TextChoices):
    MAJOR = 'major', _('Major')
    MINOR = 'minor', _('Minor')

class ScaleShape(models.TextChoices):
    NATURAL = 'natural', _('Natural')
    HARMONIC = 'harmonic', _('Harmonic')
    MELODIC = 'melodic', _('Melodic')

class Scale:
    """Diatonic major/minor scale"""

    gender: ScaleGender
    shape: ScaleShape
    accs: int # e.g. 0: C-major/a-minor, 1: G-major/e-minor, -1: F-major/d-minor etc.
    interval_matrix = { # matrix of interval quality of all major/minor scales
        (ScaleGender.MAJOR, ScaleShape.NATURAL): [Interval.MAJOR, Interval.MAJOR, Interval.MINOR, Interval.MAJOR,
                                                  Interval.MAJOR, Interval.MAJOR, Interval.MINOR],
        (ScaleGender.MAJOR, ScaleShape.HARMONIC): [Interval.MAJOR, Interval.MAJOR, Interval.MINOR, Interval.MAJOR,
                                                  Interval.MINOR, Interval.AUGMENTED, Interval.MINOR],
        (ScaleGender.MAJOR, ScaleShape.MELODIC): [Interval.MAJOR, Interval.MAJOR, Interval.MINOR, Interval.MAJOR,
                                                   Interval.MINOR, Interval.MAJOR, Interval.MAJOR],
        (ScaleGender.MINOR, ScaleShape.NATURAL): [Interval.MAJOR, Interval.MINOR, Interval.MAJOR, Interval.MAJOR,
                                                  Interval.MINOR, Interval.MAJOR, Interval.MAJOR],
        (ScaleGender.MINOR, ScaleShape.HARMONIC): [Interval.MAJOR, Interval.MINOR, Interval.MAJOR, Interval.MAJOR,
                                                  Interval.MINOR, Interval.AUGMENTED, Interval.MINOR],
        (ScaleGender.MINOR, ScaleShape.MELODIC): [Interval.MAJOR, Interval.MINOR, Interval.MAJOR, Interval.MAJOR,
                                                   Interval.MAJOR, Interval.MAJOR, Interval.MINOR],
    }

    def __init__(self, gender: ScaleGender, shape: ScaleShape, accs: int):
        self.gender = gender
        self.shape = shape
        self.accs = accs

    def __repr__(self):
        return "({}, {}, {})".format(self.gender, self.shape, self.accs)

    def get_pitches(self) -> []:
        init_pitch = DiatonicPitch(0,0)
        for i in range(0, self.accs):
            init_pitch += Interval(Interval.PERFECT, Interval.FIFTH)
        for i in range(0, self.accs, -1):
            init_pitch -= Interval(Interval.PERFECT, Interval.FIFTH)

        if self.gender==ScaleGender.MINOR:
            init_pitch -= Interval(Interval.MINOR, Interval.THIRD)

        init_pitch.pitch %= 7
        if init_pitch.pitch < 0:
            init_pitch += 7

        pitches = [init_pitch]
        for i in range(0,7):
            pitches.append(pitches[-1] + Interval(Scale.interval_matrix[(self.gender, self.shape)][i], Interval.SECOND))

        return pitches