import os
import json
import hashlib
import logging
from src.OP_CODE.op_code_implementation import *

# from OP_CODE.op_code_implementation import *

unique_OP_CODES = []


# https://learnmeabitcoin.com/technical/general/compact-size/
def compact_size(size):
    if size < 0xFD:
        return size.to_bytes(1, byteorder="little")
    elif size < 0xFFFF:
        return b"\xfd" + size.to_bytes(2, byteorder="little")
    elif size < 0xFFFFFFFF:
        return b"\xfe" + size.to_bytes(4, byteorder="little")
    else:
        return b"\xff" + size.to_bytes(8, byteorder="little")


def calculate_double_sha256_hash(data):
    double_sha256_hash = calculate_sha256_hash(calculate_sha256_hash(data), False)
    return double_sha256_hash[::-1].hex()


def calculate_sha256_hash(data, isHex=True):
    if isHex:
        data_in_bytes = bytes.fromhex(data)
    else:
        data_in_bytes = data
    sha256_hash = hashlib.sha256(data_in_bytes).digest()
    # returns in byte format
    return sha256_hash


def calculate_ripemd160_hash(data):
    ripemd160_hash = hashlib.new("ripemd160", data).hexdigest()
    return ripemd160_hash


def check_scriptpubkey_type(
    json_data, different_vin_scriptpubkey_types, different_vout_scriptpubkey_types
):
    for i in json_data["vin"]:
        if i["prevout"]["scriptpubkey_type"] not in different_vin_scriptpubkey_types:
            different_vin_scriptpubkey_types.append(i["prevout"]["scriptpubkey_type"])
    for i in json_data["vout"]:
        if i["scriptpubkey_type"] not in different_vout_scriptpubkey_types:
            different_vout_scriptpubkey_types.append(i["scriptpubkey_type"])
    # for i in json_data["vout"]:
    #   if i["scriptpubkey_type"] == 'unknown':
    #     logging.debug(f'{GREEN}[LOG:]{json_data}{RESET}')


# A transaction is a segwit tx if at least one of the inputs contain a witness. Or if you are inspecting the raw tx then you check the 5th byte (the input count) and if it is 0x00 then it is a segwit tx.


def is_sigwit(json_data):
    is_sigwit = False
    for i in json_data["vin"]:
        if "witness" in i and i["witness"]:
            is_sigwit = True
    return is_sigwit


def is_singleSig_P2PKH(json_data, filename, count):
    target_dir = "target/singleSig_p2pkh/"
    if (
        len(json_data["vin"]) == 1
        and json_data["vin"][0]["prevout"]["scriptpubkey_type"] == "p2pkh"
    ):
        os.makedirs(target_dir, exist_ok=True)
        target_file_path = os.path.join(target_dir, filename)
        with open(target_file_path, "w") as f_target:
            json.dump(json_data, f_target, indent=4)
        # check only for non segwit transactions
        if len(json_data["vin"][0]["scriptsig_asm"]) > 0:
            signature_verification_stack(
                f'{json_data["vin"][0]["scriptsig_asm"]} {json_data["vin"][0]["prevout"]["scriptpubkey_asm"]}'
            )
            count += 1
    return count


def seperate_sigwit_and_nonsigwit(json_data, filename):
    is_tx_sigwit = is_sigwit(json_data)
    if is_tx_sigwit == True:
        target_dir = "target/sigwit/"
    else:
        target_dir = "target/non_sigwit/"
    os.makedirs(target_dir, exist_ok=True)
    target_file_path = os.path.join(target_dir, filename)

    with open(target_file_path, "w") as f_target:
        json.dump(json_data, f_target, indent=4)


# Calculate again
""" unique_OP_CODES: [
'OP_PUSHBYTES_71', 
'OP_PUSHBYTES_33',
'OP_PUSHBYTES_20', 
'OP_PUSHBYTES_72',
'OP_PUSHBYTES_70',
'OP_PUSHBYTES_65'
'OP_EQUALVERIFY',
'OP_CHECKSIG',
'OP_HASH160', 
'OP_DUP',
]
"""


