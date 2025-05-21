const {Web3} = require('web3');
const fs = require('fs');

// 1. Setup Web3 (Ganache)
const web3 = new Web3('http://127.0.0.1:8545');

// 2. Load ABI and address from Truffle build output
const artifact = JSON.parse(fs.readFileSync('./build/contracts/TokenTransfer.json', 'utf8'));
const abi = artifact.abi;
const address = artifact.networks['5777'].address; // Ganache default network ID

// 3. Create contract instance
const contract = new web3.eth.Contract(abi, address);

// 4. Main logic
const main = async () => {
  const accounts = await web3.eth.getAccounts();
  const admin = accounts[0];
  const user = accounts[1];

  console.log('Admin:', admin);
  console.log('User:', user);

  // Read public variables
//   const adminAddress = await contract.admin();
  const adminAddress = await contract.methods.admin().call();
  const supply = await contract.methods.totalSupply().call();
  const adminBalance = await contract.methods.getBalance(admin).call();
  const userBalance = await contract.methods.getBalance(user).call();

  console.log('\n=== Initial Balances ===');
  console.log('Admin Address:', adminAddress);
  console.log('Total Supply:', supply);
  console.log('Admin Balance:', adminBalance);
  console.log('User Balance:', userBalance);

  // Transfer tokens (admin to user)
  const transferAmount = web3.utils.toWei('1', 'ether');
  await contract.methods.transferToken(user, transferAmount).send({ from: admin, gas: 200000 });

  console.log('\nTransferred 1 token from admin to user.');

  // Show updated balances
  const newUserBalance = await contract.methods.getBalance(user).call();
  console.log('User New Balance:', newUserBalance);

  // Admin adds tokens to user
  await contract.methods.addTokens(user, web3.utils.toWei('5', 'ether')).send({ from: admin });
  console.log('\nAdmin added 5 tokens to user.');

  // Deposit ETH to contract (user)
  await contract.methods.deposit().send({ from: user, value: web3.utils.toWei('0.1', 'ether'), gas: 100000 });
  console.log('User deposited 0.1 ETH to the contract.');

  // Trigger fallback by sending plain ETH
  await web3.eth.sendTransaction({
    from: user,
    to: address,
    value: web3.utils.toWei('0.05', 'ether'),
    gas: 100000
  });
  console.log('User sent 0.05 ETH directly (fallback triggered).');

  // Display final user balance
  const finalUserBalance = await contract.methods.getBalance(user).call();
  console.log('Final User Token Balance:', finalUserBalance);

  // Show past Transfer events
  const events = await contract.getPastEvents('Transfer', {
    fromBlock: 0,
    toBlock: 'latest'
  });

  console.log('\n=== Transfer Events ===');
  events.forEach(e => {
    console.log(`${e.returnValues.from} -> ${e.returnValues.to} : ${e.returnValues.value}`);
  });
};

main().catch(console.error);
