from time import time
from json import dumps
from hashlib import sha256

class Blockchain(object):
    def __init__(self):
        """
        Initializes the blockchain
        """
        self.podchain = []
        self.current_transactions = []
        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)
        
    def new_block(self, proof, previous_hash=None) -> dict:
        """
        Add a new block to the PodChain
        :param proof: <int> The proof calculated from the PoW alg
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        # If the previous has does not exist, recreate the hash of the previous block
        block = {
            'index': len(self.podchain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.podchain[-1])
        }

        # Reset the current list of transactions
        self.current_transactions = []

        self.podchain.append(block)
        return block
    
    def new_transaction(self, sender, recipient, amount) -> int:
        """
        Adds a new transaction to be mined
        :param sender: <str> Public key of the Sender
        :param recipient: <str> Public key of the Recipient
        :param amount: <int> Amount to be exchanged
        :return: <int> The index of the Block that will contain the transaction data
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block['index'] + 1

    def proof_of_work(self, last_proof) -> int:
        """
        Find a number such that hashing it with the data contains 4 leading zeroes
        :param last_proof: <int> The proof from the previous block
        :return: <int>
        """
        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    @staticmethod
    def valid_proof(last_proof, proof) -> bool:
        """
        Checks if hash(last_proof, proof) contain 4 leading zeroes
        :param last_proof: <int> Previous Proof
        :param proof: <int> Current Guessed Proof
        :return: <bool> True if correct, False if not.
        """
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"
    
    @staticmethod
    def hash(block) -> str:
        """
        Encrypts a the block of data with SHA256
        :param block: <dict> Block containing the data
        :return: <str> The hashed value of the given block
        """
        # Dictionary is sorted to ensure correct location of previous hashes and such
        block_string = dumps(block, sort_keys=True).encode()
        return sha256(block_string).hexdigest()

    @property
    def last_block(self) -> dict:
        """
        Returns the last block in the PodChain
        :return: <dict> The last Block in the PodChain
        """
        return self.podchain[-1]
