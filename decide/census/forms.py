from django import forms
from django.contrib.auth.models import User

class AtributosUser(forms.Form):
    user = User.objects.all().values()[0]
    atributes_list = []

    counter = 0
    for atribute in user.keys():
        if not atribute == 'id' and not atribute == 'password':
            atributes_list.append((counter, atribute))
            counter += 1

    user_atributes = forms.MultipleChoiceField(label="Selecciona los atributos ", choices=atributes_list, widget=forms.CheckboxSelectMultiple)