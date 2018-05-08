import unittest
from contract_methods import ContractMethods
from test_utils import TestElasticSearch

class ContractMethodsTestCase(unittest.TestCase):
  def setUp(self):
    self.client = TestElasticSearch()
    self.client.recreate_index(TEST_INDEX)
    self.contract_methods = ContractMethods(TEST_INDEX)
    
  def test_iterate_contracts(self):
    self.client.index(TEST_INDEX, 'contract', {'address': TEST_CONTRACT_ADDRESSES[0]}, id=1, refresh=True)
    self.client.index(TEST_INDEX, 'contract', {'address': TEST_CONTRACT_ADDRESSES[1]}, id=2, refresh=True)
    self.client.index(TEST_INDEX, 'contract', {'address': TEST_CONTRACT_ADDRESSES[2]}, id=3, refresh=True)
    iterator = self.contract_methods._iterate_contracts()
    contracts = [c for contracts_list in iterator for c in contracts_list]
    contracts = [contract['_id'] for contract in contracts]
    self.assertCountEqual(["1", "2", "3"], contracts)
  
  def test_search_methods(self):
    self.client.index(TEST_INDEX, 'contract', {'address': TEST_CONTRACT_ADDRESSES[0]}, id=1, refresh=True)
    self.client.index(TEST_INDEX, 'contract', {'address': TEST_CONTRACT_ADDRESSES[1]}, id=2, refresh=True)
    self.client.index(TEST_INDEX, 'contract', {'address': TEST_CONTRACT_ADDRESSES[2]}, id=3, refresh=True)
    self.client.index(TEST_INDEX, 'contract', {'address': TEST_CONTRACT_ADDRESSES[3]}, id=4, refresh=True)
    self.client.index(TEST_INDEX, 'contract', {'address': TEST_CONTRACT_ADDRESSES[4]}, id=5, refresh=True)
    self.contract_methods.search_methods()
    iterator = self.contract_methods._iterate_contracts()
    contracts = [c for contracts_list in iterator for c in contracts_list]
    bytecodes = [contract["_source"]["bytecode"] for contract in contracts]
    standards = [contract["_source"]["standards"] for contract in contracts if contract['_source']['is_token'] == True]
    tokens_names = [contract['_source']['token_name'] for contract in contracts if contract['_source']['is_token'] == True]
    tokens_symbols = [contract['_source']['token_symbol'] for contract in contracts if contract['_source']['is_token'] == True]
    is_token = [contract['_source']['is_token'] for contract in contracts]
    self.assertCountEqual([True, True, True, False, True], is_token)
    self.assertCountEqual(['RUN COIN', 'bangbeipay', 'YNOTCoin', 'Josh Bucks'], tokens_names)
    self.assertCountEqual(['RUN', 'BBP', 'YNOT', '%'], tokens_symbols)
    self.assertCountEqual([['erc20'], ['erc20'], ['erc20'], None], standards)
    assert TEST_BYTECODE in bytecodes
 

