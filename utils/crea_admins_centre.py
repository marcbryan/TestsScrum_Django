# script per testejar ràpid sobre el live server
# abans d'executar-ho posar en marxa el server executant al terminal:
# ./manage.py runserver

from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException

from selenium.webdriver.support.ui import Select

class Tests():
    loged = False
    username = None
    selenium = None

    def __init__(self):
        # crea driver
        self.selenium = WebDriver()
        self.selenium.implicitly_wait(3)

    def backend_login(self,usuari,contrasenya):
        # accedeix a URL
        self.selenium.get('%s%s' % ("http://localhost:8000", '/admin/login/'))
        username_input = self.selenium.find_element_by_name("username")
        username_input.send_keys(usuari)
        password_input = self.selenium.find_element_by_name("password")
        password_input.send_keys(contrasenya)
        self.selenium.find_element_by_xpath('//input[@value="Iniciar sessió"]').click()
        try:
            boto_logout = self.selenium.find_element_by_xpath('//a[text()="Finalitzar sessió"]')
        except NoSuchElementException as e:
            raise Exception("ERROR en login de l'usuari: "+usuari)
        self.logat = True
        self.username = usuari

    def backend_logout(self):
        self.selenium.find_element_by_xpath('//a[text()="Finalitzar sessió"]').click()

    def ves_al_menu_principal(self):
        # anar a menu principal
        self.selenium.find_element_by_xpath('//a[@href="/admin/"]').click()

    def crea_usuari(self,usuari,contrasenya):
        # tornem a menu principal
        self.ves_al_menu_principal()
        self.selenium.find_element_by_xpath('//a[@href="/admin/core/user/add/"]').click()
        usuari_input = self.selenium.find_element_by_name('username')
        usuari_input.send_keys(usuari)
        p1_input = self.selenium.find_element_by_name('password1')
        p1_input.send_keys(contrasenya)
        p2_input = self.selenium.find_element_by_name('password2')
        p2_input.send_keys(contrasenya)
        self.selenium.find_element_by_xpath('//input[@value="Desar"]').click()
        # comprovem usuari creat OK
        # TODO: millorar test (comprovar no errors/warnings)
        #self.selenium.find_element_by_xpath('//li[@class="success" and contains(text(),"fou afegit amb èxit")]')
        self.selenium.find_element_by_xpath('//li[@class="success"]')

    def crea_admin_centre(self,usuari,contrasenya):
        # afegim permisos admin centre
        self.crea_usuari(usuari,contrasenya)
        # afegim grup
        self.selenium.find_element_by_xpath('//option[text()="admin_borsa"]').click()
        self.selenium.find_element_by_id('id_groups_add_link').click()
        # guardem
        self.selenium.find_element_by_xpath('//input[@value="Desar"]').click()
        # comprovem usuari creat OK
        self.selenium.find_element_by_xpath('//li[@class="success"]')

    def assigna_admin_a_centre(self,usuari,centre):
        self.ves_al_menu_principal()
        # anar a menu centres per assignar l'usuari al centre
        self.selenium.find_element_by_xpath('//a[@href="/admin/core/centre/"]').click()
        # cerca "centre"
        self.selenium.find_element_by_id("searchbar").send_keys(centre)
        self.selenium.find_element_by_xpath("//input[@value='Cerca']").click()
        # cliquem resultat
        self.selenium.find_element_by_xpath("//div[@class='results']//tr[@class='row1']//a").click()
        # assignem admin a l'usuari
        self.selenium.find_element_by_xpath('//option[text()="'+usuari+'"]').click()
        self.selenium.find_element_by_id('id_admins_add_link').click()
        # guardem
        self.selenium.find_element_by_xpath('//input[@value="Desar"]').click()
        self.selenium.find_element_by_xpath('//li[@class="success"]')


# tests
tests = Tests()

# creem admins centre
tests.backend_login("admin","admin123")
tests.crea_admin_centre("admin1","enric123")
tests.crea_admin_centre("admin2","enric123")
tests.assigna_admin_a_centre("admin1","terradas")
tests.assigna_admin_a_centre("admin2","montilivi")

#tests.backend_logout()

