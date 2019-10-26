from unittest.mock import Mock
import pytest
import secrets
import logging
import pathlib

from tests.integration.libs.integration_test_config import IntegrationTestConfig


from starfish import Ocean
from starfish.agent import (
    RemoteAgent,
    SquidAgent,
)

INTEGRATION_PATH = pathlib.Path.cwd() / 'tests' / 'integration'
CONFIG_FILE_PATH = INTEGRATION_PATH / 'config.ini'

@pytest.fixture(scope="module")
def ocean():
    integrationTestConfig = IntegrationTestConfig(CONFIG_FILE_PATH)
    ocean = Ocean(
        keeper_url=integrationTestConfig.keeper_url,
        contracts_path=integrationTestConfig.contracts_path,
        gas_limit=integrationTestConfig.gas_limit,
        log_level=logging.WARNING
    )

    return ocean

@pytest.fixture(scope="module")
def config():
    integrationTestConfig = IntegrationTestConfig(CONFIG_FILE_PATH)
    return integrationTestConfig

@pytest.fixture(scope="module")
def remote_agent(ocean):
    integrationTestConfig = IntegrationTestConfig(CONFIG_FILE_PATH)

    ddo_options = None
    if integrationTestConfig.koi_url:
        ddo_options = {
            'invoke': f'{integrationTestConfig.koi_url}/api/v1',
        }
    ddo = RemoteAgent.generate_ddo(integrationTestConfig.remote_agent_url, ddo_options)
    options = {
        'url': integrationTestConfig.remote_agent_url,
        'username': integrationTestConfig.remote_agent_username,
        'password': integrationTestConfig.remote_agent_password,
    }
    return RemoteAgent(ocean, did=ddo.did, ddo=ddo, options=options)

@pytest.fixture(scope="module")
def squid_agent(ocean):
    integrationTestConfig = IntegrationTestConfig(CONFIG_FILE_PATH)
    return SquidAgent(ocean, integrationTestConfig.squid_config)

@pytest.fixture(scope='module')
def publisher_account(ocean, config):
    return ocean.load_account(config.publisher_account['address'], config.publisher_account['password'], config.publisher_account['keyfile'])


@pytest.fixture(scope='module')
def purchaser_account(ocean, config):
    return ocean.load_account(config.purchaser_account['address'], config.purchaser_account['password'], config.purchaser_account['keyfile'])


@pytest.fixture(scope='module')
def agent_account(ocean, config):
    return ocean.load_account(config.agent_account['address'], config.agent_account['password'], config.agent_account['keyfile'])