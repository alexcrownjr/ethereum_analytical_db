import requests
from custom_elastic_search import CustomElasticSearch
from config import INDICES
import datetime
from datetime import date
from pyelasticsearch import bulk_chunks
from tqdm import *
import time
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

MOVING_AVERAGE_WINDOW = 5

class TokenPrices:
  '''
  Extract token prices from Coinmarketcap and CryptoCompare and save in Elasticsearch
  '''
  def __init__(self, elasticsearch_indices=INDICES, elasticsearch_host='http://localhost:9200'):
    self.indices = elasticsearch_indices
    self.client = CustomElasticSearch(elasticsearch_host)

  def _chunks(self, l, n):
    '''
    Break list into list of n list of equal size

    Parameters
    ----------
    l: list
      Lisymbol_listst that will be breaked into chunks
    n: int
      Number of chunks
    '''
    for i in range(0, len(l), n):
        yield l[i:i+n]

  def _to_usd(self, value, price):
    '''
    Convert token BTC price to USD price

    Parameters
    ----------
    value: float
      Token price
    price: float
      BTC price in USD

    Returns
    -------
    float
      Token price in USD
    '''
    return value * price

  def _from_usd(self, value, price):
    '''
    Convert token USD price to BTC or ETH price

    Parameters
    ----------
    value: float
      Token price
    price: float
      USD price in BTC or ETH

    Returns
    -------
    float
      Token price in BTC or ETH
    '''
    return value / price

  def _iterate_cc_tokens(self):
    '''
    Iterate over token contracts that are listed on Cryptocompare

    Returns
    -------
    generator
      Generator that iterates over listed token contracts in Elasticsearch
    '''
    return self.client.iterate(self.indices['contract'], 'contract', 'cc_sym:*')

  def _get_cc_tokens(self):
    '''
    Extract list of tokens listed on Cryptocompare

    Returns
    -------
    list
      List of listed tokens contracts
    '''
    tokens = [token_chunk for token_chunk in self._iterate_cc_tokens()]
    token_list = [t['_source'] for token_chunk in tokens for t in token_chunk]
    return token_list

  def _get_prices_for_fsyms(self, symbol_list):
    '''
    Extract tokens historical prices from CryptoCompare
    
    Parameters
    ----------
    symbol_list: list
      List of token symbols

    Returns
    -------
    list
      List of tokens prices
    '''
    fsyms = ','.join(symbol_list)
    url = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms={}&tsyms=BTC'.format(fsyms)
    try:
      prices = requests.get(url).json()
    except:
      prices = None
    return prices

  def _make_multi_prices_req(self, tokens):
    '''
    Extract tokens BTC prices from CryptoCompare

    Parameters
    ----------
    tokens: list
      List of tokens

    Returns
    -------
    list
      List of tokens prices
    '''
    token_list_chunks = list(self._chunks(tokens, 60))
    all_prices = []
    for symbols in token_list_chunks:
      prices = self._get_prices_for_fsyms(symbols)
      if prices != None:
        prices = [{'token': key, 'BTC': float('{:0.10f}'.format(prices[key]['BTC']))} for key in prices.keys()]
        all_prices.append(prices)
    all_prices = [price for prices in all_prices for price in prices]
    return all_prices

  def _get_btc_eth_current_prices(self):
    '''
    Extract current BTC and ETH prices from CryptoCompare
    '''
    url = 'https://min-api.cryptocompare.com/data/pricemulti?fsyms=BTC,ETH&tsyms=USD'
    res = requests.get(url).json()
    self.btc_price = res['BTC']['USD']
    self.eth_price = res['ETH']['USD']

  def _get_multi_prices(self):
    '''
    Extract listed tokens current prices from CryptoCompare

    Returns
    -------
    list
      List of tokens prices
    '''
    now = datetime.datetime.now()
    self._get_btc_eth_current_prices()
    token_syms = [token['cc_sym'] for token in self._get_cc_tokens()]
    prices = self._make_multi_prices_req(token_syms)
    for price in prices:
      price['USD'] = float('{:0.10f}'.format(self._to_usd(price['BTC'], self.btc_price)))
      price['ETH'] = float('{:0.10f}'.format(self._from_usd(price['USD'], self.eth_price)))
      price['timestamp'] = now.strftime("%Y-%m-%d")
    return prices

  def _construct_bulk_insert_ops(self, docs):
    '''
    Iterate over docs and create document-inserting operations used in bulk insert

    Parameters
    ----------
    docs: list
      List of dictionaries with new data
    '''
    for doc in docs:
      yield self.client.index_op(doc, id=doc['token']+'_'+doc['timestamp'])

  def _insert_multiple_docs(self, docs, doc_type, index_name):
    ''' 
    Index multiple documents simultaneously

    Parameters
    ----------
    docs: list
      List of dictionaries with new data
    doc_type: str 
      Type of inserted documents
    index_name: str
      Name of the index that contains inserted documents
    '''
    for chunk in bulk_chunks(self._construct_bulk_insert_ops(docs), docs_per_chunk=1000):
      self.client.bulk(chunk, doc_type=doc_type, index=index_name, refresh=True)

  def get_recent_token_prices(self):
    '''
    Extract listed tokens current prices from CryptoCompare and saves in Elasticsearch
    '''
    prices = self._get_multi_prices()
    self._insert_multiple_docs(prices, 'price', self.indices['token_price'])

  def _set_moving_average(self, prices):
    prices_stack = []
    for price in prices:
      prices_stack.append(price["close"])
      if len(prices_stack) == MOVING_AVERAGE_WINDOW:
        price["average"] = np.mean(prices_stack)
        prices_stack.pop(0)
      else:
        price["average"] = price["close"]

  def _process_hist_prices(self, prices):
    '''
    Convert tokens historical prices from BTC to USD and ETH

    Parameters
    ----------
    prices: list
      List of tokens prices

    Returns
    -------
    list
      List of tokens prices
    '''
    points = []
    self._set_moving_average(prices)
    for price in prices:
      point = {}
      point['BTC'] = price["average"]
      point['BTC'] = float('{:0.10f}'.format(point['BTC']))
      point['timestamp'] = datetime.datetime.fromtimestamp(price['time']).strftime("%Y-%m-%d")
      point['token'] = price['token']
      point['USD'] = self._to_usd(point['BTC'], self.btc_prices[point['timestamp']])
      point['USD'] = float('{:0.10f}'.format(point['USD']))
      if point['timestamp'] in self.eth_prices.keys():
        point['ETH'] = self._from_usd(point['USD'], self.eth_prices[point['timestamp']])
        point['ETH'] = float('{:0.10f}'.format(point['ETH']))
      point['source'] = 'cryptocompare'
      points.append(point)
    return points

  def _make_historical_prices_req(self, symbol, days_count):
    '''
    Make call to CryptoCompare API to extract token historical data

    Parameters
    ----------
    symbol: str
      Token symbol
    days_count: int
      Days limit

    Returns
    -------
    list
      List of token historical prices
    '''
    url = 'https://min-api.cryptocompare.com/data/histoday?fsym={}&tsym=BTC&limit={}'.format(symbol, days_count)
    try:
      res = requests.get(url).json()
      for point in res['Data']:
        point['token'] = symbol
      return res['Data']
    except:
      return

  def _get_last_avail_price_date(self):
    '''
    Get last price available in Elasticsearch token_price index

    Returns
    -------
    string
      Timestamp of last available date or 2013-01-01 if there are no prices in index
    '''
    query = {
      "from" : 0, "size" : 1,
      'sort': {
        'timestamp': {'order': 'desc'}
      }
    }
    try:
      res = self.client.send_request('GET', [self.indices['token_price'], 'price', '_search'], query, {})['hits']['hits']
      last_date = res[0]['_source']['timestamp']
    except:
      last_date = '2013-01-01'
    last_date = last_date.split('-')
    return last_date

  def _convert_btc_eth_prices(self, price):
    '''
    Convert BTC and ETH prices into usable format

    Parameters
    ----------
    price: dict
      A dictionary with raw data from cryptocompare

    Returns
    -------
    dict
      A dictionary with converted price data
    '''
    point = {}
    point['USD'] = (price['open'] + price['close']) / 2
    point['date'] = datetime.datetime.fromtimestamp(price['time']).strftime("%Y-%m-%d")
    return point

  def _get_btc_eth_prices(self):
    '''
    Extract BTC and ETH historcial data and convert it into usable format
    '''
    btc_prices = requests.get('https://min-api.cryptocompare.com/data/histoday?fsym=BTC&tsym=USD&allData=true').json()['Data']
    eth_prices = requests.get('https://min-api.cryptocompare.com/data/histoday?fsym=ETH&tsym=USD&allData=true').json()['Data']
    btc_prices = [self._convert_btc_eth_prices(price) for price in btc_prices]
    eth_prices = [self._convert_btc_eth_prices(price) for price in eth_prices]
    btc_prices_dict = {price['date']: price['USD'] for price in btc_prices}
    eth_prices_dict = {price['date']: price['USD'] for price in eth_prices}
    self.btc_prices = btc_prices_dict
    self.eth_prices = eth_prices_dict

  def _get_days_count(self, now, last_price_date):
    '''
    Count number of days for that prices are unavailable

    Parameters
    ----------
    now: str
      Current date
    last_price_date: str
      Timestamp of last available price

    Returns
    -------
    int
      Number of days
    '''
    start_date = date(int(now[0]), int(now[1]), int(now[2]))
    end_date = date(int(last_price_date[0]), int(last_price_date[1]), int(last_price_date[2]))
    days_count = (start_date - end_date).days + 1
    return days_count

  def _get_historical_multi_prices(self):
    '''
    Extract historical token prices from CryptoCompare

    Returns
    -------
    list
      List ot token historical prices
    '''
    self._get_btc_eth_prices()
    token_syms = [token['cc_sym'] for token in self._get_cc_tokens()]
    now = datetime.datetime.now().strftime("%Y-%m-%d").split('-')
    last_price_date = self._get_last_avail_price_date()
    days_count = self._get_days_count(now, last_price_date)
    prices = []
    for token in tqdm(token_syms):
      price = self._make_historical_prices_req(token, days_count)
      if price != None:
        price = self._process_hist_prices(price) 
        prices.append(price)
      else:
        continue
    prices = [p for price in prices for p in price]
    return prices

  def get_prices_within_interval(self):
    '''
    Extract historcial token prices and then add to this prices data from Coinmarketcap

    This function is an entry point for extract-prices operation
    '''
    prices = self._get_historical_multi_prices()
    if prices != None:
      self._insert_multiple_docs(prices, 'price', self.indices['token_price'])
    self.add_market_cap()

  def _construct_bulk_update_ops(self, docs):
    '''
    Iterate over docs and create document-updating operations used in bulk update

    Parameters
    ----------
    docs: list
      List of dictionaries with new data
    '''
    for doc in docs:
      yield self.client.update_op(doc, id=doc['token'] + '_' + doc['timestamp'], upsert=doc)

  def _update_multiple_docs(self, docs, doc_type, index_name):
    '''
    Update multiple documents simultaneously

    Parameters
    ----------
    docs: list
      List of dictionaries with new data
    doc_type: str 
      Type of updated documents
    index_name: str
      Name of the index that contains updated documents
    '''
    for chunk in bulk_chunks(self._construct_bulk_update_ops(docs), docs_per_chunk=1000):
      self.client.bulk(chunk, doc_type=doc_type, index=index_name, refresh=True)

  def _iterate_cmc_tokens(self):
    '''
    Iterate over token contracts that are listed on Coinmarketcap

    Returns
    -------
    generator
      Generator that iterates over listed token contracts in Elasticsearch
    '''
    return self.client.iterate(self.indices['contract'], 'contract', '_exists_:website_slug')

  def get_token_list(self):
    '''
    Scrap page from Coinmarketcap that contains a list of all token and parse this list to pandas DataFrame

    Returns
    -------
    pandas.DataFrame
      DataFrame with list of tokens and corresponding links to token pages
    '''
    url = 'https://coinmarketcap.com/tokens/views/all/'
    res = requests.get(url).text
    soup = BeautifulSoup(res, 'html.parser')
    links = soup.find_all(class_='currency-name-container')
    links = ['https://coinmarketcap.com' + link['href'] for link in links]
    slugs = [link.split('/') for link in links]
    slugs = [l[len(l) - 2] for l in slugs]
    tokens = pd.read_html(res)[0]
    tokens['link'] = links
    tokens['slug'] = slugs
    tokens = tokens.loc[tokens.Platform == 'Ethereum']
    tokens = tokens[['Name', 'link', 'slug']]
    return tokens

  def get_token_cmc_historical_info(self, page):
    '''
    Scrap page from Coinmarketcap that contains a table with historical price info for token and parse 
    it to list of prices

    Parameters
    ----------
    page: str
      Link to the token page

    Returns
    -------
    list
      List of token historical prices
    '''
    today = datetime.date.today().strftime('%Y%m%d')
    url = page + 'historical-data/?start=20130428&end={}'.format(today)
    res = requests.get(url).text
    
    soup = BeautifulSoup(res, 'html.parser')
    symbol = soup.find(class_='details-panel-item--name')
    symbol = symbol.find('span').text if symbol != None else page.split('/')[4]
    symbol = symbol[1:len(symbol) -1]
    parsed_data = pd.read_html(res)[0]
    
    try:
      info = [{
        'market_cap': int(row['Market Cap']) if row['Market Cap'] != '-' and row['Market Cap']!=None else row['Market Cap'],
        'timestamp': datetime.datetime.strptime(row['Date'], '%b %d, %Y').strftime('%Y-%m-%d'),
        'USD': (row['Open*'] + row['Close**']) / 2,
        'token': symbol,
        'source': 'coinmarketcap'
      } for i, row in parsed_data.iterrows()]
      return info
    except:
      return page.split('/')[4]

  def get_historical_prices(self, links):
    '''
    Get historical prices from Coinmarketcap for specified list of tokens

    Parameters
    ----------
    links: list
      List of links to token pages

    Returns
    -------
    tuple
      Tuple that contains 2 elements: list of token prices and list of token names for 
      which Coinmarketcap didn't return data
    '''
    data = []
    unprocessed = []
    for i, link in tqdm_notebook(enumerate(links)):
        token_info = get_token_cmc_historical_info(link)
        if type(token_info) is str:
            unprocessed.append(token_info)
            continue
        data.append(token_info)
        if i > 0 and i % 10 == 0:
            time.sleep(10)
    data = [point for points in data for point in points]
    return data, unprocessed

  def get_current_cmc_prices(self):
    '''
    Get current token prices from Coinmarketcap API

    Returns
    -------
    list
      List of tokens prices
    '''
    eth_tokens = self.get_token_list()
    res = requests.get(
      'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=3000',
      headers={'X-CMC_PRO_API_KEY': '06eef9b3-7f2f-4f0a-9a5d-e3ff7a1dbf1a'}
      )
    prices = res.json()['data']
    btc_price = [price for price in prices if price['symbol'] == 'BTC'][0]['quote']['USD']['price']
    eth_price = [price for price in prices if price['symbol'] == 'ETH'][0]['quote']['USD']['price']
    today = date.today()
    prices = [{
      'token': p['symbol'], 
      'USD': p['quote']['USD']['price'],
      'ETH': float('{:0.10f}'.format(self._from_usd(p['quote']['USD']['price'], eth_price))),
      'BTC': float('{:0.10f}'.format(self._from_usd(p['quote']['USD']['price'], btc_price))),
      'source': 'coinmarketcap', 
      'market_cap': int(p['quote']['USD']['market_cap']),
      'timestamp': today,
      } for p in prices if p['slug'] in eth_tokens.slug.values]
    return prices
