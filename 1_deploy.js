const TokenTransfer = artifacts.require("TokenTransfer");

module.exports = async function(deployer, network, accounts) {
  try {
    // Get the first account as the admin
    const admin = accounts[0];
    
    console.log('Deploying TokenTransfer contract...');
    console.log('Network:', network);
    console.log('Admin address:', admin);

    // Deploy the contract
    await deployer.deploy(TokenTransfer);
    
    // Get the deployed contract instance
    const tokenTransfer = await TokenTransfer.deployed();
    
    console.log('TokenTransfer contract deployed at:', tokenTransfer.address);
    
    // Verify the admin is set correctly
    const contractAdmin = await tokenTransfer.admin();
    console.log('Contract admin:', contractAdmin);
    
    // Verify initial total supply
    const totalSupply = await tokenTransfer.totalSupply();
    console.log('Initial total supply:', totalSupply.toString());

  } catch (error) {
    console.error('Error during deployment:', error);
    throw error; // Re-throw to ensure Truffle knows the deployment failed
  }
};
