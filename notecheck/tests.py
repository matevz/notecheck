from django.test import TestCase

from .models import DiatonicPitch, Interval, Scale, ScaleGender, ScaleShape

class DiatonicPitchTests(TestCase):
    def test_add(self):
        self.assertEquals(DiatonicPitch(0,0)+Interval(Interval.PERFECT, Interval.PRIME), DiatonicPitch(0,0))
        self.assertEquals(DiatonicPitch(0,0)+Interval(Interval.MAJOR, Interval.SECOND), DiatonicPitch(1,0))
        self.assertEquals(DiatonicPitch(0,0)+Interval(Interval.MAJOR, Interval.THIRD), DiatonicPitch(2,0))
        self.assertEquals(DiatonicPitch(0,0)+Interval(Interval.PERFECT, Interval.FOURTH), DiatonicPitch(3,0))
        self.assertEquals(DiatonicPitch(0,0)+Interval(Interval.PERFECT, Interval.FIFTH), DiatonicPitch(4,0))
        self.assertEquals(DiatonicPitch(0,0)+Interval(Interval.MAJOR, Interval.SIXTH), DiatonicPitch(5,0))
        self.assertEquals(DiatonicPitch(0,0)+Interval(Interval.MAJOR, Interval.SEVENTH), DiatonicPitch(6,0))
        self.assertEquals(DiatonicPitch(0,0)+Interval(Interval.PERFECT, Interval.OCTAVE), DiatonicPitch(7,0))

        self.assertEquals(DiatonicPitch(2,0)+Interval(Interval.MAJOR, Interval.SECOND), DiatonicPitch(3,1))
        self.assertEquals(DiatonicPitch(6,0)+Interval(Interval.MAJOR, Interval.SECOND), DiatonicPitch(7,1))

    def test_sub(self):
