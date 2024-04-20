import logging

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


def handle_opcode_stack(opcode, stack, index, asm_instruction_in_list):
    if opcode == "OP_EQUALVERIFY":
        stack_top = stack.pop()
        stack_top_2 = stack.pop()
        if stack_top == stack_top_2:
            logging.debug("[LOG:] OP_EQUALVERIFY ✅")
        else:
            logging.debug("[LOG:] OP_EQUALVERIFY ❌")
            # don't continue further
            index = -1

    # https://wiki.bitcoinsv.io/index.php/OP_CHECKSIG
    elif opcode == "OP_CHECKSIG":
        logging.debug(asm_instruction_in_list)
        logging.debug(stack)
        # https://en.bitcoin.it/wiki/OP_CHECKSIG

        # expects if there is two elements in the stack
        if len(stack) >= 2:
            public_key = stack.pop()
            signature = stack.pop()
            logging.debug(f"Public Key 😇: {public_key}")
            logging.debug(f"Signature 👨‍🚀: {signature}")
            # check if the last byte is 0x01
            sigHashType = signature[len(signature) - 2 :]
            logging.debug(f"Signature[-2] 🧐: {sigHashType}")
            if sigHashType == "01":
                logging.debug("Signature is of SIGHASH_ALL ")
        else:
            logging.debug("Signature verification failed ❌")
            index = -1
            # break

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
        logging.debug("[LOG:] OP_HASH150 ✅")

    elif opcode == "OP_DUP":
        stack.append(stack[-1])
        logging.debug("[LOG:] OP_DUP ✅")

    elif opcode[:13] == "OP_PUSHBYTES_":
        # asssuming that the bytes to be pushed is the length of the string
        stack.append(asm_instruction_in_list[index + 1])
        index = index + 1
        logging.debug(f"[LOG:] {opcode} ✅")
    return index, stack
