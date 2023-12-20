import requests
import urllib
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
import webbrowser
from contextlib import contextmanager
import os, sys
from pprint import pprint

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        return

    def do_GET(self):
        print("Got GET request!")
        self.send_response(200)
        self.end_headers()
        print("Parsing query...")
        query = urlparse(self.path).query
        print("Query parsed!")
        params = parse_qs(query)
        print("Query parameters parsed!")
        self.server.code = params['code'][0]
        self.server.stop = True

class StoppableHTTPServer(HTTPServer):
    def __init__(self, *args, **kw):
        self.stop = False
        self.code = None
        super().__init__(*args, **kw)

    def serve_forever(self):
        while not self.stop:
            self.handle_request()

class Token:
    def __init__(self, config) -> None:
        # Define the server's port
        self.port = 4000
        self.redirect_host = "localhost"
        self.scope = 'channel:manage:broadcast channel:read:charity channel:edit:commercial channel:read:editors channel:manage:extensions channel:read:goals channel:read:guest_star channel:manage:guest_star channel:read:hype_train channel:manage:moderators channel:read:polls channel:manage:polls channel:read:predictions channel:manage:predictions channel:manage:raids channel:read:redemptions channel:manage:redemptions channel:manage:schedule channel:read:stream_key channel:read:subscriptions channel:manage:videos channel:read:vips channel:manage:vips moderation:read moderator:manage:announcements moderator:manage:automod moderator:read:automod_settings moderator:manage:automod_settings moderator:manage:banned_users moderator:read:blocked_terms moderator:manage:blocked_terms moderator:manage:chat_messages moderator:read:chat_settings moderator:manage:chat_settings moderator:read:chatters moderator:read:followers moderator:read:guest_star moderator:manage:guest_star moderator:read:shield_mode moderator:manage:shield_mode moderator:read:shoutouts moderator:manage:shoutouts channel:moderate chat:edit chat:read whispers:read whispers:edit'
        self.client_id = config["twitch_client_id"]
        self.client_secret = config["twitch_client_secret"]
        self.username = config["channel"]

        code = self.authorize()
        self.access_token = self.get_access_token(code)
        self.client_id = self.get_user_id()

    def authorize(self):
        # Define the URL, headers, and parameters for the initial API call
        url1 = 'https://id.twitch.tv/oauth2/authorize'
        redirect_uri = f"http://{self.redirect_host}:{self.port}"
        params1 = {
            'client_id': self.client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'channel:manage:broadcast channel:read:charity channel:edit:commercial channel:read:editors channel:manage:extensions channel:read:goals channel:read:guest_star channel:manage:guest_star channel:read:hype_train channel:manage:moderators channel:read:polls channel:manage:polls channel:read:predictions channel:manage:predictions channel:manage:raids channel:read:redemptions channel:manage:redemptions channel:manage:schedule channel:read:stream_key channel:read:subscriptions channel:manage:videos channel:read:vips channel:manage:vips moderation:read moderator:manage:announcements moderator:manage:automod moderator:read:automod_settings moderator:manage:automod_settings moderator:manage:banned_users moderator:read:blocked_terms moderator:manage:blocked_terms moderator:manage:chat_messages moderator:read:chat_settings moderator:manage:chat_settings moderator:read:chatters moderator:read:followers moderator:read:guest_star moderator:manage:guest_star moderator:read:shield_mode moderator:manage:shield_mode moderator:read:shoutouts moderator:manage:shoutouts channel:moderate chat:edit chat:read whispers:read whispers:edit',
            'state': 'c3ab8aa609ea11e793ae92361f002671'
        }
        headers1 = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }

        # Open URL in default web browser
        print("Opening URL in default web browser...")
        webbrowser.open(f"{url1}?{urllib.parse.urlencode(params1)}")

        # Start the server#
        print("Starting web server...")
        with StoppableHTTPServer(("", self.port), Handler) as httpd:
            httpd.serve_forever()

        # Extract the 'code' from the response
        code = httpd.code

        return code

    def get_access_token(self, code):
        url = 'https://id.twitch.tv/oauth2/token'
        params = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': 'https://localhost'
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        response = requests.post(url, headers=headers, data=urllib.parse.urlencode(params))
        return response.json()['access_token']

    def get_user_id(self):
        url = 'https://api.twitch.tv/helix/users'
        headers = {
            'Client-ID': self.client_id,
            'Authorization': f'Bearer {self.access_token}',
        }
        params = {
            'login': self.username,
        }
        response = requests.get(url, headers=headers, params=params)
        data = response.json()
        return data['data'][0]['id']