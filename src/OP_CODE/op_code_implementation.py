import logging

""" unique_OP_CODES: [
'OP_PUSHBYTES_71', 
'OP_PUSHBYTES_33',
'OP_PUSHBYTES_20', 
'OP_PUSHBYTES_72',
'OP_PUSHBYTES_70',
'OP_PUSHBYTES_65'
'OP_EQUALVERIFY',
'OP_CHECKSIG',
'OP_HASH160', 
'OP_DUP',
]
"""
# switch case with different op codes


def handle_opcode_stack(opcode, stack, index, asm_instruction_in_list):
    if opcode == "OP_EQUALVERIFY":
        stack_top = stack.pop()
        stack_top_2 = stack.pop()
        if stack_top == stack_top_2:
            logging.debug("[LOG:] OP_EQUALVERIFY Signature verification passed")
        else:
            logging.fatal("[LOG:] OP_EQUALVERIFY Signature verification failed")
            # don't continue further
            index = -1

    elif opcode == "OP_CHECKSIG":
        # https://en.bitcoin.it/wiki/OP_CHECKSIG
        """
        Hint: You have to serialise the transaction and then create a commitment hash.
        """
        """
      OP_CHECKSIG 	172 	0xac 	sig pubkey 	True / false 	The entire transaction's outputs, inputs, and script (from the most recently-executed OP_CODESEPARATOR to the end) are hashed. The signature used by OP_CHECKSIG must be a valid signature for this hash and public key. If it is, 1 is returned, 0 otherwise. 
      """
        # expects if there is two elements in the stack
        if len(stack) < 2:
            public_key = stack.pop()
            signature = (
                stack.pop()
            )  # Signature format is [<DER signature> <1 byte hash-type>]
            logging.CRITICAL(f"[LOG:] Signature is {signature}")
            """
          A new subScript is created from the scriptCode (the scriptCode is the actually executed script - either the scriptPubKey for non-segwit, non-P2SH scripts, or the redeemscript in non-segwit P2SH scripts). The script from the immediately after the most recently parsed OP_CODESEPARATOR to the end of the script is the subScript. If there is no OP_CODESEPARATOR the entire script becomes the subScript
          """
        else:
            logging.debug("Signature verification failed")
            # break
        """
      These are, in order of stack depth, the public key and the signature of the script
      """

    elif opcode == "OP_HASH160":
        # from src.helper import calculate_sha256_hash, calculate_ripemd160_hash
        from ..helper import calculate_sha256_hash, calculate_ripemd160_hash

        """
        The input is hashed twice: first with SHA-256 and then with RIPEMD-160. 
        """
        stack_top = stack.pop()
        sha_256_hash_value = calculate_sha256_hash(stack_top)
        ripemd160_hash_value = calculate_ripemd160_hash(sha_256_hash_value)
        stack.append(ripemd160_hash_value)
        logging.debug(
            f"[LOG:] logging.debuging the ripemd160_hash_value: {ripemd160_hash_value}"
        )

    elif opcode == "OP_DUP":
        stack.append(stack[-1])

    elif opcode[:13] == "OP_PUSHBYTES_":
        # asssuming that the bytes to be pushed is the length of the string
        stack.append(asm_instruction_in_list[index + 1])
        index = index + 1
    return index, stack
