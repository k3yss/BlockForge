import unittest
import logging
from src.helper import Transaction

# version: 02000000
# marker: 00
# flag: 01
# inputs:  01
#   txid: ac4994014aa36b7f53375658ef595b3cb2891e1735fe5b441686f5e53338e76a
#   vout: 01000000
#   scriptsigsize: 00
#   scriptsig:
#   sequence: ffffffff
# outputs: 01
#   amount: 204e000000000000
#   scriptpubkeysize: 19
#   scriptpubkey: 76a914ce72abfd0e6d9354a660c18f2825eb392f060fdc88ac
# witness: 00
# locktime: 00000000


class TestMessage(unittest.TestCase):
    json_data = {
        "version": 2,
        "locktime": 0,
        "vin": [
            {
                "txid": "6ae73833e5f58616445bfe35171e89b23c5b59ef585637537f6ba34a019449ac",
                "vout": 1,
                "prevout": {
                    "scriptpubkey": "0014aa966f56de599b4094b61aa68a2b3df9e97e9c48",
                    "scriptpubkey_asm": "OP_0 OP_PUSHBYTES_20 f8d9f2203c6f0773983392a487d45c0c818f9573",
                    "scriptpubkey_type": "v0_p2wpkh",
                    "scriptpubkey_address": "bc1qlrvlygpudurh8xpnj2jg04zupjqcl9tnk5np40",
                    "value": 30000,
                },
                "scriptsig": "",
                "scriptsig_asm": "",
                "witness": [],
                "is_coinbase": False,
                "sequence": 4294967295,
            }
        ],
        "vout": [
            {
                "scriptpubkey": "76a914ce72abfd0e6d9354a660c18f2825eb392f060fdc88ac",
                "scriptpubkey_asm": "OP_DUP OP_HASH160 OP_PUSHBYTES_20 6085312a9c500ff9cc35b571b0a1e5efb7fb9f16 OP_EQUALVERIFY OP_CHECKSIG",
                "scriptpubkey_type": "p2pkh",
                "scriptpubkey_address": "19oMRmCWMYuhnP5W61ABrjjxHc6RphZh11",
                "value": 20000,
            }
        ],
    }

    def test_message_generation(self):
        transaction = Transaction(self.json_data)
        # seralised_trasansaction = transaction.serialise_transaction(True)
        message = transaction.calculate_segwit_message(0, "01")
        logging.debug(f"{message=}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    unittest.main()
