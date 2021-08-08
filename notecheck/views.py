import random
import json
import time

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

    if request.method == 'POST':
        answers = []
        for i in range(len(pitches)):
            answers.append(request.POST['pitch'+str(i)])

        submission.answers = answers
        submission.save()

    svgs = []
    for p in pitches:
        lilysrc = "{{ \\clef {clefname} {pitch}1 }}".format(clefname=ex.clef.lower(), pitch=p.to_lilypond())
        svgs.append(generate_svg(lilysrc))

    questions = []
    for i, s in enumerate(svgs):
        questions.append( { "svg": s, "answer": submission.answers[i], "correct": pitches[i].to_name(lang='sl')==submission.answers[i] } )

    context = {
        'exercise': ex,
        'submission': submission,
        'questions': questions
    }
    return HttpResponse(template.render(context, request))
