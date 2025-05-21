import hashlib
import time

# Merkle Tree class
class MerkleTree:
    def __init__(self, transactions):
        self.transactions = transactions
        self.root = self.build_merkle_root(transactions)

    def hash_pair(self, a, b):
        return hashlib.sha256((a + b).encode()).hexdigest()

    def build_merkle_root(self, transactions):
        if not transactions:
            return None

        layer = [hashlib.sha256(tx.encode()).hexdigest() for tx in transactions]

        while len(layer) > 1:
            temp_layer = []
            for i in range(0, len(layer), 2):
                left = layer[i]
                right = layer[i+1] if i+1 < len(layer) else layer[i]  # duplicate last if odd
                temp_layer.append(self.hash_pair(left, right))
            layer = temp_layer

        return layer[0]

# Block class
class Block:
    def __init__(self, index, transactions, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.transactions = transactions
        self.merkle_root = MerkleTree(transactions).root
        self.previous_hash = previous_hash
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = str(self.index) + str(self.timestamp) + str(self.transactions) + self.merkle_root + self.previous_hash
        return hashlib.sha256(block_string.encode()).hexdigest()

# Blockchain class
class Blockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, ["Genesis Block"], "0")
        self.chain.append(genesis_block)

    def add_block(self, transactions):
        previous_hash = self.chain[-1].hash
        new_block = Block(len(self.chain), transactions, previous_hash)
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            previous = self.chain[i - 1]

            if current.hash != current.compute_hash():
                print(f"Block {i} hash mismatch.")
                return False

            if current.previous_hash != previous.hash:
                print(f"Block {i} previous hash mismatch.")
                return False

        return True

    def tamper_with_block(self, block_index, tx_index, new_value):
        if block_index < len(self.chain) and tx_index < len(self.chain[block_index].transactions):
            print(f"Tampering Block {block_index} - changing transaction {tx_index} to '{new_value}'")
            self.chain[block_index].transactions[tx_index] = new_value
            self.chain[block_index].merkle_root = MerkleTree(self.chain[block_index].transactions).root
            self.chain[block_index].hash = self.chain[block_index].compute_hash()

# Main logic
if __name__ == "__main__":
    # Initialize blockchain
    bc = Blockchain()

    # Add 2 blocks with 2 transactions each
    bc.add_block(["Alice pays Bob 5 BTC", "Bob pays Charlie 2 BTC"])
    bc.add_block(["Charlie pays Dave 1 BTC", "Dave pays Eve 0.5 BTC"])

    print("\n--- Blockchain state BEFORE tampering ---")
    for block in bc.chain:
        print(f"Block {block.index} - Hash: {block.hash}, Merkle Root: {block.merkle_root}")

    print(f"\nIs blockchain valid? {bc.is_chain_valid()}")

    # Tamper with transaction
    print("\nAltering state in Block 1...")
    bc.tamper_with_block(1, 0, "Alice pays Bob 500 BTC")

    print("\n--- Blockchain state AFTER tampering ---")
    for block in bc.chain:
        print(f"Block {block.index} - Hash: {block.hash}, Merkle Root: {block.merkle_root}")

    print(f"\nIs blockchain valid? {bc.is_chain_valid()}")
