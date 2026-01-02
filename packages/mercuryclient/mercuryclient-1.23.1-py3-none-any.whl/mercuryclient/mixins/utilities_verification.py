from typing import Tuple

from mercuryclient.types.utilities_verification.enums import UtilityTypes


class UtilitiesVerificationMixin:
    """
    Mixin for verifying Utilities
    """

    def request_verify_utilities(
        self,
        provider: str,
        profile: str,
        utility_type: UtilityTypes,
        utility_number: str,
        code: str,
        **kwargs,
    ) -> str:
        api = "api/v1/utilities_verification/"

        try:
            utility_enum = UtilityTypes(utility_type)
        except ValueError:
            raise Exception(f"{utility_type} is not a valid utility_type")

        utility_type_value = utility_enum.value

        data = {
            "provider": provider,
            "profile": profile,
            "utility_type": utility_type_value,
            "utility_number": utility_number,
            "code": code,
        }

        if (
            "installation_number" in kwargs
            and kwargs["installation_number"] is not None
        ):
            data["installation_number"] = kwargs["installation_number"]

        if "mobile_number" in kwargs and kwargs["mobile_number"] is not None:
            data["mobile_number"] = kwargs["mobile_number"]

        request_id, r = self._post_json_http_request(
            api, data=data, send_request_id=True, add_bearer_token=True
        )

        if r.status_code == 201:
            return request_id

        try:
            response_json = r.json()
        except Exception:
            response_json = {}
        raise Exception(
            "Error while sending Utilities verification request. Status: {}, Response is {}".format(
                r.status_code, response_json
            )
        )

    def get_verify_utilities_result(self, request_id: str) -> Tuple[str, dict]:
        api = "api/v1/utilities_verification/"

        request_id, r = self._get_json_http_request(
            api,
            headers={"X-Mercury-Request-Id": request_id},
            send_request_id=False,
            add_bearer_token=True,
        )

        if r.status_code == 200:
            result = r.json()
            return request_id, result

        try:
            response_json = r.json()
        except Exception:
            response_json = {}
        raise Exception(
            "Error getting Utilities Verification result. Status: {}, Response is {}".format(
                r.status_code, response_json
            )
        )
