from django.contrib.auth.models import User
from django.test.testcases import TestCase, LiveServerTestCase
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.firefox.webdriver import WebDriver
import time

class AjaxAdminTests(TestCase, LiveServerTestCase):

    @classmethod
    def setUpClass(cls):
        super(AjaxAdminTests, cls).setUpClass()
        cls.browser = WebDriver()

    @classmethod
    def tearDownClass(cls):
        super(AjaxAdminTests, cls).tearDownClass()
        cls.browser.quit()

    def setUp(self):
        list(User.objects.all())
        self.login()

    def login(self):
        self.browser.get("%s/admin/" % self.live_server_url)
        user = self.browser.find_element_by_css_selector('#id_username')
        user.send_keys("admin")
        pswd = self.browser.find_element_by_css_selector('#id_password')
        pswd.send_keys("test")
        self.click_element(selector=".submit-row>[type='submit']")

    def click_element(self, name=None, selector=None):
        element = None
        if name:
            element = self.browser.find_element_by_name(name)
        elif selector:
            element = self.browser.find_element_by_css_selector(selector)
        element.click()
        time.sleep(2)

    def assert_selected_option(self, element_id, value):
        option = self.browser.find_element_by_css_selector('#' + element_id + ' option[selected="selected"]')
        self.assertEqual(value, option.text)

    def assert_select_has_options(self, element_id, expected_ingredients):
        details = self.browser.find_element_by_css_selector('#' + element_id)
        options = details.find_elements_by_tag_name('option')
        self.assertItemsEqual(expected_ingredients, [o.text for o in options])

    def change_value_for_element(self, element_id, value):
        element = self.browser.find_element_by_css_selector('#' + element_id)
        element.send_keys(value)
        # click off of the element to trigger the change event
        self.click_element(selector='label[for="' + element_id + '"]')

    def test_main_ingredient_element_not_present_initially(self):
        self.browser.get("%s/admin/sample/meal/add/" % self.live_server_url)
        self.browser.find_element_by_css_selector('#id_food_type')
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_css_selector('#id_main_ingredient')

    def test_main_ingredient_element_shows_when_pizza_food_type_is_selected(self):
        self.browser.get("%s/admin/sample/meal/add/" % self.live_server_url)
        self.change_value_for_element('id_food_type', 'pizza')

        self.assert_select_has_options('id_main_ingredient', [u'---------', u'pepperoni', u'mushrooms', u'beef', u'anchovies'])

    def test_main_ingredient_element_shows_when_burger_food_type_is_selected(self):

        self.browser.get("%s/admin/sample/meal/add/" % self.live_server_url)
        self.change_value_for_element('id_food_type', 'burger')

        self.assert_select_has_options('id_main_ingredient', [u'---------', u'mushrooms', u'beef', u'lettuce'])

    def test_ingredient_details_is_shown_when_beef_is_selected(self):
        self.browser.get("%s/admin/sample/meal/add/" % self.live_server_url)
        self.change_value_for_element('id_food_type', 'burger')
        self.change_value_for_element('id_main_ingredient', 'beef')

        self.assert_select_has_options('id_ingredient_details', [u'---------', u'Grass Fed', u'Cardboard Fed'])

    def test_ingredient_details_is_reset_when_main_ingredient_changes(self):
        self.browser.get("%s/admin/sample/meal/add/" % self.live_server_url)
        self.change_value_for_element('id_food_type', 'burger')
        self.change_value_for_element('id_main_ingredient', 'beef')

        details = self.browser.find_element_by_css_selector('#id_ingredient_details')
        self.assertTrue(details.is_displayed())

        self.change_value_for_element('id_main_ingredient', 'lettuce')

        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_css_selector('#id_ingredient_details')

    def test_ingredient_details_change_when_main_ingredient_changes(self):
        self.browser.get("%s/admin/sample/meal/add/" % self.live_server_url)
        self.change_value_for_element('id_food_type', 'pizza')
        self.change_value_for_element('id_main_ingredient', 'beef')

        self.assert_select_has_options('id_ingredient_details', [u'---------', u'Grass Fed', u'Cardboard Fed'])

        self.change_value_for_element('id_main_ingredient', 'pepperoni')

        self.assert_select_has_options('id_ingredient_details', [u'---------', u'Grass Fed Goodness', u'Cardboard Not So Goodness'])

    def test_main_ingredient_does_not_change_when_food_type_changes_if_valid_option(self):
        self.browser.get("%s/admin/sample/meal/add/" % self.live_server_url)
        self.change_value_for_element('id_food_type', 'pizza')
        self.change_value_for_element('id_main_ingredient', 'beef')

        self.assert_selected_option('id_main_ingredient', 'beef')

        self.change_value_for_element('id_food_type', 'burger')
        self.assert_selected_option('id_main_ingredient', 'beef')

    def test_shows_dynamic_field_on_existing_instance(self):
        self.browser.get("%s/admin/sample/meal/1/" % self.live_server_url)
        self.assert_selected_option('id_main_ingredient', 'anchovies')

    def test_sets_ingredient_details_when_available(self):
        self.browser.get("%s/admin/sample/meal/add/" % self.live_server_url)

        self.change_value_for_element('id_food_type', 'burger')
        self.change_value_for_element('id_main_ingredient', 'beef')
        self.change_value_for_element('id_ingredient_details', 'Grass Fed')

        self.click_element(name='_continue')

        self.assert_selected_option('id_ingredient_details', 'Grass Fed')

    def test_allows_changing_dynamic_field_on_existing_instance(self):
        self.browser.get("%s/admin/sample/meal/add/" % self.live_server_url)

        self.change_value_for_element('id_food_type', 'burger')

        # create new meal
        main_ingredient = self.browser.find_element_by_css_selector('#id_main_ingredient')
        main_ingredient.send_keys('mushrooms')
        self.click_element(name='_continue')

        # change main_ingredient for new meal
        main_ingredient2 = self.browser.find_element_by_css_selector('#id_main_ingredient')
        main_ingredient2.send_keys('lettuce')
        self.click_element(name='_continue')

        # make sure there are no errors
        with self.assertRaises(NoSuchElementException):
            self.browser.find_element_by_css_selector(".errors")

        # make sure our new main_ingredient was saved
        self.assert_selected_option('id_main_ingredient', 'lettuce')

        #delete our meal when we're done
        self.click_element(selector='.deletelink')
        self.click_element(selector='[type="submit"]')

    def test_gives_field_required_error_when_dynamic_field_not_chosen(self):
        self.browser.get("%s/admin/sample/meal/add/" % self.live_server_url)
        food_type = self.browser.find_element_by_css_selector('#id_food_type')
        food_type.send_keys('burger')

        self.click_element(name='_save')

        error_item = self.browser.find_element_by_css_selector(".errors.field-main_ingredient li")
        self.assertEqual("This field is required.", error_item.text)
