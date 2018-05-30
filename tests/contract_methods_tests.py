import unittest
from contract_methods import ContractMethods
from test_utils import TestElasticSearch

class ContractMethodsTestCase(unittest.TestCase):
  def setUp(self):
    self.client = TestElasticSearch()
    self.client.recreate_index(TEST_INDEX)
    self.contract_methods = ContractMethods({"contract": TEST_INDEX})

  def test_iterate_non_standard(self):
    self.client.index(TEST_INDEX, 'contract', {'address': TEST_CONTRACT_ADDRESSES[0], 'bytecode': TEST_BYTECODES[0]}, id=1, refresh=True)
    self.client.index(TEST_INDEX, 'contract', {'address': TEST_CONTRACT_ADDRESSES[3], 'bytecode': TEST_BYTECODES[3]}, id=2, refresh=True)
    self.client.index(TEST_INDEX, 'contract', {'address': TEST_CONTRACT_ADDRESSES[4], 'bytecode': TEST_BYTECODES[4]}, id=3, refresh=True)
    self.contract_methods.search_methods()
    iterator = self.contract_methods._iterate_non_standard()
    contracts = [c for contracts_list in iterator for c in contracts_list]
    contracts = [contract['_id'] for contract in contracts]
    self.assertCountEqual(['3'], contracts)
  
  def test_check_if_token(self):
    is_token = self.contract_methods._check_is_token(TEST_BYTECODES[2])
    assert is_token == True

  def test_search_standards(self):
    standards = self.contract_methods._check_standards(TEST_BYTECODES[2])
    assert standards == ['erc20']

  def test_get_constants(self):
    constants = self.contract_methods._get_constants('0xd26114cd6EE289AccF82350c8d8487fedB8A0C07')
    self.assertCountEqual(('OMGToken', 'OMG', '140245398', 18, '0x000000000000000000000000000000000000dEaD'), constants)

  def test_get_empty_constants(self):
    empty_constants = self.contract_methods._get_constants(TEST_EMPTY_CONTRACT)
    self.assertCountEqual(('', '', '0', 0, 'None',), empty_constants)

  def test_search_methods(self):
    for i, address in enumerate(TEST_CONTRACT_ADDRESSES):
      self.client.index(TEST_INDEX, 'contract', {'address': address, 'bytecode': TEST_BYTECODES[i]}, refresh=True)
    self.contract_methods.search_methods()
    iterator = self.contract_methods._iterate_contracts()
    contracts = contracts = [c for contracts_list in iterator for c in contracts_list]
    tokens = [contract['_source']['token_name'] for contract in contracts if contract['_source']['is_token'] == True]
    self.assertCountEqual(['RUN COIN', 'bangbeipay', 'YNOTCoin', 'Josh Bucks'], tokens)
    
