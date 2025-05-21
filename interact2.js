const Web3 = require("web3");
const provider = new Web3.providers.HttpProvider("http://127.0.0.1:8545");
const web3 = new Web3(provider);


(async () => {

  const accounts = await web3.eth.getAccounts();
  const admin = accounts[0];
  const user1 = accounts[1];
  const user2 = accounts[2];

  console.log("Admin:", admin);
  console.log("User1:", user1);
  console.log("User2:", user2);

  const instance = await TokenTransfer.deployed();
  console.log("Contract address:", instance.address);

  // --- Public variables ---
  const contractAdmin = await instance.admin();
  console.log("Contract Admin:", contractAdmin);

  const supply = await instance.totalSupply();
  console.log("Total Supply:", supply.toString());

})();
