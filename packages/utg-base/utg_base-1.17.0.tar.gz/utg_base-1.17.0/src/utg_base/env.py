import os
import typing

import dotenv
import hvac
from django.conf import settings
from environs import Env, _StrType

dotenv.load_dotenv(settings.BASE_DIR / '.env')

assert os.environ.get('VAULT_URL') is not None, "VAULT_URL not defined, please set VAULT_URL on .env file"
assert os.environ.get('VAULT_TOKEN') is not None, "VAULT_TOKEN not defined, please set VAULT_TOKEN on .env file"
assert os.environ.get('VAULT_PATH') is not None, "VAULT_PATH not defined, please set VAULT_PATH on .env file"

client = hvac.Client(
    url=os.environ.get("VAULT_URL"),
    token=os.environ.get("VAULT_TOKEN"),
    verify=False
)
if not client.is_authenticated():
    raise Exception("Vault authentication failed")

envs = client.secrets.kv.read_secret_version(
    path=os.environ.get("VAULT_PATH"),
    mount_point="utg-scada"
)['data']['data']


class VaultEnv(Env):
    def _get_value(self, env_key: _StrType, default: typing.Any) -> typing.Any:
        if env_key in os.environ:
            return os.environ.get(env_key, default)
        else:
            return envs.get(env_key, default)


env = VaultEnv()
