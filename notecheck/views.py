import random
from datetime import datetime

from django.http import HttpResponse

from .models import *

def index(request):
    return HttpResponse("missing token")

def submission(request, token):
    ex = NotePitchExercise.objects.get(token=token)

    ambitus = NotePitchExercise.AMBITUS[ex.clef]

    seed = int(datetime.now())
    rnd = random.Random(seed)
    notes = []
    for i in range(20):
        notes.append( DiatonicPitch(rnd.randrange(ambitus[0],ambitus[0]), 0) )

    for n in notes:
        lilysrc = "{{ \\clef {clefname} {note}1 }}".format(clefname=ex.clef.lower(), note=n)

    return HttpResponse("this is ex {}".format(ex.clef))
