import unittest
from token_holders import TokenHolders
from contract_methods import ContractMethods
from test_utils import TestElasticSearch
import json

class TokenHoldersTestCase(unittest.TestCase):
  def setUp(self):
    self.client = TestElasticSearch()
    self.client.recreate_index(TEST_INDEX)
    self.client.recreate_index(TEST_TX_INDEX)
    self.client.recreate_index(TEST_LISTED_INDEX)
    self.client.recreate_index(TEST_TOKEN_TX_INDEX)
    self.token_holders = TokenHolders({'contract': TEST_INDEX, 'transaction': TEST_TX_INDEX, 'listed_token': TEST_LISTED_INDEX, 'token_tx': TEST_TOKEN_TX_INDEX})
    self.contract_methods = ContractMethods({"contract": TEST_INDEX}, ethereum_api_host='https://mainnet.infura.io/SuP0gwmZ0hYfutY70s6V')
  '''
  def test_get_listed_tokens(self):
    for address in TEST_TOKEN_ADDRESSES:
      self.client.index(TEST_INDEX, 'contract', {'address': address}, refresh=True)
    self.contract_methods.search_methods()

    listed_tokens = self.token_holders._get_listed_tokens()
    listed_tokens = [token[0]['_source']['token_name'] for token in listed_tokens]
    listed_tokens = set(listed_tokens)
    self.assertCountEqual(['Aeternity', 'Populous Platform', 'Golem Network Token'], listed_tokens)
  
  def test_search_duplicates(self):
    for address in TEST_TOKEN_ADDRESSES:
      self.client.index(TEST_INDEX, 'contract', {'address': address}, refresh=True)
    for tx in TEST_TOKEN_TXS:
      self.client.index(TEST_TX_INDEX, 'tx', tx, refresh=True)
    self.contract_methods.search_methods()

    listed_tokens = self.token_holders._search_duplicates()
    duplicated = [token for token in listed_tokens if token['duplicated'] == True]
    real_golem = [token for token in duplicated if token['token_name'] == 'Golem Network Token'][0]
    real_aeternity = [token for token in duplicated if token['token_name'] == 'Aeternity'][0]
    assert real_golem['address'] == '0xa74476443119a942de498590fe1f2454d7d4ac0d'
    assert real_aeternity['address'] == '0x5ca9a71b1d01849c0a95490cc00559717fcf0d1d'

  def test_load_tokens(self):
    for address in TEST_TOKEN_ADDRESSES:
      self.client.index(TEST_INDEX, 'contract', {'address': address}, refresh=True)
    for tx in TEST_TOKEN_TXS:
      self.client.index(TEST_TX_INDEX, 'tx', tx, refresh=True)
    self.contract_methods.search_methods()

    self.token_holders._load_listed_tokens()
    loaded_tokens = self.token_holders._iterate_tokens()
    loaded_tokens = [c for contracts_list in loaded_tokens for c in contracts_list]
    loaded_tokens = [token['_source']['token_name'] for token in loaded_tokens]
    self.assertCountEqual(['Aeternity', 'Populous Platform', 'Golem Network Token'], loaded_tokens)
  
  def test_search_token_holders(self):
    for tx in TEST_TOKEN_TXS:
      self.client.index(TEST_TX_INDEX, 'tx', tx, refresh=True)

    self.token_holders._extract_token_txs('0x5ca9a71b1d01849c0a95490cc00559717fcf0d1d')
    token_txs = self.token_holders._iterate_tx_descriptions('0x5ca9a71b1d01849c0a95490cc00559717fcf0d1d')
    token_txs = [tx for txs_list in token_txs for tx in txs_list]
    methods = [tx['_source']['method'] for tx in token_txs]
    amounts = [tx['_source']['value'] for tx in token_txs] 
    self.assertCountEqual(['transfer', 'approve', 'transferFrom'], methods)
    self.assertCountEqual(['356245680000000000000', '356245680000000000000', '2266000000000000000000'], amounts)
  
  def test_count_token_balances_from_txs(self):
    for tx in TEST_TOKEN_TXS:
      self.client.index(TEST_TX_INDEX, 'tx', tx, refresh=True)

    self.token_holders._extract_token_txs('0x5ca9a71b1d01849c0a95490cc00559717fcf0d1d')
    
    balances = self.token_holders._count_token_holders_balances('0x5ca9a71b1d01849c0a95490cc00559717fcf0d1d')
    balances = [balance['Aeternity'] for balance in balances]
    self.assertCountEqual(['2266000000000000000000', '-2266000000000000000000', '356245680000000000000', '-356245680000000000000'], balances)
    '''
  def test_get_balances_for_listed_tokens(self):
    for address in TEST_TOKEN_ADDRESSES:
      self.client.index(TEST_INDEX, 'contract', {'address': address}, refresh=True)
    for tx in TEST_TOKEN_TXS:
      self.client.index(TEST_TX_INDEX, 'tx', tx, refresh=True)
    self.contract_methods.search_methods()

    self.token_holders.get_balances_for_listed_tokens()
    holders = self.token_holders._iterate_holders()
    holders = [c for contracts_list in holders for c in contracts_list]
    print(holders)
    holders_addressses = [holder['_source']['address'] for holder in holders]
    holders_balances = [holder['_source']['Aeternity'] for holder in holders]
    self.assertCountEqual(['0xa60c4c379246a7f1438bd76a92034b6c82a183a5', '0x6b25d0670a34c1c7b867cd9c6ad405aa1759bda0', '0xc917e19946d64aa31d1aeacb516bae2579995aa9', '0x4e6b129bbb683952ed1ec935c778d74a77b352ce'], holders_addressses)
    self.assertCountEqual(['2266000000000000000000', '-2266000000000000000000', '356245680000000000000', '-356245680000000000000'], holders_balances)

