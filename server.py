from podchain import PodChain

from flask import Flask, jsonify
from uuid import uuid4

# Initialize Flask Object
app = Flask(__name__)

# Generate a globally unique address for this server node
node_identifier = str(uuid4()).replace('-', '')

# Initialize the PodChain
podchain = PodChain()


@app.route('/mine', methods=['GET'])
def mine():
    """
    A block is mined (verified in chain)
    """
    return "This is where the block is mined."
  
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """
    A new transaction is added
    """
    return "This is where the transaction is added."

@app.route('/chain', methods=['GET'])
def full_chain():
    """
    The entire chain is returned for verification
    """
    response = {
        'chain': podchain.chain,
        'length': len(podchain.chain),
    }
    return jsonify(response), 200

if __name__ == '__main__':
    app.run(port=5000)
