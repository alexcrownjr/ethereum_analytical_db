from tqdm import *
import re
from web3 import Web3, HTTPProvider
from custom_elastic_search import CustomElasticSearch

NUMBER_OF_JOBS = 1000

class ContractMethods:
  def __init__(self, elasticsearch_index, elasticsearch_host="http://localhost:9200", ethereum_api_host="http://localhost:8545"):
    self.index = elasticsearch_index
    self.client = CustomElasticSearch(elasticsearch_host)
    self.w3 = Web3(HTTPProvider(ethereum_api_host))

  def _extract_first_bytes(self, func):
    return str(self.w3.toHex(self.w3.sha3(text=func)[0:4]))[2:]

  def _iterate_contracts(self):
    return self.client.iterate(self.index, 'contract', 'address:*', paginate=True)

  def _extract_methods_signatures(self):
    return {
      'erc20': {
        'totalSupply': self._extract_first_bytes('totalSupply()'),
        'balanceOf': self._extract_first_bytes('balanceOf(address)'),
        'allowance': self._extract_first_bytes('allowance(address,address)'),
        'transfer': self._extract_first_bytes('transfer(address,uint256)'),
        'transferFrom': self._extract_first_bytes('transferFrom(address,address,uint256)'),
        'approve': self._extract_first_bytes('approve(address,uint256)'),
      },
      'erc223': {
        'tokenFallback': self._extract_first_bytes('tokenFallback(address,uint256,bytes)')
      }
    }

  def search_methods(self):
    standards = self._extract_methods_signatures()
    for contracts_chunk in self._iterate_contracts():
      for contract in contracts_chunk:
        contract_checksum_addr = self.w3.toChecksumAddress(contract['_source']['address'])
        contract_code_bytearr = self.w3.eth.getCode(contract_checksum_addr)
        code = self.w3.toHex(contract_code_bytearr)
        avail_standards = []
        for standard in standards:
          methods = []
          for method in standards[standard]:
            res = re.search(r'' + standards[standard][method], code) != None
            methods.append(res)
          if False not in methods:
            avail_standards.append(standard)
        self.client.update(self.index, 'contract', contract['_id'], doc={'standards': avail_standards, 'bytecode': code}, refresh=True)