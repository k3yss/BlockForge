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


def main():
    """
    This function processes the files in the 'mempool' directory, performs various calculations,
    and writes the results to output files. It also logging.debugs some log messages to the console.
    """

    mempool_dir = "mempool"
    num_of_valid_p2pkh = 0

    valid_transaction_list = []
    valid_transaction_wtxid_list = []

    # iterate over the files in the directory
    for filename in os.listdir(mempool_dir):
        file_path = os.path.join(mempool_dir, filename)
        with open(file_path, "r") as f:
            json_data = json.load(f)

            # convert the json data to an interface like data structure for
            # data manipulation
            transaction = helper.Transaction(json_data)

            # check if the transaction is valid
            # logging.debug(f"Checking validity for {filename} 👨‍🚀")
            validity = transaction.is_transaction_valid()
            if validity:
                # logging.debug(f"File: {filename} ✅")
                num_of_valid_p2pkh += 1
                serialised_transanction = transaction.serialise_transaction()
                valid_transaction_list.append(
                    helper.calculate_double_sha256_hash(serialised_transanction)
                )
                wtxid = transaction.serialise_transaction(True)
                valid_transaction_wtxid_list.append(wtxid)
            else:
                # logging.debug(f"File: {filename} ❌")
                pass

    # opening the output.txt file and writing stuff to it

    # logging.debug(valid_transaction_list)

    # valid_transaction_list = [
    #     "0843a125fdce55b2c87431a295a90732d02e8e547fb0b8e53e9c088d9e2e441b",
    #     "e2dbcac985d31594ffa1193638e6fa07c948ba8199158b9bcdc4ea2a39dadc50",
    #     "1d9e3caa9bcda611782372d0186a69bc20759f65a10e6566cb79a375bd5343de",
    #     "4e4b14e0d955bfa053ce4a7c3245ab1253406b480f70247d7a5ba92636d13926",
    #     "30296c8fd2fc9ef712dd572846767e4f8bd09788350ead55456e57db2fa22e45",
    #     "2b7222221ef1f49b38f0b7d5ce04a312dd4c56492ef4ca45fdaa57f419a4f2d4",
    #     "379c9c1070725589a0fa9626a59bfab6de21a50e600815be7d6af70edf059f3c",
    # ]

    coinbase_wtxid = "0000000000000000000000000000000000000000000000000000000000000000"

    witness_reserved_value = (
        "0000000000000000000000000000000000000000000000000000000000000000"
    )

    valid_transaction_wtxid_list.insert(0, coinbase_wtxid)

    temp_file = "temp.txt"

    with open(temp_file, "w") as f:
        f.write(f"{valid_transaction_list}")

    output_file_path = "output.txt"
    with open(output_file_path, "w") as f:
        witness_root_hash = calculate_merkle_root(valid_transaction_wtxid_list)

        if witness_root_hash != None:
            concat_before_hash = witness_root_hash + witness_reserved_value

        logging.debug(f"{concat_before_hash=}")

        wTXID_commitment = helper.calculate_double_sha256_hash(concat_before_hash)

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
