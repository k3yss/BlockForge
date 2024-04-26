import unittest
import os

from src.helper import calculate_double_sha256_hash, Transaction, calculate_sha256_hash
import json
import logging
from src.block_generation.block_header import calculate_coinbase_transaction_hash


class TestTransaction(unittest.TestCase):
    coinbase_json_data = {
        "version": 2,
        "locktime": 4294967295,
        "vin": [
            {
                "txid": "0000000000000000000000000000000000000000000000000000000000000000",
                "vout": 4294967295,
                "prevout": {
                    "scriptpubkey": "41047eda6bd04fb27cab6e7c28c99b94977f073e912f25d1ff7165d9c95cd9bbe6da7e7ad7f2acb09e0ced91705f7616af53bee51a238b7dc527f2be0aa60469d140ac",
                    "scriptpubkey_asm": "OP_HASH160 OP_PUSHBYTES_20 423877331b30a905240c7e1f2adee4ebaa47c5f6 OP_EQUAL",
                    "scriptpubkey_type": "p2sh",
                    "scriptpubkey_address": "14gnf7L2DjBYKFuWb6iftBoWE9hmAoFbcF",
                    "value": 2504928,
                },
                "scriptsig": "03233708184d696e656420627920416e74506f6f6c373946205b8160a4256c0000946e0100",
                "scriptsig_asm": "OP_PUSHBYTES_22 001415ff0337937ecadd10ce56ffdfd4674817613223",
                "witness": [
                    "0000000000000000000000000000000000000000000000000000000000000000",
                ],
                "is_coinbase": True,
                "sequence": 4294967295,
                "inner_redeemscript_asm": "OP_0 OP_PUSHBYTES_20 15ff0337937ecadd10ce56ffdfd4674817613223",
            }
        ],
        "vout": [
            {
                "scriptpubkey": "76a91471a3d2f54b0917dc9d2c877b2861ac52967dec7f88ac",
                "scriptpubkey_asm": "OP_DUP OP_HASH160 OP_PUSHBYTES_20 71a3d2f54b0917dc9d2c877b2861ac52967dec7f OP_EQUALVERIFY OP_CHECKSIG",
                "scriptpubkey_type": "p2pkh",
                "scriptpubkey_address": "1BMscNZbFKdUDYi3bnF5XEmkWT3WPmRBDJ",
                "value": 28278016,
            },
            {
                "scriptpubkey": "faa194df59043645ba0f58aad74bfd5693fa497093174d12a4bb3b0574a878db",
                "scriptpubkey_asm": "OP_HASH160 OP_PUSHBYTES_20 423877331b30a905240c7e1f2adee4ebaa47c5f6 OP_EQUAL",
                "scriptpubkey_type": "p2sh",
                "scriptpubkey_address": "37jAAWEdJ9D9mXybRobcveioxSkt7Lkwog",
                "value": 0000000000000000,
            },
        ],
    }

    def test_coinbase_serialisation(self):
        coinbase_transaction_hash = calculate_coinbase_transaction_hash(
            self.coinbase_json_data
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    unittest.main()
