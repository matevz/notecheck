from datetime import timedelta
import uuid
import random

from django.contrib import admin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

class Clefs(models.TextChoices):
    TREBLE = 'treble', _('Treble')
    BASS = 'bass', _('Bass')

class Exercise(models.Model):
    token = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    active = models.BooleanField(default=True)
    title = models.CharField(max_length=100)
    created = models.DateTimeField('date published', auto_now=True)
    num_questions = models.IntegerField(default=20)

class NotePitchExercise(Exercise):
    AMBITUS = {
        Clefs.TREBLE: (25, 45),
        Clefs.BASS: (12, 33),
    }
    clef = models.CharField(max_length=10, choices=Clefs.choices, default=Clefs.TREBLE)
    max_sharps = models.PositiveSmallIntegerField(default=0)
    max_flats = models.PositiveSmallIntegerField(default=0)

@admin.register(NotePitchExercise)
class NotePitchExerciseAdmin(admin.ModelAdmin):
    list_display = ('title', 'token', 'created', 'num_questions', 'link')

    @admin.display(description='Link')
    def link(self, obj):
        return mark_safe("<a href={}>🔗</a>".format(reverse('submission', args=(obj.token,))))

class Submission(models.Model):
    token = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    seed = models.IntegerField(default=0)
    answers = models.JSONField(null=True)
    created = models.DateTimeField('submission created date', auto_now=True)
    duration = models.DurationField(default=timedelta(0))

    def get_score(self, lang: str) -> int:
        """return number of correct answers"""
        raise NotImplementedError()

    def get_besttime(self, lang: str) -> timedelta:
        """return the best time among the submissions with full score"""
        best_time = timedelta.max
        for s in Submission.objects(token=self.token).exclude(duration=timedelta(0)):
            if s.get_score(lang=lang)==s.token.num_questions and s.duration < best_time:
                best_time = s.duration

        return best_time

@admin.register(Submission)
@admin.display(ordering='created')
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'duration', 'view_score')
    list_filter = ['token']

    def get_queryset(self, request):
        # Hide submissions which weren't submitted yet.
        return super(SubmissionAdmin, self).get_queryset(request).filter(duration__gt=timedelta(0))

    @admin.display(description='Exercise')
    def name(self, obj) -> str:
        return "{} ({})".format(obj.token.title, str(obj.token.token)[:8])

    @admin.display(description='Score')
    def view_score(self, obj) -> str:
        if obj.duration:
            return "{} / {}".format(obj.get_score('sl'), obj.token.num_questions)
        else:
            return ""

class NotePitchSubmission(Submission):
    def get_pitches(self) -> []:
        """return pitch instances generated from the seed"""
        ex = NotePitchExercise.objects.get(token=self.token.token)
        ambitus = NotePitchExercise.AMBITUS[ex.clef]

        rnd = random.Random(self.seed)
        notes = []
        pitch: DiatonicPitch = None
        oldPitch: DiatonicPitch = None
        for i in range(ex.num_questions):
            # Avoid the same pitch one right after another.
            while oldPitch == pitch:
                accs = 0
                if ex.max_sharps != 0 or ex.max_flats != 0:
                    accs = rnd.randrange(-ex.max_flats, ex.max_sharps+1)

                pitch = DiatonicPitch(rnd.randrange(ambitus[0],ambitus[1]), accs)

            notes.append( pitch )
            oldPitch = pitch

        return notes

    def get_score(self, lang: str) -> int:
        pitches = self.get_pitches()
        num_correct = 0
        for i, s in enumerate(self.answers):
            correct = pitches[i]==DiatonicPitch.from_name(self.answers[i], lang=lang)
            num_correct += int(correct)
        return num_correct

class IntervalAnswerTypes(models.TextChoices):
    INTERVAL_QUANTITY = 'interval_quantity', _('Interval quantity (e.g. 4)')
    INTERVAL_QUANTITY_QUALITY = 'interval_quantity_quality', _('Interval quantity and quality (e.g. p4)')
    FULLTONES = 'fulltones', _('Fulltones and remaining semitone (e.g. 2.5)')
    SEMITONES = 'semitones', _('Semitones (e.g. 5)')

class IntervalExercise(Exercise):
    AMBITUS = {
        Clefs.TREBLE: (25, 45),
        Clefs.BASS: (12, 33),
    }
    clef = models.CharField(max_length=10, choices=Clefs.choices, default=Clefs.TREBLE)
    answer_type = models.CharField(max_length=50, choices=IntervalAnswerTypes.choices, default=IntervalAnswerTypes.INTERVAL_QUANTITY_QUALITY)
    direction = models.SmallIntegerField(default=0, validators=[MaxValueValidator(1), MinValueValidator(-1)])
    max_quantity = models.PositiveSmallIntegerField(default=8)
    max_sharps = models.PositiveSmallIntegerField(default=0)
    max_flats = models.PositiveSmallIntegerField(default=0)

