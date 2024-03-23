- `version`: This is the version number of the transaction format

- `locktime`: The locktime field allows you to prevent a transaction from being mined until after a specific block height or time. [link](https://learnmeabitcoin.com/technical/transaction/locktime/)

- `vin`: Input of the transaction | Doesn't contain any information about the receipient

- `vin[index].txid`:  Transaction id of the previous transaction

- `vin[index].vout`: Index of the previous transaction that contains our money

- `vin[index].prevout`: Details about that previous output

- `vin[index].prevout.scriptpubkey`: The locking script that needs to be satisfied to spend the output in its raw binary format.

- `vin[index].prevout.scriptpubkey_asm`: The locking script that needs to be satisfied to spend the output in its assembly format.

- `vin[index].prevout.scriptpubkey_type`: The type of the locking script (e.g., p2wpkh for Pay-to-Witness-Public-Key-Hash).

- `vin[index].prevout.scriptpubkey_address`:  The Bitcoin address associated with the locking script who received the money in the first place (previous recepient) ([NOTE]:This is not the final recepient).

- `vin[index].prevout.value`: The amount of Bitcoin (in satoshis) associated with the output being spent.

- `vin[index].scriptsig`: Empty because solve some scalability problem and we are following the sigvit format

- `vin[index].scriptsig_asm`: Empty because we are trying to solve some scalability problem and we are following the sigvit format

- `vin[index].witness`: contains the data necessary to unlock the locking script.
  - `vin[index].witness[0]`: Signature
  - `vin[index].witness[1]`: Public Key

- `vin[index].is_coinbase`: is a coinbase transaction or not ([INFO:] A coinbase transaction is the first transaction in a new block, and it is the transaction that generates the newly created bitcoins (block reward) for the miner who mined that block.).

- `vin[index].sequence`: 
  - Enabling replaceable transactions by setting a value lower than the maximum.
  - Implementing relative lock-time transactions in conjunction with the locktime field.

- `vout[index]`: Specify how much and to whom I am spending the money

- `vout[index].scriptpubkey`: 
    - defines the rules for spending the new outputs being created, while `vin[index].prevout.scriptpubkey` represents the rules that were set for the previous outputs being spent as inputs.
    - `vout[index].scriptpubkey` looks forward and sets the conditions for future spending, while `vin[index].prevout.scriptpubkey` looks backward and references the conditions that were set in the past for the outputs being spent.
- `vout[index].scriptpubkey_asm`: The above but in assembly format.

- `vout[index].scriptpubkey_type`: The type of scriptpubkey

- `vout[index].scriptpubkey_address`: The address of the receipent 

- `vout[index].value`: The amount to be received by the receipient
 



> ref:

```json
{
  "version": 1,
  "locktime": 0,
  "vin": [
    {
      "txid": "c7a1682bdf54913a4d825b4f1b79ae9c3ad0638cb70ed4e60cab88ab39a5de26",
      "vout": 1,
      "prevout": {
        "scriptpubkey": "0014d817581d6c580afe261df66d2e2d5e8b809cd9f9",
        "scriptpubkey_asm": "OP_0 OP_PUSHBYTES_20 d817581d6c580afe261df66d2e2d5e8b809cd9f9",
        "scriptpubkey_type": "v0_p2wpkh",
        "scriptpubkey_address": "bc1qmqt4s8tvtq90ufsa7ekjut273wqfek0eejlcju",
        "value": 44714275
      },
      "scriptsig": "",
      "scriptsig_asm": "",
      "witness": [
        "3044022046b55b16617ad822f31d7ac9364dc4535b26e30b57f1ad8c52160e6b88c4a2f20220307ebe829c68cb2489da9e5dd9420c22828ce555ba3daf1de5fa8413583ce0e001",
        "02138ca2409aeb3038672f000b4c01de5389a2ad95fca50f60579ab61d0a2bd7d4"
      ],
      "is_coinbase": false,
      "sequence": 4294967295
    }
  ],
  "vout": [
    {
      "scriptpubkey": "0014a32080f407842f1729a3baf52737617916b90e78",
      "scriptpubkey_asm": "OP_0 OP_PUSHBYTES_20 a32080f407842f1729a3baf52737617916b90e78",
      "scriptpubkey_type": "v0_p2wpkh",
      "scriptpubkey_address": "bc1q5vsgpaq8ssh3w2drht6jwdmp0yttjrnccj66lq",
      "value": 151900
    },
    {
      "scriptpubkey": "0014d817581d6c580afe261df66d2e2d5e8b809cd9f9",
      "scriptpubkey_asm": "OP_0 OP_PUSHBYTES_20 d817581d6c580afe261df66d2e2d5e8b809cd9f9",
      "scriptpubkey_type": "v0_p2wpkh",
      "scriptpubkey_address": "bc1qmqt4s8tvtq90ufsa7ekjut273wqfek0eejlcju",
      "value": 44560006
    }
  ]
}
```