TEST_INDEX = 'test-ethereum-contracts'
TEST_TX_INDEX = 'test-ethereum-txs'
TEST_LISTED_INDEX = 'test-listed-tokens'
TEST_TOKEN_TX_INDEX = 'test-token-txs'

TEST_TOKEN_ADDRESSES = ['0x5ca9a71b1d01849c0a95490cc00559717fcf0d1d',
  '0xd4fa1460f537bb9085d22c7bccb5dd450ef28e3a',
  '0x51ada638582e51c931147c9abd2a6d63bc02e337',
  '0xa74476443119a942de498590fe1f2454d7d4ac0d',
  '0xbe78d802c2aeebdc34c810b805c2691885a61257',
  '0x83199a2bd905dd5f2f61828e5a705790b782cf43'
  ]
TEST_TOKEN_TXS = [
  {'from': '0x6b25d0670a34c1c7b867cd9c6ad405aa1759bda0', 'to': '0x5ca9a71b1d01849c0a95490cc00559717fcf0d1d', 'decoded_input': {'name': 'transfer', 'params': [{'type': 'address', 'value': '0xa60c4c379246a7f1438bd76a92034b6c82a183a5'}, {'type': 'uint256', 'value': '2266000000000000000000'}]}, 'blockNumber': 5635149},
  {'from': '0x58d46475da68984bacf1f2843b85e0fdbcbc6cef', 'to': '0x5ca9a71b1d01849c0a95490cc00559717fcf0d1d', 'decoded_input': {'name': 'approve', 'params': [{'type': 'address', 'value': '0x4e6b129bbb683952ed1ec935c778d74a77b352ce'}, {'type': 'uint256', 'value': '356245680000000000000'}]}, 'blockNumber': 5635141},
  {'from': '0xc917e19946d64aa31d1aeacb516bae2579995aa9', 'to': '0x5ca9a71b1d01849c0a95490cc00559717fcf0d1d', 'decoded_input': {'name': 'transferFrom', 'params': [{'type': 'address', 'value': '0xc917e19946d64aa31d1aeacb516bae2579995aa9'}, {'type': 'address', 'value': '0x4e6b129bbb683952ed1ec935c778d74a77b352ce'}, {'type': 'uint256', 'value': '356245680000000000000'}]}, 'blockNumber': 5635142},
  {'from': '0x892ce7dbc4a0efbbd5933820e53d2c945ef9f722', 'to': '0x51ada638582e51c931147c9abd2a6d63bc02e337', 'decoded_input': {'name': 'transfer', 'params': [{'type': 'address', 'value': '0x3f5ce5fbfe3e9af3971dd833d26ba9b5c936f0be'}, {'type': 'uint256', 'value': '2294245680000000000000'}]}}
  #{'to': '0xa74476443119a942de498590fe1f2454d7d4ac0d'},
  #{'to': '0xa74476443119a942de498590fe1f2454d7d4ac0d'},
  #{'to': '0xbe78d802c2aeebdc34c810b805c2691885a61257'}
]
    