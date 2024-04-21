import unittest
from src.transaction import *
from src.helper import calculate_double_sha256_hash, calculate_sha256_hash
from src.block_generation.block_header import (
    calculate_block_header,
    calculate_merkle_root,
)
import logging


class TestBlockHeader(unittest.TestCase):
    def test_serialize_for_OP_CHECKSIG(self):
        transaction_list = [
            "4eda2b12862c3aff56323d76a33f0739c655249305ad68a49d73afd8b4ee6a89",
            "fbcca1ef33984eaad190fb0f481ac0f8c9d2f0baf7718794ef596f74abef2837",
        ]

        tmp = calculate_merkle_root(transaction_list)
        logging.debug(tmp)


if __name__ == "__main__":
    # logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    unittest.main()
