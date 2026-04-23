import hashlib
import json
import time
import os

BLOCKCHAIN_FILE = "blockchain.json"

class Block:
    def __init__(self, index, timestamp, data, previous_hash, nonce=0, hash=None):
        self.index = index
        self.timestamp = timestamp
        self.data = data # {username, public_key, user_id}
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = hash if hash else self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def mine_block(self, difficulty=2):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    def __init__(self):
        self.difficulty = 2
        self.chain = []
        if not self.load_from_disk():
            self.chain = [self.create_genesis_block()]
            self.save_to_disk()

    def create_genesis_block(self):
        genesis_block = Block(0, time.time(), "Genesis Block", "0")
        genesis_block.mine_block(self.difficulty)
        return genesis_block

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, data):
        new_block = Block(
            len(self.chain),
            time.time(),
            data,
            self.get_latest_block().hash
        )
        new_block.mine_block(self.difficulty)
        self.chain.append(new_block)
        self.save_to_disk()

    def save_to_disk(self):
        with open(BLOCKCHAIN_FILE, "w") as f:
            chain_data = [b.__dict__ for b in self.chain]
            json.dump(chain_data, f, indent=4)

    def load_from_disk(self):
        if os.path.exists(BLOCKCHAIN_FILE):
            try:
                with open(BLOCKCHAIN_FILE, "r") as f:
                    chain_data = json.load(f)
                    self.chain = [Block(**b) for b in chain_data]
                    return True
            except Exception as e:
                print(f"Error loading blockchain: {e}")
        return False

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i-1]

            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
        return True

# Singleton instance
blockchain_instance = Blockchain()
