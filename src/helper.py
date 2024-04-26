import hashlib
import logging
from src.OP_CODE.op_code_implementation import *
from src.helper import *
from Crypto.Hash import RIPEMD160


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

        script_sig = bytes.fromhex(self.scriptsig)

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
    def v0_p2wpkh(self, initial_stack_instruction, initial_stack, message):
        # convert instruction to p2pkh type structure
        check_validity = signature_verification_stack(
            initial_stack_instruction, message, initial_stack
        )
        return check_validity

    # {'scriptsig', 'prevout', 'is_coinbase', 'scriptsig_asm', 'txid', 'sequence', 'witness', 'vout'}
    def verify_v1_p2tr(self):
        pass

    # {'scriptsig', 'inner_witnessscript_asm', 'prevout', 'inner_redeemscript_asm', 'is_coinbase', 'scriptsig_asm', 'txid', 'sequence', 'witness', 'vout'
    def verify_p2sh(self):
        pass

    # {'scriptsig', 'inner_witnessscript_asm', 'prevout', 'is_coinbase', 'scriptsig_asm', 'txid', 'sequence', 'witness', 'vout'
    def verify_v0_p2wsh(self):
        pass

    def vin_serialize_for_message(self, current_vin_index, expected_vin_index):
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
        vin_serialized += self.sequence.to_bytes(4, byteorder="little", signed=False)
        return vin_serialized

    def txid_plus_vout(self):
        txid_plus_vin = bytes.fromhex(self.txid)[::-1] + self.vout.to_bytes(
            4, byteorder="little", signed=False
        )
        return txid_plus_vin