TEST_INDEX = 'test-ethereum-contracts'
TEST_EMPTY_CONTRACT = '0xd3857e9ab037454e47281e51e42fc3e32677337f'
TEST_CONTRACT_ADDRESSES = ['0xa0e89120768bf166d228988627e4ac8af350220a', '0x6d6fb0951b769a6246f0246472856b2f70049c53', '0xaff9f95b455662c893bf3bb752557faa962d8355', '0x6Dabe61eD0212141951292e47d866cf0b3F2bfBD', '0x7681ac00c991852ad683d235377e8557256d769f']
TEST_BYTECODES = ['0x60a060405260046060527f48302e31000000000000000000000000000000000000000000000000000000006080526006805460008290527f48302e310000000000000000000000000000000000000000000000000000000882556100b5907ff652222313e28459528d920b65115c16c04f3efc82aaedc97be59f3f377c0d3f602060026001841615610100026000190190931692909204601f01919091048101905b8082111561017957600081556001016100a1565b505060405161094b38038061094b83398101604052808051906020019091908051820191906020018051906020019091908051820191906020015050836000600050600033600160a060020a0316815260200190815260200160002060005081905550836002600050819055508260036000509080519060200190828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f1061017d57805160ff19168380011785555b506101ad9291506100a1565b5090565b8280016001018555821561016d579182015b8281111561016d57825182600050559160200191906001019061018f565b50506004805460ff19168317905560058054825160008390527f036b6384b5eca791c62761152d0c79bb0604c104a5fb6f4eb0703f3154bb3db0602060026001851615610100026000190190941693909304601f90810184900482019386019083901061022d57805160ff19168380011785555b5061025d9291506100a1565b82800160010185558215610221579182015b8281111561022157825182600050559160200191906001019061023f565b5050505050506106da806102716000396000f36060604052361561008d5760e060020a600035046306fdde038114610095578063095ea7b3146100f357806318160ddd1461016857806323b872dd14610171578063313ce5671461025c57806354fd4d501461026857806370a08231146102c657806395d89b41146102f4578063a9059cbb14610352578063cae9ca51146103f7578063dd62ed3e146105be575b6105f2610002565b6040805160038054602060026001831615610100026000190190921691909104601f81018290048202840182019094528383526105f493908301828280156106b75780601f1061068c576101008083540402835291602001916106b7565b61066260043560243533600160a060020a03908116600081815260016020908152604080832094871680845294825280832086905580518681529051929493927f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925929181900390910190a35060015b92915050565b6102e260025481565b610662600435602435604435600160a060020a0383166000908152602081905260408120548290108015906101c4575060016020908152604080832033600160a060020a03168452909152812054829010155b80156101d05750600082115b156106bf57600160a060020a0383811660008181526020818152604080832080548801905588851680845281842080548990039055600183528184203390961684529482529182902080548790039055815186815291519293927fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef9281900390910190a35060016106c3565b61067660045460ff1681565b6040805160068054602060026001831615610100026000190190921691909104601f81018290048202840182019094528383526105f493908301828280156106b75780601f1061068c576101008083540402835291602001916106b7565b600160a060020a03600435166000908152602081905260409020545b60408051918252519081900360200190f35b6105f46005805460408051602060026001851615610100026000190190941693909304601f810184900484028201840190925281815292918301828280156106b75780601f1061068c576101008083540402835291602001916106b7565b61066260043560243533600160a060020a03166000908152602081905260408120548290108015906103845750600082115b156106ca5733600160a060020a0390811660008181526020818152604080832080548890039055938716808352918490208054870190558351868152935191937fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef929081900390910190a3506001610162565b604080516020604435600481810135601f810184900484028501840190955284845261066294813594602480359593946064949293910191819084018382808284375094965050505050505033600160a060020a03908116600081815260016020908152604080832094881680845294825280832087905580518781529051929493927f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925929181900390910190a383600160a060020a031660405180807f72656365697665417070726f76616c28616464726573732c75696e743235362c81526020017f616464726573732c627974657329000000000000000000000000000000000000815260200150602e019050604051809103902060e060020a9004338530866040518560e060020a0281526004018085600160a060020a0316815260200184815260200183600160a060020a031681526020018280519060200190808383829060006004602084601f0104600f02600301f150905090810190601f1680156105965780820380516001836020036101000a031916815260200191505b509450505050506000604051808303816000876161da5a03f19250505015156106d257610002565b6102e2600435602435600160a060020a03828116600090815260016020908152604080832093851683529290522054610162565b005b60405180806020018281038252838181518152602001915080519060200190808383829060006004602084601f0104600f02600301f150905090810190601f1680156106545780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b604080519115158252519081900360200190f35b6040805160ff9092168252519081900360200190f35b820191906000526020600020905b81548152906001019060200180831161069a57829003601f168201915b505050505081565b5060005b9392505050565b506000610162565b5060016106c356',
    "0x6060604052600436106101275763ffffffff7c010000000000000000000000000000000000000000000000000000000060003504166305fefda7811461012c57806306fdde0314610147578063095ea7b3146101d157806318160ddd1461020757806323b872dd1461022c578063313ce5671461025457806342966c681461027d5780634b7503341461029357806370a08231146102a657806379c65068146102c557806379cc6790146102e75780638620410b146103095780638da5cb5b1461031c57806395d89b411461034b578063a6f2ae3a1461035e578063a9059cbb14610366578063b414d4b614610388578063cae9ca51146103a7578063dd62ed3e1461040c578063e4849b3214610431578063e724529c14610447578063f2fde38b1461046b575b600080fd5b341561013757600080fd5b61014560043560243561048a565b005b341561015257600080fd5b61015a6104b0565b60405160208082528190810183818151815260200191508051906020019080838360005b8381101561019657808201518382015260200161017e565b50505050905090810190601f1680156101c35780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b34156101dc57600080fd5b6101f3600160a060020a036004351660243561054e565b604051901515815260200160405180910390f35b341561021257600080fd5b61021a61057e565b60405190815260200160405180910390f35b341561023757600080fd5b6101f3600160a060020a0360043581169060243516604435610584565b341561025f57600080fd5b6102676105fb565b60405160ff909116815260200160405180910390f35b341561028857600080fd5b6101f3600435610604565b341561029e57600080fd5b61021a61068f565b34156102b157600080fd5b61021a600160a060020a0360043516610695565b34156102d057600080fd5b610145600160a060020a03600435166024356106a7565b34156102f257600080fd5b6101f3600160a060020a036004351660243561076d565b341561031457600080fd5b61021a610849565b341561032757600080fd5b61032f61084f565b604051600160a060020a03909116815260200160405180910390f35b341561035657600080fd5b61015a61085e565b6101456108c9565b341561037157600080fd5b610145600160a060020a03600435166024356108e9565b341561039357600080fd5b6101f3600160a060020a03600435166108f8565b34156103b257600080fd5b6101f360048035600160a060020a03169060248035919060649060443590810190830135806020601f8201819004810201604051908101604052818152929190602084018383808284375094965061090d95505050505050565b341561041757600080fd5b61021a600160a060020a0360043581169060243516610a3f565b341561043c57600080fd5b610145600435610a5c565b341561045257600080fd5b610145600160a060020a03600435166024351515610ab9565b341561047657600080fd5b610145600160a060020a0360043516610b45565b60005433600160a060020a039081169116146104a557600080fd5b600791909155600855565b60018054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156105465780601f1061051b57610100808354040283529160200191610546565b820191906000526020600020905b81548152906001019060200180831161052957829003601f168201915b505050505081565b600160a060020a033381166000908152600660209081526040808320938616835292905220819055600192915050565b60045481565b600160a060020a038084166000908152600660209081526040808320339094168352929052908120548211156105b957600080fd5b600160a060020a03808516600090815260066020908152604080832033909416835292905220805483900390556105f1848484610b8f565b5060019392505050565b60035460ff1681565b600160a060020a0333166000908152600560205260408120548290101561062a57600080fd5b600160a060020a03331660008181526005602052604090819020805485900390556004805485900390557fcc16f5dbb4873280815c1ee09dbd06736cffcc184412cf7a71a0fdb75d397ca59084905190815260200160405180910390a2506001919050565b60075481565b60056020526000908152604090205481565b60005433600160a060020a039081169116146106c257600080fd5b600160a060020a03808316600090815260056020526040808220805485019055600480548501905530909216917fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef9084905190815260200160405180910390a381600160a060020a031630600160a060020a03167fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef8360405190815260200160405180910390a35050565b600160a060020a0382166000908152600560205260408120548290101561079357600080fd5b600160a060020a03808416600090815260066020908152604080832033909416835292905220548211156107c657600080fd5b600160a060020a038084166000818152600560209081526040808320805488900390556006825280832033909516835293905282902080548590039055600480548590039055907fcc16f5dbb4873280815c1ee09dbd06736cffcc184412cf7a71a0fdb75d397ca59084905190815260200160405180910390a250600192915050565b60085481565b600054600160a060020a031681565b60028054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156105465780601f1061051b57610100808354040283529160200191610546565b6000600854348115156108d857fe5b0490506108e6303383610b8f565b50565b6108f4338383610b8f565b5050565b60096020526000908152604090205460ff1681565b60008361091a818561054e565b15610a375780600160a060020a0316638f4ffcb1338630876040518563ffffffff167c01000000000000000000000000000000000000000000000000000000000281526004018085600160a060020a0316600160a060020a0316815260200184815260200183600160a060020a0316600160a060020a0316815260200180602001828103825283818151815260200191508051906020019080838360005b838110156109d05780820151838201526020016109b8565b50505050905090810190601f1680156109fd5780820380516001836020036101000a031916815260200191505b5095505050505050600060405180830381600087803b1515610a1e57600080fd5b6102c65a03f11515610a2f57600080fd5b505050600191505b509392505050565b600660209081526000928352604080842090915290825290205481565b6007548102600160a060020a033016311015610a7757600080fd5b610a82333083610b8f565b33600160a060020a03166108fc60075483029081150290604051600060405180830381858888f1935050505015156108e657600080fd5b60005433600160a060020a03908116911614610ad457600080fd5b600160a060020a03821660009081526009602052604090819020805460ff19168315151790557f48335238b4855f35377ed80f164e8c6f3c366e54ac00b96a6402d4a9814a03a5908390839051600160a060020a039092168252151560208201526040908101905180910390a15050565b60005433600160a060020a03908116911614610b6057600080fd5b6000805473ffffffffffffffffffffffffffffffffffffffff1916600160a060020a0392909216919091179055565b600160a060020a0382161515610ba457600080fd5b600160a060020a03831660009081526005602052604090205481901015610bca57600080fd5b600160a060020a03821660009081526005602052604090205481810111610bf057600080fd5b600160a060020a03831660009081526009602052604090205460ff1615610c1657600080fd5b600160a060020a03821660009081526009602052604090205460ff1615610c3c57600080fd5b600160a060020a038084166000818152600560205260408082208054869003905592851680825290839020805485019055917fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef9084905190815260200160405180910390a35050505600a165627a7a72305820f763879a776dcb694a89a7f513363f09c42efc65fe50f91792ec6523f1e540f00029",
    '0x60a060405260046060527f48302e31000000000000000000000000000000000000000000000000000000006080526006805460008290527f48302e310000000000000000000000000000000000000000000000000000000882556100b5907ff652222313e28459528d920b65115c16c04f3efc82aaedc97be59f3f377c0d3f602060026001841615610100026000190190931692909204601f01919091048101905b8082111561017957600081556001016100a1565b505060405161094b38038061094b83398101604052808051906020019091908051820191906020018051906020019091908051820191906020015050836000600050600033600160a060020a0316815260200190815260200160002060005081905550836002600050819055508260036000509080519060200190828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f1061017d57805160ff19168380011785555b506101ad9291506100a1565b5090565b8280016001018555821561016d579182015b8281111561016d57825182600050559160200191906001019061018f565b50506004805460ff19168317905560058054825160008390527f036b6384b5eca791c62761152d0c79bb0604c104a5fb6f4eb0703f3154bb3db0602060026001851615610100026000190190941693909304601f90810184900482019386019083901061022d57805160ff19168380011785555b5061025d9291506100a1565b82800160010185558215610221579182015b8281111561022157825182600050559160200191906001019061023f565b5050505050506106da806102716000396000f36060604052361561008d5760e060020a600035046306fdde038114610095578063095ea7b3146100f357806318160ddd1461016857806323b872dd14610171578063313ce5671461025c57806354fd4d501461026857806370a08231146102c657806395d89b41146102f4578063a9059cbb14610352578063cae9ca51146103f7578063dd62ed3e146105be575b6105f2610002565b6040805160038054602060026001831615610100026000190190921691909104601f81018290048202840182019094528383526105f493908301828280156106b75780601f1061068c576101008083540402835291602001916106b7565b61066260043560243533600160a060020a03908116600081815260016020908152604080832094871680845294825280832086905580518681529051929493927f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925929181900390910190a35060015b92915050565b6102e260025481565b610662600435602435604435600160a060020a0383166000908152602081905260408120548290108015906101c4575060016020908152604080832033600160a060020a03168452909152812054829010155b80156101d05750600082115b156106bf57600160a060020a0383811660008181526020818152604080832080548801905588851680845281842080548990039055600183528184203390961684529482529182902080548790039055815186815291519293927fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef9281900390910190a35060016106c3565b61067660045460ff1681565b6040805160068054602060026001831615610100026000190190921691909104601f81018290048202840182019094528383526105f493908301828280156106b75780601f1061068c576101008083540402835291602001916106b7565b600160a060020a03600435166000908152602081905260409020545b60408051918252519081900360200190f35b6105f46005805460408051602060026001851615610100026000190190941693909304601f810184900484028201840190925281815292918301828280156106b75780601f1061068c576101008083540402835291602001916106b7565b61066260043560243533600160a060020a03166000908152602081905260408120548290108015906103845750600082115b156106ca5733600160a060020a0390811660008181526020818152604080832080548890039055938716808352918490208054870190558351868152935191937fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef929081900390910190a3506001610162565b604080516020604435600481810135601f810184900484028501840190955284845261066294813594602480359593946064949293910191819084018382808284375094965050505050505033600160a060020a03908116600081815260016020908152604080832094881680845294825280832087905580518781529051929493927f8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925929181900390910190a383600160a060020a031660405180807f72656365697665417070726f76616c28616464726573732c75696e743235362c81526020017f616464726573732c627974657329000000000000000000000000000000000000815260200150602e019050604051809103902060e060020a9004338530866040518560e060020a0281526004018085600160a060020a0316815260200184815260200183600160a060020a031681526020018280519060200190808383829060006004602084601f0104600f02600301f150905090810190601f1680156105965780820380516001836020036101000a031916815260200191505b509450505050506000604051808303816000876161da5a03f19250505015156106d257610002565b6102e2600435602435600160a060020a03828116600090815260016020908152604080832093851683529290522054610162565b005b60405180806020018281038252838181518152602001915080519060200190808383829060006004602084601f0104600f02600301f150905090810190601f1680156106545780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b604080519115158252519081900360200190f35b6040805160ff9092168252519081900360200190f35b820191906000526020600020905b81548152906001019060200180831161069a57829003601f168201915b505050505081565b5060005b9392505050565b506000610162565b5060016106c356',
    '0x6060604052341561000f57600080fd5b6040516107513803806107518339810160405280805182019190602001805182019190602001805182019190602001805182019190602001805182019190602001805182019190602001805160008054600160a060020a03191633600160a060020a0316179055919091019050600187805161008f929160200190610114565b5060028680516100a3929160200190610114565b5060038580516100b7929160200190610114565b5060048480516100cb929160200190610114565b5060058380516100df929160200190610114565b5060068280516100f3929160200190610114565b506007818051610107929160200190610114565b50505050505050506101af565b828054600181600116156101000203166002900490600052602060002090601f016020900481019282601f1061015557805160ff1916838001178555610182565b82800160010185558215610182579182015b82811115610182578251825591602001919060010190610167565b5061018e929150610192565b5090565b6101ac91905b8082111561018e5760008155600101610198565b90565b610593806101be6000396000f3006060604052600436106100985763ffffffff7c0100000000000000000000000000000000000000000000000000000000600035041663218fd1c4811461009d57806331e8c7ba146101275780633eb1eb1a1461013a57806349cf2eae1461014d5780635f1ff54914610189578063a2240eb01461019c578063afa936b8146101af578063b1cb0db3146101c4578063f82ec3e6146101d7575b600080fd5b34156100a857600080fd5b6100b06101ea565b60405160208082528190810183818151815260200191508051906020019080838360005b838110156100ec5780820151838201526020016100d4565b50505050905090810190601f1680156101195780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b341561013257600080fd5b6100b0610288565b341561014557600080fd5b6100b06102f3565b341561015857600080fd5b61016061035e565b60405173ffffffffffffffffffffffffffffffffffffffff909116815260200160405180910390f35b341561019457600080fd5b6100b061037a565b34156101a757600080fd5b6100b06103e5565b34156101ba57600080fd5b6101c2610450565b005b34156101cf57600080fd5b6100b0610491565b34156101e257600080fd5b6100b06104fc565b60018054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156102805780601f1061025557610100808354040283529160200191610280565b820191906000526020600020905b81548152906001019060200180831161026357829003601f168201915b505050505081565b60038054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156102805780601f1061025557610100808354040283529160200191610280565b60078054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156102805780601f1061025557610100808354040283529160200191610280565b60005473ffffffffffffffffffffffffffffffffffffffff1681565b60048054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156102805780601f1061025557610100808354040283529160200191610280565b60068054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156102805780601f1061025557610100808354040283529160200191610280565b6000543373ffffffffffffffffffffffffffffffffffffffff90811691161461047857600080fd5b3273ffffffffffffffffffffffffffffffffffffffff16ff5b60058054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156102805780601f1061025557610100808354040283529160200191610280565b60028054600181600116156101000203166002900480601f0160208091040260200160405190810160405280929190818152602001828054600181600116156101000203166002900480156102805780601f10610255576101008083540402835291602001916102805600a165627a7a72305820e927c42bcb07ebb80bff298873e50f5c9a815ce3f9b9eee5eeb087ec5a50e109002900000000000000000000000000000000000000000000000000000000000000e00000000000000000000000000000000000000000000000000000000000000120000000000000000000000000000000000000000000000000000000000000016000000000000000000000000000000000000000000000000000000000000001a000000000000000000000000000000000000000000000000000000000000001e000000000000000000000000000000000000000000000000000000000000002200000000000000000000000000000000000000000000000000000000000000340000000000000000000000000000000000000000000000000000000000000000e524f53454e205377697373204147000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000001544494e20454e2049534f2031343030313a323031350000000000000000000000000000000000000000000000000000000000000000000000000000000000000a44453030383432362d3100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a30342f33302f3230313800000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000a30342f32392f323032310000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000f0496e7370656374696f6e202620696e746567726974792073657276696365732c206669656c642070726f6475637473202620736572766963657320616e6420696e74656c6c6967656e7420706c617374696320736f6c7574696f6e7320666f7220746865206f696c2c2067617320616e6420776174657220737570706c7920696e6475737472792061732077656c6c2061732074686520646576656c6f706d656e7420616e64206661627269636174696f6e206f662074686520726571756972656420746f6f6c732c206163636573736f726965732c2065717569706d656e7420616e642070726f636564757265732000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002942757265617520566572697461732043657274696669636174696f6e204765726d616e7920476d62480000000000000000000000000000000000000000000000',
    '0x606060405263ffffffff7c010000000000000000000000000000000000000000000000000000000060003504166306fdde038114610066578063313ce567146100f657806370a082311461011c57806395d89b4114610157578063a9059cbb146101e7575bfe5b341561006e57fe5b610076610215565b6040805160208082528351818301528351919283929083019185019080838382156100bc575b8051825260208311156100bc57601f19909201916020918201910161009c565b505050905090810190601f1680156100e85780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b34156100fe57fe5b6101066102a3565b6040805160ff9092168252519081900360200190f35b341561012457fe5b61014573ffffffffffffffffffffffffffffffffffffffff600435166102ac565b60408051918252519081900360200190f35b341561015f57fe5b6100766102be565b6040805160208082528351818301528351919283929083019185019080838382156100bc575b8051825260208311156100bc57601f19909201916020918201910161009c565b505050905090810190601f1680156100e85780820380516001836020036101000a031916815260200191505b509250505060405180910390f35b34156101ef57fe5b61021373ffffffffffffffffffffffffffffffffffffffff6004351660243561034b565b005b6000805460408051602060026001851615610100026000190190941693909304601f8101849004840282018401909252818152929183018282801561029b5780601f106102705761010080835404028352916020019161029b565b820191906000526020600020905b81548152906001019060200180831161027e57829003601f168201915b505050505081565b60025460ff1681565b60036020526000908152604090205481565b60018054604080516020600284861615610100026000190190941693909304601f8101849004840282018401909252818152929183018282801561029b5780601f106102705761010080835404028352916020019161029b565b820191906000526020600020905b81548152906001019060200180831161027e57829003601f168201915b505050505081565b73ffffffffffffffffffffffffffffffffffffffff3316600090815260036020526040902054819010806103a5575073ffffffffffffffffffffffffffffffffffffffff8216600090815260036020526040902054818101105b156103b05760006000fd5b73ffffffffffffffffffffffffffffffffffffffff338116600081815260036020908152604080832080548790039055938616808352918490208054860190558351858152935191937fddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef929081900390910190a35b50505600a165627a7a723058204b9b10c1454a0c1f1fe9a5ba79c52533376392073a3d926a6dad6ee2e8c175290029'
    ]
