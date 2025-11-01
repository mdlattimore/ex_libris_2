from django.test import TestCase

from django.test import RequestFactory, TestCase
from unittest.mock import patch
from catalog.views import isbn_lookup
from catalog.services.book_lookup import perform_isbn_lookup

class ISBNLookupViewTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    @patch("catalog.views.isbn_lookup.perform_isbn_lookup")
    def test_lookup_returns_result(self, mock_lookup):
        mock_lookup.return_value = {"result": {"title": "The Silmarillion"}}

        request = self.factory.post("/isbn-lookup/", data={"isbn":
            "9780063396197"})
        response = isbn_lookup(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"The Silmarillion", response.content)
        mock_lookup.assert_called_once_with("9780063396197")
