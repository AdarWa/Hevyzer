from typing import cast
from stravalib.client import Client
from .models import Config, StravaAccess
import os
from auth.models import config
from stravalib.protocol import AccessInfo
from flask import url_for

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID", "0")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET", "")
STRAVA_VERIFY_TOKEN = os.getenv("STRAVA_VERIFY_TOKEN", "VERIFY_TOKEN")

def get_strava_client(access: StravaAccess):
    global config
    config = Config.load()
    client = Client(
        access_token=access.access_token,
        refresh_token=access.refresh_token,
        token_expires=access.token_expires
    )
    return client


def validate_tokens(client: Client,access: StravaAccess):
    assert client.access_token
    assert client.refresh_token
    assert client.token_expires
    global config
    config = Config.load()
    if access.access_token != client.access_token:
        access.access_token = client.access_token
        access.refresh_token = client.refresh_token
        access.token_expires = client.token_expires
        config.save()
        

def exchange_token(code: str) -> Client:
    client = Client()
    auth_info = cast(AccessInfo,client.exchange_code_for_token(int(STRAVA_CLIENT_ID), STRAVA_CLIENT_SECRET, code))
    client.access_token = auth_info["access_token"]
    client.refresh_token = auth_info["refresh_token"]
    client.token_expires = auth_info["expires_at"]    
    return client

def create_subscription(client: Client):
    client.create_subscription(int(STRAVA_CLIENT_ID), STRAVA_CLIENT_SECRET, url_for("auth.webhook_callback", _external=True, _scheme="https"), STRAVA_VERIFY_TOKEN)

def get_auth_url():
    client = Client()
    url = client.authorization_url(
        client_id=int(STRAVA_CLIENT_ID),
        redirect_uri=url_for("auth.auth_strava", _external=True, _scheme="https"),
        scope=["read","activity:read_all"]
    )
    return url
