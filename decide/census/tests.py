from django.contrib.auth.models import User
from voting.models import Voting
from .models import Census
from base import mods
from base.tests import BaseTestCase
from census import census_utils as censusUtils
from django.conf import settings
from django.utils import timezone
from voting.models import Voting, Question
from mixnet.models import Auth
from django.urls import reverse

from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver
from selenium.webdriver.common.by import By
from booth.tests import TestViews
import time
import os

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

class ImportCensusTestCase(BaseTestCase):

    def crear_votacion(self):
        q = Question(desc = 'test question')
        q.save()

        v = Voting(name='test voting', question=q)
        v.save()

        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.v_id = v.id
        return v.id

    def login(self, user='admin', log='qwerty'):
        data = {'username': user, 'password': log}
        response = mods.post('authentication/login', json=data, response=True)
        self.assertEqual(response.status_code, 200)
        self.token = response.json().get('token')
        self.assertTrue(self.token)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)

    def setUp(self):
        
        u2 = User(username='decide')
        u2.set_password('decidedecide')
        u2.is_superuser = True
        u2.save()
        self.admin_user = 'decide'
        self.admin_pwd = 'decidedecide'

        super().setUp()

    def tearDown(self):
        User.objects.all().delete()
        Voting.objects.all().delete()
        Census.objects.all().delete()
        super().tearDown()

    def test_page_exists(self):
        pass
        response = self.client.get('/census/manage')
        self.assertEqual(response.status_code, 200)
    
    def test_bad_input_form(self):
        pass
        data = {
            'algo':'algo'
        }
        response = self.client.post('/census/manage',data,format='json')
        self.assertEqual(response.status_code, 422)
    
    def test_format_not_supported(self):
        pass
        self.crear_votacion()
        file = open("census/testfiles/voters.txt", 'rb')
        data = {
            'votation':self.v_id,
            'user':self.admin_user,
            'password':self.admin_pwd,
            'file': file
        }
        response = self.client.post(reverse('census_manage'), data=data)
        self.assertEqual(response.status_code, 400)

    def test_good_input_form_xlsx(self):
        pass
        self.assertEqual(0,Census.objects.count()) #Inincialmente no hay censo
        ImportCensusTestCase.login(self)
        self.crear_votacion()
        file = open("census/testfiles/voters.xlsx", 'rb')
        data = {
            'votation':self.v_id,
            'user':self.admin_user,
            'password':self.admin_pwd,
            'file': file
        }
        response = self.client.post(reverse('census_manage'), data=data)
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(0,Census.objects.count())
        self.assertEqual(23,Census.objects.count()) #Hay 23 usuarios en el xlsx
        file.close()

    def test_good_input_form_csv(self):
        pass
        self.assertEqual(0,Census.objects.count()) #Inincialmente no hay censo
        ImportCensusTestCase.login(self)
        self.crear_votacion()
        file = open("census/testfiles/voters.csv", 'rb')
        data = {
            'votation':self.v_id,
            'user':self.admin_user,
            'password':self.admin_pwd,
            'file': file
        }
        response = self.client.post(reverse('census_manage'), data=data)
        self.assertEqual(response.status_code, 201)
        self.assertNotEqual(0,Census.objects.count())
        self.assertEqual(23,Census.objects.count()) #Hay 23 usuarios en el csv
        file.close()

class ImportCensusTestCaseSelenium(StaticLiveServerTestCase):
    
    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()
        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        super().setUp()  
    def tearDown(self):           
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

    def tests_import(self):
        TestViews.login_admin(self)
        TestViews.create_voting(self)
        self.driver.get(f'{self.live_server_url}/census/manage')
        self.driver.find_element(By.NAME, "votation").click()
        self.driver.find_element(By.NAME,'votation').send_keys(self.v_id)
        current_path = os.path.dirname(__file__)
        self.driver.find_element(By.NAME, "file").send_keys(current_path+'/testfiles/voters.csv')
        self.driver.find_element(By.NAME, "user").click()
        self.driver.find_element(By.NAME,'user').send_keys('admin')
        self.driver.find_element(By.NAME, "password").click()
        self.driver.find_element(By.NAME,'password').send_keys('qwerty')
        self.driver.find_element(By.ID, "submitButton").click()
        time.sleep(5)
        print(self.driver.find_element(By.CLASS_NAME,'str').text)
        self.assertTrue(self.driver.find_element(By.CLASS_NAME,'str').text =='"Votación poblada satisfactoriamente, 23 votantes añadidos"')

class ExportCensusTestCase(BaseTestCase):

    def setUp(self):
        super().setUp()
        self.voter_id = User.objects.all().values()[0]['id']
        self.census = Census(voting_id=1, voter_id=self.voter_id)
        self.census.save()

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
        self.login(user='admin')
        response = self.client.get('/census/export/{}/'.format(1), format='json')
        self.assertEqual(response.status_code, 401)

class ExportCensusTransTestCase(StaticLiveServerTestCase):

    def setUp(self):
        self.base = BaseTestCase()
        self.base.setUp()
        super().setUp()
        self.voter_id = User.objects.all().values()[0]['id']
        self.crear_votacion()
        self.census = Census(voting_id=self.v_id, voter_id=self.voter_id)
        self.census.save()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
    

    def tearDown(self):           
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

    def crear_votacion(self):
        q = Question(desc = 'test question')
        q.save()

        v = Voting(name='test voting', question=q)
        v.save()
        a, _ = Auth.objects.get_or_create(url=settings.BASEURL,
                                          defaults={'me': True, 'name': 'test auth'})
        a.save()
        v.auths.add(a)
        v.create_pubkey()
        v.start_date = timezone.now()
        v.save()

        self.v_id = v.id
        return v.id

    def login_admin(self):
        self.driver.get(f'{self.live_server_url}/admin/login/?next=/admin/')
        self.driver.find_element(By.ID, "id_username").click()
        self.driver.find_element(By.ID, "id_username").send_keys("admin")
        self.driver.find_element(By.ID, "id_password").click()
        self.driver.find_element(By.ID, "id_password").send_keys("qwerty")
        self.driver.find_element(By.CSS_SELECTOR, ".submit-row > input").click()

    def testCheckExportName(self):
        self.login_admin()
        self.driver.get(f'{self.live_server_url}/census/export/{self.v_id}')
        title = self.driver.find_element(By.TAG_NAME, 'h1').text
        title = title.split(": ")[0]
        return self.assertEqual(str(title),'Nombre de la votación')
        
