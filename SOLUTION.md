# Solutions.md

### Design Approach and Implementation Details 
![solutions-image](solutions.svg)

### Results and Performance
* The solution handles two types of transactions vin: p2pkh and v0_p2wpkh
* To optimize the solution, checks like amount and double spend checks have been omitted.
* This solution gets a score of 62/100 and performs this under 3 minutes. 

### Conclusion
* Insights gained 
  * The solution was not difficult but rather tricky, and I learned a lot about the internals of Bitcoin systems while doing this assignment.
*  Potential areas for future improvement or research
    * Handle other 3 remaining type of transaction and aim for higher score.
*  List of references or resources    
    * https://learnmeabitcoin.com/
    * https://wiki.bitcoinsv.io/
    * https://en.bitcoin.it/ 
    * #assignment discord chat