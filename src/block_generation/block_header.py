import logging
from ..helper import *
import time
from ..transaction import serialise_transaction_vin, serialise_transaction_vout
from hashlib import sha256


def hash256(data):
    """
    Hashes the provided data using SHA-256 twice.
    """
    h1 = sha256(bytes.fromhex(data)).digest()

    return sha256(h1).hexdigest()


def reverse_hex(data):
    """
    Reverses the byte order of a hex string.
    """
    return bytes.fromhex(data)[::-1].hex()


def split_into_pairs(arr):
    # logging.debug(len(arr))
    if len(arr) % 2 != 0:
        arr.append(arr[-1])
    return [arr[i : i + 2] for i in range(0, len(arr), 2)]


def calculate_merkle_root(txids):
    # Hash the TXIDs together in pairs.
    if not txids:
        return None

    # Reverse the transaction IDs
    level = [reverse_hex(txid) for txid in txids]

    while len(level) > 1:
        next_level = []

        for i in range(0, len(level), 2):
            pair_hash = hash256(
                level[i] + level[i + 1] if i + 1 < len(level) else level[i] * 2
            )
            next_level.append(pair_hash)

        level = next_level

    return level[0]


def calculate_coinbase_transaction_hash(coinbase_json_data):
    # transaction = Transaction(json_data)

    segwit_transaction = Transaction(coinbase_json_data)

    serialised_transaction = segwit_transaction.serialise_transaction(True)

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
            # logging.debug(f"{block_hash=}")
            # logging.debug(f"{nonce=}")
            return nonce  # Return the valid nonce

        nonce += 1


def calculate_block_header(transaction_list: list):
    vesion_in_hex = 0x20000000
    bits = 0x1F00FFFF

    # block_header
    block_header = vesion_in_hex.to_bytes(4, byteorder="little", signed=False)

    random_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    block_header += bytes.fromhex(random_hash)

    # A fingerprint for all of the transactions included in the block.
    # tmp = "62ee903bc68e48d444d4de4cb1c4514c5f9dcaa617bbdcd9558fe338be504869"

    tmp = calculate_merkle_root(transaction_list)

    if tmp is not None:
        logging.debug(f"{len(tmp)}=")
        calculated_merkle_root = bytes.fromhex(tmp)
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
