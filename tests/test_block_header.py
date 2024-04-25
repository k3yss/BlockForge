import unittest
from src.block_generation.block_header import (
    calculate_block_header,
    calculate_merkle_root,
)
import logging


class TestBlockHeader(unittest.TestCase):
    transaction_list = [
        "0843a125fdce55b2c87431a295a90732d02e8e547fb0b8e53e9c088d9e2e441b",
        "e2dbcac985d31594ffa1193638e6fa07c948ba8199158b9bcdc4ea2a39dadc50",
        "1d9e3caa9bcda611782372d0186a69bc20759f65a10e6566cb79a375bd5343de",
        "4e4b14e0d955bfa053ce4a7c3245ab1253406b480f70247d7a5ba92636d13926",
        "30296c8fd2fc9ef712dd572846767e4f8bd09788350ead55456e57db2fa22e45",
        "2b7222221ef1f49b38f0b7d5ce04a312dd4c56492ef4ca45fdaa57f419a4f2d4",
        "379c9c1070725589a0fa9626a59bfab6de21a50e600815be7d6af70edf059f3c",
    ]

    def test_calculate_block_header(self):
        # probably a useless test
        expected_block_header = "000000200000000000000000000000000000000000000000000000000000000000000000ca9c5c00c212be7a17ab9756a032a8fc9f9fcd0b5eafb27145fb18d9ecf85998c2542966ffff001f01090300"
        block_header = calculate_block_header(self.transaction_list).hex()
        logging.debug(block_header)
        self.assertNotEqual(block_header, expected_block_header)

    def test_merkle_root_generation(self):
        expected_result = (
            "ca9c5c00c212be7a17ab9756a032a8fc9f9fcd0b5eafb27145fb18d9ecf85998"
        )
        result = calculate_merkle_root(self.transaction_list)
        self.assertEqual(result, expected_result)


if __name__ == "__main__":
    # logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S",
    )
    unittest.main()
