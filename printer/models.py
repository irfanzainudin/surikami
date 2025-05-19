from django.db import models

# Create your models here.

class Shape(models.Model):
    SHAPES = [
        ("1", "Sphere"),
        ("2", "Cylinder"),
        ("3", "Cube")
    ]
    type = models.CharField(max_length=1, choices=SHAPES)
    colour = models.CharField(max_length=7)

    def __str__(self):
        return f"{self.type} - {self.colour}"
    