def signature_verification_stack(asm_instruction):
    logging.debug(asm_instruction)
    stack = []
    index = 0
    asm_instruction_in_list = asm_instruction.split(" ")
    # logging.debug(f"[LOG:]asm_instruction: { asm_instruction_in_list}")

    while index < len(asm_instruction_in_list):
        ins = asm_instruction_in_list[index]
        # logging.debug(f"[LOG:]ins: {ins}")

        if ins[:3] == "OP_":
            index, stack = handle_opcode_stack(
                ins, stack, index, asm_instruction_in_list
            )
            # https://en.bitcoin.it/wiki/Script
            if ins[:13] == "OP_PUSHBYTES_":
                logging.debug(ins)
                bytes_to_be_pushed = int(ins[13:])
                logging.debug(bytes_to_be_pushed)
                stack.append(asm_instruction_in_list[index + 1][bytes_to_be_pushed:])
                logging.error(len(asm_instruction_in_list[index + 1]))
                if (
                    int(len(asm_instruction_in_list[index + 1]) / 2)
                    == bytes_to_be_pushed
                ):
                    stack.append(asm_instruction_in_list[index + 1])
                logging.debug(stack)
            elif ins == "OP_EQUALVERIFY":
                """
                OP_EQUAL 	135 	0x87 	x1 x2 	True / false 	Returns 1 if the inputs are exactly equal, 0 otherwise.
                OP_EQUALVERIFY 	136 	0x88 	x1 x2 	Nothing / fail 	Same as OP_EQUAL, but runs OP_VERIFY afterward.
                """
                stack_top = stack.pop()
                stack_top_2 = stack.pop()
                if stack_top == stack_top_2:
                    pass
                else:
                    logging.debug("[LOG:] OP_EQUALVERIFY Signature verification failed")
                    break

            elif ins == "OP_CHECKSIG":
                # https://en.bitcoin.it/wiki/OP_CHECKSIG
                """
                OP_CHECKSIG 	172 	0xac 	sig pubkey 	True / false 	The entire transaction's outputs, inputs, and script (from the most recently-executed OP_CODESEPARATOR to the end) are hashed. The signature used by OP_CHECKSIG must be a valid signature for this hash and public key. If it is, 1 is returned, 0 otherwise.
                """
                # expects if there is two elements in the stack
                if len(stack) < 2:
                    public_key = stack.pop()
                    signature = (
                        stack.pop()
                    )  # Signature format is [<DER signature> <1 byte hash-type>]
                    logging.CRITICAL(f"[LOG:] Signature is {signature}")
                    """
                    A new subScript is created from the scriptCode (the scriptCode is the actually executed script - either the scriptPubKey for non-segwit, non-P2SH scripts, or the redeemscript in non-segwit P2SH scripts). The script from the immediately after the most recently parsed OP_CODESEPARATOR to the end of the script is the subScript. If there is no OP_CODESEPARATOR the entire script becomes the subScript
                    """
                else:
                    logging.debug("Signature verification failed")
                    # break
                """
                These are, in order of stack depth, the public key and the signature of the script
                """

                # logging.debug(ins)
                # logging.debug(stack)

            elif ins == "OP_HASH160":
                """
                The input is hashed twice: first with SHA-256 and then with RIPEMD-160.
                """
                stack_top = stack.pop()
                sha_256_hash_value = calculate_sha256_hash(stack_top)
                ripemd160_hash_value = calculate_ripemd160_hash(sha_256_hash_value)
                stack.append(ripemd160_hash_value)
                logging.debug(
                    f"[LOG:] logging.debuging the ripemd160_hash_value: {ripemd160_hash_value}"
                )
            elif ins == "OP_DUP":
                # OP_DUP 	118 	0x76 	x 	x x 	Duplicates the top stack item.
                stack.append(stack[-1])
        index = index + 1

    # logging.debug(f"[LOG:]unique_OP_CODES: {unique_OP_CODES}")
