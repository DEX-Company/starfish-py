"""

Ocean class to access the Ocean eco system.

"""
from web3 import (
    Web3,
    HTTPProvider
)

from starfish import Account
from starfish.models.squid_model import SquidModel


GAS_LIMIT_DEFAULT = 30000


class Ocean():
    """
    .. _Asset class: asset.html
    .. _Config class: config.html

    The Ocean class connects to the ocean network.

    For example to use this class you can do the following: ::

        from starfish.ocean import Ocean

        my_config = {
            'contracts_path': 'artifacts',
            'keeper_url': 'http://localhost:8545',
            'gas_limit': 1000,
        }
        ocean = Ocean(my_config)

    or you can do the following setup: ::

        from starfish.ocean import Ocean
        ocean = Ocean(keeper_url='http://localhost:8545', contracts_path= artifacts, gas_limit=1000)


    You can provide these parameters in a dictionary or as individual parameters.

    :param contracts_path: path to the contract files ( artifacts ).
    :type contracts_path: str or None
    :param keeper_url: url to the keeper node ( http://localhost:8545 ).
    :type keeper_url: str or None
    :param gas_limit: The amount of gas you are willing to spend on each block chain transaction ( 30000 ).
    :type gas_limit: int or string

    """

    def __init__(self, *args, **kwargs):
        """
        .. :class: starfish.Ocean

        init the basic Ocean class for the connection and contract info

        """
        if args and isinstance(args[0], dict):
            kwargs = args[0]

        self._keeper_url = kwargs.get('keeper_url', 'http://localhost:8545')
        self._contracts_path = kwargs.get('contracts_path', 'artifacts')
        self._gas_limit = kwargs.get('gas_limit', GAS_LIMIT_DEFAULT)

        # For development, we use the HTTPProvider Web3 interface
        self.__web3 = Web3(HTTPProvider(self._keeper_url))

    def register_update_agent_service(self, service_name, endpoint_url, account, did=None):
        """

        Register this agent service with a DDO on the block chain.

        :param str service_name: service name of the agent service to register.
        :param str endpoint_url: URL of the agents service to add to the DDO to register.
        :param account: account to use as the owner of the registration.
        :type account: :class:`.Account`
        :param did: Optional DID to use to update the registration for this agent, you must use the same account as the when you did the original registartion.
        :type did: str or None
        :return: a tuple of (DID, DDO, private_pem).

        | *DID*: of the registerered agent.
        | *DDO*: record writtern to the block chain as part of the registration.
        | *private_pem*: private PEM used to sign the DDO.

        :type: string

        For example::

            # register the public surfer on the block chain
            did, ddo, key_pem = ocean.register_agent('surfer', 'https://market_surfer.io', ocean.accounts[0])

        TODO: Need to split this up into two calls, one to add, other to update
        """

        if not isinstance(account, Account):
            raise TypeError('You need to pass an Account object')

        if not account.is_valid:
            raise ValueError('You must pass a valid account')

        if did is None:
            # if no did then we need to create a new one
            did = id_to_did(secrets.token_hex(32))

        # create a new DDO
        ddo = DDO(did)
        # add a signature
        private_key_pem = ddo.add_signature()
        # add the service endpoint with the meta data
        ddo.add_service(service_name, endpoint_url)
        # add the static proof
        ddo.add_proof(0, private_key_pem)
        if self._register_ddo(did, ddo, account._squid_account):
            return [did, ddo, private_key_pem]
        return None

    def get_account(self, address, password=None):
        """
        Get an account object based on it's address

        :param address: address of the account, if dict then use the fields, `address` and `password`.
        :type address: str or dict
        :param password: optional password to save with the account
        :type password: str or None

        :return: return the :class:`Account` object or None if the account can not be used.
        :type: :class:`Account` or None

        >>> account = ocean.get_account('0x00bd138abd70e2f00903268f3db08f2d25677c9e')
        """
        return Account(self, address, password)

    @property
    def accounts(self):
        """
        :return: a list of :class:`.Account` objects
        :type: list of :class:`Account` objects

        >>> ocean.accounts
        {'0x00Bd138aBD70e2F00903268F3Db08f2D25677C9e': <starfish.account.Account object at 0x10456c080>, ...
        """
        model = SquidModel(self)
        accounts = {}
        for address in model.accounts:
            account = Account(self, address)
            accounts[account.address] = account
        return accounts

    @property
    def _web3(self):
        """return the web3 instance"""
        return self.__web3

    @property
    def keeper_url(self):
        return self._keeper_url

    @property
    def contracts_path(self):
        return self._contracts_path

    @property
    def gas_limit(self):
        return self._gas_limit
