from django.shortcuts import render
from printer.models import Shape
import json


def shapes_home(request):
    shapes = [
        {
            "type": int(x.type),
            "colour": x.colour
        } for x in Shape.objects.all()
    ]
    shapes_json = json.dumps(shapes)
    context = {
        "shapes": shapes_json
    }

    return render(request, 'main.html', context)