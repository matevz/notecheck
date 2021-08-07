from django.test import TestCase

from .models import DiatonicPitch

class DiatonicPitchTests(TestCase):
    def test_pitch_to_name(self):
        self.assertEquals(DiatonicPitch(0,0).to_name(), 'C2')
        self.assertEquals(DiatonicPitch(9,1).to_name(), 'Eis1')
        self.assertEquals(DiatonicPitch(27,0).to_name(), 'b')
        self.assertEquals(DiatonicPitch(28,-1).to_name(), 'ces1')
        self.assertEquals(DiatonicPitch(36,0).to_name(), 'd2')

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
        self.assertEquals(DiatonicPitch.from_name('b'), DiatonicPitch(27,0))
        self.assertEquals(DiatonicPitch.from_name('h'), DiatonicPitch(27,0))
        self.assertEquals(DiatonicPitch.from_name('ces1'), DiatonicPitch(28,-1))
        self.assertEquals(DiatonicPitch.from_name('d2'), DiatonicPitch(36,0))
