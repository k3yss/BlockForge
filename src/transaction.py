# A transaction classs with a constructor and a method to parse the transaction
import logging
from . import helper


# For segwit transactions you HASH256 all of the transaction data except the marker, flag, witness fields.


# https://learnmeabitcoin.com/technical/transaction/#structure-witness
def serialise_transaction(json_data, is_segwit):
    # version to 4 byte, little endian
    transaction_after_serialisation = json_data["version"].to_bytes(
        4, byteorder="little"
    )
    # logging.debug(transaction_after_serialisation)

    # if is_segwit:
    #     transaction_after_serialisation += b"\x00\x01"

    transaction_after_serialisation += helper.compact_size(len(json_data["vin"]))

    # Serialize each transaction input in the vin list.
    for vin in json_data["vin"]:
        transaction_after_serialisation += serialise_transaction_vin(vin)

    transaction_after_serialisation += helper.compact_size(len(json_data["vout"]))

    for vout in json_data["vout"]:
        transaction_after_serialisation += serialise_transaction_vout(vout)

    # if is_segwit:
    #     # The number of items to be pushed on to the stack as part of the unlocking code.
    #     for vin in json_data["vin"]:
    #         if "witness" in vin:
    #             transaction_after_serialisation += helper.compact_size(
    #                 len(vin["witness"])
    #             )
    #             for witness in vin["witness"]:
    #                 witness_in_bytes = bytes.fromhex(witness)
    #                 transaction_after_serialisation += helper.compact_size(
    #                     len(witness_in_bytes)
    #                 )
    #                 transaction_after_serialisation += witness_in_bytes
    #         else:
    #             transaction_after_serialisation += b"\x00"

    # locktime to 4 byte, little endian
    transaction_after_serialisation += json_data["locktime"].to_bytes(
        4, byteorder="little"
    )
    return transaction_after_serialisation.hex()


"""
Input(s) 	
Field 	Example 	Size 	Format 	Description
TXID 	[TXID] 	32 bytes 	Natural Byte Order 	The TXID of the transaction containing the output you want to spend.
VOUT 	01000000 	4 bytes 	Little-Endian 	The index number of the output you want to spend.
ScriptSig Size 	6b 	variable 	Compact Size 	The size in bytes of the upcoming ScriptSig.
ScriptSig 	[script] 	variable 	Script 	The unlocking code for the output you want to spend.
Sequence 	fdffffff 	4 bytes 	Little-Endian 	Set whether the transaction can be replaced or when it can be mined.

"""


def serialise_transaction_vin(tx_vin):
    # Previous Transaction Hash, 32 bytes (little-endian)
    vin_serialized = bytes.fromhex(tx_vin["txid"])[::-1]  # Reverse byte order
    vin_serialized += tx_vin["vout"].to_bytes(4, byteorder="little", signed=False)
    # The size in bytes of the upcoming ScriptSig.
    script_sig = bytes.fromhex(tx_vin["scriptsig"])
    # The unlocking code for the output you want to spend.
    vin_serialized += helper.compact_size(len(script_sig)) + script_sig
    # Set whether the transaction can be replaced or when it can be mined.
    vin_serialized += tx_vin["sequence"].to_bytes(4, byteorder="little", signed=False)
    return vin_serialized


"""
Output(s) 	
Field 	Example 	Size 	Format 	Description
Amount 	e99e060000000000 	8 bytes 	Little-Endian 	The value of the output in satoshis.
ScriptPubKey Size 	19 	variable 	Compact Size 	The size in bytes of the upcoming ScriptPubKey.
ScriptPubKey 	[script] 	variable 	Script 	The locking code for this output.

This structure repeats for every output.
"""


def serialise_transaction_vout(tx_vout):
    # Previous Transaction Hash, 32 bytes (little-endian)
    vout_serialized = tx_vout["value"].to_bytes(8, byteorder="little", signed=False)
    # The size in bytes of the upcoming ScriptPubKey.
    script_pub_key = bytes.fromhex(tx_vout["scriptpubkey"])
    # The unlocking code for the output you want to spend.
    vout_serialized += helper.compact_size(len(script_pub_key)) + script_pub_key
    return vout_serialized