#        self.assertEquals(DiatonicPitch(7,0)-Interval(Interval.PERFECT, Interval.PRIME), DiatonicPitch(7,0))
        self.assertEquals(DiatonicPitch(7,0)-Interval(Interval.MINOR, Interval.SECOND), DiatonicPitch(6,0))
        self.assertEquals(DiatonicPitch(7,0)-Interval(Interval.MINOR, Interval.THIRD), DiatonicPitch(5,0))
        self.assertEquals(DiatonicPitch(7,0)-Interval(Interval.PERFECT, Interval.FOURTH), DiatonicPitch(4,0))
        self.assertEquals(DiatonicPitch(7,0)-Interval(Interval.PERFECT, Interval.FIFTH), DiatonicPitch(3,0))
        self.assertEquals(DiatonicPitch(7,0)-Interval(Interval.MINOR, Interval.SIXTH), DiatonicPitch(2,0))
        self.assertEquals(DiatonicPitch(7,0)-Interval(Interval.MINOR, Interval.SEVENTH), DiatonicPitch(1,0))
        self.assertEquals(DiatonicPitch(7,0)-Interval(Interval.PERFECT, Interval.OCTAVE), DiatonicPitch(0,0))

        self.assertEquals(DiatonicPitch(3,0)-Interval(Interval.MAJOR, Interval.SECOND), DiatonicPitch(2,-1))
        self.assertEquals(DiatonicPitch(7,0)-Interval(Interval.MAJOR, Interval.SECOND), DiatonicPitch(6,-1))

    def test_pitch_to_name(self):
        self.assertEquals(DiatonicPitch(0,0).to_name(), 'C2')
        self.assertEquals(DiatonicPitch(1,0).to_name(), 'D2')
        self.assertEquals(DiatonicPitch(2,0).to_name(), 'E2')
        self.assertEquals(DiatonicPitch(3,0).to_name(), 'F2')
        self.assertEquals(DiatonicPitch(4,0).to_name(), 'G2')
        self.assertEquals(DiatonicPitch(5,0).to_name(), 'A2')
        self.assertEquals(DiatonicPitch(6,0).to_name(), 'B2')
        self.assertEquals(DiatonicPitch(9,1).to_name(), 'Eis1')
        self.assertEquals(DiatonicPitch(26,0).to_name(), 'a')
        self.assertEquals(DiatonicPitch(27,0).to_name(), 'b')
        self.assertEquals(DiatonicPitch(28,-1).to_name(), 'ces1')
        self.assertEquals(DiatonicPitch(36,0).to_name(), 'd2')

    def test_pitch_to_name_locale(self):
        self.assertEquals(DiatonicPitch(26,0).to_name(lang='sl'), 'a')
        self.assertEquals(DiatonicPitch(26,0).to_name(lang='de'), 'a')
        self.assertEquals(DiatonicPitch(27,0).to_name(lang='sl'), 'h')
        self.assertEquals(DiatonicPitch(27,0).to_name(lang='de'), 'h')
        self.assertEquals(DiatonicPitch(27,-1).to_name(lang='sl'), 'hes')
        self.assertEquals(DiatonicPitch(27,-1).to_name(lang='de'), 'hes')
        self.assertEquals(DiatonicPitch(34,-1).to_name(lang='sl'), 'hes1')
        self.assertEquals(DiatonicPitch(34,-1).to_name(lang='de'), 'hes1')

    def test_name_to_pitch(self):
        self.assertEquals(DiatonicPitch.from_name('C2'), DiatonicPitch(0,0))
        self.assertEquals(DiatonicPitch.from_name('C1'), DiatonicPitch(7,0))
        self.assertEquals(DiatonicPitch.from_name('C'), DiatonicPitch(14,0))
        self.assertEquals(DiatonicPitch.from_name('c'), DiatonicPitch(21,0))
        self.assertEquals(DiatonicPitch.from_name('c1'), DiatonicPitch(28,0))
        self.assertEquals(DiatonicPitch.from_name('c2'), DiatonicPitch(35,0))
        self.assertEquals(DiatonicPitch.from_name('c3'), DiatonicPitch(42,0))
        self.assertEquals(DiatonicPitch.from_name('c4'), DiatonicPitch(49,0))
        self.assertEquals(DiatonicPitch.from_name('c5'), DiatonicPitch(56,0))
        self.assertEquals(DiatonicPitch.from_name('Eis1'), DiatonicPitch(9,1))
        self.assertEquals(DiatonicPitch.from_name('EIS1'), DiatonicPitch(9,1))
        self.assertEquals(DiatonicPitch.from_name('Eisis1'), DiatonicPitch(9,2))
        self.assertEquals(DiatonicPitch.from_name('a'), DiatonicPitch(26,0))
        self.assertEquals(DiatonicPitch.from_name('b'), DiatonicPitch(27,0))
        self.assertEquals(DiatonicPitch.from_name('ces1'), DiatonicPitch(28,-1))
        self.assertEquals(DiatonicPitch.from_name('cES1'), DiatonicPitch(28,-1))
        self.assertEquals(DiatonicPitch.from_name('ceses1'), DiatonicPitch(28,-2))
        self.assertEquals(DiatonicPitch.from_name('d2'), DiatonicPitch(36,0))

    def test_name_to_pitch_locale(self):
        self.assertEquals(DiatonicPitch.from_name('a', lang='sl'), DiatonicPitch(26,0))
        self.assertEquals(DiatonicPitch.from_name('a', lang='de'), DiatonicPitch(26,0))
        self.assertEquals(DiatonicPitch.from_name('b', lang='sl'), DiatonicPitch(27,-1))
        self.assertEquals(DiatonicPitch.from_name('b', lang='de'), DiatonicPitch(27,-1))
        self.assertEquals(DiatonicPitch.from_name('bb', lang='sl'), DiatonicPitch(27,-2))
        self.assertEquals(DiatonicPitch.from_name('bb', lang='de'), DiatonicPitch(27,-2))
        self.assertEquals(DiatonicPitch.from_name('hes', lang='sl'), DiatonicPitch(27,-1))
        self.assertEquals(DiatonicPitch.from_name('hes', lang='de'), DiatonicPitch(27,-1))
        self.assertEquals(DiatonicPitch.from_name('heses', lang='sl'), DiatonicPitch(27,-2))
        self.assertEquals(DiatonicPitch.from_name('heses', lang='de'), DiatonicPitch(27,-2))

        self.assertEquals(DiatonicPitch.from_name('a1', lang='sl'), DiatonicPitch(33,0))
        self.assertEquals(DiatonicPitch.from_name('a1', lang='de'), DiatonicPitch(33,0))
        self.assertEquals(DiatonicPitch.from_name('b1', lang='sl'), DiatonicPitch(34,-1))
        self.assertEquals(DiatonicPitch.from_name('b1', lang='de'), DiatonicPitch(34,-1))
        self.assertEquals(DiatonicPitch.from_name('bb1', lang='sl'), DiatonicPitch(34,-2))
        self.assertEquals(DiatonicPitch.from_name('bb1', lang='de'), DiatonicPitch(34,-2))
        self.assertEquals(DiatonicPitch.from_name('hes1', lang='sl'), DiatonicPitch(34,-1))
        self.assertEquals(DiatonicPitch.from_name('hes1', lang='de'), DiatonicPitch(34,-1))
        self.assertEquals(DiatonicPitch.from_name('heses1', lang='sl'), DiatonicPitch(34,-2))
        self.assertEquals(DiatonicPitch.from_name('heses1', lang='de'), DiatonicPitch(34,-2))

    def test_pitch_to_lilypond(self):
        self.assertEquals(DiatonicPitch(21,0).to_lilypond(), "c")
        self.assertEquals(DiatonicPitch(0,0).to_lilypond(), 'c,,,')
        self.assertEquals(DiatonicPitch(1,0).to_lilypond(), 'd,,,')
        self.assertEquals(DiatonicPitch(2,0).to_lilypond(), 'e,,,')
        self.assertEquals(DiatonicPitch(3,0).to_lilypond(), 'f,,,')
        self.assertEquals(DiatonicPitch(4,0).to_lilypond(), 'g,,,')
        self.assertEquals(DiatonicPitch(5,0).to_lilypond(), 'a,,,')
        self.assertEquals(DiatonicPitch(6,0).to_lilypond(), 'b,,,')
        self.assertEquals(DiatonicPitch(9,1).to_lilypond(), "eis,,")
        self.assertEquals(DiatonicPitch(27,0).to_lilypond(), "b")
        self.assertEquals(DiatonicPitch(28,-1).to_lilypond(), "ces'")
        self.assertEquals(DiatonicPitch(36,0).to_lilypond(), "d''")

