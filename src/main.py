import json
import os
from . import helper
import logging
from . import transaction
import sys


def main():
    """
    This function processes the files in the 'mempool' directory, performs various calculations,
    and writes the results to output files. It also logging.debugs some log messages to the console.
    """
    different_vin_scriptpubkey_types = []
    different_vout_scriptpubkey_types = []
    num_sigwit = 0
    num_nonsigwit = 0
    unique_OP_CODES = set()
    unique_key_fields_all = set()
    unique_key_fields_vin = set()
    unique_key_fields_vin_prevout = set()
    unique_key_fields_vout = set()
    unique_scriptpubkey_type = set()

    num_singleSig_P2PKH = 0

    with open("target/output.txt", "w") as f_out:
        mempool_dir = "mempool"
        # calculation of number of files in the directory
        number_of_files = len(os.listdir(mempool_dir))

        # iterate over the files in the directory
        for filename in os.listdir(mempool_dir):
            file_path = os.path.join(mempool_dir, filename)
            with open(file_path, "r") as f:
                json_data = json.load(f)

                keys = json_data.keys()
                unique_key_fields_all.update(keys)

                vin_keys = json_data["vin"]

                for individual_vin in vin_keys:
                    if individual_vin["prevout"]["scriptpubkey_type"] == "v0_p2wsh":
                        individual_vin_keys = individual_vin.keys()
                        unique_key_fields_vin.update(individual_vin_keys)
                        individual_vin_prevout_keys = individual_vin["prevout"].keys()
                        unique_key_fields_vin_prevout.update(
                            individual_vin_prevout_keys
                        )

                vout_key = json_data["vout"]

                for individual_vout in vout_key:
                    individual_vout_keys = individual_vout.keys()
                    unique_key_fields_vout.update(individual_vout_keys)

                # convert the json data to an interface like data structure for
                # data maniuipulation
                transaction_interface = helper.Transaction(json_data)

                # check if the transaction is valid
                is_transaction_valid = transaction_interface.is_transaction_valid()

                # logging.debug(f'{is_transaction_valid=}')

                for vin in transaction_interface.vin:
                    # logging.debug(f'{vin.prevout.scriptpubkey_type=}')
                    unique_scriptpubkey_type.add(f"{vin.prevout.scriptpubkey_type}")

                serialized_transaction = transaction.serialise_transaction(
                    json_data, helper.is_sigwit(json_data)
                )
                # check_validity(json_data)

        # logging.debug(f'{unique_key_fields_all=}')
        logging.debug(f"{unique_key_fields_vin=}")
        # logging.debug(f'{unique_key_fields_vin_prevout=}')
        # logging.debug(f'{unique_key_fields_vout=}')
        # logging.debug(f'{unique_scriptpubkey_type=}')


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    main()
