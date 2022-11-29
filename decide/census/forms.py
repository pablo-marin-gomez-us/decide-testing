from django import forms
from django.contrib.auth.models import User
import inspect

class AtributosUser(forms.Form):
    user = User.objects.all().values()[0]
    lista_atributos = []

    counter = 1
    for atribute in user.keys():
        if not atribute == 'id':
            lista_atributos.append((counter, atribute))
            counter += 1

    atributos = forms.MultipleChoiceField(label="Selecciona los atributos ", choices=lista_atributos, widget=forms.CheckboxSelectMultiple)