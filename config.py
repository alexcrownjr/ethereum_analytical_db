from datetime import datetime

# URLs of parity APIs.
# You can specify block range for each URL to use different nodes for each request
# Make sure you have the same config as in dockerfile.yml for each node:
# --tracing=on
# --jsonrpc-interface=all
PARITY_HOSTS = [
    (None, None, "http://localhost:8545")
]

# Dictionary of table names in database.
# Meaning of each table explained in Schema
INDICES = {
    "contract": "eth_contract",
    "token_transaction": "eth_token_transaction",
    "transaction": "eth_transaction",
    "internal_transaction": "eth_internal_transaction",
    "listed_token": "eth_listed_token",
    "token_tx": "eth_token_transaction",
    "block": "eth_block",
    "price": "eth_token_price",
    "block_flag": "eth_block_flag",
    "contract_abi": "eth_contract_abi",
    "contract_block": "eth_contract_block",
    "transaction_input": "eth_transaction_input",
    "event_input": "eth_event_input",
    "miner_transaction": "eth_miner_transaction",
    "event": "eth_event",
    "contract_description": "eth_contract_description",
    "bancor_trade": "eth_bancor_trade"
}

# List of contract addresses to process in several operations.
# All other contracts will be skipped during certain operations
PROCESSED_CONTRACTS = ["0xe94327d07fc17907b4db788e5adf2ed424addff6", "0xd850942ef8811f2a866692a623011bde52a462c1", "0x9f8f72aa9304c8b593d555f12ef6589cc3a579a2", "0x744d70fdbe2ba4cf95131626614a1763df805b9e", "0xb5a5f22694352c15b00323844ad545abb2b11028", "0xfa1a856cfa3409cfa145fa4e20eb270df3eb21ab", "0xd26114cd6ee289accf82350c8d8487fedb8a0c07", "0x168296bb09e24a88805cb9c33356536b980d3fc5", "0x0d8775f648430679a709e98d2b0cb6250d2887ef", "0xa74476443119a942de498590fe1f2454d7d4ac0d", "0xd4fa1460f537bb9085d22c7bccb5dd450ef28e3a", "0x5ca9a71b1d01849c0a95490cc00559717fcf0d1d", "0xcb97e65f07da24d46bcdd078ebebd7c6e6e3d750", "0x86fa049857e0209aa7d9e616f7eb3b3b78ecfdb0", "0x05f4a42e251f2d52b8ed15e9fedaacfcef1fad27", "0xb8c77482e45f1f44de1745f52c74426c631bdd52", "0xb7cb1c96db6b22b0d3d9536e0108d062bd488f74", "0xe41d2489571d322189246dafa5ebde1f4699f498", "0xf230b790e05390fc8295f4d3f60332c93bed42e2", "0xe0b7927c4af23765cb51314a0e0521a9645f0e2a", "0xef68e7c694f40c8202821edf525de3782458639f", "0xbf2179859fc6d5bee9bf9158632dc51678a4100e", "0x1f573d6fb3f13d689ff844b4ce37794d79a7ff1c", "0x08d32b0da63e2c3bcf8019c9c5d849d7a9d791e6", "0x3893b9422cd5d70a81edeffe3d5a1c6a978310bb", "0x8f3470a7388c05ee4e7af3d01d8c722b0ff52374", "0x5af2be193a6abca9c8817001f45744777db30756", "0xd0352a019e9ab9d757776f532377aaebd36fd541", "0x419d0d8bdd9af5e606ae2232ed285aff190e711b", "0x4672bad527107471cb5067a887f4656d585a8a31", "0xb3104b4b9da82025e8b9f8fb28b3553ce2f67069", "0xa4e8c3ec456107ea67d3075bf9e3df3a75823db0", "0x618e75ac90b12c6049ba3b27f5d5f8651b0037f6", "0xb91318f35bdb262e9423bc7c7c2a3a93dd93c92c", "0xea11755ae41d889ceec39a63e6ff75a02bc1c00d", "0x0f5d2fb29fb7d3cfee444a200298f468908cc942", "0x9f5f3cfd7a32700c93f971637407ff17b91c7342", "0x818fc6c2ec5986bc6e2cbf00939d90556ab12ce5", "0x9992ec3cf6a55b00978cddf2b27bc6882d88d1ec", "0xf0ee6b27b759c9893ce4f094b49ad28fd15a23e4", "0x905e337c6c8645263d3521205aa37bf4d034e745", "0x12480e24eb5bec1a9d4369cab6a80cad3c0a377a", "0x3883f5e181fccaf8410fa61e12b59bad963fb645", "0x419c4db4b9e25d6db2ad9691ccb832c8d9fda05e", "0x595832f8fc6bf59c85c527fec3740a1b7a361269", "0x7e9e431a0b8c4d532c745b1043c7fa29a48d4fba", "0xd0a4b8946cb52f0661273bfbc6fd0e0c75fc6433", "0x01ff50f8b7f74e4f00580d9596cd3d0d6d6e326f", "0xc5bbae50781be1669306b9e001eff57a2957b09d", "0xb63b606ac810a52cca15e44bb630fd42d8d1d83d", "0x607f4c5bb672230e8672085532f7e901544a7375", "0xb64ef51c888972c908cfacf59b47c1afbc0ab8ac", "0x2d0e95bd4795d7ace0da3c0ff7b706a5970eb9d3", "0x39bb259f66e1c59d5abef88375979b4d20d98022", "0x48f775efbe4f5ece6e0df2f7b5932df56823b990", "0x38c6a68304cdefb9bec48bbfaaba5c5b47818bb2", "0xe25bcec5d3801ce3a794079bf94adf1b8ccd802d", "0x8f8221afbb33998d8584a2b05749ba73c37a938a", "0x4156d3342d5c385a87d264f90653733592000581", "0x514910771af9ca656af840dff83e8264ecf986ca", "0x41e5560054824ea6b0732e656e3ad64e20e94e45", "0xb62132e35a6c13ee1ee0f84dc5d40bad8d815206", "0x66186008c1050627f979d464eabb258860563dbe", "0xb97048628db6b661d4c2aa833e95dbe1a905b280", "0x8eb24319393716668d768dcec29356ae9cffe285", "0x983f6d60db79ea8ca4eb9968c6aff8cfa04b3c63", "0x36905fc93280f52362a1cbab151f25dc46742fb5", "0x960b236a07cf122663c4303350609a66a7b288c0", "0xf7920b0768ecb20a123fac32311d07d193381d6f", "0x8dd5fbce2f6a956c3022ba3663759011dd51e73e", "0xb98d4c97425d9908e66e53a6fdf673acca0be986", "0x809826cceab68c387726af962713b64cb5cb3cca", "0xf278c1ca969095ffddded020290cf8b5c424ace2", "0x7c5a0ce9267ed19b22f8cae653f198e3e8daf098", "0x5c3a228510d246b78a3765c20221cbf3082b44a4", "0xd4c435f5b09f855c3317c8524cb1f586e42795fa", "0x3597bfd533a99c9aa083587b074434e61eb0a258", "0x99ea4db9ee77acd40b119bd1dc4e33e1c070b80d", "0x6810e776880c02933d47db1b9fc05908e5386b96", "0xf629cbd94d3791c9250152bd8dfbdf380e2a3b9c", "0x57ad67acf9bf015e4820fbd66ea1a21bed8852ec", "0x4092678e4e78230f46a1534c0fbc8fa39780892b", "0x6ec8a24cabdc339a06a172f8223ea557055adaa5", "0x0cf0ee63788a0849fe5297f3407f701e122cc023", "0x80a7e048f37a50500351c204cb407766fa3bae7f", "0x55f93985431fc9304077687a35a1ba103dc1e081", "0xeda8b016efa8b1161208cf041cd86972eee0f31e", "0xd234bf2410a0009df9c3c63b610c09738f18ccd7", "0x014b50466590340d41307cc54dcee990c8d58aa8", "0x4dc3643dbc642b72c158e7f3d2ff232df61cb6ce", "0x46b9ad944d1059450da1163511069c718f699d31", "0xe3818504c1b32bf1557b16c238b2e01fd3149c17", "0x26e75307fc0c021472feb8f727839531f112f317", "0x3833dda0aeb6947b98ce454d89366cba8cc55528", "0x68d57c9a1c35f63e2c83ee8e49a64e9d70528d25", "0x255aa6df07540cb5d3d297f0d0d4d84cb52bc8e6", "0x408e41876cccdc0f92210600ef50372656052a38", "0x85e076361cc813a908ff672f9bad1541474402b2", "0x519475b31653e46d20cd09f9fdcf3b12bdacb4f5", "0x93e682107d1e9defb0b5ee701c71707a4b2e46bc", "0xa15c7ebe1f07caf6bff097d8a589fb8ac49ae5b3", "0xaec2e87e0a235266d9c5adc9deb4b2e29b54d009", "0x92e52a1a235d9a103d970901066ce910aacefd37"]

# Size of pages received from Clickhouse
BATCH_SIZE = 1000 # recommended

# Max size of chunk inserted into Clickhouse
MAX_CHUNK_SIZE = 20000000 # recommended, average size of block

# Number of chunks processed simultaneously while extracting transactions from parity
PARITY_EXTRACTION_PROCESSES = 3 # recommended

# Number of chunks processed simultaneously during input parsing
INPUT_PARSING_PROCESSES = 10 # recommended

# Number of blocks processed simultaneously during events extraction
EVENTS_RANGE_SIZE = 5 # recommended

# Max memory usage for clickhouse
MAX_MEMORY_USAGE = 1000000000 # recommended

# API key for etherscan.io ABI extraction
ETHERSCAN_API_KEY = "YourApiKeyToken"

DATABASE = "clickhouse"
GENESIS = "genesis.json"
ETHEREUM_START_DATE = datetime(2015, 7, 30)

# Node URL for tests
TEST_PARITY_NODE = "http://localhost:8545/"

NUMBER_OF_JOBS = BATCH_SIZE
