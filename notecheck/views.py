import time
from datetime import datetime, timezone

from django.http import HttpResponse
from django.template import loader

from .models import *
from .lilypond import *

def index(request):
    return HttpResponse("Missing exercise token.")

def submission(request, token):
    # TODO: First fetch the exercise and then the corresponding template.
    template = loader.get_template('notecheck/notepitch.html')
    ex = NotePitchExercise.objects.get(token=token)
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

    pitches = submission.get_pitches()

    if request.method == 'POST' and not submission.duration:
        answers = []
        for i in range(ex.num_questions):
            answer = request.POST['pitch'+str(i)].strip()
            answers.append(answer)

        submission.answers = answers
        submission.duration = datetime.now(timezone.utc)-submission.created
        submission.save()

    svgs = []
    for p in pitches:
        lilysrc = "{{ \\clef {clefname} {pitch}1 }}".format(clefname=ex.clef.lower(), pitch=p.to_lilypond())
        svgs.append(generate_svg(lilysrc))

    questions = []
    for i, s in enumerate(svgs):
        correct = pitches[i]==DiatonicPitch.from_name(submission.answers[i], lang='sl')
        questions.append( { "svg": s, "answer": submission.answers[i], "correct": correct } )

    context = {
        'exercise': ex,
        'submission': submission,
        'questions': questions,
        'num_correct': submission.get_score(lang='sl'),
        'top_10': submission.get_score(lang='sl')/ex.num_questions >= 0.9,
        'besttime': submission.get_score(lang='sl')==ex.num_questions and Submission.get_besttime(lang='sl')>=submission.duration,
        'duration': '{m}:{s}'.format(m=int(submission.duration.total_seconds()//60), s=int(submission.duration.total_seconds()%60))
    }
    return HttpResponse(template.render(context, request))
