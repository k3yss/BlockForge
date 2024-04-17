import hashlib
import os
import json


def calculate_sha256_hash(data):
    sha256_hash_obj = hashlib.sha256()
    sha256_hash_obj.update(bytes.fromhex(data))
    sha256_hash = sha256_hash_obj.digest()
    return sha256_hash


def calculate_ripemd160_hash(data):
    ripemd160_hash = hashlib.new("ripemd160", data).hexdigest()
    return ripemd160_hash


def check_v0_p22wpkh(json_data):
    for i in json_data["vin"]:
        if i["prevout"]["scriptpubkey_type"] == "v0_p2wpkh":
            scriptpubkey = i["prevout"]["scriptpubkey"][4:]
            # logging.debug(scriptpubkey)
            witness_second_parameter = i["witness"][1]
            sha_256_hash_value = calculate_sha256_hash(witness_second_parameter)
            ripemd160_hash_value = calculate_ripemd160_hash(sha_256_hash_value)
            # logging.debug(f'[LOG]: PUBLIC_KEY_HASH \t{ripemd160_hash_value}')
            if ripemd160_hash_value == scriptpubkey:
                # logging.debug('[LOG]: Test Passed')
                pass
            else:
                logging.debug("[LOG]: Test Failed")


def main():
    with open("target/output.txt", "w") as f_out:
        mempool_dir = "mempool"
        number_of_files = len(os.listdir(mempool_dir))
        for filename in os.listdir(mempool_dir):
            f_out.write(f"{filename}: {number_of_files}\n")
            file_path = os.path.join(mempool_dir, filename)
            with open(file_path, "r") as f:
                json_data = json.load(f)
                check_v0_p22wpkh(json_data)
                # num_sigwit, num_nonsigwit, is_sigwit = helper.is_vin_sigwit(
                #     json_data, num_sigwit, num_nonsigwit
                # )
                # if is_sigwit == True:
                #     target_dir = "target/sigwit/"
                # else:
                #     target_dir = "target/non_sigwit/"
                # os.makedirs(target_dir, exist_ok=True)
                # target_file_path = os.path.join(target_dir, filename)

                # with open(target_file_path, "w") as f_target:
                #     json.dump(json_data, f_target, indent=4)

                # check_validity(json_data)


if __name__ == "__main__":
    main()
