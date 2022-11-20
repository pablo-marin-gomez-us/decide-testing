from django.db import models
from django.contrib.postgres.fields import JSONField
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import MaxValueValidator, MinValueValidator

from base import mods
from base.models import Auth, Key

class RangeIntegerField(models.IntegerField):
    def __init__(self, *args, **kwargs):
        validators = kwargs.pop("validators", [])
        
        # turn min_value and max_value params into validators
        min_value = kwargs.pop("min_value", None)
        if min_value is not None:
            validators.append(MinValueValidator(min_value))
        max_value = kwargs.pop("max_value", None)
        if max_value is not None:
            validators.append(MaxValueValidator(max_value))

        kwargs["validators"] = validators

        super().__init__(*args, **kwargs)

class Question(models.Model):
    desc = models.TextField()

    def __str__(self):
        return self.desc


class QuestionOption(models.Model):
    question = models.ForeignKey(Question, related_name='options', on_delete=models.CASCADE)
    number = models.PositiveIntegerField(blank=True, null=True)
    option = models.TextField()

    def save(self):
        if not self.number:
            self.number = self.question.options.count() + 2
        return super().save()

    def __str__(self):
        return '{} ({})'.format(self.option, self.number)


class Voting(models.Model):
    name = models.CharField(max_length=200)
    desc = models.TextField(blank=True, null=True)
    question = models.ForeignKey(Question, related_name='voting', on_delete=models.CASCADE)
    
    #Para hacer una votación que use la ley d'Hont en el postprocesado, se debe añadir mínimo un escaños(seats)
    #Además, se deber poner el porcentaje de votos mínimos necesarios para poder obtener escaños
    #Si no se añade ningún escaño, se usará el postprocesado por defecto
    seats = models.PositiveIntegerField(default=0)
    min_percentage_representation = RangeIntegerField(min_value=0, max_value=100, default=5)

    start_date = models.DateTimeField(blank=True, null=True)
    end_date = models.DateTimeField(blank=True, null=True)

    pub_key = models.OneToOneField(Key, related_name='voting', blank=True, null=True, on_delete=models.SET_NULL)
    auths = models.ManyToManyField(Auth, related_name='votings')

    tally = JSONField(blank=True, null=True)
    postproc = JSONField(blank=True, null=True)

    def create_pubkey(self):
        if self.pub_key or not self.auths.count():
            return

        auth = self.auths.first()
        data = {
            "voting": self.id,
            "auths": [ {"name": a.name, "url": a.url} for a in self.auths.all() ],
        }
        key = mods.post('mixnet', baseurl=auth.url, json=data)
        pk = Key(p=key["p"], g=key["g"], y=key["y"])
        pk.save()
        self.pub_key = pk
        self.save()

    def get_votes(self, token=''):
        # gettings votes from store
        votes = mods.get('store', params={'voting_id': self.id}, HTTP_AUTHORIZATION='Token ' + token)
        # anon votes
        return [[i['a'], i['b']] for i in votes]

    def tally_votes(self, token=''):
        '''
        The tally is a shuffle and then a decrypt
        '''

        votes = self.get_votes(token)

        auth = self.auths.first()
        shuffle_url = "/shuffle/{}/".format(self.id)
        decrypt_url = "/decrypt/{}/".format(self.id)
        auths = [{"name": a.name, "url": a.url} for a in self.auths.all()]

        # first, we do the shuffle
        data = { "msgs": votes }
        response = mods.post('mixnet', entry_point=shuffle_url, baseurl=auth.url, json=data,
                response=True)
        if response.status_code != 200:
            # TODO: manage error
            pass

        # then, we can decrypt that
        data = {"msgs": response.json()}
        response = mods.post('mixnet', entry_point=decrypt_url, baseurl=auth.url, json=data,
                response=True)

        if response.status_code != 200:
            # TODO: manage error
            pass

        self.tally = response.json()
        self.save()

        self.do_postproc()
    
    def hont(dicc, seats, min_percentage_representation):
        dicc_div={}
        partidos = list(dicc.keys())
        partidos_sin_escaños=[]
        min = min_percentage_representation/100

        #Sacamos una lista con los partidos con menos representación del 5%
        for partido in partidos:
            porcentaje=dicc[partido]/sum(dicc.values())
            if porcentaje < min:
                partidos_sin_escaños.append(partido)

        #Eliminamos los partidos con menos representación del mínimo % del diccionario
        for partido in partidos_sin_escaños:
            dicc.pop(partido)

        #Calculamos el cociente electoral de cada partido con mas representación del porcentaje mínimo
        partidos = list(dicc.keys())
        for partido in partidos:
            lista_votos=[]
            for i in range(seats):
                numero_division = dicc[partido]/(i+1)
                lista_votos.append(numero_division)
                dicc_div[partido]=lista_votos

        #Calculamos el número de escaños de cada partido gracias a la lista de cocientes electorales
        escaños_partidos={}
        for partido in partidos:
            escaños_partidos[partido]=0

        #Para cada escaño hacemos una busqueda del partido con mayor cociente electoral
        for i in range(seats):
            maximo = 0
            partido_maximo = ""
            for partido in partidos:
                valores = dicc_div[partido]
                for valor in valores:

                    #Si el cociente electoral es mayor que el máximo actual, se actualiza el máximo y el partido con mayor cociente electoral
                    if valor > maximo:
                        maximo = valor
                        partido_maximo = partido

                    #Si el cociente electoral es igual que el máximo actual, se compara el número de votos total de cada partido
                    elif valor == maximo:
                        votos_nuevo_partido = dicc[partido]
                        votos_partido_maximo = dicc[partido_maximo]

                        #El escaño irá al partido con mayor número de votos totales
                        if votos_nuevo_partido > votos_partido_maximo:
                            maximo = valor
                            partido_maximo = partido

            #Una vez calculado el partido con mayor coeficiente se le suma un escaño
            escaños_partidos[partido_maximo] += 1

            #Y se elimina el valor del coeficiente electoral de la lista de ese partido
            dicc_div[partido_maximo].remove(maximo)

        #Añadimos los partidos los cuales no han obtenido ningún escaño con 0 escaños, para que el dicc esta completo con todos los partidos
        for partido in partidos_sin_escaños:
            escaños_partidos[partido]=0

        return escaños_partidos

    def do_postproc(self):
        tally = self.tally
        options = self.question.options.all()
        seats = self.seats
        min_percentage_representation = self.min_percentage_representation

        if seats==0:
            opts = []
            for opt in options:
                if isinstance(tally, list):
                    votes = tally.count(opt.number)
                else:
                    votes = 0
                opts.append({
                    'option': opt.option,
                    'number': opt.number,
                    'votes': votes
                })

            data = { 'type': 'IDENTITY', 'options': opts }
            postp = mods.post('postproc', json=data)

            self.postproc = postp
            self.save()
        else:
            #Hacemos el recuento de votos de todas las opciones
            opts = []
            for opt in options:
                if isinstance(tally, list):
                    votes = tally.count(opt.number)
                else:
                    votes = 0
                opts.append({
                    'option': opt.option,
                    'number': opt.number,
                    'votes': votes
                })

            #Ahora con todos los votos contados hacemos el reparto de escaños
            dicc_options_votes={}
            for opt in opts:
                dicc_options_votes[opt['option']]=opt['votes']
            escaños_partidos=Voting.hont(dicc_options_votes, seats, min_percentage_representation)
            
            #Una vez calculados los escaños de cada partido, se añaden a la lista de opciones
            for opt in opts:
                opt['seats']=escaños_partidos[opt['option']]

            data = { 'type': 'IDENTITY', 'options': opts }
            postp = mods.post('postproc', json=data)
            print(postp)
            self.postproc = postp
            self.save()

    def __str__(self):
        return self.name
