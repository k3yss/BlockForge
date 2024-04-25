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