class Vout:
    def __init__(self, vout_json_data) -> None:
        self.scriptpubkey = vout_json_data.get("scriptpubkey")
        self.scriptpubkey_asm = vout_json_data.get("scriptpubkey_asm")
        self.scriptpubkey_type = vout_json_data.get("scriptpubkey_type")
        self.scriptpubkey_address = vout_json_data.get("scriptpubkey_address")
        self.value = vout_json_data.get("value")

    def vout_serialize_for_message(self):
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

    def calculate_segwit_message(self, expected_vin_index, sighash_type):
        # 1. Grab the version field (reusable)

        version = self.version.to_bytes(4, byteorder="little")

        version = version.hex()

        # 2. Serialize and hash the TXIDs and VOUTs for the inputs (reusable)
        # hash256((TXID+VOUT)+(TXID+VOUT)+(TXID+VOUT)...)
        all_txid_plus_vout = ""
        for vin in self.vin:
            all_txid_plus_vout += vin.txid_plus_vout().hex()

        hash256_inputs = calculate_double_sha256_hash(all_txid_plus_vout, True)

        # 3. Serialize and hash the sequences for the inputs (reusable)

        # serialise_and_hash_sequences = ""
        for vin in self.vin:
            sequence_value_bytes = vin.sequence.to_bytes(
                4, byteorder="little", signed=False
            )
            sequence_value_hex = sequence_value_bytes.hex()
            serialise_and_hash_sequences = bytes.fromhex(
                calculate_double_sha256_hash(sequence_value_hex, True)
            )

        hash256_sequences = serialise_and_hash_sequences.hex()

        # 4. Serialize the TXID and VOUT for the input we're signing (not reusable)
        # specific_txid_plus_vout = ""
        for vin in self.vin:
            if self.vin.index(vin) == expected_vin_index:
                specific_txid_plus_vout = vin.txid_plus_vout().hex()

        # 5. Create a scriptcode for the input we're signing (not reusable)
        # To create the scriptcode, you need to find to the ScriptPubKey on the output you want to spend, extract the public key hash, and place it in to the following P2PKH ScriptPubKey structure:
        # public key hash, SHA256 + RIPEMD160

        for vin in self.vin:
            if self.vin.index(vin) == expected_vin_index:
                script_pub_key = vin.prevout.scriptpubkey[4:]

        scriptcode = f"1976a914{script_pub_key}88ac"

        # 6. Find the input amount (not reusable)
        for vin in self.vin:
            if self.vin.index(vin) == expected_vin_index:
                input_amount = vin.prevout.value.to_bytes(
                    8, byteorder="little", signed=False
                ).hex()
                sequence = vin.sequence.to_bytes(
                    4, byteorder="little", signed=False
                ).hex()

        # 8. Serialize and hash all the outputs (reusable)
        # hash256(amount+scriptpubkeysize+scriptpubkey)
        all_vout_serialised = b""
        for vout in self.vout:
            all_vout_serialised += vout.serialise_transaction_vout()

        hash256_outputs = calculate_double_sha256_hash(all_vout_serialised.hex(), True)

        # segwit_message += compact_size()

        # 9. Grab the locktime (reusable)
        lock_time = self.locktime.to_bytes(4, byteorder="little", signed=False).hex()

        # 10. Combine to create a hash preimage

        preimage = (
            version
            + hash256_inputs
            + hash256_sequences
            + specific_txid_plus_vout
            + scriptcode
            + input_amount
            + sequence
            + hash256_outputs
            + lock_time
        )

        # sighash type at the end

        if sighash_type == "01":
            sig_hash = 0x01.to_bytes(4, byteorder="little", signed=False).hex()

        preimage = preimage + sig_hash

        message = calculate_double_sha256_hash(preimage, True)

        return message

    # unique_scriptpubkey_type={'v0_p2 wpkh', 'p2sh', 'p2pkh', 'v1_p2tr', 'v0_p2wsh'}      │
    def is_transaction_valid(self):
        check_validity = False
        individual_vin_check = 0

        for vin in self.vin:
            expected_vin_index = self.vin.index(vin)
            if vin.prevout.scriptpubkey_type == "p2pkh":
                # get the currect index of vin
                script_sig_prevout_instructions = vin.prevout.scriptpubkey_asm.split(
                    " "
                )
                script_sig_instructions = vin.scriptsig_asm.split(" ")
                OP_CODE_INST = script_sig_instructions + script_sig_prevout_instructions

                signature = OP_CODE_INST[1]

                sighash_type = signature[len(signature) - 2 :]

                if sighash_type == "01":
                    serialized_transaction = self.calculate_non_segwit_message(
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
                template_instruction = [
                    "OP_DUP",
                    "OP_HASH160",
                    "OP_EQUALVERIFY",
                    "OP_CHECKSIG",
                ]

                signature = vin.witness[0]
                public_key = vin.witness[1]

                initial_stack = []

                initial_stack.append(signature)
                initial_stack.append(public_key)

                sighash_type = signature[len(signature) - 2 :]

                script_sig_instructions = vin.prevout.scriptpubkey_asm.split(" ")

                if script_sig_instructions[0] == "OP_0":
                    # insert PKH at the third position of the template_instruction array and push the remaining elements by one
                    template_instruction.insert(2, script_sig_instructions[1])
                    template_instruction.insert(3, script_sig_instructions[2])

                    initial_stack_instruction = template_instruction

                if sighash_type == "01":
                    message = self.calculate_segwit_message(
                        expected_vin_index, sighash_type
                    )

                    message = int(message, 16)
                    verification_status = vin.v0_p2wpkh(
                        initial_stack_instruction, initial_stack, message
                    )

                    if verification_status == False:
                        return False
                    elif verification_status == True:
                        individual_vin_check = individual_vin_check + 1

                    if len(self.vin) == individual_vin_check:
                        return True

            elif vin.prevout.scriptpubkey_type == "p2sh":
                pass
            elif vin.prevout.scriptpubkey_type == "v1_p2tr":
                pass
            elif vin.prevout.scriptpubkey_type == "v0_p2wsh":
                pass

        return check_validity

    def calculate_non_segwit_message(self, sighash_type, expected_vin_index) -> str:
        non_segwit_message = self.version.to_bytes(4, byteorder="little")

        non_segwit_message += compact_size(len(self.vin))

        for vin in self.vin:
            # get the current vin index
            current_vin_index = self.vin.index(vin)
            vin_after_serialising = vin.vin_serialize_for_message(
                current_vin_index, expected_vin_index
            )
            non_segwit_message += vin_after_serialising

        non_segwit_message += compact_size(len(self.vout))

        for vout in self.vout:
            non_segwit_message += vout.vout_serialize_for_message()

        non_segwit_message += self.locktime.to_bytes(4, byteorder="little")

        non_segwit_message += int(sighash_type, 16).to_bytes(4, byteorder="little")

        return non_segwit_message.hex()

    def serialise_transaction(self, full_serialisation=False):
        # The version number for the transaction. Used to enable new features.
        transaction_after_serialisation = self.version.to_bytes(4, byteorder="little")

        # Marker and Flag
        if self.is_segwit and full_serialisation:
            # If the transaction is a segwit transaction, the 5th byte is 0x00.
            transaction_after_serialisation += b"\x00"
            transaction_after_serialisation += b"\x01"

        # Input count
        transaction_after_serialisation += compact_size(len(self.vin))

        # Serialize each transaction input in the vin list.

        for vin in self.vin:
            transaction_after_serialisation += vin.serialise_transaction_vin()

        transaction_after_serialisation += compact_size(len(self.vout))

        for vout in self.vout:
            transaction_after_serialisation += vout.serialise_transaction_vout()

        if self.is_segwit and full_serialisation:
            for vin in self.vin:
                transaction_after_serialisation += compact_size(len(vin.witness))
                for witness in vin.witness:
                    transaction_after_serialisation += compact_size(len(witness) // 2)
                    transaction_after_serialisation += bytes.fromhex(witness)

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
    vin_serialized += vinData["sequence"].to_bytes(4, byteorder="little", signed=False)
    return vin_serialized


# incomplete for now
def vout_message_serialize(tx_vout):
    vout_serialized = tx_vout["value"].to_bytes(8, byteorder="little", signed=False)
    script_pub_key = bytes.fromhex(tx_vout["scriptpubkey"])
    vout_serialized += compact_size(len(script_pub_key)) + script_pub_key
    return vout_serialized


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
    # ripemd160_hash = hashlib.new("ripemd160", data).hexdigest()
    ripemd160_hash = RIPEMD160.new(data).hexdigest()
    return ripemd160_hash


# A transaction is a segwit tx if at least one of the inputs contain a witness. Or if you are inspecting the raw tx then you check the 5th byte (the input count) and if it is 0x00 then it is a segwit tx.


def is_sigwit(json_data):
    is_sigwit = False
    for i in json_data["vin"]:
        if "witness" in i:
            is_sigwit = True
    return is_sigwit


def signature_verification_stack(
    asm_instruction_in_list, serialized_transaction, stack=[]
):
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


def create_coinbase_transaction_json(wTXID_commitment):
    coinbase_json_data = {
        "version": 1,
        "locktime": 0,
        "vin": [
            {
                "txid": "0000000000000000000000000000000000000000000000000000000000000000",
                "vout": 4294967295,
                "prevout": {
                    "scriptpubkey": "41047eda6bd04fb27cab6e7c28c99b94977f073e912f25d1ff7165d9c95cd9bbe6da7e7ad7f2acb09e0ced91705f7616af53bee51a238b7dc527f2be0aa60469d140ac",
                    "scriptpubkey_asm": "OP_HASH160 OP_PUSHBYTES_20 423877331b30a905240c7e1f2adee4ebaa47c5f6 OP_EQUAL",
                    "scriptpubkey_type": "p2sh",
                    "scriptpubkey_address": "14gnf7L2DjBYKFuWb6iftBoWE9hmAoFbcF",
                    "value": 2504928,
                },
                "scriptsig": "03233708184d696e656420627920416e74506f6f6c373946205b8160a4256c0000946e0100",
                "scriptsig_asm": "OP_PUSHBYTES_22 001415ff0337937ecadd10ce56ffdfd4674817613223",
                "witness": [
                    "0000000000000000000000000000000000000000000000000000000000000000",
                ],
                "is_coinbase": True,
                "sequence": 4294967295,
            }
        ],
        "vout": [
            {
                "scriptpubkey": "76a914edf10a7fac6b32e24daa5305c723f3de58db1bc888ac",
                "scriptpubkey_asm": "OP_DUP OP_HASH160 OP_PUSHBYTES_20 71a3d2f54b0917dc9d2c877b2861ac52967dec7f OP_EQUALVERIFY OP_CHECKSIG",
                "scriptpubkey_type": "p2pkh",
                "scriptpubkey_address": "1BMscNZbFKdUDYi3bnF5XEmkWT3WPmRBDJ",
                "value": 28278016,
            },
            {
                "scriptpubkey": f"6a24aa21a9ed{wTXID_commitment}",
                "scriptpubkey_asm": "OP_HASH160 OP_PUSHBYTES_20 423877331b30a905240c7e1f2adee4ebaa47c5f6 OP_EQUAL",
                "scriptpubkey_type": "p2sh",
                "scriptpubkey_address": "37jAAWEdJ9D9mXybRobcveioxSkt7Lkwog",
                "value": 0000000000000000,
            },
        ],
    }

    return coinbase_json_data
