from datetime import timedelta
import random
import uuid

from django.conf import settings
from django.contrib import admin
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from .score import *

# Two same questions one after another should not appear in any of the exercises.
# If this cannot be satisfied, give up after UNIQUE_QUESTION_RETRIES to avoid
# infinite loop.
UNIQUE_QUESTION_RETRIES = 5

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
    custom_pitches = models.JSONField(blank=True, default=list, decoder=DiatonicPitchDecoder, encoder=DiatonicPitchEncoder)

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
            if s.get_score(lang=lang)==s.token.num_questions and s.duration < best_time:
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
            num_retries = 0
            while oldPitch == pitch and num_retries < UNIQUE_QUESTION_RETRIES:
                accs = rnd.randrange(-ex.max_flats, ex.max_sharps+1)
                if not ex.custom_pitches:
                    pitch = DiatonicPitch(rnd.randrange(ambitus[0], ambitus[1]), accs)
                else:
                    if ex.max_sharps == 0 and ex.max_flats == 0:
                        pitch = rnd.choice(ex.custom_pitches)
                    else:
                        pitch = DiatonicPitch(rnd.choice(ex.custom_pitches).pitch, accs)

                num_retries += 1

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
            num_retries = 0
            while old_pitch_pair == pitch_pair and num_retries < UNIQUE_QUESTION_RETRIES:
                pitch1 = DiatonicPitch(rnd.randrange(ambitus[0],ambitus[1]), 0)
                pitch2 = DiatonicPitch(rnd.randrange(ambitus[0],ambitus[1]), 0)

                if ex.max_sharps != 0 or ex.max_flats != 0:
                    pitch1.accs = rnd.randrange(-ex.max_flats, ex.max_sharps+1)
                    pitch2.accs = rnd.randrange(-ex.max_flats, ex.max_sharps+1)

                # Check other exercise constrains.
                interval_candidate = Interval.from_diatonic_pitches((pitch1, pitch2), False)
                if (ex.max_quantity == 0 or abs(interval_candidate.quantity) <= ex.max_quantity) and (ex.direction == 0 or interval_candidate.quantity / abs(interval_candidate.quantity) == ex.direction):
                    pitch_pair = (pitch1, pitch2)

                num_retries += 1

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
            num_retries = 0
            while old_scale == scale and num_retries < UNIQUE_QUESTION_RETRIES:
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

                num_retries += 1

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
