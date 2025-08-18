from typing import Optional, cast
from stravalib.client import Client
from .models import StravaAccount
from server import db
import os
from stravalib.protocol import AccessInfo
from flask import url_for

STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID", "0")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET", "")

def get_strava_client(account: StravaAccount):
    client = Client(
        access_token=account.access_token,
        refresh_token=account.refresh_token,
        token_expires=account.expires_at
    )
    return client

def get_strava_account(user_id: int) -> StravaAccount | None:
    account = StravaAccount.query.filter_by(user_id=user_id).first()
    if not account:
        return None
    return cast(StravaAccount,account)

def validate_tokens(client: Client,account: StravaAccount):
    if account.access_token != client.access_token:
        account.access_token = client.access_token
        account.refresh_token = client.refresh_token
        account.expires_at = client.token_expires
        db.session.commit()

def exchange_token(code: str) -> Client:
    client = Client()
    auth_info = cast(AccessInfo,client.exchange_code_for_token(int(STRAVA_CLIENT_ID), STRAVA_CLIENT_SECRET, code))
    client.access_token = auth_info["access_token"]
    client.refresh_token = auth_info["refresh_token"]
    client.token_expires = auth_info["expires_at"]
    return client

def get_auth_url():
    client = Client()
    url = client.authorization_url(
        client_id=int(STRAVA_CLIENT_ID),
        redirect_uri=url_for("auth.auth_strava", _external=True)
    )
    return url
