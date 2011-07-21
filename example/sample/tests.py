
import os
import shlex
import subprocess
import sys
import time

from django.utils import unittest

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException

class SeleniumTestCase(unittest.TestCase):
    test_fixtures = None

    scheme = "http"
    host = "localhost"
    port = "8000"

    @classmethod
    def base_url(cls):
        url = "%s://%s" % (cls.scheme, cls.host)
        if cls.port:
            url += ":%s" % cls.port
        return unicode(url)

    @classmethod
    def setUpClass(cls):
        cls.start_test_server()

        profile = webdriver.FirefoxProfile()
        cls.browser = webdriver.Firefox(firefox_profile=profile)
        cls.browser.implicitly_wait(1) # browser will wait up to 1 second before failing because element is not found
        cls.browser.get("%s/admin" % cls.base_url())

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.p.terminate()

    @classmethod
    def login(cls):
        user = cls.browser.find_element_by_css_selector('#id_username')
        user.send_keys("admin")
        pswd = cls.browser.find_element_by_css_selector('#id_password')
        pswd.send_keys("test")
        submit_button = cls.browser.find_element_by_css_selector(".submit-row>[type='submit']")
        submit_button.click()

    @classmethod
    def start_test_server(cls):
        # try to find the settings file and assume manage.py is in the
        # same directory.
        settings_module = os.environ['DJANGO_SETTINGS_MODULE']
        root_dir = os.path.abspath(os.path.join(os.path.dirname(sys.modules.get(settings_module).__file__)))

        fixtures = ''
        if cls.test_fixtures:
            fixtures = ' '.join(f for f in cls.test_fixtures)
        cmd = "%s/manage.py testserver %s" % (root_dir, fixtures)
        cls.p = subprocess.Popen(shlex.split(cmd))

        time.sleep(3) # wait for the test server to start...

    @classmethod
    def terminate_test_server(cls):
        cls.p.terminate()

class AjaxAdminTests(SeleniumTestCase):
    
    @classmethod
    def setUpClass(cls):
        super(AjaxAdminTests, cls).setUpClass()
        cls.login()

    def test_django_test_server_is_running(self):
        """
        Before running these tests, in a separate terminal window run
        ./manage.py testserver
        """
        try:
            element = self.browser.find_element_by_css_selector('#site-name')
        except NoSuchElementException:
            self.fail("""
                django's test server does not appear to be running,
                please start it and run the tests again.
            """)
        self.assertEqual("Django administration", element.text)

    def test_main_ingredient_element_not_present_initially(self):
        self.browser.get("http://localhost:8000/admin/sample/meal/add/")
        self.browser.find_element_by_css_selector('#id_food_type')
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_css_selector('#id_main_ingredient')

    def test_main_ingredient_element_shows_when_pizza_food_type_is_selected(self):
        self.browser.get("http://localhost:8000/admin/sample/meal/add/")
        food_type = self.browser.find_element_by_css_selector('#id_food_type')
        food_type.send_keys('pizza')

        # click off of the food_type drop down to trigger the change event
        self.browser.find_element_by_css_selector('label[for="id_food_type"]').click()

        main_ingredient = self.browser.find_element_by_css_selector('#id_main_ingredient')
        options = main_ingredient.find_elements_by_tag_name('option')

        expected_ingredients = [u'---------', u'pepperoni', u'mushrooms', u'beef', u'anchovies']
        self.assertItemsEqual(expected_ingredients, [o.text for o in options])

    def test_main_ingredient_element_shows_when_burger_food_type_is_selected(self):
        self.browser.get("http://localhost:8000/admin/sample/meal/add/")
        food_type = self.browser.find_element_by_css_selector('#id_food_type')
        food_type.send_keys('burger')

        # click off of the food_type drop down to trigger the change event
        self.browser.find_element_by_css_selector('label[for="id_food_type"]').click()

        main_ingredient = self.browser.find_element_by_css_selector('#id_main_ingredient')
        options = main_ingredient.find_elements_by_tag_name('option')

        expected_ingredients = [u'---------', u'mushrooms', u'beef', u'lettuce']
        self.assertItemsEqual(expected_ingredients, [o.text for o in options])

    def test_shows_dynamic_field_on_existing_instance(self):
        self.browser.get("http://localhost:8000/admin/sample/meal/1/")
        option = self.browser.find_element_by_css_selector('#id_main_ingredient option[selected="selected"]')
        self.assertEqual('anchovies', option.text)

    def test_allows_changing_dynamic_field_on_existing_instance(self):
        self.browser.get("http://localhost:8000/admin/sample/meal/add/")

        food_type = self.browser.find_element_by_css_selector('#id_food_type')
        food_type.send_keys('burger')

        # click off of the food_type drop down to trigger the change event
        self.browser.find_element_by_css_selector('label[for="id_food_type"]').click()

        # create new meal
        main_ingredient = self.browser.find_element_by_css_selector('#id_main_ingredient')
        main_ingredient.send_keys('beef')
        self.browser.find_element_by_name('_continue').click()

        # change main_ingredient for new meal
        main_ingredient2 = self.browser.find_element_by_css_selector('#id_main_ingredient')
        main_ingredient2.send_keys('lettuce')
        self.browser.find_element_by_name('_continue').click()

        # make sure there are no errors
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_css_selector(".errors")

        # make sure our new main_ingredient was saved
        option = self.browser.find_element_by_css_selector('#id_main_ingredient option[selected="selected"]')
        self.assertEqual('lettuce', option.text)

        #delete our meal when we're done
        self.browser.find_element_by_css_selector('.deletelink').click()
        self.browser.find_element_by_css_selector('[type="submit"]').click()

    def test_gives_field_required_error_when_dynamic_field_not_chosen(self):
        self.browser.get("http://localhost:8000/admin/sample/meal/add/")
        food_type = self.browser.find_element_by_css_selector('#id_food_type')
        food_type.send_keys('burger')

        self.browser.find_element_by_name('_save').click()

        error_item = self.browser.find_element_by_css_selector(".errors.main_ingredient li")
        self.assertEqual("This field is required.", error_item.text)