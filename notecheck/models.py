import math
from datetime import timedelta
import random
import re
import uuid

from django.conf import settings
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

    def get_instance(self):
        """hack which returns a concrete implementation of exercise"""
        for e_class in [NotePitchExercise, IntervalExercise, ScaleExercise]:
            if e_class.objects.filter(token=self.token):
                return e_class.objects.get(token=self.token)

        raise TypeError()

    def get_title(self):
        return ""

class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('title', 'token', 'created', 'num_questions', 'share')

    @admin.display(description='Share')
    def share(self, obj):
        return mark_safe("<a href={}>🔗</a>".format(reverse('submission', args=(obj.token,))))

class NotePitchAnswerTypes(models.TextChoices):
    NOTENAME_OCTAVE = 'notename_octave', _('Note pitch and octave (e.g. fis2)')
    NOTENAME = 'notename', _('Note pitch only (e.g. fis)')

class NotePitchExercise(Exercise):
    AMBITUS = {
        Clefs.TREBLE: (25, 45),
        Clefs.BASS: (12, 33),
    }
    clef = models.CharField(max_length=10, choices=Clefs.choices, default=Clefs.TREBLE)
    answer_type = models.CharField(max_length=50, choices=NotePitchAnswerTypes.choices, default=NotePitchAnswerTypes.NOTENAME_OCTAVE)
    max_sharps = models.PositiveSmallIntegerField(default=1)
    max_flats = models.PositiveSmallIntegerField(default=1)

    def get_title(self):
        return NotePitchAnswerTypes(self.answer_type).label

@admin.register(NotePitchExercise)
class NotePitchExerciseAdmin(ExerciseAdmin):
    pass

class IntervalAnswerTypes(models.TextChoices):
    INTERVAL_QUANTITY = 'interval_quantity', _('Interval quantity (e.g. 4)')
    INTERVAL_QUANTITY_QUALITY = 'interval_quantity_quality', _('Interval quality and quantity (e.g. p4)')
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
    max_sharps = models.PositiveSmallIntegerField(default=1)
    max_flats = models.PositiveSmallIntegerField(default=1)

    def get_title(self):
        return IntervalAnswerTypes(self.answer_type).label

@admin.register(IntervalExercise)
class IntervalExerciseAdmin(ExerciseAdmin):
    pass

class ScaleGender(models.TextChoices):
    MAJOR = 'major', _('Major')
    MINOR = 'minor', _('Minor')

class ScaleShape(models.TextChoices):
    NATURAL = 'natural', _('Natural')
    HARMONIC = 'harmonic', _('Harmonic')
    MELODIC = 'melodic', _('Melodic')

class ScaleExercise(Exercise):
    AMBITUS = { # At most one semiline below and above the staff.
        Clefs.TREBLE: (27, 41),
        Clefs.BASS: (15, 29),
    }
    clef = models.CharField(max_length=10, choices=Clefs.choices, default=Clefs.TREBLE)
    direction = models.SmallIntegerField(default=0, validators=[MaxValueValidator(1), MinValueValidator(-1)])
    gender = models.CharField(max_length=50, choices=ScaleGender.choices, default=ScaleGender.MAJOR)
    shape = models.CharField(max_length=50, choices=ScaleShape.choices, default=ScaleShape.NATURAL)
    max_sharps = models.PositiveSmallIntegerField(default=7)
    max_flats = models.PositiveSmallIntegerField(default=7)

    def get_title(self):
        return "{gender} {shape}".format(gender=ScaleGender(self.gender).label, shape=ScaleShape(self.shape).label)

@admin.register(ScaleExercise)
class ScaleExerciseAdmin(ExerciseAdmin):
    pass

