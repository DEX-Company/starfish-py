from unittest.mock import Mock
import pytest
import secrets
import logging
import pathlib
import requests
from web3 import Web3, HTTPProvider

from starfish.agent import RemoteAgent
from starfish.network.ddo import DDO
from starfish.network.ethereum import (
    EthereumAccount,
    EthereumNetwork
)

from starfish.network.convex import (
    ConvexAccount,
    ConvexNetwork
)


INTEGRATION_PATH = pathlib.Path.cwd() / 'tests' / 'integration'

logging.getLogger('web3').setLevel(logging.INFO)
logging.getLogger('urllib3').setLevel(logging.INFO)


@pytest.fixture(scope='module')
def ethereum_network(config):
    network = EthereumNetwork(config['ethereum']['network']['url'])
    return network

@pytest.fixture(scope='module')
def convex_network(config):
    network = ConvexNetwork(config['convex']['network']['url'])
    return network


@pytest.fixture(scope='module')
def remote_agent_surfer(config):
    ddo_options = None
    local_agent = config['agents']['surfer']
    ddo = DDO.create(local_agent['url'], [
        'meta',
        'storage',
        'invoke',
        'market',
        'trust',
        'auth'
    ])
    authentication = {
        'username': local_agent['username'],
        'password': local_agent['password'],
    }
    return RemoteAgent(ddo, authentication)

@pytest.fixture(scope='module')
def remote_agent_invokable(config):
    ddo_options = None
    local_agent = config['agents']['invokable']
    ddo = DDO.create(local_agent['url'])
    authentication = {
        'username': local_agent['username'],
        'password': local_agent['password'],
    }
    return RemoteAgent(ddo, authentication)



@pytest.fixture(scope='module')
def ethereum_accounts(config):
    result = []
    # load in the test accounts
    account_1 = config['ethereum']['accounts']['account1']
    account_2 = config['ethereum']['accounts']['account2']
    result = [
        EthereumAccount.import_from_file(account_1['keyfile'], account_1['password']),
        EthereumAccount.import_from_file(account_2['keyfile'], account_2['password']),
    ]
    return result

@pytest.fixture(scope='module')
def convex_accounts(config):
    result = []
    # load in the test accounts
    account_1 = config['convex']['accounts']['account1']
    result = [
        ConvexAccount.import_from_file(account_1['keyfile'], account_1['password']),
        ConvexAccount.create(),
    ]
    return result




@pytest.fixture(scope='module')
def invokable_list(config):

    local_agent = config['agents']['surfer']

    url = f'{local_agent["url"]}/api/v1/admin/import-demo?id=operations'
    username = local_agent['username']
    password = local_agent['password']
    response = requests.post(url, auth=(username, password), headers={'accept':'application/json'})
    result = response.json()
    return result.get('invokables')