TEST_INDEX = 'test-ethereum-contracts'
TEST_CONTRACT_ADDRESSES = ['0xa0e89120768bf166d228988627e4ac8af350220a', '0x6d6fb0951b769a6246f0246472856b2f70049c53', '0xaff9f95b455662c893bf3bb752557faa962d8355', '0x6Dabe61eD0212141951292e47d866cf0b3F2bfBD', '0x7681ac00c991852ad683d235377e8557256d769f']
TEST_BYTECODE = "0x6060604052600436106101275763ffffffff7c010000000000000000000000000000000000000000000000000000000060003504166305fefda7811461012c57806306fdde0314610147578063095ea7b3146101d157806318160ddd1461020757806323b872dd1461022c578063313ce5671461025457806342966c681461027d5780634b7503341461029357806370a08231146102a657806379c65068146102c557806379cc6790146102e75780638620410b146103095780638da5cb5b1461031c57806395d89b411461034b578063a6f2ae3a1461035e578063a9059cbb14610366578063b414d4b614610388578063cae9ca51146103a7578063dd62ed3e1461040c578063e4849b3214610431578063e724529c14610447578063f2fde38b1461046b575b600080fd5b341561013757600080fd5b61014560043560243561048a565b005b341561015257600080fd5b61015a6104b0565b60405160208082528190810183818151815260200191508051906020019080838360005b8381101561019657808201518382015260200161017e565b50505050905090810190601f1680156101c35780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b34156101dc57600080fd5b6101f3600160a060020a036004351660243561054e565b604051901515815260200160405180910390f35b341561021257600080fd5b61021a61057e565b60405190815260200160405180910390f35b341561023757600080fd5b6101f3600160a060020a0360043581169060243516604435610584565b341561025f57600080fd5b6102676105fb565b60405160ff909116815260200160405180910390f35b341561028857600080fd5b6101f3600435610604565b341561029e57600080fd5b61021a61068f565b34156102b157600080fd5b61021a600160a060020a0360043516610695565b34156102d057600080fd5b610145600160a060020a03600435166024356106a7565b34156102f257600080fd5b6101f3600160a060020a036004351660243561076d565b341561031457600080fd5b61021a610849565b341561032757600080fd5b61032f61084f565b604051600160a060020a03909116815260200160405180910390f35b341561035657600080fd5b61015a61085e565b6101456108c9565b341561037157600080fd5b610145600160a060020a03600435166024356108e9565b341561039357600080fd5b6101f3600160a060020a03600435166108f8565b34156103b257600080fd5b6101f360048035600160a060020a03169060248035919060649060443590810190830135806020601f8201819004810201604051908101604052818152929190602084018383808284375094965061090d95505050505050565b341561041757600080fd5b61021a600160a060020a0360043581169060243516610a3f565b341561043c57600080fd5b610145600435610a5c565b341561045257600080fd5b610145600160a060020a03600435166024351515610ab9565b341561047657600080fd5b610145600160a060020a0360043516610b45565b60005433600160a060020a039081169116146104a557600080fd5b600791909155600855565b60018054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156105465780601f1061051b57610100808354040283529160200191610546565b820191906000526020600020905b81548152906001019060200180831161052957829003601f168201915b505050505081565b600160a060020a033381166000908152600660209081526040808320938616835292905220819055600192915050565b60045481565b600160a060020a038084166000908152600660209081526040808320339094168352929052908120548211156105b957600080fd5b600160a060020a03808516600090815260066020908152604080832033909416835292905220805483900390556105f1848484610b8f565b5060019392505050565b60035460ff1681565b600160a060020a0333166000908152600560205260408120548290101561062a57600080fd5b600160a060020a03331660008181526005602052604090819020805485900390556004805485900390557fcc16f5dbb4873280815c1ee09dbd06736cffcc184412cf7a71a0fdb75d397ca59084905190815260200160405180910390a2506001919050565b60075481565b60056020526000908152604090205481565b60005433600160a060020a039081169116146106c257600080fd5b600160a060020a03808316600090815260056020526040808220805485019055600480548501905530909216917fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef9084905190815260200160405180910390a381600160a060020a031630600160a060020a03167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef8360405190815260200160405180910390a35050565b600160a060020a0382166000908152600560205260408120548290101561079357600080fd5b600160a060020a03808416600090815260066020908152604080832033909416835292905220548211156107c657600080fd5b600160a060020a038084166000818152600560209081526040808320805488900390556006825280832033909516835293905282902080548590039055600480548590039055907fcc16f5dbb4873280815c1ee09dbd06736cffcc184412cf7a71a0fdb75d397ca59084905190815260200160405180910390a250600192915050565b60085481565b600054600160a060020a031681565b60028054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156105465780601f1061051b57610100808354040283529160200191610546565b6000600854348115156108d857fe5b0490506108e6303383610b8f565b50565b6108f4338383610b8f565b5050565b60096020526000908152604090205460ff1681565b60008361091a818561054e565b15610a375780600160a060020a0316638f4ffcb1338630876040518563ffffffff167c01000000000000000000000000000000000000000000000000000000000281526004018085600160a060020a0316600160a060020a0316815260200184815260200183600160a060020a0316600160a060020a0316815260200180602001828103825283818151815260200191508051906020019080838360005b838110156109d05780820151838201526020016109b8565b50505050905090810190601f1680156109fd5780820380516001836020036101000a031916815260200191505b5095505050505050600060405180830381600087803b1515610a1e57600080fd5b6102c65a03f11515610a2f57600080fd5b505050600191505b509392505050565b600660209081526000928352604080842090915290825290205481565b6007548102600160a060020a033016311015610a7757600080fd5b610a82333083610b8f565b33600160a060020a03166108fc60075483029081150290604051600060405180830381858888f1935050505015156108e657600080fd5b60005433600160a060020a03908116911614610ad457600080fd5b600160a060020a03821660009081526009602052604090819020805460ff19168315151790557f48335238b4855f35377ed80f164e8c6f3c366e54ac00b96a6402d4a9814a03a5908390839051600160a060020a039092168252151560208201526040908101905180910390a15050565b60005433600160a060020a03908116911614610b6057600080fd5b6000805473ffffffffffffffffffffffffffffffffffffffff1916600160a060020a0392909216919091179055565b600160a060020a0382161515610ba457600080fd5b600160a060020a03831660009081526005602052604090205481901015610bca57600080fd5b600160a060020a03821660009081526005602052604090205481810111610bf057600080fd5b600160a060020a03831660009081526009602052604090205460ff1615610c1657600080fd5b600160a060020a03821660009081526009602052604090205460ff1615610c3c57600080fd5b600160a060020a038084166000818152600560205260408082208054869003905592851680825290839020805485019055917fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef9084905190815260200160405180910390a35050505600a165627a7a72305820f763879a776dcb694a89a7f513363f09c42efc65fe50f91792ec6523f1e540f00029"