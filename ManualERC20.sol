// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

/**
 * @title ManualERC20
 * @dev Basic ERC20 token with manual implementation and ETH handling.
 */
contract ManualERC20 {
    // Token metadata
    string private _name;
    string private _symbol;
    uint8 private _decimals;

    // Supply and balances
    uint256 private _totalSupply;
    mapping(address => uint256) private _balances;
    mapping(address => mapping(address => uint256)) private _allowances;

    // Admin/Owner address
    address public owner;

    // Events (ERC20)
    event Transfer(address indexed _from, address indexed _to, uint256 _value);
    event Approval(address indexed _owner, address indexed _spender, uint256 _value);

    // Events (ETH handling)
    event receiveFallback(address indexed sender, uint256 amount);
    event LogFallback(address indexed sender, uint256 amount, bytes data);

    // Modifiers
    modifier onlyOwner() {
        require(msg.sender == owner, "Not contract owner");
        _;
    }

    modifier hasEnough(address _from, uint256 _value) {
        require(_balances[_from] >= _value, "Insufficient balance");
        _;
    }

    modifier validAddress(address _addr) {
        require(_addr != address(0), "Zero address not allowed");
        _;
    }

    constructor(string memory name_, string memory symbol_, uint8 decimals_) {
        _name = name_;
        _symbol = symbol_;
        _decimals = decimals_;
        owner = msg.sender;
    }

    // ERC20 view functions

    function name() public view returns (string memory) {
        return _name;
    }

    function symbol() public view returns (string memory) {
        return _symbol;
    }

    function decimals() public view returns (uint8) {
        return _decimals;
    }

    function totalSupply() public view returns (uint256) {
        return _totalSupply;
    }

    function balanceOf(address _owner) public view returns (uint256) {
        return _balances[_owner];
    }

    function allowance(address _owner, address _spender) public view returns (uint256) {
        return _allowances[_owner][_spender];
    }

    // ERC20 logic

    function transfer(address _to, uint256 _value)
        public
        validAddress(_to)
        hasEnough(msg.sender, _value)
        returns (bool)
    {
        _balances[msg.sender] -= _value;
        _balances[_to] += _value;
        emit Transfer(msg.sender, _to, _value);
        return true;
    }

    function approve(address _spender, uint256 _value)
        public
        validAddress(_spender)
        returns (bool)
    {
        _allowances[msg.sender][_spender] = _value;
        emit Approval(msg.sender, _spender, _value);
        return true;
    }

    function transferFrom(address _from, address _to, uint256 _value)
        public
        validAddress(_to)
        hasEnough(_from, _value)
        returns (bool)
    {
        require(_allowances[_from][msg.sender] >= _value, "Allowance exceeded");

        _balances[_from] -= _value;
        _balances[_to] += _value;
        _allowances[_from][msg.sender] -= _value;
        emit Transfer(_from, _to, _value);
        return true;
    }

    // Mint tokens (onlyOwner)
    function mint(address _to, uint256 _amount)
        public
        onlyOwner
        validAddress(_to)
        returns (bool)
    {
        _totalSupply += _amount;
        _balances[_to] += _amount;
        emit Transfer(address(0), _to, _amount);
        return true;
    }

    // Burn tokens (onlyOwner)
    function burn(address _from, uint256 _amount)
        public
        onlyOwner
        hasEnough(_from, _amount)
        returns (bool)
    {
        _balances[_from] -= _amount;
        _totalSupply -= _amount;
        emit Transfer(_from, address(0), _amount);
        return true;
    }

    // Receive Ether directly
    receive() external payable {
        _balances[owner] += msg.value;
        emit receiveFallback(msg.sender, msg.value);
    }

    // Fallback function for unknown calls or calldata
    fallback() external payable {
        transferToken(owner, msg.value);
        emit LogFallback(msg.sender, msg.value, msg.data);
    }

    // Internal token-like transfer for fallback demo
    function transferToken(address _to, uint256 _value) internal {
        require(_balances[owner] >= _value, "Insufficient tokens");
        _balances[owner] -= _value;
        _balances[_to] += _value;
        emit Transfer(owner, _to, _value);
    }
}
