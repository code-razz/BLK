import socket
import threading
import sys
import time
import hashlib
import json

# -------------------- Block Class -------------------- #
class Block:
    def __init__(self, index, timestamp, data, previous_hash, hash=None):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = hash or self.calculate_hash()

    def calculate_hash(self):
        block_content = {
            'index': self.index,
            'timestamp': self.timestamp,
            'data': self.data,
            'previous_hash': self.previous_hash
        }
        block_string = json.dumps(block_content, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def to_dict(self):
        return {
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "hash": self.hash
        }

    @staticmethod
    def from_dict(data):
        return Block(
            data["index"],
            data["timestamp"],
            data["data"],
            data["previous_hash"],
            data["hash"]
        )

# -------------------- Blockchain Class -------------------- #
class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, 0, "Genesis Block", "0")

    def get_last_block(self):
        return self.chain[-1]

    def add_block(self, data):
        last = self.get_last_block()
        new_block = Block(len(self.chain), time.time(), data, last.hash)
        if self.is_valid_new_block(new_block, last):
            self.chain.append(new_block)
            return new_block
        return None

    def is_valid_new_block(self, new_block, previous_block):
        return (
            previous_block.index + 1 == new_block.index and
            previous_block.hash == new_block.previous_hash and
            new_block.hash == new_block.calculate_hash()
        )

    def is_valid_chain(self, chain):
        if not chain or chain[0].hash != self.chain[0].hash:
            return False
        for i in range(1, len(chain)):
            if not self.is_valid_new_block(chain[i], chain[i-1]):
                return False
        return True

    def replace_chain(self, new_chain):
        if len(new_chain) > len(self.chain) and self.is_valid_chain(new_chain):
            self.chain = new_chain
            return True
        return False

# -------------------- Peer Node Class -------------------- #
class PeerNode:
    def __init__(self, port, peer_ports):
        self.port = port
        self.peers = peer_ports
        self.blockchain = Blockchain()
        self.connections = []

        threading.Thread(target=self.start_server, daemon=True).start()

        for peer_port in self.peers:
            self.connect_to_peer(peer_port)

        self.run_console()

    def start_server(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(("localhost", self.port))
        server.listen()
        while True:
            conn, _ = server.accept()
            self.connections.append(conn)
            threading.Thread(target=self.handle_connection, args=(conn,), daemon=True).start()

    def connect_to_peer(self, peer_port):
        try:
            conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            conn.connect(("localhost", peer_port))
            self.connections.append(conn)
            threading.Thread(target=self.handle_connection, args=(conn,), daemon=True).start()
            # Request full chain from the peer
            self.send_message(conn, {"type": "CHAIN_REQUEST"})
        except:
            print(f"[{self.port}] Could not connect to peer {peer_port}")

    def handle_connection(self, conn):
        while True:
            try:
                data = conn.recv(8192)
                if not data:
                    break
                message = json.loads(data.decode())
                self.handle_message(conn, message)
            except:
                continue

    def handle_message(self, conn, message):
        msg_type = message.get("type")

        if msg_type == "CHAIN_REQUEST":
            chain_data = [block.to_dict() for block in self.blockchain.chain]
            self.send_message(conn, {"type": "CHAIN_RESPONSE", "chain": chain_data})

        elif msg_type == "CHAIN_RESPONSE":
            new_chain = [Block.from_dict(b) for b in message["chain"]]
            replaced = self.blockchain.replace_chain(new_chain)
            if replaced:
                print(f"[{self.port}] Chain updated with longer valid chain from peer.")

        elif msg_type == "NEW_BLOCK":
            block = Block.from_dict(message["block"])
            if self.blockchain.is_valid_new_block(block, self.blockchain.get_last_block()):
                self.blockchain.chain.append(block)
                print(f"[{self.port}] New block added from peer: {block.data}")
                self.broadcast_block(block, exclude=conn)
            else:
                print(f"[{self.port}] Received invalid block, ignored.")

    def send_message(self, conn, message):
        try:
            conn.sendall(json.dumps(message).encode())
        except:
            pass

    def broadcast_block(self, block, exclude=None):
        message = {"type": "NEW_BLOCK", "block": block.to_dict()}
        for conn in self.connections:
            if conn != exclude:
                self.send_message(conn, message)

    def run_console(self):
        while True:
            print(f"\n[{self.port}] Choose an option:\n1. Mine Block\n2. Print Blockchain")
            choice = input("Enter choice: ").strip()
            if choice == "1":
                data = input("Enter data for block: ")
                new_block = self.blockchain.add_block(data)
                if new_block:
                    print(f"[{self.port}] Block mined and broadcasted: {data}")
                    self.broadcast_block(new_block)
            elif choice == "2":
                print(f"\n[{self.port}] Current Blockchain:")
                for block in self.blockchain.chain:
                    print(f"Index: {block.index}, Data: {block.data}, Hash: {block.hash[:10]}...")
            else:
                print("Invalid choice.")
