const Web3 = require("web3");
const fs = require("fs");

// 1. Connect to Ganache
const web3 = new Web3("http://127.0.0.1:8545");

// 2. Read compiled ABI and contract address
const contractJson = JSON.parse(fs.readFileSync("build/contracts/TokenTransfer.json"));
const abi = contractJson.abi;
const networkId = Object.keys(contractJson.networks)[0];
const address = contractJson.networks[networkId].address;

// 3. Create contract instance
const contract = new web3.eth.Contract(abi, address);

(async () => {
  const accounts = await web3.eth.getAccounts();
  const admin = accounts[0];
  const user1 = accounts[1];
  const user2 = accounts[2];

  console.log("Admin:", admin);
  console.log("Contract address:", address);

  // --- Read public variables ---
  const contractAdmin = await contract.methods.admin().call();
  const totalSupply = await contract.methods.totalSupply().call();
  console.log("Admin (in contract):", contractAdmin);
  console.log("Total Supply:", totalSupply);

  // --- View functions ---
  const adminBal = await contract.methods.getBalance(admin).call();
  const user1Bal = await contract.methods.getBalance(user1).call();
  const user1SelfBal = await contract.methods.myBalance().call({ from: user1 });

  console.log("Admin balance:", adminBal);
  console.log("User1 balance:", user1Bal);
  console.log("User1 self-check:", user1SelfBal);

  const fee = await contract.methods.calculateTransferFee(1000).call();
  console.log("Transfer fee for 1000:", fee);

  // --- Write: transferToken ---
  console.log("Transferring 1000 tokens from Admin to User1...");
  const transferTx = await contract.methods.transferToken(user1, 1000).send({ from: admin });
  console.log("Transfer Tx hash:", transferTx.transactionHash);

  // --- Admin adds tokens ---
  console.log("Admin adding 500 tokens to User2...");
  const addTx = await contract.methods.addTokens(user2, 500).send({ from: admin });
  console.log("AddTokens Tx hash:", addTx.transactionHash);

  // --- Deposit Ether via deposit() function ---
  console.log("User2 depositing 0.01 ETH...");
  const depositTx = await contract.methods.deposit().send({
    from: user2,
    value: web3.utils.toWei("0.01", "ether")
  });
  console.log("Deposit Tx hash:", depositTx.transactionHash);

  // --- Trigger fallback by sending Ether with data ---
  console.log("Triggering fallback with 0.005 ETH from User1...");
  const fallbackTx = await web3.eth.sendTransaction({
    from: user1,
    to: address,
    value: web3.utils.toWei("0.005", "ether"),
    data: "0x12345678"
  });
  console.log("Fallback Tx hash:", fallbackTx.transactionHash);

  // --- Trigger receive() by sending ETH with no data ---
  console.log("Triggering receive() with 0.002 ETH from User1...");
  const receiveTx = await web3.eth.sendTransaction({
    from: user1,
    to: address,
    value: web3.utils.toWei("0.002", "ether")
  });
  console.log("Receive Tx hash:", receiveTx.transactionHash);

  // --- Listen to events ---
  console.log("Subscribing to all contract events...");
  contract.events
    .allEvents({ fromBlock: 0 })
    .on("data", event => {
      console.log(`📢 Event: ${event.event}`, event.returnValues);
    })
    .on("error", console.error);

  // Wait 5 sec for events to log (optional)
  setTimeout(() => {
    console.log("✅ Done");
    process.exit(0);
  }, 5000);
})();
