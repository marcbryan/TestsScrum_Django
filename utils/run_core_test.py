# script per testejar ràpid sobre el live server
# abans d'executar-ho posar en marxa el server executant al terminal:
# ./manage.py runserver
# Executar script amb:
# ./manage.py shell < utils/run_core_test.py



from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException

from core.tests import BaseCoreTest, CoreTest
from borsApp.tests import BorsaTests

# Utilitzem el BaseCoreTest com a llibreria
class LocalTest(CoreTest):
	pass


class LocalTest2(BorsaTests):
	pass

# build
tests = LocalTest2()
tests.selenium = WebDriver()
tests.live_server_url = "http://localhost:8000"

# test
#tests.test_superadmin()
#tests.test_1_crea_empreses()
tests.backend_login("admin1","enric123")
tests.backend_titol_alumne("alumne11","web","terradas")

