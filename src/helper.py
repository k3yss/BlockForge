import os
import json
import hashlib
import logging
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

    def serialise_transaction_vin(self):
        vin_serialized = bytes.fromhex(self.txid)[::-1]
        vin_serialized += self.vout.to_bytes(4, byteorder="little", signed=False)
        script_sig = bytes.fromhex(self.prevout.scriptpubkey)
        vin_serialized += compact_size(len(script_sig)) + script_sig
        vin_serialized += self.sequence.to_bytes(4, byteorder="little", signed=False)
        return vin_serialized

    # {'scriptsig', 'prevout', 'scriptsig_asm', 'txid', 'sequence', 'is_coinbase', 'vout'}
    def verify_p2pkh(self, OP_CODE_INST, serialized_transaction):
        check_validity = signature_verification_stack(
            OP_CODE_INST, serialized_transaction
        )
        return check_validity

    # {'scriptsig', 'prevout', 'is_coinbase', 'scriptsig_asm', 'txid', 'sequence', 'witness', 'vout'}
    def v0_p2wpkh(self, INST, serialized_transaction):
        p2pkh_template = ["DUP", "HASH160", "PUSHBYTES_20", "EQUALVERIFY", "CHECKSIG"]
        # convert instruction to p2pkh type structure

        # updated_inst =
        logging.debug(f"{len(INST[0])=}")
        logging.debug(f"{len(INST[1])=}")
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

    def vin_message_serialize_interfaced(self, current_vin_index, expected_vin_index):
        vin_serialized = bytes.fromhex(self.txid)[::-1]
        # ✅
        vin_serialized += self.vout.to_bytes(4, byteorder="little", signed=False)
        # ✅
        # only for the current tranasction we want to unlock
        if current_vin_index == expected_vin_index:
            script_sig = bytes.fromhex(self.prevout.scriptpubkey)
        else:
            script_sig = bytes.fromhex("")
        vin_serialized += compact_size(len(script_sig)) + script_sig
        # logging.debug(f"{len(script_sig)=}")
        vin_serialized += self.sequence.to_bytes(4, byteorder="little", signed=False)
        return vin_serialized


