import unittest

from main import FindPhoneNumber


class PhonePatternTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.service = FindPhoneNumber()
        super().setUpClass()

    def test_phone_number_regular_pattern(self):
        result = self.service.get_phone_numbers_from_text(' 79261234567 ')
        self.assertEqual(result, {'79261234567'})

        result = self.service.get_phone_numbers_from_text(' +7 926 123 45 67 ')
        self.assertEqual(result, {'79261234567'})

        result = self.service.get_phone_numbers_from_text(' 8(926)123-45-67 ')
        self.assertEqual(result, {'89261234567'})

        result = self.service.get_phone_numbers_from_text(' 123-45-67 ')
        self.assertEqual(result, {'1234567'})

        result = self.service.get_phone_numbers_from_text(' 9261234567 ')
        self.assertEqual(result, {'9261234567'})

        result = self.service.get_phone_numbers_from_text(' 79261234567 ')
        self.assertEqual(result, {'79261234567'})

        result = self.service.get_phone_numbers_from_text(' (495)1234567 ')
        self.assertEqual(result, {'4951234567'})

        result = self.service.get_phone_numbers_from_text(' 89261234567 ')
        self.assertEqual(result, {'89261234567'})

        result = self.service.get_phone_numbers_from_text(' 8-926-123-45-67 ')
        self.assertEqual(result, {'89261234567'})

        result = self.service.get_phone_numbers_from_text(' 8 927 1234 234 ')
        self.assertEqual(result, {'89271234234'})

        result = self.service.get_phone_numbers_from_text(' 8 927 12 12 888 ')
        self.assertEqual(result, {'89271212888'})

        result = self.service.get_phone_numbers_from_text(' 8 927 12 555 12 ')
        self.assertEqual(result, {'89271255512'})

        result = self.service.get_phone_numbers_from_text(' 8 927 123 8 123 ')
        self.assertEqual(result, {'89271238123'})

    def test_get_phone_number_from_texts(self):
        result = self.service.get_phone_numbers_from_texts([' +79261234567 '])
        self.assertEqual(result, {('8', '926', '1234567')})

        result = self.service.get_phone_numbers_from_texts([' 9261234567 '])
        self.assertEqual(result, {('8', '926', '1234567')})

        result = self.service.get_phone_numbers_from_texts([' 926123456 '])
        self.assertEqual(result, set())

        result = self.service.get_phone_numbers_from_texts([' 8-926-123-45-67 '])
        self.assertEqual(result, {('8', '926', '1234567')})

        result = self.service.get_phone_numbers_from_texts([' 123-45-67 '])
        self.assertEqual(result, {('8', '', '1234567')})

        result = self.service.get_phone_numbers_from_texts([' 8', '      '])
        self.assertEqual(result, set())

    def test_delete_not_unique_phone_number(self):
        result = self.service._delete_not_unique_phone_number(
            {('8', '925', '1234567'), ('8', '925', '1234567')}
        )
        self.assertCountEqual(result, ['89251234567'])

        result = self.service._delete_not_unique_phone_number(
            {('8', '925', '1234567'), ('8', '925', '1234567'), ('8', '', '1234564')}
        )
        self.assertCountEqual(result, ['89251234567', '1234564'])

        result = self.service._delete_not_unique_phone_number(
            {('8', '925', '1234567'), ('8', '925', '1234566'), ('8', '432', '1234564')}
        )
        self.assertCountEqual(result, ['89251234567', '89251234566', '84321234564'])
