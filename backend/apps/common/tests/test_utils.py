from django.test import SimpleTestCase

from apps.common.utils import generate_random_string


class UtilsTest(SimpleTestCase):
    def test_random_string_length(self):
        token = generate_random_string(32)

        self.assertEqual(len(token), 32)

    def test_random_string_type(self):
        token = generate_random_string()

        self.assertIsInstance(token, str)