from ..helper import *
import time


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
            pair_hash = calculate_double_sha256_hash(
                level[i] + level[i + 1] if i + 1 < len(level) else level[i] * 2, True
            )
            next_level.append(pair_hash)

        level = next_level

    return level[0]


def calculate_coinbase_transaction_hash(coinbase_json_data):
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
            return nonce  # Return the valid nonce

        nonce += 1


def calculate_block_header(transaction_list: list):
    vesion_in_hex = 0x20000000
    bits = 0x1F00FFFF

    # block_header
    block_header = vesion_in_hex.to_bytes(4, byteorder="little", signed=False)

    random_hash = "0000000000000000000000000000000000000000000000000000000000000000"
    block_header += bytes.fromhex(random_hash)

    merkle_root_value = calculate_merkle_root(transaction_list)

    if merkle_root_value is not None:
        calculated_merkle_root = bytes.fromhex(merkle_root_value)
        block_header += calculated_merkle_root

    # get the current time as a Unix timestamp.
    block_header += int(time.time()).to_bytes(4, byteorder="little", signed=False)

    # The bits field is compact representation of the target at the time the block was mined.
    block_header += bits.to_bytes(4, byteorder="little", signed=False)

    initial_nonce = 0
    calculated_nonce_value = mine_block(block_header, initial_nonce)

    block_header += calculated_nonce_value.to_bytes(4, byteorder="little", signed=False)

    return block_header