class Submission(models.Model):
    token = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    seed = models.IntegerField(default=0)
    answers = models.JSONField(null=True)
    created = models.DateTimeField('submission created date', auto_now=True)
    duration = models.DurationField(default=timedelta(0))

    def get_instance(self):
        """hack which returns a concrete implementation of submission"""
        if NotePitchExercise.objects.filter(token=self.token.token):
            return NotePitchSubmission.objects.get(pk=self.pk)
        elif IntervalExercise.objects.filter(token=self.token.token):
            return IntervalSubmission.objects.get(pk=self.pk)
        elif ScaleExercise.objects.filter(token=self.token.token):
            return ScaleSubmission.objects.get(pk=self.pk)
        raise TypeError()

    def get_expected_answers(self, lang: str) -> []:
        """return expected answers used as a helper in admin pages"""
        return self.get_instance().get_expected_answers(lang=lang)

    def get_score(self, lang: str) -> int:
        """return number of correct answers"""
        return self.get_instance().get_score_vector(lang).count(1)

    def get_score_vector(self, lang: str) -> []:
        """return binary array of correct/incorrect answers"""
        return self.get_instance().get_score_vector(lang=lang)

    def get_besttime(self, lang: str) -> timedelta:
        """return the best time among the submissions with full score"""
        best_time = timedelta.max
        for s in Submission.objects.filter(token=self.token).exclude(duration=timedelta(0)):
            if s.get_score(lang=lang)==len(s.get_expected_answers(lang=lang)) and s.duration < best_time:
                best_time = s.duration

        return best_time

@admin.register(Submission)
@admin.display(ordering='created')
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'created', 'duration', 'view_score', 'view')
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
            return "{} / {}".format(obj.get_instance().get_score(lang=settings.LANGUAGE_CODE), len(obj.get_expected_answers(lang=settings.LANGUAGE_CODE)))
        else:
            return ""

    @admin.display(description='View')
    def view(self, obj):
        return mark_safe("<a href={}>🔍</a>".format(reverse('submission', args=[obj.token.token, obj.pk])))

class NotePitchSubmission(Submission):
    class Meta:
        proxy = True

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

    def get_expected_answers(self, lang: str) -> []:
        pitches_str = []
        for i, p in enumerate(self.get_pitches()):
            pitches_str.append(p.to_name(lang))
        return pitches_str

    def get_score_vector(self, lang: str) -> []:
        answer_type = self.token.get_instance().answer_type
        pitches = self.get_pitches()
        correct_vec = []
        for i, s in enumerate(self.answers):
            if i>=len(pitches):
                break

            if answer_type == NotePitchAnswerTypes.NOTENAME_OCTAVE:
                correct = (pitches[i]==DiatonicPitch.from_name(s, lang=lang))
            elif answer_type == NotePitchAnswerTypes.NOTENAME:
                expected_pitch = DiatonicPitch(pitch=pitches[i].pitch % 7, accs=pitches[i].accs)
                answered_pitch = DiatonicPitch.from_name(s, lang=lang)
                if answered_pitch:
                    answered_pitch.pitch %= 7
                correct = expected_pitch==answered_pitch

            correct_vec.append(correct)
        return correct_vec

