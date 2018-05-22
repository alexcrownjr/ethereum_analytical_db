from web3 import Web3, HTTPProvider
from custom_elastic_search import CustomElasticSearch
from config import INDICES
import requests
import json
from pyelasticsearch import bulk_chunks

class TokenHolders:
  def __init__(self, elasticsearch_indices=INDICES, elasticsearch_host="http://localhost:9200", ethereum_api_host="http://localhost:8545"):
    self.indices = elasticsearch_indices
    self.client = CustomElasticSearch(elasticsearch_host)
    self.w3 = Web3(HTTPProvider(ethereum_api_host))

  def _get_tokens_list(self):
    response = requests.get('https://api.coinmarketcap.com/v2/listings/')
    return response.json()['data']

  def _construct_msearch_body(self, names_list):
    search_list = []
    for name in names_list:
      search_list.append({'index': self.indices['contract'], 'type': 'contract'})
      search_list.append({'query': {'match': {'token_name': {'query': name, 'minimum_should_match': '100%'}}}})
    body = ''
    for obj in search_list:
      body += '%s \n' %json.dumps(obj)
    return body

  def _search_multiple_tokens(self, token_names):
    body = self._construct_msearch_body(token_names)
    response = self.client.send_request('GET', [self.indices['contract'], 'contract', '_msearch'], body, {})
    results = response['responses']
    erc_tokens = [result['hits']['hits'] for result in results if len(result['hits']['hits']) > 0]
    return erc_tokens

  def _get_listed_tokens(self):
    coinmarketcap_tokens = self._get_tokens_list()
    coinmarketcap_names = [token['name'] for token in coinmarketcap_tokens]
    token_contracts = self._search_multiple_tokens(coinmarketcap_names)
    return token_contracts

  def _get_token_txs_count(self, token_address):
    count_body = {
      'query': {
        'term': {
          'to': token_address
        }
      }
    }
    # TODO: replace by pyelasticsearch send_request
    txs_count = requests.get('http://localhost:9200/' + self.indices['transaction'] + '/tx/_count', json=count_body)
    txs_count = txs_count.json()['count']
    return txs_count

  def _find_real_token(self, duplicates_list):
    for duplicate in duplicates_list:
      duplicate['_source']['txs_count'] = self._get_token_txs_count(duplicate['_source']['address'])
    duplicates_list = sorted(duplicates_list, key=lambda x: x['_source']['txs_count'], reverse=True)
    real_token = duplicates_list[0]
    real_token['_source']['duplicated'] = True
    real_token['_source']['duplicates'] = [duplicate['_source']['address'] for duplicate in duplicates_list[0:]]
    return real_token

  def _extend_token_descr(self, token):
    token['_source']['txs_count'] = self._get_token_txs_count(token['_source']['address'])
    token['_source']['duplicated'] = False
    return token

  def _remove_identical_descriptions(self, descr_list):
    descr_list = [json.dumps(token['_source']) for token in descr_list]
    descr_list = set(descr_list)
    descr_list = [json.loads(token) for token in descr_list]
    return descr_list

  def _search_duplicates(self):
    token_contracts = self._get_listed_tokens()
    non_duplicated_tokens = [self._extend_token_descr(contracts[0]) for contracts in token_contracts if len(contracts) == 1]
    duplicated_tokens = [self._find_real_token(contracts) for contracts in token_contracts if len(contracts) > 1]
    result = non_duplicated_tokens + duplicated_tokens
    result = self._remove_identical_descriptions(result)
    return result

  def _construct_bulk_insert_ops(self, docs):
    for doc in docs:
      yield self.client.index_op(doc)

  def _insert_multiple_docs(self, docs, doc_type, index_name):
    for chunk in bulk_chunks(self._construct_bulk_insert_ops(docs), docs_per_chunk=1000):
      self.client.bulk(chunk, doc_type=doc_type, index=index_name, refresh=True)

  def _iterate_tokens(self):
    return self.client.iterate(self.indices['listed_token'], 'token', 'token_name:*')

  def _load_listed_tokens(self):
    listed_tokens = self._search_duplicates()
    self._insert_multiple_docs(listed_tokens, 'token', self.indices['listed_token'])

  def _iterate_token_txs(self, token_addr):
    return self.client.iterate(self.indices['transaction'], 'tx', 'to:' + token_addr)

  def _iterate_token_tx_descriptions(self, token_address):
    return self.client.iterate(self.indices['token_tx'], 'tx', 'token:' + token_addr)

  def _construct_tx_descr_from_input(self, tx):
    tx_input = tx['decoded_input']
    if tx_input['name'] == 'transfer':
      return {'method': tx_input['name'], 'from': tx['from'], 'to': tx_input['params'][0]['value'], 'value': tx_input['params'][1]['value'],'block_id': tx['blockNumber'], 'token': tx['to'], 'tx_index': self.indices['transaction']}
    elif tx_input['name'] == 'transferFrom':
      return {'method': tx_input['name'], 'from': tx_input['params'][0]['value'], 'to': tx_input['params'][1]['value'], 'value': tx_input['params'][2]['value'], 'block_id': tx['blockNumber'], 'token': tx['to'], 'tx_index': self.indices['transaction']}
    elif tx_input['name'] == 'approve':
      return {'method': tx_input['name'], 'from': tx['from'], 'spender': tx_input['params'][0]['value'], 'value': tx_input['params'][1]['value'],'block_id': tx['blockNumber'], 'token': tx['to'], 'tx_index': self.indices['transaction']}
    else:
      return {'method': 'unknown', 'txHash': tx['hash']}

  def _extract_descriptions_from_txs(self, txs):
    txs_info = []
    for tx in txs:
      tx_descr = self._construct_tx_descr_from_input(tx['_source'])
      txs_info.append(tx_descr)
    self._insert_multiple_docs(txs_info, 'tx', self.indices['token_tx'])

  def _iterate_tx_descriptions(self, token_address):
    return self.client.iterate(self.indices['token_tx'], 'tx', 'token:' + token_address)

  def _extract_token_txs(self, token_address):
    for txs_chunk in self._iterate_token_txs(token_address):
      self._extract_descriptions_from_txs(txs_chunk)

  def _extract_token_balances(self, tx_descriptions, holders_dict, token_name):
    for descr in tx_descriptions:
      if descr['_source']['method'] == 'transfer' or descr['_source']['method'] == 'transferFrom':
        delta = descr['_source']['value']
        if descr['_source']['from'] in holders_dict.keys():
          holders_dict[descr['_source']['from']][token_name] = int(holders_dict[descr['_source']['from']][token_name])
          holders_dict[descr['_source']['from']][token_name] -= int(delta)
        else:
          holders_dict[descr['_source']['from']] = {}
          holders_dict[descr['_source']['from']][token_name] = -(int(delta))
        if descr['_source']['to'] in holders_dict.keys():
          holders_dict[descr['_source']['to']][token_name] = int(holders_dict[descr['_source']['to']][token_name])
          holders_dict[descr['_source']['to']][token_name] += int(delta)
        else:
          holders_dict[descr['_source']['to']] = {}
          holders_dict[descr['_source']['to']][token_name] = int(delta)
        holders_dict[descr['_source']['from']][token_name] = str(holders_dict[descr['_source']['from']][token_name])
        holders_dict[descr['_source']['to']][token_name] = str(holders_dict[descr['_source']['to']][token_name])
    holders_list = []
    for item in holders_dict.items():
      tmp_dict = item[1]
      tmp_dict['address'] = item[0]
      holders_list.append(tmp_dict)
    return holders_list

  def _get_saved_holders(self, descriptions):
    current_holders = [[tx_descr['_source']['from'], tx_descr['_source']['to']] for tx_descr in descriptions if tx_descr['_source']['method'] != 'approve']
    current_holders = set([t for tokens_list in current_holders for t in tokens_list])
    saved_holders = self._search_multiple_holders(current_holders)
    holders_dict = {}
    for holder in saved_holders:
      address = holder['address']
      holders_dict[address] = holder['_source']
    return holders_dict

  def _count_token_holders_balances(self, token_address, token_name):
    token_holders = {}
    for tx_descr_chunk in self._iterate_tx_descriptions(token_address):
      saved_holders = self._get_saved_holders(tx_descr_chunk)
      token_holders = self._extract_token_balances(tx_descr_chunk, saved_holders, token_name)
    #token_holders = [{'address': key, token_name: str(token_holders[key])} for key in token_holders.keys()]
    return token_holders

  def _search_multiple_holders(self, holders_addresses):
    body = self._construct_msearch_body(holders_addresses)
    response = self.client.send_request('GET', [self.indices['contract'], 'contract', '_msearch'], body, {})
    results = response['responses']
    holders = [result['hits']['hits'] for result in results if len(result['hits']['hits']) > 0]
    return holders

  def _iterate_holders(self):
    return self.client.iterate(self.indices['listed_token'], 'holder', 'address:*')

  def get_balances_for_listed_tokens(self):
    self._load_listed_tokens()
    tokens = self._iterate_tokens()
    tokens = [t for tokens_list in tokens for t in tokens_list]
    for token in tokens:
      self._extract_token_txs(token['_source']['address'])
      token_holders = self._count_token_holders_balances(token['_source']['address'], token['_source']['token_name'])
      print(token_holders)
      self._insert_multiple_docs(token_holders, 'holder', self.indices['listed_token'])