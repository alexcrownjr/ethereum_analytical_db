#!/usr/bin/env python3
import click
from operations import elasticsearch, clickhouse
from config import DATABASE

OPERATIONS = {
  "elasticsearch": {
    "prepare-indices": elasticsearch.prepare_indices
  },
  "clickhouse": {
    "prepare-indices": clickhouse.prepare_indices,
    "prepare-blocks": clickhouse.prepare_blocks,
    "prepare-contracts-view": clickhouse.prepare_contracts_view,
    "extract-traces": clickhouse.extract_traces,
    "extract-contracts-abi": clickhouse.extract_contracts_abi,
    "extract-transaction-fees": clickhouse.extract_transaction_fees,
    "extract-events": clickhouse.extract_events,
    "parse-transactions-inputs": clickhouse.parse_transactions_inputs,
    "parse-events-inputs": clickhouse.parse_events_inputs,
    "extract-token-transactions": clickhouse.extract_token_transactions
    "extract-multitransfers": clickhouse.extract_multitransfers,
    "extract-prices": clickhouse.extract_prices
  }
}

def get_operation(name):
  return OPERATIONS[DATABASE][name]

@click.command()
@click.option('--operation', help='Action to perform', default='prepare-indices')
def start_process(operation):
  get_operation(operation)()

if __name__ == '__main__':
  start_process()
