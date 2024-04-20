import os
import json
import hashlib
import logging

from pycoin.ecdsa.Generator import *
from src.OP_CODE.op_code_implementation import *
import ecdsa
import codecs

# import modular_sqrt from pycoin


# from OP_CODE.op_code_implementation import *

unique_OP_CODES = []


# decompress a compressed public key into x and y values
def decompress_pubkey(pk):
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    x = int.from_bytes(pk[1:33], byteorder="big")
    y_sq = (pow(x, 3, p) + 7) % p
    y = pow(y_sq, (p + 1) // 4, p)
    if y % 2 != pk[0] % 2:
        y = p - y
    y = y.to_bytes(32, byteorder="big")
    return y


# incomplete for now
def vin_message_serialize(vinData):
    vin_serialized = bytes.fromhex(vinData["txid"])[::-1]
    # ✅
    vin_serialized += vinData["vout"].to_bytes(4, byteorder="little", signed=False)
    # ✅
    # only for the current tranasction we want to unlock
    script_sig = bytes.fromhex(vinData["prevout"]["scriptpubkey"])
    vin_serialized += compact_size(len(script_sig)) + script_sig
    logging.debug(f"{len(script_sig)=}")
    vin_serialized += vinData["sequence"].to_bytes(4, byteorder="little", signed=False)
    return vin_serialized


# incomplete for now
def vout_message_serialize(tx_vout):
    vout_serialized = tx_vout["value"].to_bytes(8, byteorder="little", signed=False)
    script_pub_key = bytes.fromhex(tx_vout["scriptpubkey"])
    vout_serialized += compact_size(len(script_pub_key)) + script_pub_key
    return vout_serialized


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


def calculate_double_sha256_hash(data, reverseOutput=False):
    double_sha256_hash = calculate_sha256_hash(calculate_sha256_hash(data), False)
    if reverseOutput:
        return double_sha256_hash.hex()
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
    stack = []
    index = 0
    asm_instruction_in_list = asm_instruction.split(" ")

    while index < len(asm_instruction_in_list):
        ins = asm_instruction_in_list[index]
        if ins[:3] == "OP_":
            index, stack = handle_opcode_stack(
                ins, stack, index, asm_instruction_in_list
            )
        index = index + 1
