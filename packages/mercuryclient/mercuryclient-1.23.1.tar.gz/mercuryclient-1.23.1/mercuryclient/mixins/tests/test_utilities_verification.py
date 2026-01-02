from unittest import TestCase, mock

from mercuryclient.api import MercuryApi


class UtilitiesVerificationMixinTest(TestCase):
    def setUp(self):
        self.client = MercuryApi(
            {
                "username": "username",
                "password": "password",
                "url": "https://mercury-dev.esthenos.in",
            }
        )

        self.post_api_mock = mock.patch(
            "mercuryclient.api.MercuryApi._post_json_http_request"
        ).start()
        self.addCleanup(self.post_api_mock.stop)

        self.get_api_mock = mock.patch(
            "mercuryclient.api.MercuryApi._get_json_http_request"
        ).start()
        self.addCleanup(self.get_api_mock.stop)

    def test_wrong_utility_type_raises_exception(self):
        # Using an invalid string should trigger the ValueError inside the mixin
        with self.assertRaises(Exception) as exc:
            self.client.request_verify_utilities(
                provider="surepass",
                profile="some_profile",
                utility_type="SOMETHING",  # invalid
                utility_number="1234567890",
                code="BS",
            )

        self.assertEqual(str(exc.exception), "SOMETHING is not a valid utility_type")
        self.post_api_mock.assert_not_called()

    def test_request_utilities_minimal_payload(self):
        # Happy path: 201 returns request_id
        mock_response = mock.MagicMock()
        mock_response.status_code = 201
        self.post_api_mock.return_value = ("random_req_id", mock_response)

        request_id = self.client.request_verify_utilities(
            provider="surepass",
            profile="some_profile",
            utility_type="ELECTRICITY_BILL",  # must match actual UtilityTypes value in codebase
            utility_number="KA1234567",
            code="BS",
        )
        self.assertEqual(request_id, "random_req_id")

        self.post_api_mock.assert_called_with(
            "api/v1/utilities_verification/",
            data={
                "provider": "surepass",
                "profile": "some_profile",
                "utility_type": "ELECTRICITY_BILL",
                "utility_number": "KA1234567",
                "code": "BS",
            },
            send_request_id=True,
            add_bearer_token=True,
        )

    def test_request_utilities_with_optional_fields(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 201
        self.post_api_mock.return_value = ("random_req_id", mock_response)

        self.client.request_verify_utilities(
            provider="signzy",
            profile="some_profile",
            utility_type="ELECTRICITY_BILL",
            utility_number="KA1234567",
            code="BS",
            installation_number="IN98765",
            mobile_number="9876543210",
        )

        self.post_api_mock.assert_called_with(
            "api/v1/utilities_verification/",
            data={
                "provider": "signzy",
                "profile": "some_profile",
                "utility_type": "ELECTRICITY_BILL",
                "utility_number": "KA1234567",
                "code": "BS",
                "installation_number": "IN98765",
                "mobile_number": "9876543210",
            },
            send_request_id=True,
            add_bearer_token=True,
        )

    def test_request_utilities_skips_none_optionals(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 201
        self.post_api_mock.return_value = ("random_req_id", mock_response)

        self.client.request_verify_utilities(
            provider="signzy",
            profile="some_profile",
            utility_type="ELECTRICITY_BILL",
            utility_number="KA1234567",
            code="BS",
            installation_number=None,  # should be omitted
            # mobile_number omitted entirely
        )

        # Inspect the actual call to ensure optional None/omitted keys aren't present
        args, kwargs = self.post_api_mock.call_args
        self.assertEqual(args[0], "api/v1/utilities_verification/")
        payload = kwargs["data"]
        self.assertNotIn("installation_number", payload)
        self.assertNotIn("mobile_number", payload)

        # also sanity check core fields
        self.assertEqual(
            payload,
            {
                "provider": "signzy",
                "profile": "some_profile",
                "utility_type": "ELECTRICITY_BILL",
                "utility_number": "KA1234567",
                "code": "BS",
            },
        )

    def test_request_exception_raised_if_status_code_error_json(self):
        # Non-201 triggers exception; JSON body is present
        mock_response = mock.MagicMock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "bad request"}
        self.post_api_mock.return_value = ("random_req_id", mock_response)

        with self.assertRaises(Exception) as exc:
            self.client.request_verify_utilities(
                provider="surepass",
                profile="some_profile",
                utility_type="ELECTRICITY_BILL",
                utility_number="KA1234567",
                code="BS",
            )
        self.assertIn(
            "Error while sending Utilities verification request", str(exc.exception)
        )

    def test_request_exception_raised_if_status_code_error_non_json(self):
        # Non-201 with non-JSON response path (r.json raises)
        mock_response = mock.MagicMock()
        mock_response.status_code = 500
        mock_response.json.side_effect = Exception("not json")  # forces except branch
        self.post_api_mock.return_value = ("random_req_id", mock_response)

        with self.assertRaises(Exception) as exc:
            self.client.request_verify_utilities(
                provider="surepass",
                profile="some_profile",
                utility_type="ELECTRICITY_BILL",
                utility_number="KA1234567",
                code="BS",
            )
        self.assertIn(
            "Error while sending Utilities verification request", str(exc.exception)
        )

    def test_get_result_sends_header_and_parses_success(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "status": "SUCCESS",
            "data": {"verified": True},
        }
        self.get_api_mock.return_value = ("random_req_id", mock_response)

        req_id, result = self.client.get_verify_utilities_result("random_req_id")
        self.assertEqual(req_id, "random_req_id")
        self.assertEqual(result["status"], "SUCCESS")
        self.assertTrue(result["data"]["verified"])

        self.get_api_mock.assert_called_with(
            "api/v1/utilities_verification/",
            headers={"X-Mercury-Request-Id": "random_req_id"},
            send_request_id=False,
            add_bearer_token=True,
        )

    def test_get_result_raises_on_error_status_json(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"detail": "Not found"}
        self.get_api_mock.return_value = ("random_req_id", mock_response)

        with self.assertRaises(Exception) as exc:
            self.client.get_verify_utilities_result("random_req_id")
        self.assertIn("Error getting Utilities Verification result", str(exc.exception))

    def test_get_result_raises_on_error_status_non_json(self):
        mock_response = mock.MagicMock()
        mock_response.status_code = 401
        mock_response.json.side_effect = Exception("not json")
        self.get_api_mock.return_value = ("random_req_id", mock_response)

        with self.assertRaises(Exception) as exc:
            self.client.get_verify_utilities_result("random_req_id")
        self.assertIn("Error getting Utilities Verification result", str(exc.exception))
