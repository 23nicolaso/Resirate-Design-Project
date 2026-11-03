import ssl
from io import BytesIO
from unittest.mock import patch
from urllib.error import URLError

from django.test import Client, RequestFactory, SimpleTestCase, TestCase

from .geosearch import AddressResult, ThirdPartyServiceError, search_addresses
from .models import Building
from .views import address_suggestion, search


class GeoSearchTests(SimpleTestCase):
    @patch("buildings.geosearch.urlopen")
    def test_maps_provider_results(self, opener):
        opener.return_value = BytesIO(b'{"features":[{"properties":{"label":"120 Broadway, Manhattan","name":"120 Broadway","borough":"Manhattan","postalcode":"10271"}}]}')
        result = search_addresses("120 Broadway")[0]
        self.assertEqual(result.address, "120 Broadway")
        self.assertEqual(result.borough, "Manhattan")
        self.assertEqual(result.zip_code, "10271")
        self.assertEqual(opener.call_args.kwargs["timeout"], 5)
        context = opener.call_args.kwargs["context"]
        self.assertTrue(context.check_hostname)
        self.assertEqual(context.verify_mode, ssl.CERT_REQUIRED)

    @patch("buildings.geosearch.urlopen")
    def test_network_failure_preserves_cause(self, opener):
        opener.side_effect = URLError("private provider details")
        with self.assertRaises(ThirdPartyServiceError) as caught:
            search_addresses("Broadway")
        self.assertIs(caught.exception.__cause__, opener.side_effect)
        self.assertNotIn("private", str(caught.exception))

    @patch("buildings.geosearch.urlopen")
    def test_invalid_responses_are_translated(self, opener):
        for body in (b'not json', b'{"features":null}', b'{"features":[{}]}'):
            with self.subTest(body=body):
                opener.return_value = BytesIO(body)
                with self.assertRaises(ThirdPartyServiceError):
                    search_addresses("Broadway")

    @patch("buildings.geosearch.urlopen")
    def test_empty_query_does_not_call_provider(self, opener):
        self.assertEqual(search_addresses(" "), [])
        opener.assert_not_called()

    @patch("buildings.views.logger")
    @patch("buildings.views.Building")
    @patch("buildings.views.search_addresses")
    def test_search_displays_friendly_failure(self, lookup, building, logger):
        building.objects.filter.return_value.__getitem__.return_value = []
        lookup.side_effect = ThirdPartyServiceError("Address search is temporarily unavailable.")
        response = search(RequestFactory().get("/", {"q": "Broadway"}))
        self.assertContains(response, "Address search is temporarily unavailable.")
        logger.warning.assert_called_once()

    @patch("buildings.views.Building")
    @patch("buildings.views.search_addresses")
    def test_search_displays_city_addresses(self, lookup, building):
        from .geosearch import AddressResult
        building.objects.filter.return_value.__getitem__.return_value = []
        lookup.return_value = [AddressResult("120 Broadway, Manhattan", "120 Broadway", "Manhattan", "10271")]
        response = search(RequestFactory().get("/", {"q": "120 Broadway"}))
        self.assertContains(response, "120 Broadway, Manhattan")





class AddressEndpointTests(TestCase):
    def setUp(self):
        self.address = AddressResult("87 WHITE STREET, New York", "87 WHITE STREET", "Manhattan", "10013", "nycpad:venue:14047", "1001870")
        self.token = address_suggestion(self.address)["selection_token"]

    @patch("buildings.views.search_addresses")
    def test_suggestions_and_short_queries(self, lookup):
        lookup.return_value = [self.address]
        response = self.client.get("/api/addresses/suggestions/", {"q": "87 white"})
        self.assertEqual(response.status_code, 200)
        self.assertIn("selection_token", response.json()["suggestions"][0])
        lookup.assert_called_once_with("87 white", autocomplete=True)
        lookup.reset_mock()
        self.assertEqual(self.client.get("/api/addresses/suggestions/?q=a").json(), {"suggestions": []})
        lookup.assert_not_called()

    @patch("buildings.views.search_addresses", side_effect=ThirdPartyServiceError("Address search is temporarily unavailable."))
    @patch("buildings.views.logger")
    def test_provider_failure_returns_503(self, logger, lookup):
        self.assertEqual(self.client.get("/api/addresses/suggestions/?q=white").status_code, 503)

    def test_repeated_selection_creates_one_building(self):
        for status in (201, 200):
            response = self.client.post("/buildings/resolve/", {"selection_token": self.token})
            self.assertEqual(response.status_code, status)
            self.assertEqual(response.json()["url"], f"/buildings/{Building.objects.get().pk}/")
        self.assertEqual(Building.objects.count(), 1)

    def test_existing_building_is_reused(self):
        building = Building.objects.create(address="87 White Street", borough="Manhattan", zip_code="10013")
        response = self.client.post("/buildings/resolve/", {"selection_token": self.token}, content_type="application/json")
        self.assertEqual(response.json()["building_id"], building.pk)
        self.assertEqual(Building.objects.count(), 1)

    def test_invalid_and_expired_tokens(self):
        for payload in ({}, {"selection_token": self.token + "tampered"}, []):
            self.assertEqual(self.client.post("/buildings/resolve/", payload, content_type="application/json").status_code, 400)
        with patch("django.core.signing.time.time", return_value=1):
            expired = address_suggestion(self.address)["selection_token"]
        self.assertEqual(self.client.post("/buildings/resolve/", {"selection_token": expired}).status_code, 400)
        self.assertEqual(Building.objects.count(), 0)

    def test_methods_and_csrf(self):
        self.assertEqual(self.client.get("/buildings/resolve/").status_code, 405)
        self.assertEqual(self.client.post("/api/addresses/suggestions/").status_code, 405)
        self.assertEqual(Client(enforce_csrf_checks=True).post("/buildings/resolve/", {"selection_token": self.token}).status_code, 403)
