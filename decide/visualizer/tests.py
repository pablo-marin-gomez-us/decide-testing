from voting.models import Voting, Question
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.utils import timezone

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from mixnet.models import Auth
from django.conf import settings
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


class VotingVisualizerTestCase(StaticLiveServerTestCase):

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
        
    def test_noStartVoting_visualizer(self):
        q = Question(desc='test question 1')
        q.save()
        v = Voting(name='test voting 1', question=q, desc='test voting 1')
        v.save()
        
        response =self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        vState= self.driver.find_element(By.TAG_NAME,"h2").text
        self.assertTrue(vState=="Votación no comenzada")
        
        vDesc= self.driver.find_element(By.TAG_NAME,"h3").text
        textoDesc="Descripción de la votación: {}".format(v.desc)
        self.assertTrue(vDesc==textoDesc)
    
    def test_startVoting_visualizer(self):
        q = Question(desc='test question 2')
        q.save()
        date = timezone.now()
        v = Voting(name='test voting 2', question=q, desc='test voting 2',start_date=date)
        v.save()
        
        response =self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        vState= self.driver.find_element(By.TAG_NAME,"h2").text
        self.assertTrue(vState=="Votación en curso")
        
        vDesc= self.driver.find_element(By.TAG_NAME,"h3").text
        textoDesc="Descripción de la votación: {}".format(v.desc)
        self.assertTrue(vDesc==textoDesc)
        
        vDate= self.driver.find_element(By.CLASS_NAME,"inicio").text
        textoFechaInicio="Fecha de inicio de la votación: {}".format(v.start_date.strftime("%d/%m/%Y, %H:%M:%S"))
        self.assertTrue(vDate==textoFechaInicio)

    def test_finishVoting_visualizer(self):
        q = Question(desc='test question 3')
        q.save()
        date = timezone.now()
        v = Voting(name='test voting 3', question=q, desc='test voting 3', start_date=date, end_date=date)
        v.save()
        
        response =self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        vDesc= self.driver.find_element(By.TAG_NAME,"h3").text
        textoDesc="Descripción de la votación: {}".format(v.desc)
        self.assertTrue(vDesc==textoDesc)
        
        vStartDate= self.driver.find_element(By.CLASS_NAME,"inicio").text
        textoFechaInicio="Fecha de inicio de la votación: {}".format(v.start_date.strftime("%d/%m/%Y, %H:%M:%S"))
        self.assertTrue(vStartDate==textoFechaInicio)
        
        vEndDate= self.driver.find_element(By.CLASS_NAME,"fin").text
        textoFechaFin="Fecha de fin de la votación: {}".format(v.end_date.strftime("%d/%m/%Y, %H:%M:%S"))
        self.assertTrue(vEndDate==textoFechaFin)

    def test_postProcVoting_noSeats_visualizer(self):
        q = Question(desc='test question 4')
        q.save()
        date = timezone.now()
        v = Voting(name='test voting 4', question=q, desc='test voting 4', start_date=date, end_date=date)
        v.save()

        response =self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        vDesc= self.driver.find_element(By.TAG_NAME,"h3").text
        textoDesc="Descripción de la votación: {}".format(v.desc)
        
        self.assertTrue(vDesc==textoDesc)
        vStartDate= self.driver.find_element(By.CLASS_NAME,"inicio").text
        textoFechaInicio="Fecha de inicio de la votación: {}".format(v.start_date.strftime("%d/%m/%Y, %H:%M:%S"))
        self.assertTrue(vStartDate==textoFechaInicio)
        
        vEndDate= self.driver.find_element(By.CLASS_NAME,"fin").text
        textoFechaFin="Fecha de fin de la votación: {}".format(v.end_date.strftime("%d/%m/%Y, %H:%M:%S"))
        self.assertTrue(vEndDate==textoFechaFin)

        tipoResultado = self.driver.find_element(By.XPATH,"//table/thead/tr/th[2]").text
        print(tipoResultado)
        self.assertTrue(tipoResultado=="Puntuación")
    
    def test_postProcVoting_seats_visualizer(self):
        q = Question(desc='test question 5')
        q.save()
        date = timezone.now()
        v = Voting(name='test voting 5', question=q, desc='test voting 5', seats=5, min_percentage_representation=10, start_date=date, end_date=date)
        v.save()
        
        response =self.driver.get(f'{self.live_server_url}/visualizer/{v.pk}/')
        vDesc= self.driver.find_element(By.TAG_NAME,"h3").text
        textoDesc="Descripción de la votación: {}".format(v.desc)
        
        self.assertTrue(vDesc==textoDesc)
        vStartDate= self.driver.find_element(By.CLASS_NAME,"inicio").text
        textoFechaInicio="Fecha de inicio de la votación: {}".format(v.start_date.strftime("%d/%m/%Y, %H:%M:%S"))
        self.assertTrue(vStartDate==textoFechaInicio)
        
        vEndDate= self.driver.find_element(By.CLASS_NAME,"fin").text
        textoFechaFin="Fecha de fin de la votación: {}".format(v.end_date.strftime("%d/%m/%Y, %H:%M:%S"))
        self.assertTrue(vEndDate==textoFechaFin)

        tipoResultado = self.driver.find_element(By.XPATH,"//table/thead/tr/th[2]").text
        self.assertTrue(tipoResultado=="Escaños")

        minPercentage = self.driver.find_element(By.CLASS_NAME,"minPercentage").text
        textoMinPercentage="Porcentaje mínimo para tener representación: {}% de los votos totales".format(v.min_percentage_representation)
        self.assertTrue(minPercentage==textoMinPercentage)


class VotingVisualizerTransalationTestCase(StaticLiveServerTestCase):
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

    def testCheckIDTransES(self):
        self.crear_votacion()
        self.driver.get(f'{self.live_server_url}/visualizer/'+str(self.v_id))
        ID_text= self.driver.find_elements(By.TAG_NAME, 'h1')[1].text
        ID_text = ID_text.split(":")[0]
        return self.assertEqual(str(ID_text),'ID de la votación')
    