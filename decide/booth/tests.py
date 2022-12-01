from django.test import TestCase
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from voting.models import Voting, Question
from django.utils import timezone
from mixnet.models import Auth
from django.conf import settings

from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys

from base.tests import BaseTestCase


class BoothTranslationTestCase(StaticLiveServerTestCase):

    def setUp(self):
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

        super().setUp()    
        self.base = BaseTestCase()
        self.base.setUp()

        options = webdriver.ChromeOptions()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        

    def tearDown(self):           
        super().tearDown()
        self.driver.quit()
        self.base.tearDown()

    def testCheckIDTransES(self):
        self.driver.get(f'{self.live_server_url}/booth/'+str(self.v_id))
        title = self.driver.find_elements(By.TAG_NAME, 'h1')[1].text
        title = title.split(": ")[0]
        print("'"+ title + "'")     
        return self.assertEqual(str(title),'ID de la votación')

    def testCheckNombreTransES(self):
        self.driver.get(f'{self.live_server_url}/booth/'+str(self.v_id))
        sub_title = self.driver.find_element(By.TAG_NAME, 'h3').text
        sub_title = sub_title.split(": ")[0]      
        return self.assertEqual(str(sub_title),'Nombre de la votación')

        