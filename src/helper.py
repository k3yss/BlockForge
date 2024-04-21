import os
import json
import hashlib
import logging
from types import SimpleNamespace

from src.OP_CODE.op_code_implementation import *


class Vin_Prevout:
    def __init__(self, vin_prevout) -> None:
        self.scriptpubkey = vin_prevout.get("scriptpubkey")
        self.scriptpubkey_asm = vin_prevout.get("scriptpubkey_asm")
        self.scriptpubkey_type = vin_prevout.get("scriptpubkey_type")
        self.scriptpubkey_address = vin_prevout.get("scriptpubkey_address")
        self.value = vin_prevout.get("value")


# 'scriptsig', 'inner_witnessscript_asm', 'prevout', 'inner_redeemscript_asm', 'is_coinbase', 'scriptsig_asm', 'txid', 'sequence', 'witness', 'vout'
class Vin:
    def __init__(self, vin_json_data) -> None:
        self.txid = vin_json_data.get("txid")
        self.vout = vin_json_data.get("vout")
        self.prevout = Vin_Prevout(vin_json_data.get("prevout"))
        self.scriptsig = vin_json_data.get("scriptsig", "")
        self.scriptsig_asm = vin_json_data.get("scriptsig_asm", "")
        self.witness = vin_json_data.get("witness")
        self.is_coinbase = vin_json_data.get("is_coinbase")
        self.sequence = vin_json_data.get("sequence")
        self.inner_witnessscript_asm = vin_json_data.get("inner_witnessscript_asm", "")
        self.inner_redeemscript_asm = vin_json_data.get("inner_redeemscript_asm", "")

    # {'scriptsig', 'prevout', 'scriptsig_asm', 'txid', 'sequence', 'is_coinbase', 'vout'}
    def verify_p2pkh(self):
        pass

    # {'scriptsig', 'prevout', 'is_coinbase', 'scriptsig_asm', 'txid', 'sequence', 'witness', 'vout'}
    def v0_p2wpkh(self):
        pass

    # {'scriptsig', 'prevout', 'is_coinbase', 'scriptsig_asm', 'txid', 'sequence', 'witness', 'vout'}
    def verify_v1_p2tr(self):
        pass

    # {'scriptsig', 'inner_witnessscript_asm', 'prevout', 'inner_redeemscript_asm', 'is_coinbase', 'scriptsig_asm', 'txid', 'sequence', 'witness', 'vout'
    def verify_p2sh(self):
        pass

    # {'scriptsig', 'inner_witnessscript_asm', 'prevout', 'is_coinbase', 'scriptsig_asm', 'txid', 'sequence', 'witness', 'vout'
    def verify_v0_p2wsh(self):
        pass


class Vout:
    def __init__(self, vout_json_data) -> None:
        self.scriptpubkey = vout_json_data.get("scriptpubkey")
        self.scriptpubkey_asm = vout_json_data.get("scriptpubkey_asm")
        self.scriptpubkey_type = vout_json_data.get("scriptpubkey_type")
        self.scriptpubkey_address = vout_json_data.get("scriptpubkey_address")
        self.value = vout_json_data.get("value")


class Transaction:
    def __init__(self, json_data):
        self.version = json_data.get("version", 1)
        self.locktime = json_data.get("locktime", 0)
        self.vin = [Vin(vin) for vin in json_data.get("vin", [])]

        # iterate over all the vins and pass it to the class
        self.vout = [Vout(vout) for vout in json_data.get("vout", [])]

        self.is_segwit = is_sigwit(json_data)

    # unique_scriptpubkey_type={'v0_p2wpkh', 'p2sh', 'p2pkh', 'v1_p2tr', 'v0_p2wsh'}      │
    def is_transaction_valid(self):
        for vin in self.vin:
            if vin.prevout.scriptpubkey_type == "p2pkh":
                vin.verify_p2pkh()
            elif vin.prevout.scriptpubkey_type == "v0_p2wpkh":
                pass
            elif vin.prevout.scriptpubkey_type == "p2sh":
                pass
            elif vin.prevout.scriptpubkey_type == "v1_p2tr":
                pass
            elif vin.prevout.scriptpubkey_type == "v0_p2wsh":
                pass

        return True


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
    return pk[1:33] + y


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
