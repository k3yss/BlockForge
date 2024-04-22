# A transaction classs with a constructor and a method to parse the transaction

import logging
from . import helper
from pycoin.ecdsa import generator_secp256k1, verify


def verifyECDSAsecp256k1(msg, signature, pubKey):
    valid = verify(generator_secp256k1, pubKey, msg, signature)
    return valid


def parse_element(hex_str, offset, element_size):
    """
    :param hex_str: string to parse the element from.
    :type hex_str: hex str
    :param offset: initial position of the object inside the hex_str.
    :type offset: int
    :param element_size: size of the element to extract.
    :type element_size: int
    :return: The extracted element from the provided string, and the updated offset after extracting it.
    :rtype tuple(str, int)
    """

    return hex_str[offset : offset + element_size], offset + element_size


def dissect_signature(hex_sig):
    """
    Extracts the r, s and ht components from a Bitcoin ECDSA signature.
    :param hex_sig: Signature in  hex format.
    :type hex_sig: hex str
    :return: r, s, t as a tuple.
    :rtype: tuple(str, str, str)
    """

    offset = 0
    # Check the sig contains at least the size and sequence marker
    assert len(hex_sig) > 4, "Wrong signature format."
    sequence, offset = parse_element(hex_sig, offset, 2)
    # Check sequence marker is correct
    assert sequence == "30", "Wrong sequence marker."
    signature_length, offset = parse_element(hex_sig, offset, 2)
    # Check the length of the remaining part matches the length of the signature + the length of the hashflag (1 byte)
    assert len(hex_sig[offset:]) / 2 == int(signature_length, 16) + 1, "Wrong length."
    # Get r
    marker, offset = parse_element(hex_sig, offset, 2)
    assert marker == "02", "Wrong r marker."
    len_r, offset = parse_element(hex_sig, offset, 2)
    len_r_int = int(len_r, 16) * 2  # Each byte represents 2 characters
    r, offset = parse_element(hex_sig, offset, len_r_int)
    # Get s
    marker, offset = parse_element(hex_sig, offset, 2)
    assert marker == "02", "Wrong s marker."
    len_s, offset = parse_element(hex_sig, offset, 2)
    len_s_int = int(len_s, 16) * 2  # Each byte represents 2 characters
    s, offset = parse_element(hex_sig, offset, len_s_int)
    # Get ht
    ht, offset = parse_element(hex_sig, offset, 2)
    assert offset == len(hex_sig), "Wrong parsing."

    return r, s


# https://wiki.bitcoinsv.io/index.php/OP_CHECKSIG
def message_serialize(json_data, sighash_type=1) -> str:
    transaction_after_opcod_checksig_serialisation = json_data["version"].to_bytes(
        4, byteorder="little"
    )

    transaction_after_opcod_checksig_serialisation += helper.compact_size(
        len(json_data["vin"])
    )

    for vin in json_data["vin"]:
        vin_after_serialising = helper.vin_message_serialize(vin)
        transaction_after_opcod_checksig_serialisation += vin_after_serialising

    # logging.debug(f'{transaction_after_opcod_checksig_serialisation.hex()=}')

    transaction_after_opcod_checksig_serialisation += helper.compact_size(
        len(json_data["vout"])
    )

    for vout in json_data["vout"]:
        transaction_after_opcod_checksig_serialisation += helper.vout_message_serialize(
            vout
        )

    transaction_after_opcod_checksig_serialisation += json_data["locktime"].to_bytes(
        4, byteorder="little"
    )

    transaction_after_opcod_checksig_serialisation += sighash_type.to_bytes(
        4, byteorder="little"
    )

    return transaction_after_opcod_checksig_serialisation.hex()


def pow_mod(x, y, z):
    "Calculate (x ** y) % z efficiently."
    number = 1
    while y:
        if y & 1:
            number = number * x % z
        y >>= 1
        x = x * x % z
    return number


def uncompress_pubkey(compressed_key):
    p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
    y_parity = int(compressed_key[:2]) - 2
    x = int(compressed_key[2:], 16)
    a = (pow_mod(x, 3, p) + 7) % p
    y = pow_mod(a, (p + 1) // 4, p)
    if y % 2 != y_parity:
        y = -y % p
    # uncompressed_key = '{:x}{:x}'.format(x, y)
    return [x, y]


# https://learnmeabitcoin.com/technical/transaction/#structure-witness
def serialise_transaction(json_data, is_segwit):
    # version to 4 byte, little endian
    transaction_after_serialisation = json_data["version"].to_bytes(
        4, byteorder="little"
    )

    transaction_after_serialisation += helper.compact_size(len(json_data["vin"]))

    # Serialize each transaction input in the vin list.
    for vin in json_data["vin"]:
        transaction_after_serialisation += serialise_transaction_vin(vin)

    transaction_after_serialisation += helper.compact_size(len(json_data["vout"]))

    for vout in json_data["vout"]:
        transaction_after_serialisation += serialise_transaction_vout(vout)

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
