import json
import os
from . import helper
import logging
from . import transaction
import sys

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"


def amount_test(json_data):
    input_amount = 0
    output_amount = 0
    for i in json_data["vin"]:
        input_amount += int(i["prevout"]["value"])
    for i in json_data["vout"]:
        output_amount += int(i["value"])
    if input_amount < output_amount:
        return False
    else:
        return True


def check_validity(json_data):
    is_amount_test_passed = amount_test(json_data)
    logging.debug("[LOG:]is_amount_test_passed: ", is_amount_test_passed)


def manual_test():
    asm_instruction = "OP_PUSHBYTES_72 30450221009eb05e52c05023c4239806f6ad4bf5595e6d81fee329e3794f38259170e4d8b302200a1f7174be46c657dab0449ecaa9002a4480a7ba6bef26492e2990e6426fe55a01 OP_PUSHBYTES_33 026e9a6cf3ae45ee0d0e1fa75e36471c7b9f1909b8b8e4ecf27bd9b8e207f21d74 OP_DUP OP_HASH160 OP_PUSHBYTES_20 25bab9d2a1e5c188ef7e6219904984fe16951f6c OP_EQUALVERIFY OP_CHECKSIG"
    helper.signature_verification_stack(asm_instruction)


def main():
    """
    This function processes the files in the 'mempool' directory, performs various calculations,
    and writes the results to output files. It also logging.debugs some log messages to the console.
    """
    different_vin_scriptpubkey_types = []
    different_vout_scriptpubkey_types = []
    num_sigwit = 0
    num_nonsigwit = 0
    num_singleSig_P2PKH = 0

    manual_test()

    with open("target/output.txt", "w") as f_out:
        mempool_dir = "mempool"
        # calculation of number of files in the directory
        number_of_files = len(os.listdir(mempool_dir))

        # iterate over the files in the directory
        for filename in os.listdir(mempool_dir):
            file_path = os.path.join(mempool_dir, filename)
            with open(file_path, "r") as f:
                json_data = json.load(f)
                helper.seperate_sigwit_and_nonsigwit(json_data, filename)

                # helper.check_scriptpubkey_type(
                #     json_data,
                #     different_vin_scriptpubkey_types,
                #     different_vout_scriptpubkey_types,
                # )

                serialized_transaction = transaction.serialise_transaction(
                    json_data, helper.is_sigwit(json_data)
                )
                # check_validity(json_data)
    logging.info(
        f"[LOG:]Different vin scriptpubkey types: {different_vin_scriptpubkey_types}"
    )
    logging.debug(
        f"[LOG:]Different vout scriptpubkey types: {different_vout_scriptpubkey_types}"
    )
    logging.debug(f"[LOG:]Total singleSig_P2PKH transactions: {num_singleSig_P2PKH}")


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    main()
