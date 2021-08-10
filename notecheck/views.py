import time
from datetime import datetime, timezone

from django.http import HttpResponse
from django.template import loader

from .models import *
from .lilypond import *

def index(request):
    return HttpResponse("missing token")

def submission(request, token):
    template = loader.get_template('notecheck/notepitch.html')
    ex = NotePitchExercise.objects.get(token=token)

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
            answers.append(request.POST['pitch'+str(i)])

        submission.answers = answers
        submission.duration = datetime.now(timezone.utc)-submission.created
        submission.save()

    svgs = []
    for p in pitches:
        lilysrc = "{{ \\clef {clefname} {pitch}1 }}".format(clefname=ex.clef.lower(), pitch=p.to_lilypond())
        svgs.append(generate_svg(lilysrc))

    questions = []
    for i, s in enumerate(svgs):
        correct = pitches[i].to_name(lang='sl')==submission.answers[i]
        questions.append( { "svg": s, "answer": submission.answers[i], "correct": correct } )

    context = {
        'exercise': ex,
        'submission': submission,
        'questions': questions,
        'num_correct': submission.get_score(lang='sl'),
        'top_10': submission.get_score(lang='sl')/ex.num_questions >= 0.9,
    }
    return HttpResponse(template.render(context, request))
