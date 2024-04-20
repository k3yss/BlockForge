- Hint: You have to serialise the transaction and then create a commitment hash. @anmol Sharma

- Name of the file is the hash of txid

- So to check if you are parsing the transaction correctly, you can calculate txid from hex and hash the txid to match against file name 

- sha256(sha256(serialized transaction)) is txid, sha256(txid) is the file name

- You have to:
- serialize the transaction as per the input address type (scriptpubkey_type in the prevout)
append the sighash_type (present at the end of the signature you are verifying) at the end of the trimmed tx byte sequence 
- double hash 256(trimmed_tx)
- parse the signature, publickey, tx_hash into SIGNATURE, PUBLIC KEY and MESSAGE objects using Secp256k1 libraries, then verify the message against the public key and signature  using ecdsa verification functions

basic procedure is this, you have do research for the whole thing.


- if b is spending a, then a should come before b in the final block


- I created a message hash and checked the message with the signature and public key in scriptsig

- assume validity of locktime based on block height. You need to validate locktime which are UNIX timestamps

- So we cannot include transactions that have a future UNIX timestamp?
  - Yep   

- In the output.txt file we have to write txids in reverse byte order right?

- For anyone here who's having difficulty understanding/parsing scripts
https://github.com/bitcoin-core/btcdeb