from requests import Session, Response
import time
from typing import Any


class Credentials:
    base_url: str
    username: str
    password: str
    domain: str
    home_domain_id: int
    auth_token: str

    def __init__(
        self,
        base_url: str,
        username: str,
        password: str,
        domain: str,
        home_domain_id: int,
        auth_token: str = "",
    ):
        self.base_url = base_url
        self.username = username
        self.password = password
        self.domain = domain
        self.home_domain_id = home_domain_id
        self.auth_token = auth_token

    def store_auth_token(self, auth_response: dict) -> str:
        login_token = (
            auth_response.get("response", {}).get("user", {}).get("token", None)
        )

        if login_token is None:
            error_code = auth_response.get("response", {}).get("code", "Generic Error")
            error_message = auth_response.get("response", {}).get(
                "message", "Generic Error"
            )
            raise Exception(f"{error_code}: {error_message}")

        self.auth_token = login_token
        return login_token


class Connection:
    credentials: Credentials
    session: Session

    def __init__(
        self,
        credentials: Credentials,
        session: Session = Session(),
    ):
        self.credentials = credentials
        self.session = session

    def __construct_login_payload(self):
        return {
            "request": {
                "cmd": "login3",
                "username": f"{self.credentials.domain}/{self.credentials.username}",
                "password": self.credentials.password,
            }
        }

    def authenticate(self):
        response = self.session.post(
            self.credentials.base_url, json=self.__construct_login_payload()
        )
        response.raise_for_status()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {self.credentials.store_auth_token(response.json())}"
            }
        )

    def response_handler(
        self,
        http_verb: str,
        response: Response,
        cmd: str | None,
        attempt: int,
        max_retries: int,
        params: dict | None = None,
        payload: dict | None = None,
    ) -> Any:
        # RETRY ERROR HANDLING
        if response.status_code != 200 and attempt > max_retries:
            response.raise_for_status()

        # RESPONSE ERROR HANDLING
        if response.status_code == 502:
            # BAD GATEWAY - WAIT A MOMENT AND RETRY
            time.sleep(10)
            self.authenticate()

            if http_verb == "GET":
                return self.get(cmd, params, attempt=attempt + 1)
            elif http_verb == "POST":
                return self.post(cmd, params, payload, attempt=attempt + 1)
            else:
                raise Exception(f"Invalid HTTP Verb: {http_verb}")
        elif response.status_code == 429:
            # TOO MANY REQUESTS - WAIT A SPECIFIC AMOUNT OF TIME AND RETRY
            retry_after = response.headers.get("Retry-After")
            sleep_for = (
                int(retry_after) if retry_after and retry_after.isdigit() else 60
            )
            time.sleep(sleep_for)
            self.authenticate()

            if http_verb == "GET":
                return self.get(cmd, params, attempt=attempt + 1)
            elif http_verb == "POST":
                return self.post(cmd, params, payload, attempt=attempt + 1)
            else:
                raise Exception(f"Invalid HTTP Verb: {http_verb}")
        elif response.status_code != 200:
            response.raise_for_status()

        return response.json()

    def get(
        self,
        cmd: str,
        params: dict | None = None,
        *,
        attempt: int = 1,
        max_retries: int = 3,
    ):
        # DEFAULT PARAMS
        params = params or {}
        # APPEND CMD TO PARAMS
        query_params = {**params, "cmd": cmd}

        # ACTUAL CALL
        response = self.session.get(self.credentials.base_url, params=query_params)
        return self.response_handler("GET", response, cmd, attempt, max_retries, params)

    def post(
        self,
        cmd: str | None,
        params: dict | None = None,
        payload: dict | None = None,
        *,
        attempt: int = 1,
        max_retries: int = 3,
    ):
        # DEFAULT PARAMS
        params = params or {}
        payload = payload or {}
        # APPEND CMD TO PARAMS
        query_params = {**params, "cmd": cmd}

        # NEED TO DO A POST PAYLOAD WITH THE TOKEN ADDED TO THE REQUESTS OBJECT
        # ACTUAL CALL
        response = self.session.post(
            self.credentials.base_url, params=query_params, json=payload
        )
        return self.response_handler(
            "POST", response, cmd, attempt, max_retries, params, payload
        )
