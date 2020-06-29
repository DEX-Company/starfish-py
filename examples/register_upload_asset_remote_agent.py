#!/usr/bin/env python3

from starfish import Network
from starfish.asset import DataAsset
from starfish.agent import RemoteAgent, AgentManager
from starfish.agent.services import Services

def main():

    # Create a new Ocean instance.
    network = Network('http://localhost:8545')
    print(network.name)

    # we only need to call this method if we are using a local test network.
    # load in the contracts and their addresses from the local test network
    network.load_development_contracts()

    # Now create a memory asset
    asset = DataAsset.create('TestAsset', 'Some test data that I want to save for this asset')

    # Print the asset data
    print('my asset:', asset.data)

    # Create a remote agent to do the work.
    agent_url = 'http://localhost:3030'

    authentication = {
        'username': 'Aladdin',
        'password':  'OpenSesame',
    }

    # find an agent based on it's url, you can also use an agent did or asset did instead
    agent = RemoteAgent.load(network, agent_url, authentication=authentication)
    if not agent:
        print('failed to find the agent')

    # create a listing specifying the information about the asset
    listing_data = {
        'name': 'The white paper',
        'author': 'Ocean Protocol',
        'license': 'CC0: Public Domain',
        'price': '0'
    }

    asset = agent.register_asset(asset)
    print(asset.did)
    listing = agent.create_listing(listing_data, asset.did)
    print(listing.did, listing.data)

    # now upload the asset data to Surfer
    agent.upload_asset(asset)

if __name__ == '__main__':
    main()