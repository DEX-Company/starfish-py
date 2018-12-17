"""
    Test ocean class

"""

import pathlib
import json
import logging

from ocean_py.ocean import Ocean
from ocean_py.metadata_agent import MetadataAgent

from ocean_py.logging import setup_logging
from ocean_py import logger


setup_logging(level=logging.DEBUG)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("web3").setLevel(logging.WARNING)

CONTRACTS_PATH = 'artifacts'
KEEPER_URL = 'http://localhost:8545'

METADATA_STORAGE_URL = 'http://localhost:8080'
METADATA_STORAGE_AUTH = 'QWxhZGRpbjpPcGVuU2VzYW1l'
METADATA_SAMPLE_PATH = pathlib.Path.cwd() / 'tests' / 'resources' / 'metadata' / 'sample_metadata1.json'


def test_ocean_instance():
    # create an ocean object
    ocean = Ocean( keeper_url=KEEPER_URL, contract_path=CONTRACTS_PATH)
    assert ocean
    assert ocean.keeper
    assert ocean.web3
    assert ocean.accounts
    agent_account = ocean.accounts[list(ocean.accounts)[0]]

    agent = MetadataAgent(ocean, auth=METADATA_STORAGE_AUTH)
    # test register a new metadata storage agent
    password = agent.register(METADATA_STORAGE_URL, agent_account)
    assert agent
    assert password
    assert agent.did
    assert agent.ddo

    # now assign it to ocean lib for later use
    agent_did = ocean.assign_agent(agent)

    # test getting the agent from a DID
    agent = ocean.get_agent(agent_did)

    assert agent
    assert not agent.is_empty


    # load in the sample metadata
    assert METADATA_SAMPLE_PATH.exists(), "{} does not exist!".format(METADATA_SAMPLE_PATH)
    metadata = None
    with open(METADATA_SAMPLE_PATH, 'r') as file_handle:
        metadata = json.load(file_handle)
    assert metadata

    # test registering an asset
    asset = ocean.register_asset(metadata['base'], did=agent_did)
    assert asset

    # test registering an asset
    asset = ocean.register_asset(metadata['base'], agent=agent)
    assert asset


    asset_did = asset.did
    # start to test getting the asset from storage
    asset = ocean.get_asset(asset_did)
    assert asset
