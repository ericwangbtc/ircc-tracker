import unittest

from ircc_tracker.client import (
    AuthenticationError,
    IrccClient,
    application_number,
    extract_applications,
    normalize_uci,
)


class FakeResponse:
    def __init__(self, status_code, body):
        self.status_code = status_code
        self._body = body
        self.ok = 200 <= status_code < 300

    def json(self):
        return self._body


class FakeSession:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return self.responses.pop(0)


class ClientTests(unittest.TestCase):
    def test_authenticate_and_query_details(self):
        session = FakeSession([
            FakeResponse(200, {
                "AuthenticationResult": {
                    "IdToken": "id-token",
                    "AccessToken": "access-token",
                    "RefreshToken": "refresh-token",
                    "ExpiresIn": 3600,
                }
            }),
            FakeResponse(200, {"apps": [{"appNum": "E123"}]}),
            FakeResponse(200, {"app": {"appNumber": "E123"}}),
        ])
        client = IrccClient(session=session)

        tokens = client.authenticate("12-3456-7890", "secret")
        profile = client.get_profile_summary()
        details = client.get_application_details(
            application_number="E123", uci="1234567890"
        )

        self.assertEqual(tokens.id_token, "id-token")
        self.assertEqual(profile["apps"][0]["appNum"], "E123")
        self.assertEqual(details["app"]["appNumber"], "E123")
        detail_payload = session.calls[2][1]["json"]
        self.assertEqual(detail_payload["method"], "get-application-details")
        self.assertEqual(detail_payload["uci"], "1234567890")

    def test_bad_credentials_have_safe_error(self):
        session = FakeSession([
            FakeResponse(400, {
                "__type": "NotAuthorizedException",
                "message": "Incorrect username or password.",
            })
        ])
        client = IrccClient(session=session)

        with self.assertRaisesRegex(AuthenticationError, "Incorrect UCI"):
            client.authenticate("12345678", "wrong")

    def test_extract_applications(self):
        apps = extract_applications({"apps": [{"appNum": "E1"}, "bad"]})
        self.assertEqual(apps, [{"appNum": "E1"}])
        self.assertEqual(application_number(apps[0]), "E1")

    def test_normalize_uci(self):
        self.assertEqual(normalize_uci("12-3456-7890"), "1234567890")
        with self.assertRaises(ValueError):
            normalize_uci("abc")


if __name__ == "__main__":
    unittest.main()
