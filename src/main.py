import json
import os
from . import helper
import logging
import sys
from src.block_generation.block_header import (
    calculate_block_header,
    calculate_coinbase_transaction_hash,
    calculate_merkle_root,
)


# create a key value pair with


def main():
    """
    This function processes the files in the 'mempool' directory, performs various calculations,
    and writes the results to output files. It also logging.debugs some log messages to the console.
    """

    mempool_dir = "mempool"

    valid_transaction_list = []
    valid_transaction_wtxid_list = []

    # iterate over the files in the directory
    for filename in os.listdir(mempool_dir):
        file_path = os.path.join(mempool_dir, filename)
        with open(file_path, "r") as f:
            json_data = json.load(f)

            transaction = helper.Transaction(json_data)

            validity = transaction.is_transaction_valid()
            if validity:
                serialised_transanction = transaction.serialise_transaction()
                valid_transaction_list.append(
                    helper.calculate_double_sha256_hash(serialised_transanction)
                )
                if transaction.is_segwit:
                    wtxid = transaction.serialise_transaction(True)
                else:
                    wtxid = serialised_transanction
                valid_transaction_wtxid_list.append(
                    helper.calculate_double_sha256_hash(wtxid)
                )
            else:
                # logging.debug(f"File: {filename} ❌")
                pass

    coinbase_wtxid = "0000000000000000000000000000000000000000000000000000000000000000"

    witness_reserved_value = (
        "0000000000000000000000000000000000000000000000000000000000000000"
    )

    valid_transaction_wtxid_list.insert(0, coinbase_wtxid)

    output_file_path = "output.txt"
    with open(output_file_path, "w") as f:
        witness_root_hash = calculate_merkle_root(valid_transaction_wtxid_list)

        if witness_root_hash != None:
            concat_before_hash = witness_root_hash + witness_reserved_value

        logging.debug(f"{concat_before_hash=}")

        wTXID_commitment = helper.calculate_double_sha256_hash(concat_before_hash, True)

        logging.debug(f"{wTXID_commitment=}")

        coinbase_json_data = helper.create_coinbase_transaction_json(wTXID_commitment)

        coinbase_transaction_hash = calculate_coinbase_transaction_hash(
            coinbase_json_data
        )

        coinbase_pre_txid = helper.Transaction(
            coinbase_json_data
        ).serialise_transaction()

        coinbase_transaction_txid = helper.calculate_double_sha256_hash(
            coinbase_pre_txid
        )

        valid_transaction_list.insert(0, coinbase_transaction_txid)

        block_header = calculate_block_header(valid_transaction_list)

        f.write(f"{block_header.hex()}\n")

        f.write(f"{coinbase_transaction_hash}\n")

        for valid_transaction in valid_transaction_list:
            f.write(f"{valid_transaction}\n")


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    main()
