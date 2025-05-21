const {Web3} = require("web3");
const contract = require("@truffle/contract");
const fs = require("fs");

// Load ABI + network data
const contractJson = JSON.parse(fs.readFileSync("build/contracts/TokenTransfer.json"));
const TokenTransfer = contract(contractJson);

// Connect to Ganache
const provider = new Web3.providers.HttpProvider("http://127.0.0.1:8545");
const web3 = new Web3(provider);
TokenTransfer.setProvider(provider);

(async () => {
  const accounts = await web3.eth.getAccounts();
  const admin = accounts[0];
  const user1 = accounts[1];
  const user2 = accounts[2];

  console.log("Accounts:", accounts);

  const contractInstance = await TokenTransfer.deployed();
  console.log("Deployed at:", contractInstance.address);

  // ----- READ PUBLIC VARIABLES -----
  const contractAdmin = await contractInstance.admin();
  const totalSupply = await contractInstance.totalSupply();
  console.log("Admin:", contractAdmin);
  console.log("Total Supply:", totalSupply.toString());

  // ----- CHECK BALANCES -----
  const adminBalance = await contractInstance.getBalance(admin);
  const user1Balance = await contractInstance.getBalance(user1);
  console.log("Admin Balance:", adminBalance.toString());
  console.log("User1 Balance:", user1Balance.toString());

  // ----- VIEW MY BALANCE (user1) -----
  const user1MyBalance = await contractInstance.myBalance({ from: user1 });
  console.log("User1 - myBalance():", user1MyBalance.toString());

  // ----- PURE FUNCTION -----
  const fee = await contractInstance.calculateTransferFee(1000);
  console.log("Fee for 1000 tokens:", fee.toString());

  // ----- ADMIN - addTokens to user1 -----
  const addTokensTx = await contractInstance.addTokens(user1, 5000, { from: admin });
  console.log("Admin added tokens to user1:", addTokensTx.tx);

  // ----- USER1 - transferToken to user2 -----
  const amount = 1000;
  const transferTx = await contractInstance.transferToken(user2, amount, {
    from: user1,
    gas: 300000,
  });
  console.log(`User1 transferred ${amount} to User2. Tx:`, transferTx.tx);

  // ----- BALANCES AFTER TRANSFER -----
  const user2Balance = await contractInstance.getBalance(user2);
  console.log("User2 Balance:", user2Balance.toString());

  // ----- DEPOSIT to contract (user2 sends Ether) -----
  const depositTx = await contractInstance.deposit({
    from: user2,
    value: web3.utils.toWei("0.01", "ether"),
  });
  console.log("User2 deposited Ether. Tx:", depositTx.tx);

  // ----- RECEIVE FUNCTION -----
  const sendEtherToContract = await web3.eth.sendTransaction({
    from: user2,
    to: contractInstance.address,
    value: web3.utils.toWei("0.005", "ether"),
  });
  console.log("User2 triggered receive(). Tx:", sendEtherToContract.transactionHash);

  // ----- FALLBACK FUNCTION -----
  const fallbackTx = await web3.eth.sendTransaction({
    from: user2,
    to: contractInstance.address,
    value: web3.utils.toWei("0.002", "ether"),
    data: "0x12345678", // random data triggers fallback()
  });
  console.log("Fallback triggered. Tx:", fallbackTx.transactionHash);

  // ----- LISTENING TO EVENTS (OPTIONAL) -----
  const pastEvents = await contractInstance.getPastEvents("Transfer", {
    fromBlock: 0,
    toBlock: "latest",
  });
  console.log("Transfer events:", pastEvents);

  process.exit(0);
})();
