import time
from datetime import datetime, timezone

from django.conf import settings
from django.http import HttpResponse
from django.template import loader
from django.utils.translation import gettext_lazy as _

from .models import *
from .lilypond import *

def index(request):
    return HttpResponse("Missing exercise token.")

def get_template(token):
    if NotePitchExercise.objects.filter(token=token) or IntervalExercise.objects.filter(token=token):
        return loader.get_template('notecheck/grid.html')
    if ScaleExercise.objects.filter(token=token):
        return loader.get_template('notecheck/scales.html')
    raise TypeError

def get_questions_answers(submission_abstract: Submission, lang: str) -> ([], []):
    submission = submission_abstract.get_instance()
    ex = submission_abstract.token.get_instance()
    score_vector = submission.get_score_vector(lang)
    questions = []
    answers = []

    for i, a in enumerate(submission.answers):
        answers.append({"answer": a, "correct": score_vector[i], "index": i })

    if isinstance(submission, NotePitchSubmission):
        for i, p in enumerate(submission.get_pitches()):
            lilysrc = "{{ \\omit Score.TimeSignature \\clef {clefname} {pitch}1 }}".format(clefname=ex.clef.lower(), pitch=p.to_lilypond())
            s = generate_svg(lilysrc)
            questions.append( { "svg": s, "answers": [answers[i]] } )
    elif isinstance(submission, IntervalSubmission):
        for i, p in enumerate(submission.get_pitch_pairs()):
            lilysrc = "{{ \\omit Score.TimeSignature \\clef {clefname} {pitch1}1 \\omit Score.BarLine {pitch2}1 }}".format(clefname=ex.clef.lower(), pitch1=p[0].to_lilypond(), pitch2=p[1].to_lilypond())
            s = generate_svg(lilysrc)
            questions.append( { "svg": s, "answers": [answers[i]] } )
    elif isinstance(submission, ScaleSubmission):
        for i, s in enumerate(submission.get_scales()):
            lilysrc = "{{ \\omit Score.TimeSignature \\clef {clefname} {pitch1}1 \\omit Score.BarLine s1 s1 s1 s1 s1 s1 {pitch2}1 }}".format(
                clefname=ex.clef.lower(),
                pitch1=s[0].to_lilypond(),
                pitch2=s[-1].to_lilypond()
            )
            s = generate_svg(lilysrc)
            questions.append( {"svg": s, "answers": answers[i*8 : (i+1)*8], "title": "{gender} {shape}".format(gender=ex.gender, shape=ex.shape) } )

    return questions, answers

def submission(request, token, submission_id=None):
    template = get_template(token)
    ex = Exercise.objects.get(token=token)
    if not ex:
        return HttpResponse("Invalid exercise token.")

    if not ex.active:
        return HttpResponse("Exercise not activated.")

    ex = ex.get_instance()
    submission: Submission

    if request.method == 'POST':
        # Post filled submission.
        submission = Submission.objects.get(id=request.POST['submission_id'])
    elif request.method == 'GET' and submission_id:
        # View-only.
        submission = Submission.objects.get(id=submission_id)
    else:
        # Create new submission.
        submission = Submission(
            token=ex,
            seed=int(time.time()),
        )
        submission.save()

    submission = submission.get_instance()

    if request.method == 'GET' and not submission_id:
        # Prepopulate submission with empty answers, if creating new submission.
        submission.answers = [''] * len(submission.get_expected_answers(lang='sl'))
        submission.save()
    elif request.method == 'POST' and not submission.duration:
        # Only allow posting the submission for the first time by checking submission.duration field.
        ans = []
        for i, _ in enumerate(submission.get_expected_answers(lang='sl')):
            answer = request.POST['answer'+str(i)].strip().replace(',','.')
            ans.append(answer)

        submission.answers = ans
        submission.duration = datetime.now(timezone.utc)-submission.created
        submission.save()

    questions, answers = get_questions_answers(submission, settings.LANGUAGE_CODE)
    context = {
        'exercise': ex,
        'submission': submission,
        'questions': questions,
        'answers': answers,
        'num_correct': submission.get_score(lang=settings.LANGUAGE_CODE),
        'top_10': submission.get_score(lang=settings.LANGUAGE_CODE)/len(answers) >= 0.9,
        'besttime': submission.get_score(lang=settings.LANGUAGE_CODE)==len(answers) and submission.get_besttime(lang=settings.LANGUAGE_CODE)>=submission.duration,
        'duration': '{m}:{s}'.format(m=int(submission.duration.total_seconds()//60), s=int(submission.duration.total_seconds()%60))
    }
    return HttpResponse(template.render(context, request))
