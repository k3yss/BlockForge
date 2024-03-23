def check_scriptpubkey_type(
    json_data, different_vin_scriptpubkey_types, different_vout_scriptpubkey_types
):
    for i in json_data["vin"]:
        if i["prevout"]["scriptpubkey_type"] not in different_vin_scriptpubkey_types:
            different_vin_scriptpubkey_types.append(i["prevout"]["scriptpubkey_type"])
    for i in json_data["vout"]:
        if i["scriptpubkey_type"] not in different_vout_scriptpubkey_types:
            different_vout_scriptpubkey_types.append(i["scriptpubkey_type"])
    # for i in json_data["vout"]:
    #   if i["scriptpubkey_type"] == 'unknown':
    #     print(f'{GREEN}[LOG:]{json_data}{RESET}')


def is_vin_sigwit(json_data, num_sigwit, num_nonsigwit):
    is_sigwit = False
    for i in json_data["vin"]:
        if i["scriptsig"] != "" and i["scriptsig_asm"] != "":
            num_nonsigwit += 1
        else:
            num_sigwit += 1
            is_sigwit = True
        return num_sigwit, num_nonsigwit, is_sigwit
