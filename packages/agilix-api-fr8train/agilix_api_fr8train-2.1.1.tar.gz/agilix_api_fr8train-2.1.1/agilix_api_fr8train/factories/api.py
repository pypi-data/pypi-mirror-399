from dotenv import load_dotenv
from agilix_api_fr8train.models.connection import Connection, Credentials
import os
import requests


def build_credentials() -> Credentials:
    load_dotenv(override=True)

    base_url = os.getenv("AGILIX_BASE_URL")
    username = os.getenv("AGILIX_USERNAME")
    password = os.getenv("AGILIX_PASSWORD")
    domain = os.getenv("AGILIX_DOMAIN")
    home_domain_id = int(os.getenv("AGILIX_HOME_DOMAIN_ID"))

    return Credentials(
        base_url=base_url,
        username=username,
        password=password,
        domain=domain,
        home_domain_id=home_domain_id,
    )


def build_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {"Content-Type": "application/json", "Accept": "application/json"}
    )

    return session


def build_api_connection() -> Connection:
    conn = Connection(credentials=build_credentials(), session=build_session())
    conn.authenticate()

    return conn
