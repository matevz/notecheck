import time
from datetime import datetime, timezone

from django.http import HttpResponse
from django.template import loader

from .models import *
from .lilypond import *

def index(request):
    return HttpResponse("Missing exercise token.")

def get_template(token):
    if NotePitchExercise.objects.filter(token=token) or IntervalExercise.objects.filter(token=token):
        return loader.get_template('notecheck/grid.html')
    raise TypeError

def get_questions(submission_abstract: Submission, lang: str):
    submission = submission_abstract.get_instance()
    ex = submission_abstract.token.get_instance()
    score_vector = submission.get_score_vector(lang)
    questions = []

    if isinstance(submission, NotePitchSubmission):
        for i, p in enumerate(submission.get_pitches()):
            lilysrc = "{{ \\omit Score.TimeSignature \\clef {clefname} {pitch}1 }}".format(clefname=ex.clef.lower(), pitch=p.to_lilypond())
            s = generate_svg(lilysrc)
            questions.append( { "svg": s, "answer": submission.answers[i], "correct": score_vector[i] } )
    elif isinstance(submission, IntervalSubmission):
        for i, p in enumerate(submission.get_pitch_pairs()):
            lilysrc = "{{ \\omit Score.TimeSignature \\clef {clefname} {pitch1}1 \\omit Score.BarLine {pitch2}1 }}".format(clefname=ex.clef.lower(), pitch1=p[0].to_lilypond(), pitch2=p[1].to_lilypond())
            s = generate_svg(lilysrc)
            questions.append( { "svg": s, "answer": submission.answers[i], "correct": score_vector[i] } )

    return questions

def submission(request, token):
    template = get_template(token)
    ex = Exercise.objects.get(token=token)
    if not ex:
        return HttpResponse("Invalid exercise token.")

    if not ex.active:
        return HttpResponse("Exercise not activated.")

    context = {}
    submission: Submission

    if request.method == 'POST':
        submission = Submission.objects.get(id=request.POST['submission_id'])
    else:
        submission = Submission(
            token=ex,
            seed=int(time.time()),
            answers=['']*ex.num_questions,
        )
        submission.save()

    if request.method == 'POST' and not submission.duration:
        answers = []
        for i in range(ex.num_questions):
            answer = request.POST['answer'+str(i)].strip().replace(',','.')
            answers.append(answer)

        submission.answers = answers
        submission.duration = datetime.now(timezone.utc)-submission.created
        submission.save()

    questions = get_questions(submission, 'sl')

    context = {
        'exercise': ex,
        'submission': submission,
        'questions': questions,
        'num_correct': submission.get_score(lang='sl'),
        'top_10': submission.get_score(lang='sl')/ex.num_questions >= 0.9,
        'besttime': submission.get_score(lang='sl')==ex.num_questions and submission.get_besttime(lang='sl')>=submission.duration,
        'duration': '{m}:{s}'.format(m=int(submission.duration.total_seconds()//60), s=int(submission.duration.total_seconds()%60))
    }
    return HttpResponse(template.render(context, request))
