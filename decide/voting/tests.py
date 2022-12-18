import random
import itertools
from django.utils import timezone
from django.conf import settings
from django.contrib.auth.models import User

from base import mods
from base.tests import BaseTestCase
from census.models import Census
from mixnet.mixcrypt import ElGamal
from mixnet.mixcrypt import MixCrypt
from mixnet.models import Auth
from voting.models import Voting, Question, QuestionOption

class VotingModelTestCase(BaseTestCase):
    def setUp(self):
        q = Question(desc="Descripcion")
        q.save()

        opt1 = QuestionOption(question=q,option="opcion1")
        opt1.save()
        opt2 = QuestionOption(question=q,option="opcion2")
        opt2.save()

        self.v = Voting(name="Votacion", question=q)

        self.v.save()

        #Creamos una votacion con escaños y porcentaje de representacion
        q2 = Question(desc="Descripcion seats")
        q2.save()

        opt11 = QuestionOption(question=q2,option="opcion11")
        opt11.save()
        opt22 = QuestionOption(question=q2,option="opcion22")
        opt22.save()

        self.v1 = Voting(name="Votacion seats", question=q2, seats=5, min_percentage_representation=2)
        self.v1.save()

        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.v=None

    def testExist(self):
        v = Voting.objects.get(name="Votacion")
        self.assertEqual(v.question.options.all()[0].option,'opcion1')
        self.assertEqual(v.question.options.all()[1].option,'opcion2')
        self.assertEqual(len(v.question.options.all()),2)
        #Comprobamos que los escaños y el porcentaje se han inicializado correctamente por defecto, al no indicarlos
        self.assertEqual(v.seats,0)
        self.assertEqual(v.min_percentage_representation,5)

    #Comprobamos que se creó correctamente la votacion con escaños y porcentaje de representacion
    def testExistsSeats(self):
        v = Voting.objects.get(name="Votacion seats")
        self.assertEqual(v.question.options.all()[0].option,'opcion11')
        self.assertEqual(v.question.options.all()[1].option,'opcion22')
        self.assertEqual(len(v.question.options.all()),2)
        self.assertEqual(v.seats,5)
        self.assertEqual(v.min_percentage_representation,2)

    def test_create_votingAPI(self):
        self.login()
        data = {
            'name':'Example',
            'desc': 'Description example',
            'question': 'I want a',
            'question_opt': ['cat','dog','horse']
        }
        response = self.client.post('/voting/',data,format='json')
        self.assertEqual(response.status_code,201)

        voting = Voting.objects.get(name='Example')
        self.assertEqual(voting.desc,'Description example')
        self.assertEqual(voting.seats,0)
        self.assertEqual(voting.min_percentage_representation,5)

class VotingPriorityModelTestCase(BaseTestCase):
    def setUp(self):
        p = Question(desc="Pregunta con Prioridad", multioption=True)
        p.save()
        opt1 = QuestionOption(question=p, option="Primera Opción")
        opt1.save()
        opt2 = QuestionOption(question=p, option="Segunda Opción")
        opt2.save()
        opt3 = QuestionOption(question=p, option="Tercera Opción")
        opt3.save()

        self.v = Voting(name="Votacion con Prioridad", question=p)
        self.v.save()
        super().setUp()

    def tearDown(self):
        super().tearDown()
        self.v=None

    def testExist(self):
        v = Voting.objects.get(name="Votacion con Prioridad")
        self.assertEqual(v.question.options.all()[0].option,'Primera Opción')
        self.assertEqual(v.question.options.all()[1].option,'Segunda Opción')
        self.assertEqual(v.question.options.all()[2].option,'Tercera Opción')
        self.assertEqual(len(v.question.options.all()),3)
        self.assertEqual(v.question.multioption,True)
    
    def testChanginPriority(self):
        v = Voting.objects.get(name="Votacion con Prioridad")
        v.question.multioption=False
        self.v.save()
        self.assertEqual(v.question.multioption, False)
        self.assertEqual(v.seats, 0)
        self.assertEqual(v.min_percentage_representation, 5)
    
    def test_create_votingAPI(self):
        self.login()
        data = {
            'name':'Example',
            'desc': 'Description example',
            'question': 'I want a',
            'question_opt': ['cat','dog','horse']
        }
        response = self.client.post('/voting/',data,format='json')
        self.assertEqual(response.status_code,201)

        voting = Voting.objects.get(name='Example')
        self.assertEqual(voting.desc,'Description example')
        self.assertEqual(voting.question.multioption,False)

class VotingTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()

    def tearDown(self):
        super().tearDown()

    def test_toString(self):
        v = self.create_voting()
        self.assertEqual(str(v), "test voting")
        self.assertEqual(str(v.question),"test question")
        self.assertEqual(str(v.question.options.all()[0]),"option 1 (2)")
        #Comprobamos que los escaños y el porcentaje se han inicializado correctamente por defecto, al no indicarlos
        self.assertEqual(v.seats,0)
        self.assertEqual(v.min_percentage_representation,5)

        #También comprobamos el toString para una votación con escaños y porcentaje de representación indicados en la creación de la votación
        vSeats = self.create_voting_seats()
        self.assertEqual(str(vSeats), "test voting seats")
        self.assertEqual(str(vSeats.question),"test question seats")
        self.assertEqual(str(vSeats.question.options.all()[0]),"option 1 (2)")
        self.assertEqual(vSeats.seats,5)
        self.assertEqual(vSeats.min_percentage_representation,2)

        votingPriority = self.create_voting_priority()
        self.assertEqual(str(votingPriority), "test voting priority")
        self.assertEqual(str(votingPriority.question),"test question priority")
        self.assertEqual(str(votingPriority.question.options.all()[0]),"option 1 (2)")
        self.assertEqual(votingPriority.question.multioption,True)

    def test_update_voting_400(self):
        v = self.create_voting()
        data = {}
        self.login()
        response = self.client.post('/voting/{}/'.format(v.pk),data,format='json')
        self.assertEqual(response.status_code,405)


    def encrypt_msg(self, msg, v, bits=settings.KEYBITS):
        pk = v.pub_key
        p, g, y = (pk.p, pk.g, pk.y)
        k = MixCrypt(bits=bits)
        k.k = ElGamal.construct((p, g, y))
        return k.encrypt(msg)

    def create_voting(self):
        q = Question(desc='test question')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v
    
    #Creamos una votacion con escaños y porcentaje de representacion determinados
    def create_voting_seats(self):
        q = Question(desc='test question seats')
        q.save()
        for i in range(5):
            opt = QuestionOption(question=q, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting seats', question=q, seats=5, min_percentage_representation=2)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_voting_priority(self):
        p = Question(desc='test question priority', multioption=True)
        p.save()
        for i in range(5):
            opt = QuestionOption(question=p, option='option {}'.format(i+1))
            opt.save()
        v = Voting(name='test voting priority', question=p)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)

        return v

    def create_voters(self, v):
        for i in range(100):
            u, _ = User.objects.get_or_create(username='testvoter{}'.format(i))
            u.is_active = True
            u.save()
            c = Census(voter_id=u.id, voting_id=v.id)
            c.save()

    def get_or_create_user(self, pk):
        user, _ = User.objects.get_or_create(pk=pk)
        user.username = 'user{}'.format(pk)
        user.set_password('qwerty')
        user.save()
        return user

    def store_votes_priority(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()
        clear = [13542]

        a,b = self.encrypt_msg(13542, v)
        data = {
            'voting': v.id,
            'voter': voter.voter_id,
            'vote': { 'a': a, 'b': b },
        }

        user = self.get_or_create_user(voter.voter_id)
        self.login(user=user.username)
        voter = voters.pop()
        mods.post('store', json=data)

        return clear

    def store_votes(self, v):
        voters = list(Census.objects.filter(voting_id=v.id))
        voter = voters.pop()

        clear = {}
        for opt in v.question.options.all():
            clear[opt.number] = 0
            for i in range(random.randint(0, 5)):
                a, b = self.encrypt_msg(opt.number, v)
                data = {
                    'voting': v.id,
                    'voter': voter.voter_id,
                    'vote': { 'a': a, 'b': b },
                }
                clear[opt.number] += 1
                user = self.get_or_create_user(voter.voter_id)
                self.login(user=user.username)
                voter = voters.pop()
                mods.post('store', json=data)
        return clear

    def test_complete_voting(self):
        v = self.create_voting()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])

    #Comprobamos que se calculan correctamente los escaños en una votación con escaños
    def test_complete_voting_seats(self):
        v = self.create_voting_seats()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        tally.sort()
        tally = {k: len(list(x)) for k, x in itertools.groupby(tally)}

        for q in v.question.options.all():
            self.assertEqual(tally.get(q.number, 0), clear.get(q.number, 0))

        #Vamos a recoger en un dicc los votos por opción, además de comprobar que el tally es correcto
        votos_questiones = {}
        for q in v.postproc:
            self.assertEqual(tally.get(q["number"], 0), q["votes"])
            votos_questiones[q["option"]] = q["votes"]
        
        #Usamos la función hont, la cual calcula el reparto de escaños de todas las opciones mediante sus votos
        hont = Voting.hont(votos_questiones, v.seats, v.min_percentage_representation)
        
        #Por último comprobamos que los escaños que contienen cada opción obtenidos tras el postprocesado del tally
        #concuerdan con el resultado del repartao de escaños para las opciones con la función hont
        for q in v.postproc:
            self.assertEqual(q["seats"], hont[q["option"]])

    def test_complete_voting_priority(self):
        v = self.create_voting_priority()
        self.create_voters(v)

        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        clear = self.store_votes_priority(v)

        self.login()  # set token
        v.tally_votes(self.token)

        tally = v.tally
        self.assertEquals(len(tally),1)
        self.assertEquals(tally[0],13542)
        self.assertEquals(tally,clear)
   
    def test_create_voting_from_api(self):
        data = {'name': 'Example'}
        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        response = mods.post('voting', params=data, response=True)
        self.assertEqual(response.status_code, 400)

        data = {
            'name': 'Example',
            'desc': 'Description example',
            'question': 'I want a ',
            'question_opt': ['cat', 'dog', 'horse']
        }

        response = self.client.post('/voting/', data, format='json')
        self.assertEqual(response.status_code, 201)

    def test_update_voting(self):
        voting = self.create_voting()

        data = {'action': 'start'}
        #response = self.client.post('/voting/{}/'.format(voting.pk), data, format='json')
        #self.assertEqual(response.status_code, 401)

        # login with user no admin
        self.login(user='noadmin')
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 403)

        # login with user admin
        self.login()
        data = {'action': 'bad'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)

        # STATUS VOTING: not started
        for action in ['stop', 'tally']:
            data = {'action': action}
            response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json(), 'Voting is not started')

        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting started')

        # STATUS VOTING: started
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting is not stopped')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting stopped')

        # STATUS VOTING: stopped
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Voting tallied')

        # STATUS VOTING: tallied
        data = {'action': 'start'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already started')

        data = {'action': 'stop'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already stopped')

        data = {'action': 'tally'}
        response = self.client.put('/voting/{}/'.format(voting.pk), data, format='json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), 'Voting already tallied')