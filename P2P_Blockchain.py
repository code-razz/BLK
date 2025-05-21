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
        block_string = f"{self.index}{self.timestamp}{self.data}{self.previous_hash}"
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
        except:
            print(f"[{self.port}] Could not connect to peer {peer_port}")

    def handle_connection(self, conn):
        while True:
            try:
                data = conn.recv(4096)
                if not data:
                    break
                block_dict = json.loads(data.decode())
                block = Block.from_dict(block_dict)
                if self.blockchain.is_valid_new_block(block, self.blockchain.get_last_block()):
                    self.blockchain.chain.append(block)
                    print(f"[{self.port}] Block received and added: {block.data}")
            except:
                continue

    def broadcast_block(self, block):
        block_json = json.dumps(block.to_dict()).encode()
        for conn in self.connections:
            try:
                conn.sendall(block_json)
            except:
                pass

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
                else:
                    print(f"[{self.port}] Block invalid, not added.")
            elif choice == "2":
                print(f"\n[{self.port}] Current Blockchain:")
                for block in self.blockchain.chain:
                    print(f"Index: {block.index}, Data: {block.data}, Hash: {block.hash[:10]}...")
            else:
                print("Invalid choice.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python p2p_blockchain.py [this_port] [peer_port1] [peer_port2] ...")
        sys.exit(1)

    this_port = int(sys.argv[1])
    peer_ports = list(map(int, sys.argv[2:]))
    PeerNode(this_port, peer_ports)
