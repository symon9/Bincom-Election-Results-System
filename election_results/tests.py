from django.test import TestCase, Client
from django.urls import reverse
from .models import PollingUnit, LGA, Ward, AnnouncedPuResults, Party

class ElectionResultsTests(TestCase):
    def setUp(self):
        self.client = Client()
        # Create dummy data
        self.lga = LGA.objects.create(
            lga_id=1, lga_name="Test LGA", state_id=25, entered_by_user="Test", user_ip_address="127.0.0.1"
        )
        self.ward = Ward.objects.create(
            ward_id=1, ward_name="Test Ward", lga_id=1, entered_by_user="Test", user_ip_address="127.0.0.1"
        )
        self.pu = PollingUnit.objects.create(
            polling_unit_id=1, ward_id=1, lga_id=1, polling_unit_name="Test PU", 
            polling_unit_number="PU001", entered_by_user="Test", user_ip_address="127.0.0.1"
        )
        self.party = Party.objects.create(partyid="PDP", partyname="PDP")
        self.result = AnnouncedPuResults.objects.create(
            polling_unit_uniqueid=str(self.pu.uniqueid), party_abbreviation="PDP", party_score=100,
            entered_by_user="Test", date_entered="2023-01-01 12:00:00", user_ip_address="127.0.0.1"
        )

    def test_index(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)

    def test_polling_unit_result(self):
        response = self.client.get(reverse('polling_unit_result'))
        self.assertEqual(response.status_code, 200)
        
        # Test with selection
        response = self.client.get(reverse('polling_unit_result'), {'pu_uniqueid': self.pu.uniqueid})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test PU")
        self.assertContains(response, "100")

    def test_lga_summed_result(self):
        response = self.client.get(reverse('lga_summed_result'))
        self.assertEqual(response.status_code, 200)
        
        # Test with selection
        response = self.client.get(reverse('lga_summed_result'), {'lga_id': self.lga.lga_id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test LGA")
        self.assertContains(response, "100") # Sum should be 100

    def test_add_result(self):
        response = self.client.get(reverse('add_polling_unit_result'))
        self.assertEqual(response.status_code, 200)
        
        # Test post
        response = self.client.post(reverse('add_polling_unit_result'), {
            'polling_unit_uniqueid': self.pu.uniqueid,
            'party_PDP': 50,
            'entered_by_user': 'Tester'
        })
        self.assertEqual(response.status_code, 302) # Redirect
        
        # Verify added
        count = AnnouncedPuResults.objects.filter(polling_unit_uniqueid=str(self.pu.uniqueid), party_score=50).count()
        self.assertEqual(count, 1)

    def test_api_wards(self):
        response = self.client.get(reverse('get_wards', args=[self.lga.lga_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Ward")

    def test_api_polling_units(self):
        response = self.client.get(reverse('get_polling_units', args=[self.ward.ward_id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test PU")