@admin.register(IntervalExercise)
class IntervalExerciseAdmin(admin.ModelAdmin):
    list_display = ('title', 'token', 'created', 'num_questions', 'link')

    @admin.display(description='Link')
    def link(self, obj):
        return mark_safe("<a href={}>🔗</a>".format(reverse('submission', args=(obj.token,))))

class IntervalSubmission(Submission):
    def get_pitch_pairs(self) -> []:
        """return pitch pairs generated from the seed"""
        ex = self.token
        rnd = random.Random(self.seed)
        ambitus = IntervalExercise.AMBITUS[ex.clef]

        pitch_pairs = []
        pitch_pair: (DiatonicPitch, DiatonicPitch)
        old_pitch_pair: (DiatonicPitch, DiatonicPitch)
        for i in range(ex.num_questions):
            # Avoid the same note pairs one after another.
            while old_pitch_pair == pitch_pair:
                pitch1 = DiatonicPitch(rnd.randrange(ambitus[0],ambitus[1]))
                pitch2 = DiatonicPitch(rnd.randrange(ambitus[0],ambitus[1]))

                if ex.max_sharps != 0 or ex.max_flats != 0:
                    pitch1.accs = rnd.randrange(-ex.max_flats, ex.max_sharps+1)
                    pitch2.accs = rnd.randrange(-ex.max_flats, ex.max_sharps+1)

                # Check other exercise constrains.
                interval_candidate = Interval.from_diatonic_pitches(pitch1, pitch2, False)
                if (ex.max_quantity == 0 or interval_candidate.quantity <= ex.max_quantity) and (ex.direction == 0 or interval_candidate.quantity / abs(interval_candidate.quantity) == ex.direction):
                    pitch_pair = (pitch1, pitch2)

            pitch_pairs.append( pitch_pair )
            old_pitch_pair = pitch_pair

        return pitch_pairs

    def get_score(self, lang: str) -> int:
        pitch_pairs = self.get_pitch_pairs()
        num_correct = 0
        answer_type = self.tokenIntervalExercise.objects.get(token=self.token.token).answer_type
        for i, s in enumerate(self.answers):
            correct: bool
            if answer_type == IntervalAnswerTypes.FULLTONES:
                correct = Interval.from_diatonic_pitches(pitch_pairs[i], True).semitones() / 2 == float(self.answers[i].replace(',','.'))
            elif answer_type == IntervalAnswerTypes.SEMITONES:
                correct = Interval.from_diatonic_pitches(pitch_pairs[i], True).semitones() == int(self.answers[i])
            elif answer_type == IntervalAnswerTypes.INTERVAL_QUANTITY_QUALITY:
                raise NotImplementedError()
            elif answer_type == IntervalAnswerTypes.INTERVAL_QUANTITY:
                correct = Interval.from_diatonic_pitches(pitch_pairs[i], True).quantity == int(self.answers[i])
            else:
                raise NotImplementedError()
            num_correct += int(correct)
        return num_correct

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

    def to_name(self, lang: str = 'en') -> str:
        """converts pitch to note name. e.g. (0,0) -> C2, (9, 1) -> Eis1, (28, 0) -> c1"""
        name = chr(ord('C')+(self.pitch%7))

        if name=='H':
            name = 'A'
        if name=='I':
            if lang in ['sl', 'de']:
                name = 'H'
            else:
                name = 'B'

        if self.pitch >= 21:
            name = name.lower()

        name += 'is'*self.accs
        name += 'es'*-self.accs
        if name.startswith('ee'): # es
            name = name[1:]
        if name.startswith('aes'): # as
            name = name.replace('es','as')
            name = name[1:]

        if self.pitch < 7:
            name += '2'
        elif self.pitch < 14:
            name += '1'
        elif self.pitch >= 28:
            name += str((self.pitch-28) // 7 + 1)

        return name

    def from_name(name: str, lang: str = 'en'):
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

    @staticmethod
    def from_diatonic_pitches( pitch_pair: (DiatonicPitch, DiatonicPitch), absolute: bool = True):
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

        # Major and perfect intervals are default
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

        # Minor or diminished / augmented.
        # TODO: Rewrite using match statement introduced in Python 3.10
        if self.quality == Interval.DIMINISHED:
            if absQuantity == 1 or absQuantity == 3 or absQuantity == 6 or absQuantity == 7:
                semitones -= 2
            else:
                semitones -= 1
        elif self.quality == Interval.MINOR:
            semitones -= 1
        elif self.quality == Interval.MAJOR:
            semitones += 1

        # Octaves.
        semitones += 12 * ((abs(self.quantity) - 1) // 7)

        # Invert semitones for negative quantity
        semitones = abs(semitones)

        return semitones