class Vout:
    def __init__(self, vout_json_data) -> None:
        self.scriptpubkey = vout_json_data.get("scriptpubkey")
        self.scriptpubkey_asm = vout_json_data.get("scriptpubkey_asm")
        self.scriptpubkey_type = vout_json_data.get("scriptpubkey_type")
        self.scriptpubkey_address = vout_json_data.get("scriptpubkey_address")
        self.value = vout_json_data.get("value")

    def vout_message_serialize_interface(self):
        vout_serialized = self.value.to_bytes(8, byteorder="little", signed=False)
        script_pub_key = bytes.fromhex(self.scriptpubkey)
        vout_serialized += compact_size(len(script_pub_key)) + script_pub_key
        return vout_serialized

    def serialise_transaction_vout(self):
        # Previous Transaction Hash, 32 bytes (little-endian)
        vout_serialized = self.value.to_bytes(8, byteorder="little", signed=False)
        # The size in bytes of the upcoming ScriptPubKey.
        script_pub_key = bytes.fromhex(self.scriptpubkey)
        # The unlocking code for the output you want to spend.
        vout_serialized += compact_size(len(script_pub_key)) + script_pub_key
        return vout_serialized


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
        check_validity = False
        individual_vin_check = 0

        for vin in self.vin:
            if vin.prevout.scriptpubkey_type == "p2pkh":
                # get the currect index of vin
                expected_vin_index = self.vin.index(vin)
                script_sig_prevout_instructions = vin.prevout.scriptpubkey_asm.split(
                    " "
                )
                script_sig_instructions = vin.scriptsig_asm.split(" ")
                OP_CODE_INST = script_sig_instructions + script_sig_prevout_instructions

                signature = OP_CODE_INST[1]

                sighash_type = signature[len(signature) - 2 :]

                if sighash_type == "01":
                    serialized_transaction = self.message_serialize_interface(
                        sighash_type, expected_vin_index
                    )
                    message = calculate_double_sha256_hash(serialized_transaction, True)

                    message = int(message, 16)

                    verification_status = vin.verify_p2pkh(OP_CODE_INST, message)

                    if verification_status == False:
                        return False
                    elif verification_status == True:
                        individual_vin_check = individual_vin_check + 1

            if len(self.vin) == individual_vin_check:
                return True

            elif vin.prevout.scriptpubkey_type == "v0_p2wpkh":
                # signature = vin.witness[0]
                # public_key = vin.witness[1]

                # sighash_type = signature[len(signature) - 2 :]

                # script_sig_instructions = vin.prevout.scriptpubkey_asm.split(" ")

                # INST = [signature, public_key] + script_sig_instructions

                # logging.debug(INST)

                # if sighash_type == "01":
                #     serialized_transaction = self.message_serialize_interface(
                #         sighash_type
                #     )
                #     message = calculate_double_sha256_hash(serialized_transaction, True)

                #     message = int(message, 16)

                #     verification_status = vin.v0_p2wpkh(INST, message)

                #     if verification_status == False:
                #         return False
                #     elif verification_status == True:
                #         individual_vin_check = individual_vin_check + 1

                pass
            elif vin.prevout.scriptpubkey_type == "p2sh":
                pass
            elif vin.prevout.scriptpubkey_type == "v1_p2tr":
                pass
            elif vin.prevout.scriptpubkey_type == "v0_p2wsh":
                pass

        return check_validity

    def message_serialize_interface(self, sighash_type, expected_vin_index) -> str:
        transaction_after_opcod_checksig_serialisation = self.version.to_bytes(
            4, byteorder="little"
        )

        transaction_after_opcod_checksig_serialisation += compact_size(len(self.vin))

        for vin in self.vin:
            # get the current vin index
            current_vin_index = self.vin.index(vin)
            vin_after_serialising = vin.vin_message_serialize_interfaced(
                current_vin_index, expected_vin_index
            )
            transaction_after_opcod_checksig_serialisation += vin_after_serialising

        transaction_after_opcod_checksig_serialisation += compact_size(len(self.vout))

        for vout in self.vout:
            transaction_after_opcod_checksig_serialisation += (
                vout.vout_message_serialize_interface()
            )

        transaction_after_opcod_checksig_serialisation += self.locktime.to_bytes(
            4, byteorder="little"
        )

        transaction_after_opcod_checksig_serialisation += int(
            sighash_type, 16
        ).to_bytes(4, byteorder="little")

        # transaction_after_opcod_checksig_serialisation += sighash_type.to_bytes(
        #     4, byteorder="little"
        # )

        return transaction_after_opcod_checksig_serialisation.hex()

    def serialise_transaction(self):
        # version to 4 byte, little endian
        transaction_after_serialisation = self.version.to_bytes(4, byteorder="little")

        transaction_after_serialisation += compact_size(len(self.vin))

        # Serialize each transaction input in the vin list.
        for vin in self.vin:
            transaction_after_serialisation += vin.serialise_transaction_vin()

        transaction_after_serialisation += compact_size(len(self.vout))

        for vout in self.vout:
            transaction_after_serialisation += vout.serialise_transaction_vout()

        transaction_after_serialisation += self.locktime.to_bytes(4, byteorder="little")
        return transaction_after_serialisation.hex()


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
    # logging.debug(f"{len(script_sig)=}")
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


# A transaction is a segwit tx if at least one of the inputs contain a witness. Or if you are inspecting the raw tx then you check the 5th byte (the input count) and if it is 0x00 then it is a segwit tx.


def is_sigwit(json_data):
    is_sigwit = False
    for i in json_data["vin"]:
        if "witness" in i and i["witness"]:
            is_sigwit = True
    return is_sigwit


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


def signature_verification_stack(asm_instruction_in_list, serialized_transaction):
    stack = []
    index = 0

    while index < len(asm_instruction_in_list):
        ins = asm_instruction_in_list[index]
        if ins[:3] == "OP_":
            result = handle_opcode_stack(
                ins, stack, index, asm_instruction_in_list, serialized_transaction
            )
            if result is None:
                index, stack, status = 0, [], transaction_verification_status.pending
            else:
                index, stack, status = result

            if status == transaction_verification_status.failed:
                return False
            elif status == transaction_verification_status.success:
                return True
            elif status == transaction_verification_status.pending:
                index = index + 1
