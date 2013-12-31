from functools import wraps
from django.contrib.auth.models import User
from django.test.testcases import TestCase, LiveServerTestCase
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait


def retry(func):

    @wraps(func)
    def retry_test(self, countdown=30, *args, **kwargs):
        try:
            result = func(self, *args, **kwargs)
        except Exception:
            if countdown <= 0:
                raise

            self.tearDown()
            self._post_teardown()
            self._pre_setup()
            self.setUp()
            result = retry_test(self, countdown=countdown - 1, *args, **kwargs)

        return result

    return retry_test


class Retry(type):

    def __new__(cls, name, bases, attrs):
        for test in filter(lambda i: i.startswith('test_'), attrs):
            attrs[test] = retry(attrs[test])

        return super(Retry, cls).__new__(cls, name, bases, attrs)


class AjaxAdminTests(TestCase, LiveServerTestCase):
    __metaclass__ = Retry

    @classmethod
    def setUpClass(cls):
        super(AjaxAdminTests, cls).setUpClass()
        caps = webdriver.DesiredCapabilities.FIREFOX
        caps['platform'] = 'Windows XP'
        caps['version'] = '25'
        caps['name'] = 'django-admin-ext'

        cls.driver = webdriver.Remote(
            desired_capabilities=caps,
            command_executor="http://imtappswebadmin:841f95a0-c21d-4cb4-a7f4-288ed88a4b18@ondemand.saucelabs.com:80/wd/hub"
        )
        cls.driver.implicitly_wait(30)

    @classmethod
    def tearDownClass(cls):
        print "Link to your job: https://saucelabs.com/jobs/%s" % cls.driver.session_id
        cls.driver.quit()

    def setUp(self):
        list(User.objects.all())
        self.login()

    def _get_element(self, context, method, argument):
        return getattr(context, method)(argument)

    def find_element(self, context=None, name=None, selector=None, tag=None):
        argument = name or selector or tag
        context = context or self.driver
        if name:
            method = 'find_element_by_name'
        elif selector:
            method = 'find_element_by_css_selector'
        elif tag:
            method = 'find_elements_by_tag_name'
        else:
            raise Exception("No Selector")

        WebDriverWait(context, 5, 1).until(lambda d: self._get_element(d, method, argument))
        return self._get_element(context, method, argument)

    def click_element(self, **kwargs):
        element = self.find_element(**kwargs)
        element.click()

    def login(self):
        self.driver.get("%s/admin/" % self.live_server_url)
        user = self.find_element(selector='#id_username')
        user.send_keys("admin")
        pswd = self.find_element(selector='#id_password')
        pswd.send_keys("test")
        self.click_element(selector=".submit-row>[type='submit']")

    def assert_selected_option(self, element_id, value):
        option = self.find_element(selector='#' + element_id + ' option[selected="selected"]')
        self.assertEqual(value, option.text)

    def assert_select_has_options(self, element_id, expected_ingredients):
        details = self.find_element(selector='#' + element_id)
        options = self.find_element(context=details, tag='option')
        self.assertItemsEqual(expected_ingredients, [o.text for o in options])

    def change_value_for_element(self, element_id, value):
        element = self.find_element(selector='#' + element_id)
        element.send_keys(value)
        # click off of the element to trigger the change event
        self.click_element(selector='label[for="' + element_id + '"]')

    def test_main_ingredient_element_not_present_initially(self):
        self.driver.get("%s/admin/sample/meal/add/" % self.live_server_url)

        self.find_element(selector='#id_food_type')
        with self.assertRaises(TimeoutException):
            self.find_element(selector='#id_main_ingredient')

    def test_main_ingredient_element_shows_when_pizza_food_type_is_selected(self):
        self.driver.get("%s/admin/sample/meal/add/" % self.live_server_url)
        self.change_value_for_element('id_food_type', 'pizza')

        self.assert_select_has_options('id_main_ingredient', [u'---------', u'pepperoni', u'mushrooms', u'beef', u'anchovies'])

    def test_main_ingredient_element_shows_when_burger_food_type_is_selected(self):
        self.driver.get("%s/admin/sample/meal/add/" % self.live_server_url)
        self.change_value_for_element('id_food_type', 'burger')

        self.assert_select_has_options('id_main_ingredient', [u'---------', u'mushrooms', u'beef', u'lettuce'])

    def test_ingredient_details_is_shown_when_beef_is_selected(self):
        self.driver.get("%s/admin/sample/meal/add/" % self.live_server_url)
        self.change_value_for_element('id_food_type', 'burger')
        self.change_value_for_element('id_main_ingredient', 'beef')

        self.assert_select_has_options('id_ingredient_details', [u'---------', u'Grass Fed', u'Cardboard Fed'])

    def test_ingredient_details_is_reset_when_main_ingredient_changes(self):
        self.driver.get("%s/admin/sample/meal/add/" % self.live_server_url)
        self.change_value_for_element('id_food_type', 'burger')
        self.change_value_for_element('id_main_ingredient', 'beef')

        details = self.find_element(selector='#id_ingredient_details')
        self.assertTrue(details.is_displayed())

        self.change_value_for_element('id_main_ingredient', 'lettuce')

        try:
            self.find_element(selector='#id_ingredient_details')
        except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
            pass
        else:
            self.fail("Expected not to find #id_ingredient_details")

    def test_ingredient_details_change_when_main_ingredient_changes(self):
        self.driver.get("%s/admin/sample/meal/add/" % self.live_server_url)
        self.change_value_for_element('id_food_type', 'pizza')
        self.change_value_for_element('id_main_ingredient', 'beef')

        self.assert_select_has_options('id_ingredient_details', [u'---------', u'Grass Fed', u'Cardboard Fed'])

        self.change_value_for_element('id_main_ingredient', 'pepperoni')

        self.assert_select_has_options('id_ingredient_details', [u'---------', u'Grass Fed Goodness', u'Cardboard Not So Goodness'])

    def test_main_ingredient_does_not_change_when_food_type_changes_if_valid_option(self):
        self.driver.get("%s/admin/sample/meal/add/" % self.live_server_url)
        self.change_value_for_element('id_food_type', 'pizza')
        self.change_value_for_element('id_main_ingredient', 'beef')

        self.assert_selected_option('id_main_ingredient', 'beef')

        self.change_value_for_element('id_food_type', 'burger')
        self.assert_selected_option('id_main_ingredient', 'beef')

    def test_shows_dynamic_field_on_existing_instance(self):
        self.driver.get("%s/admin/sample/meal/1/" % self.live_server_url)
        self.assert_selected_option('id_main_ingredient', 'anchovies')

    def test_sets_ingredient_details_when_available(self):
        self.driver.get("%s/admin/sample/meal/add/" % self.live_server_url)

        self.change_value_for_element('id_food_type', 'burger')
        self.change_value_for_element('id_main_ingredient', 'beef')
        self.change_value_for_element('id_ingredient_details', 'Grass Fed')

        self.click_element(name='_continue')

        self.assert_selected_option('id_ingredient_details', 'Grass Fed')

    def test_allows_changing_dynamic_field_on_existing_instance(self):
        self.driver.get("%s/admin/sample/meal/add/" % self.live_server_url)

        self.change_value_for_element('id_food_type', 'burger')

        # create new meal
        main_ingredient = self.find_element(selector='#id_main_ingredient')
        main_ingredient.send_keys('mushrooms')
        self.click_element(name='_continue')

        # change main_ingredient for new meal
        main_ingredient2 = self.find_element(selector='#id_main_ingredient')
        main_ingredient2.send_keys('lettuce')
        self.click_element(name='_continue')

        # make sure there are no errors
        with self.assertRaises(TimeoutException):
            self.find_element(selector=".errors")

        # make sure our new main_ingredient was saved
        self.assert_selected_option('id_main_ingredient', 'lettuce')

        #delete our meal when we're done
        self.click_element(selector='.deletelink')
        self.click_element(selector='[type="submit"]')

    def test_gives_field_required_error_when_dynamic_field_not_chosen(self):
        self.driver.get("%s/admin/sample/meal/add/" % self.live_server_url)
        food_type = self.find_element(selector='#id_food_type')
        food_type.send_keys('burger')

        self.click_element(name='_save')

        error_item = self.find_element(selector=".errors.field-main_ingredient li")
        self.assertEqual("This field is required.", error_item.text)