class IntervalSubmission(Submission):
    class Meta:
        proxy = True

    def get_pitch_pairs(self) -> []:
        """return pitch pairs generated from the seed"""
        ex = self.token.get_instance()
        rnd = random.Random(self.seed)
        ambitus = IntervalExercise.AMBITUS[ex.clef]

        pitch_pairs = []
        pitch_pair: (DiatonicPitch, DiatonicPitch) = None
        old_pitch_pair: (DiatonicPitch, DiatonicPitch) = None
        for i in range(ex.num_questions):
            # Avoid the same note pairs one after another.
            while old_pitch_pair == pitch_pair:
                pitch1 = DiatonicPitch(rnd.randrange(ambitus[0],ambitus[1]), 0)
                pitch2 = DiatonicPitch(rnd.randrange(ambitus[0],ambitus[1]), 0)

                if ex.max_sharps != 0 or ex.max_flats != 0:
                    pitch1.accs = rnd.randrange(-ex.max_flats, ex.max_sharps+1)
                    pitch2.accs = rnd.randrange(-ex.max_flats, ex.max_sharps+1)

                # Check other exercise constrains.
                interval_candidate = Interval.from_diatonic_pitches((pitch1, pitch2), False)
                if (ex.max_quantity == 0 or abs(interval_candidate.quantity) <= ex.max_quantity) and (ex.direction == 0 or interval_candidate.quantity / abs(interval_candidate.quantity) == ex.direction):
                    pitch_pair = (pitch1, pitch2)

            pitch_pairs.append( pitch_pair )
            old_pitch_pair = pitch_pair

        return pitch_pairs

    def get_expected_answers(self, lang: str) -> []:
        answer_type = self.token.get_instance().answer_type
        expected_answers = []
        for i, p in enumerate(self.get_pitch_pairs()):
            if answer_type == IntervalAnswerTypes.FULLTONES:
                expected_answers.append(str(Interval.from_diatonic_pitches(p, True).semitones() / 2))
            elif answer_type == IntervalAnswerTypes.SEMITONES:
                expected_answers.append(str(Interval.from_diatonic_pitches(p, True).semitones()))
            elif answer_type == IntervalAnswerTypes.INTERVAL_QUANTITY_QUALITY:
                expected_answers.append(str(Interval.from_diatonic_pitches(p, True).to_name(lang=lang)))
            elif answer_type == IntervalAnswerTypes.INTERVAL_QUANTITY:
                expected_answers.append(str(Interval.from_diatonic_pitches(p, True).quantity))
            else:
                raise TypeError()
        return expected_answers

    def get_score_vector(self, lang: str) -> []:
        pitch_pairs = self.get_pitch_pairs()
        answer_type = self.token.get_instance().answer_type
        correct_vec = []
        for i, a in enumerate(self.answers):
            if i>=len(pitch_pairs):
                break

            if answer_type == IntervalAnswerTypes.FULLTONES:
                correct_vec.append(len(a) and Interval.from_diatonic_pitches(pitch_pairs[i], True).semitones() / 2 == float(a))
            elif answer_type == IntervalAnswerTypes.SEMITONES:
                correct_vec.append(len(a) and Interval.from_diatonic_pitches(pitch_pairs[i], True).semitones() == float(a))
            elif answer_type == IntervalAnswerTypes.INTERVAL_QUANTITY_QUALITY:
                correct_vec.append(Interval.from_diatonic_pitches(pitch_pairs[i], True) == Interval.from_name(a, lang=lang))
            elif answer_type == IntervalAnswerTypes.INTERVAL_QUANTITY:
                correct_vec.append(len(a) and Interval.from_diatonic_pitches(pitch_pairs[i], True).quantity == int(a))
            else:
                raise TypeError()
        return correct_vec

class ScaleSubmission(Submission):
    class Meta:
        proxy = True

    def get_scales(self) -> [ ['DiatonicPitch'] ]:
        """return scales generated from the seed"""
        ex = self.token.get_instance()
        rnd = random.Random(self.seed)
        ambitus = ScaleExercise.AMBITUS[ex.clef]

        scales: [ [DiatonicPitch] ] = []
        scale: [DiatonicPitch] = None
        old_scale: [DiatonicPitch] = None
        for i in range(ex.num_questions):
            # Avoid the same note pairs one after another.
            while old_scale == scale:
                scale = []
                accs = rnd.randrange(-ex.max_flats, ex.max_sharps + 1)
                s = Scale( ex.gender, ex.shape, accs )
                pitches = s.get_pitches()
                direction = ex.direction
                if direction == 0:
                    direction = rnd.choice([-1, 1])

                # Find start pitch octave.
                offset = 0
                while pitches[0].pitch+offset < ambitus[0]:
                    offset += 7

                if direction == -1:
                    pitches.reverse()

                for p in pitches:
                    scale.append( DiatonicPitch( p.pitch+offset, p.accs ) )

            scales.append(scale)
            old_scale = scale[:]

        return scales

    def get_expected_answers(self, lang: str) -> []:
        answers: [str] = []
        for s in self.get_scales():
            for p in s:
                answers.append( p.to_name(lang=lang, relative=True) )

        return answers

    def get_score_vector(self, lang: str) -> []:
        score_vec = []
        i=0
        for s in self.get_scales():
            for p in s:
                if not self.answers[i]:
                    score_vec.append(False)
                else:
                    ap = DiatonicPitch.from_name(self.answers[i], lang)
                    score_vec.append( DiatonicPitch(p.pitch%7, p.accs)==DiatonicPitch(ap.pitch%7, ap.accs) )
                i+=1

        return score_vec

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

        accs = name.upper().count('IS') # sharps
        if accs == 0:
            accs -= name.upper().count('S') # flats

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
