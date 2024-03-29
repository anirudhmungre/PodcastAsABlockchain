from time import time
from json import dumps
from hashlib import sha256
from urllib.parse import urlparse
from requests import get

class PodChain(object):
    def __init__(self):
        """
        Initializes the blockchain
        """
        # Change difficulty to make blocks harder to mine
        self.difficulty = 1
        # Initialize chain and transactions as empty until genesis block is created
        self.podchain = list()
        self.current_transactions = list()
        # Initialize the market cap of the blocks to 1 billion
        self.wallets = {'0': 1000000000.0 }
        # This node initially is unaware of any other node
        self.nodes = set()
        # Create the genesis block
        self.new_block(100, 1)
        
    def new_block(self, proof, previous_hash=None) -> dict:
        """
        Add a new block to the PodChain
        :param proof: <int> The proof calculated from the PoW alg
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """
        # If the previous has does not exist, recreate the hash of the previous block
        # Generate the required block info
        block = {
            'index': len(self.podchain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.last_block),
            'wallets': self.wallets
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Add new block to blockchain
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
        # Check wallets added prior
        self.add_wallet(sender)
        self.add_wallet(recipient)

        if self.wallets[sender] - amount < 0:
            return False
        # Remove sender funds
        self.wallets[sender] -= amount
        # Add to recipient wallet
        self.wallets[recipient] += amount
        # Record Transaction
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return True

    def proof_of_work(self, previous_proof) -> int:
        """
        Find a number such that hashing it with the data contains 4 leading zeroes
        :param previous_proof: <int> The proof from the previous block
        :return: <int>
        """
        # Cheat way to get server to check a bunch of prrofs
        guess = 0
        while self.valid_solution(previous_proof, guess) is False:
            guess += 1

        return guess

    def add_node(self, location) -> None:
        """
        Adds a node to the list of node locations this node is aware of
        :param location: <str> Locatable http address of the node
        :return: None
        """
        # Extracts the ip and port of the given node
        parsed_url = urlparse(location)
        self.nodes.add(parsed_url.netloc)

    def validate_chain(self, chain) -> bool:
        """
        Check if 'chain' is a valid blockchain by a series of restraints
        :param chain: <list> A blockchain to validate
        :return: <bool> True if valid, False if not
        """
        previous_block = chain[0]
        # Loop through all blocks to validate chain
        for block in chain[1:]:
            # Make sure the hash of the previous block matches
            if block['previous_hash'] != self.hash(previous_block):
                return False
            # Check that the PoW is correctly calculated
            if not self.valid_solution(previous_block['proof'], block['proof']):
                return False
            # Make this block the new previous block
            previous_block = block

        # If it passes all tests it is a valid chain
        return True
    
    def achieve_consensus(self) -> bool:
        """
        Replace chain with longest available and achieve consensus
        :return: <bool> True if the local podchain was replaced, False if it was not
        """
        new_chain = False

        # Get max length because only chains larger than the current chain are more valid
        local_length = len(self.podchain)

        # Check chains of all other nodes
        for node in self.nodes:
            # Make a get request to receive the other nodes podchain
            response = get(f'http://{node}/chain')

            # If http response is successful check chain otherwise it might be a malicious node
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Validate chain if longer, if both True, replace local chain
                if length > local_length and self.valid_chain(chain):
                    local_length = length
                    self.chain = chain
                    new_chain = True

        # Return true if local chain was replaced and false otherwise
        return new_chain

    def valid_solution(self, previous_proof, guess) -> bool:
        """
        Checks if previous and current guess combined contain 4 leading zeroes
        :param previous_proof: <int> Previous Proof
        :param proof: <int> Current Guessed Proof
        :return: <bool> True if correct, False if not.
        """
        guess = f'{previous_proof}{guess}'.encode()
        guess_hash = sha256(guess).hexdigest()
        return guess_hash[:self.difficulty] == "0" * self.difficulty

    def add_wallet(self, public_key) -> bool:
        """
        Adds a wallet to the podchains wallets
        :param public_key: <str> The public key of the wallet to add
        :return: <bool> True if wallet added, False if already exists
        """
        # Check if wallet already in podchain
        if public_key in self.wallets:
            return False
        self.wallets[public_key] = 0.0

        return True

    def get_amount(self, public_key) -> float:
        """
        Returns the PodCoin amount in a specific wallet
        :param public_key: <str> Wallet public key to get amount of
        :return: <float> Amount of PodCoin in specified wallet -1.0 if wallet doesn't exist
        """
        if public_key in self.wallets:
            return self.wallets[public_key]
        else:
            return -1.0
    
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
