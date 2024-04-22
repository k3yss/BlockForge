import json
import os
from . import helper
import logging
import sys
from src.block_generation.block_header import (
    calculate_block_header,
    calculate_coinbase_transaction_hash,
)


def main():
    """
    This function processes the files in the 'mempool' directory, performs various calculations,
    and writes the results to output files. It also logging.debugs some log messages to the console.
    """

    mempool_dir = "mempool"
    num_of_valid_p2pkh = 0

    valid_transaction_list = []

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
            else:
                # logging.debug(f"File: {filename} ❌")
                pass

    # opening the output.txt file and writing stuff to it
    output_file_path = "output.txt"
    with open(output_file_path, "w") as f:
        block_header = calculate_block_header()
        # write the block header to the file

        f.write(f"{block_header.hex()}\n")

        coinbase_transaction_hash = calculate_coinbase_transaction_hash()

        transaction_count = len(valid_transaction_list) + 1

        transaction_count = helper.compact_size(transaction_count)
        transaction_count_hex = transaction_count.hex()

        logging.debug(f"{transaction_count_hex=}")

        f.write(f"{transaction_count_hex}\n")

        f.write(f"{coinbase_transaction_hash}\n")

        for valid_transaction in valid_transaction_list:
            f.write(f"{valid_transaction}\n")


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    main()
