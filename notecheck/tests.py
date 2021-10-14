from django.test import TestCase

from .models import DiatonicPitch

class DiatonicPitchTests(TestCase):
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
        self.assertEquals(DiatonicPitch.from_name('a'), DiatonicPitch(26,0))
        self.assertEquals(DiatonicPitch.from_name('b'), DiatonicPitch(27,0))
        self.assertEquals(DiatonicPitch.from_name('ces1'), DiatonicPitch(28,-1))
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
