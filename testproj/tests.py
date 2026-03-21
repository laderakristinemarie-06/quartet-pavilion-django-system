from django.test import TestCase
from django.test import LiveServerTestCase

class TestProjTests(TestCase):
    def test_home_page(self):
        response = self.client.get('')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Welcome to the Quartet Pavilion!')

    def test_events_page(self):
        response = self.client.get('/events')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Upcoming Events')

    def test_overview_page(self):
        response = self.client.get('/overview')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Quartet Pavilion Overview')
