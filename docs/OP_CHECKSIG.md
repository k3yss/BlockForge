- OP_CHECKSIG expects two values to be on the stack
- the public key and the signature of the script

- In addition to the stack parameters and the script code itself, in order to operate correctly OP_CHECKSIG needs to know the current transaction and the index of current transaction input. 

!important 
- To verify the signature, one must have the signature, 
  - the serialized transaction, 
  - some data about the output being spent, and 
- the public key that corresponds to the private key used to create the signature.

- Bitcoin signatures have a way of indicating which part of a transaction’s data is
included in the hash signed by the private key using a SIGHASH flag.

- https://wiki.bitcoinsv.io/index.php/OP_CHECKSIG