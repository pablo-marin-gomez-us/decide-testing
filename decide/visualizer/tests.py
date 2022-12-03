from voting.models import Voting, Question
from django.contrib.staticfiles.testing import StaticLiveServerTestCase

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from base.tests import BaseTestCase


class VisualizerNavigationTest(StaticLiveServerTestCase):

    def setUp(self):
        #Load base test functionality for decide
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

    def test_simpleVisualizer(self):
        q = Question(desc = 'test question')
        q.save()

        v = Voting(name='test voting', question=q)
        v.save()

        response = self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}')
        vstate = self.driver.find_element(By.TAG_NAME,'h2').text
        self.assertEqual(vstate,'Votación no comenzada')
    
    def test_simpleCorrectLogin(self):
        self.driver.get(f'{self.live_server_url}/admin')
        self.driver.find_element(By.ID,'id_username').send_keys('admin')
        self.driver.find_element(By.ID,'id_password').send_keys('qwerty',Keys.ENTER)

        self.assertTrue(len(self.driver.find_elements(By.ID,'user-tools'))==1)

    def test_simpleWrongLogin(self):
        self.driver.get(f'{self.live_server_url}/admin')
        self.driver.find_element(By.ID,'id_username').send_keys('WRONG')
        self.driver.find_element(By.ID,'id_password').send_keys('WRONG')
        self.driver.find_element(By.ID,'login-form').submit()



        self.assertTrue(len(self.driver.find_elements(By.CLASS_NAME,'errornote'))==1)

    def test_graphs_title_exist(self):

        q = Question(desc = 'test question')
        q.save()

        v = Voting(name='test voting', question=q)
        v.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}')
        title_text = self.driver.find_element(By.ID,'graphs_title').text
        self.assertEqual(title_text,'Gráficas de la votación:')
    
    def test_graph_title_1_exist(self):

        q = Question(desc = 'test question')
        q.save()

        v = Voting(name='test voting', question=q)
        v.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}')
        title_text = self.driver.find_element(By.ID,'graph_title_1').text
        self.assertEqual(title_text,'Gráfica de votos')

    def test_graph_title_2_exist(self):

        q = Question(desc = 'test question')
        q.save()

        v = Voting(name='test voting', question=q)
        v.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}')
        title_text = self.driver.find_element(By.ID,'graph_title_2').text
        self.assertEqual(title_text,'Gráfica de escaños')
        
    def test_graph_title_3_exist(self):

        q = Question(desc = 'test question')
        q.save()

        v = Voting(name='test voting', question=q)
        v.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}')
        title_text = self.driver.find_element(By.ID,'graph_title_3').text
        self.assertEqual(title_text,'Gráfica de porcentaje de representación')

    def test_graph_canvas_1_exist(self):

        q = Question(desc = 'test question')
        q.save()

        v = Voting(name='test voting', question=q)
        v.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}')
        canvas_is_displayed = self.driver.find_element(By.ID,'Graph1').is_displayed()
        self.assertTrue(canvas_is_displayed)

    def test_graph_canvas_2_exist(self):

        q = Question(desc = 'test question')
        q.save()

        v = Voting(name='test voting', question=q)
        v.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}')
        canvas_is_displayed = self.driver.find_element(By.ID,'Graph2').is_displayed()
        self.assertTrue(canvas_is_displayed)

    def test_graph_canvas_3_exist(self):

        q = Question(desc = 'test question')
        q.save()

        v = Voting(name='test voting', question=q)
        v.save()

        self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}')
        canvas_is_displayed = self.driver.find_element(By.ID,'Graph3').is_displayed()
        self.assertTrue(canvas_is_displayed)