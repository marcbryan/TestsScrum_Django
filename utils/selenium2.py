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

    # aqui va la "chicha"
    def crea_empresa(self,nom):
        self.ves_al_menu_principal()
        # afegim empresa
        self.selenium.find_element_by_xpath('//a[@href="/admin/borsApp/empresa/add/"]').click()
        self.selenium.find_element_by_name('nom').send_keys(nom)
        # accedir dins iframe direcció
        self.selenium.switch_to_frame("id_direccio_ifr")
        self.selenium.find_element_by_xpath('//body').send_keys("c. Tal, 1")
        # tornar al main frame
        self.selenium.switch_to_default_content()
        self.selenium.find_element_by_name('poblacio').send_keys("Cornellà")
        self.selenium.find_element_by_name('cp').send_keys("08940")
        self.selenium.find_element_by_name('telefon').send_keys("931112233")
        nom2 = nom.replace(' ','_')
        self.selenium.find_element_by_name('email').send_keys("info@"+nom2+".com")
        self.selenium.find_element_by_xpath('//input[@value="Desar"]').click()
        # check
        self.selenium.find_element_by_xpath('//li[@class="success"]')

    def ajusta_usuari_empresa(self,usuari,contrasenya):
        # se suposa que estem logats com a admin_centre
        self.ves_al_menu_principal()
        # menu usuaris
        self.selenium.find_element_by_xpath('//a[text()="Usuaris"]').click()
        # accedim a l'usuari de l'empresa acabada de crear
        # el nom de l'usuari és igual al de l'empresa, al menys pels tests
        self.selenium.find_element_by_xpath('//a[text()="'+usuari+'"]').click()
        # anem a canvi de contasenya
        self.selenium.find_element_by_xpath('//a[@href="../password/"]').click()
        self.selenium.find_element_by_name('password1').send_keys(contrasenya)
        self.selenium.find_element_by_name('password2').send_keys(contrasenya)

        self.selenium.find_element_by_xpath('//input[@value="Canviar contrasenya"]').click()
        # comprovem usuari creat OK
        # TODO: millorar test (comprovar no errors/warnings)
        #self.selenium.find_element_by_xpath('//li[@class="success" and contains(text(),"fou afegit amb èxit")]')
        self.selenium.find_element_by_xpath('//li[@class="success"]')

    def crea_oferta_caducada(self):
        self.ves_al_menu_principal()
        # menu ofertes
        self.selenium.find_element_by_xpath('//a[@href="/admin/borsApp/oferta/add/"]').click()
        # omplim form
        self.selenium.find_element_by_name('inici_0').clear()
        self.selenium.find_element_by_name('inici_1').clear()
        self.selenium.find_element_by_name('final_0').clear()
        self.selenium.find_element_by_name('final_1').clear()
        self.selenium.find_element_by_name('inici_0').send_keys("01/01/2019")
        self.selenium.find_element_by_name('inici_1').send_keys("10:30:00")
        self.selenium.find_element_by_name('final_0').send_keys("10/02/2019")
        self.selenium.find_element_by_name('final_1').send_keys("10:30:00")
        self.selenium.find_element_by_name('titol').send_keys("oferta test caducada 1")
        # select2 empresa (FK)
        self.selenium.find_element_by_xpath('//span[@id="select2-id_empresa-container"]').click()
        self.selenium.find_element_by_xpath('//li[text()="'+self.username+'"]').click()
        # select2 cicles (m2m)
        self.selenium.find_element_by_xpath('//div[@class="form-row field-cicles"]').click()
        self.selenium.find_element_by_xpath('//input[@class="select2-search__field"]').send_keys("web\n")
        # direccio té el RichTextField amb un iframe pel mig
        # accedir dins iframe direcció
        self.selenium.switch_to_frame("id_descripcio_ifr")
        self.selenium.find_element_by_xpath('//body').send_keys("oferta test caducada.\nbla bla...")
        # tornar al main frame
        self.selenium.switch_to_default_content()
        # submit
        self.selenium.find_element_by_xpath('//input[@value="Desar"]').click()
        # comprovem oferta creada OK
        self.selenium.find_element_by_xpath('//li[@class="success"]')

    def veu_oferta_caducada1(self):
        self.ves_al_menu_principal()
        self.selenium.find_element_by_xpath('//a[text()="Ofertes"]').click()
        self.selenium.find_element_by_xpath('//a[text()="oferta test caducada 1"]').click()

    def no_veu_oferta_caducada1(self):
        self.ves_al_menu_principal()
        try:
            self.selenium.find_element_by_xpath('//a[text()="Ofertes"]').click()
            self.selenium.find_element_by_xpath('//a[text()="oferta test caducada 1"]').click()
            raise Exception("ERROR: l'usuari no autoritzat '%s' pot veure les ofertes de l'empresa 1"%(self.username,))
        except NoSuchElementException as e:
            # si no el troba, esta OK
            pass
        except Exception as e:
            raise e

# tests
tests = Tests()

# creem empresa11 (admin1)
tests.backend_login("admin1","enric123")
tests.crea_empresa("empresa11")
tests.ajusta_usuari_empresa("empresa11","enric123")
tests.backend_logout()
# creem empresa21 (admin2)
tests.backend_login("admin2","enric123")
tests.crea_empresa("empresa21")
tests.ajusta_usuari_empresa("empresa21","enric123")
tests.backend_logout()


# empresa1
tests.backend_login("empresa11","enric123")
tests.crea_oferta_caducada()
tests.veu_oferta_caducada1()
tests.backend_logout()
# admin2
tests.backend_login("admin2","enric123")
tests.no_veu_oferta_caducada1()
tests.backend_logout()
# empresa2
tests.backend_login("empresa21","enric123")
tests.no_veu_oferta_caducada1()
tests.backend_logout()
tests.selenium.close()
# alumne21
tests.backend_login("alumne21","enric123")
tests.no_veu_oferta_caducada1()
tests.backend_logout()

