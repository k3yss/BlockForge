import logging
from ..transaction import dissect_signature, uncompress_pubkey, verifyECDSAsecp256k1
from enum import Enum

# """ unique_OP_CODES: [
# 'OP_PUSHBYTES_71',
# 'OP_PUSHBYTES_33',
# 'OP_PUSHBYTES_20',
# 'OP_PUSHBYTES_72',
# 'OP_PUSHBYTES_70',
# 'OP_PUSHBYTES_65'
# 'OP_EQUALVERIFY',
# 'OP_CHECKSIG',
# 'OP_HASH160',
# 'OP_DUP',
# ]
# """
# switch case with different op codes


class transaction_verification_status(Enum):
    pending = 0
    failed = 1
    success = 2


def handle_opcode_stack(
    opcode, stack, index, asm_instruction_in_list, serialized_transaction
):
    if opcode == "OP_EQUALVERIFY":
        stack_top = stack.pop()
        stack_top_2 = stack.pop()
        if stack_top == stack_top_2:
            return index, stack, transaction_verification_status.pending
        else:
            return index, stack, transaction_verification_status.failed

    # https://wiki.bitcoinsv.io/index.php/OP_CHECKSIG
    # https://en.bitcoin.it/wiki/OP_CHECKSIG
    elif opcode == "OP_CHECKSIG":
        # expects if there is two elements in the stack
        if len(stack) >= 2:
            public_key = stack.pop()
            signature = stack.pop()

            r, s = dissect_signature(signature)

            # convert r to integer
            r = int(r, 16)
            s = int(s, 16)

            hex_new_signature = [r, s]

            if public_key[:2] != "04":
                uncompressed_pub_key = uncompress_pubkey(public_key)
            else:
                public_key = public_key[2:]
                half_length = 64

                x = int(public_key[:half_length], 16)
                y = int(public_key[half_length:], 16)
                uncompressed_pub_key = [x, y]

            is_valid = verifyECDSAsecp256k1(
                serialized_transaction, hex_new_signature, uncompressed_pub_key
            )
            if is_valid:
                return index, stack, transaction_verification_status.success
            elif not is_valid:
                return index, stack, transaction_verification_status.failed

        else:
            return index, stack, transaction_verification_status.failed

    elif opcode == "OP_HASH160":
        from ..helper import calculate_sha256_hash, calculate_ripemd160_hash

        """
        The input is hashed twice: first with SHA-256 and then with RIPEMD-160. 
        """
        stack_top = stack.pop()
        sha_256_hash_value = calculate_sha256_hash(stack_top)
        ripemd160_hash_value = calculate_ripemd160_hash(sha_256_hash_value)
        stack.append(ripemd160_hash_value)
        return index, stack, transaction_verification_status.pending

    elif opcode == "OP_DUP":
        stack.append(stack[-1])
        return index, stack, transaction_verification_status.pending

    elif opcode[:13] == "OP_PUSHBYTES_":
        # asssuming that the bytes to be pushed is the length of the string
        stack.append(asm_instruction_in_list[index + 1])
        index = index + 1
        return index, stack, transaction_verification_status.pending
