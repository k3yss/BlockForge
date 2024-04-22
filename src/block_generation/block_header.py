import hashlib
import random
import logging
from ..helper import *
import time
from ..transaction import serialise_transaction_vin, serialise_transaction_vout

# import transaction


# TODO Recheck the logic
def generate_random_hash():
    # Generate random nonce
    nonce = random.randint(0, 2**32)

    # Combine nonce with block header data (simplified for this example)
    data = str(nonce).encode()

    # Calculate SHA-256 hash
    hash = hashlib.sha256(data).digest()

    return hash


def split_into_pairs(arr):
    logging.debug(len(arr))
    if len(arr) == 1:
        return [arr, arr]
    return [arr[i : i + 2] for i in range(0, len(arr), 2)]


# Hash the TXIDs together in pairs.
#     Note: If you have a single item left over, hash it with itself.
# Take the resulting hashes and hash those together in pairs.
# Repeat until you are left with a single hash.


def calculate_merkle_root(transaction_list: list):
    # Hash the TXIDs together in pairs.

    # Note: If you have a single item left over, hash it with itself.

    if len(transaction_list) == 1:
        return transaction_list.pop()

    result = []
    # split the transaction hashes into pairs of two
    pairs = split_into_pairs(transaction_list)

    for pair in pairs:
        # logging.debug(f'{pair=}')
        concat = pair[0] + pair[1]
        # logging.debug(f'{concat=}')
        hashed_concat = calculate_sha256_hash(concat).hex()
        result.append(hashed_concat)

    return calculate_merkle_root(result)
    # logging.debug(result)


def calculate_coinbase_transaction_hash():
    json_data = {
        "version": 2,
        "locktime": 0,
        "vin": [
            {
                "txid": "0000000000000000000000000000000000000000000000000000000000000000",
                "vout": 0xFFFFFFFF,
                "scriptsig": "04233fa04e028b12",
                "sequence": 4294967295,
            }
        ],
        "vout": [
            {
                "scriptpubkey": "41047eda6bd04fb27cab6e7c28c99b94977f073e912f25d1ff7165d9c95cd9bbe6da7e7ad7f2acb09e0ced91705f7616af53bee51a238b7dc527f2be0aa60469d140ac",
                "value": 387156,
            }
        ],
    }

    # version to 4 byte, little endian
    transaction_after_serialisation = json_data["version"].to_bytes(
        4, byteorder="little"
    )

    transaction_after_serialisation += compact_size(len(json_data["vin"]))

    # Serialize each transaction input in the vin list.
    for vin in json_data["vin"]:
        transaction_after_serialisation += serialise_transaction_vin(vin)

    transaction_after_serialisation += compact_size(len(json_data["vout"]))

    for vout in json_data["vout"]:
        transaction_after_serialisation += serialise_transaction_vout(vout)

    transaction_after_serialisation += json_data["locktime"].to_bytes(
        4, byteorder="little"
    )
    return transaction_after_serialisation.hex()


def calculate_block_header():
    vesion_in_hex = 0x20000000
    difficultyTarget = (
        0x0000FFFF00000000000000000000000000000000000000000000000000000000
    )
    transaction_list = [
        "4eda2b12862c3aff56323d76a33f0739c655249305ad68a49d73afd8b4ee6a89"
    ]

    # block_header

    block_header = vesion_in_hex.to_bytes(4, byteorder="little", signed=False)

    # logging.debug(f'{version=}')

    random_hash = "0000000000000000000000000000000000000000000000000000000000000000"

    block_header += bytes.fromhex(random_hash)

    # A fingerprint for all of the transactions included in the block.

    calculated_merkle_root = bytes.fromhex(calculate_merkle_root(transaction_list))

    logging.debug(f"{len(calculated_merkle_root)=}")

    block_header += calculated_merkle_root

    # get the current time as a Unix timestamp.
    block_header += int(time.time()).to_bytes(4, byteorder="little", signed=False)

    # The bits field is compact representation of the target at the time the block was mined.

    bits = 0x1F00FFFF

    block_header += bits.to_bytes(4, byteorder="little", signed=False)

    nonce = 0
    block_header += nonce.to_bytes(4, byteorder="little", signed=False)

    transaction_count = len(transaction_list) + 1

    logging.debug(block_header.hex())
    logging.debug(len(block_header.hex()))

    coinbase_transaction_hash = calculate_coinbase_transaction_hash()
