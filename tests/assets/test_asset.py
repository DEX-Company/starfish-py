"""
    Test ocean class

"""

import pathlib
import json
import logging
import time
import secrets
from web3 import Web3

from ocean_py.ocean import Ocean
from ocean_py.logging import setup_logging
from ocean_py import logger

from squid_py.service_agreement.service_factory import ServiceDescriptor
from squid_py.utils.utilities import generate_new_id
from squid_py import ACCESS_SERVICE_TEMPLATE_ID
from squid_py.keeper.event_listener import EventListener

from squid_py.brizo.brizo import Brizo
from tests.helpers.brizo_mock import BrizoMock


setup_logging(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)

CONFIG_PARMS = {
    'contracts_path': 'artifacts',
    'keeper_url': 'http://localhost:8545',
    'secret_store_url': 'http://localhost:12001',
    'parity_url': 'http://localhost:8545',
    'parity_address': '0x00bd138abd70e2f00903268f3db08f2d25677c9e',
    'parity_password': 'node0',
}


METADATA_SAMPLE_PATH = pathlib.Path.cwd() / 'tests' / 'resources' / 'metadata' / 'sample_metadata1.json'

def _read_metadata():
    # load in the sample metadata
    assert METADATA_SAMPLE_PATH.exists(), "{} does not exist!".format(METADATA_SAMPLE_PATH)
    metadata = None
    with open(METADATA_SAMPLE_PATH, 'r') as file_handle:
        metadata = json.load(file_handle)
    
    return metadata

def _register_asset(ocean):

    assert ocean
    assert ocean.accounts


    # test node has the account #0 unlocked
    publisher_account = ocean.accounts[list(ocean.accounts)[0]]
    publisher_account.password = ocean.config.parity_password
    publisher_account.unlock()
    publisher_account.request_tokens(10)

    metadata = _read_metadata()
    assert metadata
    
    asset = ocean.register_asset(metadata, account=publisher_account)
    assert asset
    assert asset.did
    return asset, publisher_account

def _log_event(event_name):
    def _process_event(event):
        logging.debug(f'Received event {event_name}: {event}')
    return _process_event

def test_asset():
    # create an ocean object
    ocean = Ocean(CONFIG_PARMS)
    assert ocean
    assert ocean.accounts

    asset, publisher_account = _register_asset(ocean)
    assert asset
    assert publisher_account
    
    asset_did = asset.did
    # start to test getting the asset from storage
    asset = ocean.get_asset(asset_did)
    assert asset
    assert asset.did == asset_did


    purchase_account = ocean.accounts[list(ocean.accounts)[1]]
    logging.info(f'purchase_account {purchase_account.balance}')

    # TODO: have this password saved in config or even better a wallet.
    purchase_account.password = 'secret'
    purchase_account.unlock()

    purchase_account.request_tokens(10)

    time.sleep(10)
    logging.info(f'purchase_account {purchase_account.balance}')


    # since Brizo does not work outside in the barge , we need to start
    # brizo as a dumy client to do the brizo work...
    Brizo.set_http_client(BrizoMock(ocean.squid, publisher_account))

    # test purchase an asset
    purchase_asset = asset.purchase(purchase_account)
    assert purchase_asset

    _filter = {'agreementId': Web3.toBytes(hexstr=purchase_asset.purchase_id)}

    EventListener('ServiceExecutionAgreement', 'AgreementInitialized', filters=_filter).listen_once(
        _log_event('AgreementInitialized'),
        20,
        blocking=True
    )
    EventListener('AccessConditions', 'AccessGranted', filters=_filter).listen_once(
        _log_event('AccessGranted'),
        20,
        blocking=True
    )
    event = EventListener('ServiceExecutionAgreement', 'AgreementFulfilled', filters=_filter).listen_once(
        _log_event('AgreementFulfilled'),
        20,
        blocking=True
    )

    # This test does not work with the current barge
    """
    assert purchase_asset.is_purchased
    assert not asset.is_purchased
    assert purchase_asset.is_purchase_valid(purchase_account)

    purchase_asset.consume(purchase_account)
    """
    metadata = _read_metadata()
    assert metadata
    
#    print(ocean.search_purchased_assets('Office', purchase_account))
    assert(len(ocean.search_registered_assets('Office')) > 1)


def test_asset_search():
    
    ocean = Ocean(CONFIG_PARMS)
    assert ocean
    assert ocean.accounts

    asset, publisher_account = _register_asset(ocean)
    assert asset
    
    metadata = _read_metadata()
    assert metadata

    # randomly choose a word from the description field
    text = metadata['base']['description']
    words = text.split(' ')
    # word = secrets.choice(words)
    word = words[0]
    # should return at least 1 or more assets
    logging.info(f'search word is {word}')
    searchResult = ocean.search_registered_assets(word)
    assert searchResult
    
    assert(len(searchResult) > 1)


