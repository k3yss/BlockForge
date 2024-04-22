import json
import os
from . import helper
import logging
import sys


def main():
    """
    This function processes the files in the 'mempool' directory, performs various calculations,
    and writes the results to output files. It also logging.debugs some log messages to the console.
    """

    mempool_dir = "mempool"
    num_of_valid_p2pkh = 0

    # iterate over the files in the directory
    for filename in os.listdir(mempool_dir):
        file_path = os.path.join(mempool_dir, filename)
        with open(file_path, "r") as f:
            json_data = json.load(f)

            # convert the json data to an interface like data structure for
            # data manipulation
            transaction_interface = helper.Transaction(json_data)

            # check if the transaction is valid
            # logging.debug(f"Checking validity for {filename} 👨‍🚀")
            validity = transaction_interface.is_transaction_valid()
            if validity:
                # logging.debug(f"File: {filename} ✅")
                num_of_valid_p2pkh += 1
            else:
                # logging.debug(f"File: {filename} ❌")
                pass

    logging.debug(f"{num_of_valid_p2pkh=}")


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    main()
