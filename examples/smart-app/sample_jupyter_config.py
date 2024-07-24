from oauthenticator.generic import GenericOAuthenticator
import requests

# Base url for a simulated FHIR application, by running docker compose setup from https://github.com/smart-on-fhir/smart-dev-sandbox
# Configuration in the sandbox:
# - Launch Type: Provider Standalone Launch
# - FHIR Version: R4 (most modern)
# - Providers:  [3]
fhir_base_url = "http://localhost:4013/v/r4/sim/eyJoIjoiMSIsImoiOiIxIiwiZSI6IjMifQ/fhir"
# Location where a SMART on FHIR application broadcasts configuration
smart_config_location = ".well-known/smart-configuration"
client_id = '9dbfaca0-9b85-49b6-bddd-d5eb638c2156'
client_secret = 'unguessableclientsecret'
id_scopes = ["openid", "fhirUser"]  # both are required


# Generic OAuthenticator
c.JupyterHub.authenticator_class = GenericOAuthenticator
c.GenericOAuthenticator.oauth_callback_url = 'http://localhost:8000/hub/oauth_callback'
c.GenericOAuthenticator.client_id = client_id
c.GenericOAuthenticator.client_secret = client_secret
c.GenericOAuthenticator.scope = id_scopes
c.GenericOAuthenticator.allow_all = True
c.Application.log_level = 'DEBUG'
# SMART requires an extra parameter 'aud' which corresponds with the FHIR application URL
c.GenericOAuthenticator.extra_authorize_params = {'aud': fhir_base_url}

# Fetch the config
smart_config = requests.get(f"{fhir_base_url}/{smart_config_location}").json()
c.GenericOAuthenticator.authorize_url = smart_config["authorization_endpoint"]
c.GenericOAuthenticator.token_url = smart_config["token_endpoint"]
for scope in c.GenericOAuthenticator.scope:
    if scope not in smart_config["scopes_supported"]:
        raise AttributeError("Scope {scope} not supported through SMART application")
# With the supplied scopes, auth code also grants an ID token
c.GenericOAuthenticator.userdata_from_id_token = True
# Only one field to derive a name from, and it contains (at least) slashes
c.GenericOAuthenticator.username_claim = lambda r: r['fhirUser'].replace('/', '_')
