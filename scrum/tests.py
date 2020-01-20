from django.test import TestCase
from django.db.utils import IntegrityError
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException
from core.models import User

# Create your tests here.

from core.tests import BaseCoreTest
from scrum.models import *


class ScrumTest(StaticLiveServerTestCase):
    serialized_rollback = True
    fixtures = ['testdb.json', 'projectes.json', 'equips.json',]
    loged = False
    username = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = WebDriver()
        cls.selenium.implicitly_wait(5)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def ves_al_menu_principal(self):
        self.selenium.find_element_by_xpath('//a[@href="/admin/"]').click()

    def backend_login(self,usuari,contrasenya):
        self.selenium.get('%s%s' % (self.live_server_url, '/admin/login/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(usuari)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(contrasenya)
        self.selenium.find_element_by_xpath('//input[@value="Iniciar sessió"]').click()
        try:
            boto_logout = self.selenium.find_element_by_xpath('//a[text()="Finalitzar sessió"]')
        except NoSuchElementException as e:
            raise Exception("ERROR en login de l'usuari: "+usuari)
        self.loged = True
        self.username = usuari

    def test_6_crea_projecte(self):
        self.backend_login("profe11","profe123")
        self.crea_equip("Team 1")

    def crea_projecte(self, nom):
        self.ves_al_menu_principal()
        self.selenium.find_element_by_xpath('//a[@href="/admin/scrum/projecte/add/"]').click()
        self.selenium.find_element_by_name('nom').send_keys(nom)
        # accedir dins iframe direcció
        self.selenium.switch_to_frame("id_descripcio_ifr")
        self.selenium.find_element_by_xpath('//body').send_keys("Descripció projecte 1")
        # tornar al main frame
        self.selenium.switch_to_default_content()

    def crea_equip(self, nom):
        self.ves_al_menu_principal()
        self.selenium.find_element_by_xpath('//a[@href="/admin/scrum/equip/add/"]').click()
        self.selenium.find_element_by_name('nom').send_keys(nom)
        # accedir dins iframe direcció
        self.selenium.switch_to_frame("id_descripcio_ifr")
        self.selenium.find_element_by_xpath('//body').send_keys("Descripció equip 1")
        # tornar al main frame
        self.selenium.switch_to_default_content()
        #select2 projecte
        self.selenium.find_element_by_xpath('//span[@id="select2-id_projecte-container"]').click()
        self.selenium.find_element_by_xpath('//li[text()="Vota!"]').click()
        # afegir membres
        self.selenium.find_element_by_xpath('//option[text()="admin1"]').click()
        self.selenium.find_element_by_id('id_membres_add_link').click()
        # submit
        self.selenium.find_element_by_xpath('//input[@value="Desar"]').click()
        # check
        self.selenium.find_element_by_xpath('//li[@class="success"]')
