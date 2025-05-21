// SPDX-License-Identifier: MIT
pragma solidity >=0.6.21 <0.9.0;

contract TokenTransfer{
    address public admin;
    uint256 public totalSupply;
    mapping(address => uint256) private balances;

    constructor(){
        admin=msg.sender;
        totalSupply=1000000;
        balances[admin]=totalSupply;
    }
    
    modifier onlyAdmin(){
        require(msg.sender==admin,"Not authorized! ONly admin can call this.");
        _;
    }

    modifier hasSufficientBalance(uint256 amount){
        uint256 totAmount=amount+calculateTransferFee(amount);
        require(balances[msg.sender] >= totAmount,"Not enough balance to transfer");
        _;
    }

    //TASK 3.1:
    event Transfer(address indexed from, address indexed to, uint256 value);
    event LogFallback(address sender, uint value,bytes data);
    event Deposit(address sender,uint value,bytes data);
    event receiveFallback(address indexed sender, uint value);

    receive() external payable {
        balances[admin] += msg.value;
        emit receiveFallback(msg.sender, msg.value);
        // admin.transfer(msg.value);
    }
    fallback() external payable{
        transferToken(admin, msg.value);
        emit LogFallback(msg.sender, msg.value,msg.data);
    }

    // TASK 1:
    function getBalance(address account) public view returns(uint256){
        return balances[account];
    }

    function myBalance() public view returns(uint){
        return balances[msg.sender];
    }

    function calculateTransferFee(uint256 amount) public pure returns(uint256){
        return (amount*1)/100;     //✅✅NOTE: 0.01*amount  --> Since Solidity only supports integer arithmetic, 0.01 * amount will ❌not work as expected.
                                    //✅✅NOTE: 1/100*amount 1 / 100 in Solidity is integer division, which results in 0 because Solidity rounds down.  This means 0 * amount = 0, so the function will always return 0.
    }

    function transferToken(address to, uint256 amount) public payable hasSufficientBalance(amount){
        uint256 totAmount=amount+calculateTransferFee(amount);
        balances[msg.sender] -= totAmount;
        balances[to] += amount;
        emit Transfer(msg.sender,to,amount);
    }

    function addTokens(address to, uint256 amount) public payable  onlyAdmin{
        balances[to] += amount;
        emit Transfer(msg.sender,to,amount);
    }

    function deposit() external payable{
        balances[msg.sender] += msg.value;
        emit Deposit(msg.sender,msg.value,msg.data);
    }
}