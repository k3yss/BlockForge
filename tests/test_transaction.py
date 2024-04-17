import unittest
import os
from src.transaction import *
from src.helper import calculate_double_sha256_hash, calculate_sha256_hash
import json
import sys
import logging


class TestTransaction(unittest.TestCase):
    json_data_folder = "./tests/test_data"

    def test_segwit_serialization(self):
        segwit_json_files = [
            "0ac4f7f16822968c9fbc25e811c8acc05f29cf442f26ddfd69c1074abede59c9.json",
            "0030b203ff93ff7f4c6fdabda1026a8167038dfb94985669721086df9ad4337a.json",
        ]

        # iterate it in reverse order
        for segwit_json_file in reversed(segwit_json_files):
            # load segwit json data
            with open(
                os.path.join(f"{self.json_data_folder}/segwit", segwit_json_file), "r"
            ) as f:
                segwit_json_data = json.load(f)
                expected_sigwit_filename = segwit_json_file[:-5]
                serialized_transaction = serialise_transaction(segwit_json_data, True)

                txid = calculate_double_sha256_hash(serialized_transaction)
                calculated_filename = calculate_sha256_hash(txid).hex()
                self.assertEqual(calculated_filename, expected_sigwit_filename)

    def test_non_segwit_serialization(self):
        non_segwit_json_files = [
            "0a8b21af1cfcc26774df1f513a72cd362a14f5a598ec39d915323078efb5a240.json",
            "0a70cacb1ac276056e57ebfb0587d2091563e098c618eebf4ed205d123a3e8c4.json",
        ]

        # iterate over both the files
        for non_segwit_json_file in non_segwit_json_files:
            with open(
                os.path.join(
                    f"{self.json_data_folder}/non_segwit", non_segwit_json_file
                ),
                "r",
            ) as f:
                expected_nonsigwit_filename = non_segwit_json_file[:-5]
                non_segwit_json_data = json.load(f)
                serialized_transaction = serialise_transaction(
                    non_segwit_json_data, False
                )
                txid = calculate_double_sha256_hash(serialized_transaction)
                calculated_filename = calculate_sha256_hash(txid).hex()

                self.assertEqual(calculated_filename, expected_nonsigwit_filename)


if __name__ == "__main__":
    # logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    unittest.main()