import logging
from ..helper import *
import time
from ..transaction import serialise_transaction_vin, serialise_transaction_vout


def split_into_pairs(arr):
    logging.debug(len(arr))
    if len(arr) == 1:
        return [arr, arr]
    return [arr[i : i + 2] for i in range(0, len(arr), 2)]


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


def calculate_coinbase_transaction_hash():
    json_data = {
        "version": 2,
        "locktime": 0xFFFFFFFF,
        "vin": [
            {
                "txid": "0000000000000000000000000000000000000000000000000000000000000000",
                "vout": 0xFFFFFFFF,
                "prevout": {
                    "scriptpubkey": "41047eda6bd04fb27cab6e7c28c99b94977f073e912f25d1ff7165d9c95cd9bbe6da7e7ad7f2acb09e0ced91705f7616af53bee51a238b7dc527f2be0aa60469d140ac",
                    "scriptpubkey_address": "14gnf7L2DjBYKFuWb6iftBoWE9hmAoFbcF",
                    "value": 433833,
                },
                "scriptsig": "4830450221008f619822a97841ffd26eee942d41c1c4704022af2dd42600f006336ce686353a0220659476204210b21d605baab00bef7005ff30e878e911dc99413edb6c1e022acd012102c371793f2e19d1652408efef67704a2e9953a43a9dd54360d56fc93277a5667d",
                "sequence": 0xFFFFFFFF,
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

    transaction = Transaction(json_data)

    serialised_transaction = transaction.serialise_transaction()

    return serialised_transaction


def mine_block(block_header, nonce):
    difficultyTarget = (
        0x0000FFFF00000000000000000000000000000000000000000000000000000000
    )
    while True:
        # Append the nonce to the block header
        block_header_with_nonce = block_header + nonce.to_bytes(
            4, byteorder="little", signed=False
        )

        # Calculate the double SHA-256 hash of the block header with nonce
        block_hash = calculate_double_sha256_hash(block_header_with_nonce.hex())

        # Check if the block hash meets the difficulty target
        if int(block_hash, 16) < difficultyTarget:
            logging.debug(f"{block_hash=}")
            logging.debug(f"{nonce=}")
            return nonce  # Return the valid nonce

        nonce += 1


def calculate_block_header():
    vesion_in_hex = 0x20000000
    bits = 0x1F00FFFF

    transaction_list = [
        "4eda2b12862c3aff56323d76a33f0739c655249305ad68a49d73afd8b4ee6a89"
    ]

    # block_header
    block_header = vesion_in_hex.to_bytes(4, byteorder="little", signed=False)

    random_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    block_header += bytes.fromhex(random_hash)

    # A fingerprint for all of the transactions included in the block.
    calculated_merkle_root = bytes.fromhex(calculate_merkle_root(transaction_list))

    block_header += calculated_merkle_root

    # get the current time as a Unix timestamp.
    block_header += int(time.time()).to_bytes(4, byteorder="little", signed=False)

    # The bits field is compact representation of the target at the time the block was mined.

    block_header += bits.to_bytes(4, byteorder="little", signed=False)

    initial_nonce = 0
    calculated_nonce_value = mine_block(block_header, initial_nonce)

    block_header += calculated_nonce_value.to_bytes(4, byteorder="little", signed=False)

    return block_header


# def generate_block():
#     block_header = calculate_block_header()

#     coinbase_transaction_hash = calculate_coinbase_transaction_hash()

#     # transaction_count = len(transaction_list) + 1

#     logging.debug(block_header.hex())
#     # logging.debug(len(block_header.hex()))

#     coinbase_transaction_hash = calculate_coinbase_transaction_hash()
