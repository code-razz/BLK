import hashlib
import time

class Block:
    def __init__(self, index, previous_hash, timestamp, data, difficulty):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.data = data
        self.difficulty = difficulty
        self.nonce = 0
        self.hash = self.compute_proof_of_work()

    def compute_hash(self):
        block_string = f"{self.index}{self.previous_hash}{self.timestamp}{self.data}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()

    def compute_proof_of_work(self):
        prefix = '0' * self.difficulty
        while True:
            hash_value = self.compute_hash()
            if hash_value.startswith(prefix):
                return hash_value
            self.nonce += 1


class Blockchain:
    def __init__(self, difficulty=4):
        self.difficulty = difficulty
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, "0", time.time(), "Genesis Block", self.difficulty)

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        prev_block = self.get_latest_block()
        new_block = Block(len(self.chain), prev_block.hash, time.time(), data, self.difficulty)
        self.chain.append(new_block)

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current = self.chain[i]
            prev = self.chain[i - 1]
            if current.hash != current.compute_hash():
                return False
            if current.previous_hash != prev.hash:
                return False
        return True

    def print_chain(self):
        for block in self.chain:
            print(f"Index: {block.index}")
            print(f"Timestamp: {block.timestamp}")
            print(f"Data: {block.data}")
            print(f"Previous Hash: {block.previous_hash}")
            print(f"Hash: {block.hash}")
            print(f"Nonce: {block.nonce}")
            print("-" * 40)


# Example usage
if __name__ == "__main__":
    blockchain = Blockchain(difficulty=4)
    
    blockchain.add_block("Transaction 1: Alice -> Bob")
    blockchain.add_block("Transaction 2: Bob -> Charlie")
    blockchain.add_block("Transaction 3: Charlie -> Dave")

    blockchain.print_chain()

    print("Is blockchain valid?", blockchain.is_chain_valid())