class IntervalTests(TestCase):
    def test_from_diatonic_pitches_absolute_no_accs(self):
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(0,0), DiatonicPitch(1,0)), True), Interval(Interval.MAJOR, Interval.SECOND))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(0,0), DiatonicPitch(2,0)), True), Interval(Interval.MAJOR, Interval.THIRD))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(0,0), DiatonicPitch(3,0)), True), Interval(Interval.PERFECT, Interval.FOURTH))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(0,0), DiatonicPitch(4,0)), True), Interval(Interval.PERFECT, Interval.FIFTH))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(0,0), DiatonicPitch(5,0)), True), Interval(Interval.MAJOR, Interval.SIXTH))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(0,0), DiatonicPitch(6,0)), True), Interval(Interval.MAJOR, Interval.SEVENTH))

        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(1,0), DiatonicPitch(0,0)), True), Interval(Interval.MAJOR, Interval.SECOND))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(2,0), DiatonicPitch(0,0)), True), Interval(Interval.MAJOR, Interval.THIRD))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(3,0), DiatonicPitch(0,0)), True), Interval(Interval.PERFECT, Interval.FOURTH))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(4,0), DiatonicPitch(0,0)), True), Interval(Interval.PERFECT, Interval.FIFTH))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(5,0), DiatonicPitch(0,0)), True), Interval(Interval.MAJOR, Interval.SIXTH))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(6,0), DiatonicPitch(0,0)), True), Interval(Interval.MAJOR, Interval.SEVENTH))

    def test_from_diatonic_pitches_no_accs(self):
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(0,0), DiatonicPitch(1,0)), False), Interval(Interval.MAJOR, Interval.SECOND))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(0,0), DiatonicPitch(2,0)), False), Interval(Interval.MAJOR, Interval.THIRD))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(0,0), DiatonicPitch(3,0)), False), Interval(Interval.PERFECT, Interval.FOURTH))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(0,0), DiatonicPitch(4,0)), False), Interval(Interval.PERFECT, Interval.FIFTH))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(0,0), DiatonicPitch(5,0)), False), Interval(Interval.MAJOR, Interval.SIXTH))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(0,0), DiatonicPitch(6,0)), False), Interval(Interval.MAJOR, Interval.SEVENTH))

        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(1,0), DiatonicPitch(0,0)), False), Interval(Interval.MAJOR, -Interval.SECOND))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(2,0), DiatonicPitch(0,0)), False), Interval(Interval.MAJOR, -Interval.THIRD))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(3,0), DiatonicPitch(0,0)), False), Interval(Interval.PERFECT, -Interval.FOURTH))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(4,0), DiatonicPitch(0,0)), False), Interval(Interval.PERFECT, -Interval.FIFTH))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(5,0), DiatonicPitch(0,0)), False), Interval(Interval.MAJOR, -Interval.SIXTH))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(6,0), DiatonicPitch(0,0)), False), Interval(Interval.MAJOR, -Interval.SEVENTH))

    def test_from_diatonic_pitches(self):
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(7,0), DiatonicPitch(6,0)), False), Interval(Interval.MINOR, -Interval.SECOND))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(7,0), DiatonicPitch(6,-1)), False), Interval(Interval.MAJOR, -Interval.SECOND))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(7,1), DiatonicPitch(6,-1)), False), Interval(Interval.AUGMENTED, -Interval.SECOND))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(7,-1), DiatonicPitch(6,0)), False), Interval(Interval.DIMINISHED, -Interval.SECOND))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(7,1), DiatonicPitch(10,1)), False), Interval(Interval.PERFECT, Interval.FOURTH))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(9,1), DiatonicPitch(7,1)), False), Interval(Interval.MAJOR, -Interval.THIRD))

    def test_from_diatonic_pitches_over_octave(self):
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(7,0), DiatonicPitch(14,0)), True), Interval(Interval.PERFECT, Interval.OCTAVE))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(7,0), DiatonicPitch(15,0)), True), Interval(Interval.MAJOR, 9))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(7,0), DiatonicPitch(16,0)), True), Interval(Interval.MAJOR, 10))

    def test_from_diatonic_pitches_double_augmented(self):
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(5, 1), DiatonicPitch(5,-1)), True), Interval(Interval.AUGMENTED+1, Interval.PRIME))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(5, -1), DiatonicPitch(5,1)), True), Interval(Interval.AUGMENTED+1, Interval.PRIME))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(5, 1), DiatonicPitch(5,-1)), False), Interval(Interval.AUGMENTED+1, -Interval.PRIME))
        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(5, -1), DiatonicPitch(5,1)), False), Interval(Interval.AUGMENTED+1, Interval.PRIME))

    def test_semitones(self):
        self.assertEquals(Interval(Interval.PERFECT, Interval.PRIME).semitones(), 0)
        self.assertEquals(Interval(Interval.MAJOR, Interval.SECOND).semitones(), 2)
        self.assertEquals(Interval(Interval.MAJOR, Interval.THIRD).semitones(), 4)
        self.assertEquals(Interval(Interval.PERFECT, Interval.FOURTH).semitones(), 5)
        self.assertEquals(Interval(Interval.PERFECT, Interval.FIFTH).semitones(), 7)
        self.assertEquals(Interval(Interval.MAJOR, Interval.SIXTH).semitones(), 9)
        self.assertEquals(Interval(Interval.MAJOR, Interval.SEVENTH).semitones(), 11)

        self.assertEquals(Interval.from_diatonic_pitches((DiatonicPitch(5, 1), DiatonicPitch(5,-1)), True).semitones(), 2)

    def test_neg(self):
        self.assertEquals( -Interval(Interval.PERFECT, Interval.PRIME), Interval(Interval.PERFECT, Interval.OCTAVE) )
        self.assertEquals( -Interval(Interval.MAJOR, Interval.SECOND), Interval(Interval.MINOR, Interval.SEVENTH) )
        self.assertEquals( -Interval(Interval.MAJOR, Interval.THIRD), Interval(Interval.MINOR, Interval.SIXTH) )
        self.assertEquals( -Interval(Interval.PERFECT, Interval.FOURTH), Interval(Interval.PERFECT, Interval.FIFTH) )
        self.assertEquals( -Interval(Interval.PERFECT, Interval.FIFTH), Interval(Interval.PERFECT, Interval.FOURTH) )
        self.assertEquals( -Interval(Interval.MAJOR, Interval.SIXTH), Interval(Interval.MINOR, Interval.THIRD) )
        self.assertEquals( -Interval(Interval.MAJOR, Interval.SEVENTH), Interval(Interval.MINOR, Interval.SECOND) )
        self.assertEquals( -Interval(Interval.PERFECT, Interval.OCTAVE), Interval(Interval.PERFECT, Interval.PRIME) )

        self.assertEquals( -Interval(Interval.AUGMENTED, Interval.PRIME), Interval(Interval.DIMINISHED, Interval.OCTAVE) )
        self.assertEquals( -Interval(Interval.AUGMENTED, Interval.FOURTH), Interval(Interval.DIMINISHED, Interval.FIFTH) )
        self.assertEquals( -Interval(Interval.AUGMENTED, Interval.SECOND), Interval(Interval.DIMINISHED, Interval.SEVENTH) )
        self.assertEquals( -Interval(Interval.AUGMENTED, Interval.OCTAVE), Interval(Interval.DIMINISHED, Interval.PRIME) )

    def test_to_name(self):
        self.assertEquals(Interval(Interval.PERFECT, Interval.PRIME).to_name(lang='en'), 'p1')
        self.assertEquals(Interval(Interval.MAJOR, Interval.SECOND).to_name(lang='en'), 'maj2')
        self.assertEquals(Interval(Interval.MINOR, Interval.THIRD).to_name(lang='en'), 'min3')
        self.assertEquals(Interval(Interval.AUGMENTED, Interval.FOURTH).to_name(lang='en'), 'aug4')
        self.assertEquals(Interval(Interval.AUGMENTED+1, Interval.FOURTH).to_name(lang='en'), 'augaug4')
        self.assertEquals(Interval(Interval.DIMINISHED, Interval.FIFTH).to_name(lang='en'), 'dim5')
        self.assertEquals(Interval(Interval.DIMINISHED-1, Interval.FIFTH).to_name(lang='en'), 'dimdim5')

        self.assertEquals(Interval(Interval.PERFECT, Interval.PRIME).to_name(lang='sl'), 'č1')
        self.assertEquals(Interval(Interval.MAJOR, Interval.SECOND).to_name(lang='sl'), 'v2')
        self.assertEquals(Interval(Interval.MINOR, Interval.THIRD).to_name(lang='sl'), 'm3')
        self.assertEquals(Interval(Interval.AUGMENTED, Interval.FOURTH).to_name(lang='sl'), 'zv4')
        self.assertEquals(Interval(Interval.AUGMENTED+1, Interval.FOURTH).to_name(lang='sl'), 'zvzv4')
        self.assertEquals(Interval(Interval.DIMINISHED, Interval.FIFTH).to_name(lang='sl'), 'zm5')
        self.assertEquals(Interval(Interval.DIMINISHED-1, Interval.FIFTH).to_name(lang='sl'), 'zmzm5')

        # Negative direction.
        self.assertEquals(Interval(Interval.DIMINISHED, -Interval.FIFTH).to_name(lang='en'), '-dim5')
        self.assertEquals(Interval(Interval.DIMINISHED-1, -Interval.FIFTH).to_name(lang='en'), '-dimdim5')
        self.assertEquals(Interval(Interval.AUGMENTED, -Interval.FIFTH).to_name(lang='en'), '-aug5')
        self.assertEquals(Interval(Interval.AUGMENTED+1, -Interval.FIFTH).to_name(lang='en'), '-augaug5')
        self.assertEquals(Interval(Interval.DIMINISHED, -Interval.FIFTH).to_name(lang='sl'), '-zm5')
        self.assertEquals(Interval(Interval.DIMINISHED-1, -Interval.FIFTH).to_name(lang='sl'), '-zmzm5')
        self.assertEquals(Interval(Interval.AUGMENTED, -Interval.FIFTH).to_name(lang='sl'), '-zv5')
        self.assertEquals(Interval(Interval.AUGMENTED+1, -Interval.FIFTH).to_name(lang='sl'), '-zvzv5')

    def test_from_name(self):
        self.assertEquals(Interval.from_name('p1', lang='en'), Interval(Interval.PERFECT, Interval.PRIME))
        self.assertEquals(Interval.from_name('maj2', lang='en'), Interval(Interval.MAJOR, Interval.SECOND))
        self.assertEquals(Interval.from_name('min3', lang='en'), Interval(Interval.MINOR, Interval.THIRD))
        self.assertEquals(Interval.from_name('aug4', lang='en'), Interval(Interval.AUGMENTED, Interval.FOURTH))
        self.assertEquals(Interval.from_name('augaug4', lang='en'), Interval(Interval.AUGMENTED+1, Interval.FOURTH))
        self.assertEquals(Interval.from_name('dim5', lang='en'), Interval(Interval.DIMINISHED, Interval.FIFTH))
        self.assertEquals(Interval.from_name('dimdim5', lang='en'), Interval(Interval.DIMINISHED-1, Interval.FIFTH))

        self.assertEquals(Interval.from_name('č1', lang='sl'), Interval(Interval.PERFECT, Interval.PRIME))
        self.assertEquals(Interval.from_name('v2', lang='sl'), Interval(Interval.MAJOR, Interval.SECOND))
        self.assertEquals(Interval.from_name('m3', lang='sl'), Interval(Interval.MINOR, Interval.THIRD))
        self.assertEquals(Interval.from_name('zv4', lang='sl'), Interval(Interval.AUGMENTED, Interval.FOURTH))
        self.assertEquals(Interval.from_name('zvzv4', lang='sl'), Interval(Interval.AUGMENTED+1, Interval.FOURTH))
        self.assertEquals(Interval.from_name('zm5', lang='sl'), Interval(Interval.DIMINISHED, Interval.FIFTH))
        self.assertEquals(Interval.from_name('zmzm5', lang='sl'), Interval(Interval.DIMINISHED-1, Interval.FIFTH))

        # Negative direction.
        self.assertEquals(Interval.from_name('-aug4', lang='en'), Interval(Interval.AUGMENTED, -Interval.FOURTH))
        self.assertEquals(Interval.from_name('-augaug4', lang='en'), Interval(Interval.AUGMENTED+1, -Interval.FOURTH))
        self.assertEquals(Interval.from_name('-dim5', lang='en'), Interval(Interval.DIMINISHED, -Interval.FIFTH))
        self.assertEquals(Interval.from_name('-dimdim5', lang='en'), Interval(Interval.DIMINISHED-1, -Interval.FIFTH))
        self.assertEquals(Interval.from_name('-zv4', lang='sl'), Interval(Interval.AUGMENTED, -Interval.FOURTH))
        self.assertEquals(Interval.from_name('-zvzv4', lang='sl'), Interval(Interval.AUGMENTED+1, -Interval.FOURTH))
        self.assertEquals(Interval.from_name('-zm5', lang='sl'), Interval(Interval.DIMINISHED, -Interval.FIFTH))
        self.assertEquals(Interval.from_name('-zmzm5', lang='sl'), Interval(Interval.DIMINISHED-1, -Interval.FIFTH))

class ScaleTests(TestCase):
    def test_scales(self):
        self.assertEquals(Scale(ScaleGender.MAJOR, ScaleShape.NATURAL, 0).get_pitches(), [ DiatonicPitch(0,0), DiatonicPitch(1,0), DiatonicPitch(2,0), DiatonicPitch(3,0), DiatonicPitch(4,0), DiatonicPitch(5,0), DiatonicPitch(6,0), DiatonicPitch(7,0)])
        self.assertEquals(Scale(ScaleGender.MINOR, ScaleShape.NATURAL, -1).get_pitches(), [ DiatonicPitch(1,0), DiatonicPitch(2,0), DiatonicPitch(3,0), DiatonicPitch(4,0), DiatonicPitch(5,0), DiatonicPitch(6,-1), DiatonicPitch(7,0), DiatonicPitch(8,0)])