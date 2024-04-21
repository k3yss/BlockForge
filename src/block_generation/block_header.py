import hashlib
import random
import logging
from ..helper import *
import time
import transaction


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
                "txid": "fb7fe37919a55dfa45a062f88bd3c7412b54de759115cb58c3b9b46ac5f7c925",
                "vout": 1,
                "prevout": {
                    "scriptpubkey": "76a914286eb663201959fb12eff504329080e4c56ae28788ac",
                    "scriptpubkey_address": "14gnf7L2DjBYKFuWb6iftBoWE9hmAoFbcF",
                    "value": 433833,
                },
                "scriptsig": "4830450221008f619822a97841ffd26eee942d41c1c4704022af2dd42600f006336ce686353a0220659476204210b21d605baab00bef7005ff30e878e911dc99413edb6c1e022acd012102c371793f2e19d1652408efef67704a2e9953a43a9dd54360d56fc93277a5667d",
                "sequence": 4294967295,
            }
        ],
        "vout": [
            {
                "scriptpubkey": "76a9141ef7874d338d24ecf6577e6eadeeee6cd579c67188ac",
                "scriptpubkey_address": "13pjoLcRKqhzPCbJgYW77LSFCcuwmHN2qA",
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
        transaction_after_serialisation += transaction.serialise_transaction_vin(vin)

    transaction_after_serialisation += compact_size(len(json_data["vout"]))

    for vout in json_data["vout"]:
        transaction_after_serialisation += transaction.serialise_transaction_vout(vout)

    transaction_after_serialisation += json_data["locktime"].to_bytes(
        4, byteorder="little"
    )
    return transaction_after_serialisation.hex()


def calculate_block_header():
    vesion_in_hex = 0x1
    difficultyTarget = (
        0x0000FFFF00000000000000000000000000000000000000000000000000000000
    )
    transaction_list = [
        "4eda2b12862c3aff56323d76a33f0739c655249305ad68a49d73afd8b4ee6a89"
    ]

    version = vesion_in_hex.to_bytes(4, byteorder="little", signed=False)

    while True:
        random_hash = generate_random_hash()
        if int.from_bytes(random_hash, byteorder="big") < difficultyTarget:
            break

    previousBlockHash = random_hash

    # A fingerprint for all of the transactions included in the block.
    merkleRoot = calculate_merkle_root(transaction_list)

    # get the current time as a Unix timestamp.
    current_unix_timestap = int(time.time()).to_bytes(
        4, byteorder="little", signed=False
    )

    # The bits field is compact representation of the target at the time the block was mined.

    bits = 0x1F00FFFF

    bits_in_bytes = bits.to_bytes(4, byteorder="little", signed=False)

    nonce = random.randint(0, 2**32).to_bytes(4, byteorder="little", signed=False)
    logging.debug(previousBlockHash)

    coinbase_transaction_hash = calculate_coinbase_transaction_hash()
