import json
import os
import helper

RED = "\033[91m"
GREEN = "\033[92m"
RESET = "\033[0m"


def amount_test(json_data):
    input_amount = 0
    output_amount = 0
    for i in json_data["vin"]:
        input_amount += int(i["prevout"]["value"])
    for i in json_data["vout"]:
        output_amount += int(i["value"])
    # print(f"[LOG:]Input amount: {input_amount}")
    # print(f"[LOG:]Output amount: {output_amount}")
    if input_amount < output_amount:
        # print(f"{RED}[LOG:]Transaction amount is invalid{RESET}")
        return False
    else:
        # print(f"{GREEN}[LOG:]Transaction amount is valid{RESET}")
        return True


def check_validity(json_data):
    # print("[LOG:] Checking validity of transaction amount:")
    is_amount_test_passed = amount_test(json_data)
    print("[LOG:]is_amount_test_passed: ", is_amount_test_passed)


def main():
    different_vin_scriptpubkey_types = []
    different_vout_scriptpubkey_types = []
    num_sigwit = 0
    num_nonsigwit = 0
    with open("target/output.txt", "w") as f_out:
        mempool_dir = "mempool"
        number_of_files = len(os.listdir(mempool_dir))
        for filename in os.listdir(mempool_dir):
            f_out.write(f"{filename}: {number_of_files}\n")
            file_path = os.path.join(mempool_dir, filename)
            with open(file_path, "r") as f:
                json_data = json.load(f)
                num_sigwit, num_nonsigwit, is_sigwit = helper.is_vin_sigwit(
                    json_data, num_sigwit, num_nonsigwit
                )
                if is_sigwit == True:
                    # copy the file into target directory
                    target_file_path = os.path.join("../target/sigwit", filename)
                    os.makedirs(target_file_path, exist_ok=True)
                    with open(target_file_path, "w") as f_target:
                        json.dump(json_data, f_target, indent=4)
                else:
                    target_file_path = os.path.join("../target/non_sigwit", filename)
                    os.makedirs(target_file_path, exist_ok=True)
                    with open(target_file_path, "w") as f_target:
                        json.dump(json_data, f_target, indent=4)
                # if helper.is_vin_sigwit(json_data, num_sigwit, num_nonsigwit) == True:
                #   print(f"{RED}[LOG: {filename}]{json.dumps(json_data, indent=4)}{RESET}")
                # helper.check_scriptpubkey_type(json_data, different_vin_scriptpubkey_types, different_vout_scriptpubkey_types)
                # check_validity(json_data)
                # print(json_data["vin"][0]["txid"])
    # print(f"[LOG:]Different vin scriptpubkey types: {different_vin_scriptpubkey_types}")
    # print(f"[LOG:]Different vout scriptpubkey types: {different_vout_scriptpubkey_types}")
    print(f"[LOG:] Total sigwit transactions: {num_sigwit}")
    print(f"[LOG:] Total non sigwit transactions: {num_nonsigwit}")


if __name__ == "__main__":
    main()
