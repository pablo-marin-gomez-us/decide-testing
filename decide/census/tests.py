import random
from django.contrib.auth.models import User
from django.test import TestCase, Client
from rest_framework.test import APIClient
from .models import Census
from base import mods
from base.tests import BaseTestCase
from census import census_utils as censusUtils
from selenium import webdriver
from selenium.webdriver.common.by import By
from django.utils import timezone
from voting.models import Voting, Question, QuestionOption


class CensusTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.census = Census(voting_id=1, voter_id=1)
        self.census.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_check_vote_permissions(self):
        response = self.client.get('/census/{}/?voter_id={}'.format(1, 2), format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json(), 'Invalid voter')

        response = self.client.get('/census/{}/?voter_id={}'.format(1, 1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'Valid voter')

    def test_list_voting(self):
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.get('/census/?voting_id={}'.format(1), format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {'voters': [1]})

    def test_add_new_voters_conflict(self):
        data = {'voting_id': 1, 'voters': [1]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 409)

    def test_add_new_voters(self):
        data = {'voting_id': 2, 'voters': [1,2,3,4]}
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 401)

        self.login(user='noadmin')
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 403)

        self.login()
        response = self.client.post('/census/', data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(data.get('voters')), Census.objects.count() - 1)

    def test_destroy_voter(self):
        data = {'voters': [1]}
        response = self.client.delete('/census/{}/'.format(1), data, format='json')
        self.assertEqual(response.status_code, 204)
        self.assertEqual(0, Census.objects.count())

class ExportCensusTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.voter_id = User.objects.all().values()[0]['id']
        self.create_voting()
        self.census = Census(voting_id=self.v.id, voter_id=self.voter_id)
        self.census.save()
        self.user_admin = User.objects.filter(username='admin').all()[0]
        self.user_noadmin = User.objects.filter(username='noadmin').all()[0]

    def create_voting(self):
        q = Question(desc="Descripcion")
        q.save()

        opt1 = QuestionOption(question=q,option="opcion1")
        opt1.save()
        opt2 = QuestionOption(question=q,option="opcion2")
        opt2.save()

        self.v = Voting(name="Votacion", question=q)

        self.v.save()

    def tearDown(self):
        super().tearDown()
        self.census = None

    def test_census_utils(self):
        form_values = ['2','4','5']
        selected_atributes = ['id']
        voters_data = []

        census = Census.objects.filter(voting_id=1).values()
        user_atributes = censusUtils.get_user_atributes()
        data = censusUtils.get_csvtext_and_data(form_values, census)

        for value in form_values:
            atribute = str(user_atributes[int(value)][1])
            selected_atributes.append(atribute)
        self.assertEquals(selected_atributes, data[1]) # headers
        
        voter = User.objects.filter(id=self.voter_id).values()[0]
        voter_data = []
        for atribute in selected_atributes:
            voter_data.append(str(voter[atribute]))
        voters_data.append(voter_data)
        self.assertEquals(voters_data, data[2]) # atributes values

    def test_access_denied(self):
        self.client.force_login(self.user_noadmin)
        response = self.client.get('/census/export/{}/'.format(self.v.id))
        self.assertEqual(response.status_code, 401)

    def test_access_accepted(self):
        self.client.force_login(self.user_admin)
        response = self.client.get('/census/export/{}/'.format(1), format='json')
        self.assertEqual(response.status_code, 200)