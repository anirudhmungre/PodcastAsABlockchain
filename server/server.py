from sys import argv, exit
from podchain import PodChain
from sql import SQL

from flask import Flask, jsonify, request
from flask_cors import CORS
from uuid import uuid4
from datetime import datetime

# Make sure user is using correct number of args
if len(argv) < 2:
    print("ERROR: Not enough args")
    print("USAGE: python server.py <port>")
    exit(0)
elif len(argv) > 2:
    print("ERROR: Too many enough args")
    print("USAGE: python server.py <port>")
    exit(0)

# Initialize Flask Object
app = Flask(__name__)
CORS(app)

def check_params(required, given) -> bool:
    """
    Ensures that all the required params are posted
    :param required: <list> List of required params on POST
    :param given: <list> List of given params in body of POST
    :return: <bool> True if correct params provided, False if not
    """
    if not all(x in given for x in required):
        return False
    return True

# -------------------------------------------------
#  EVERYTHING BELOW UNTIL MARKER IS FOR BLOCKCHAIN
# -------------------------------------------------

# Generate a unique id for this server node
node_identifier = str(uuid4()).replace('-', '')

# Initialize the PodChain
podchain = PodChain()

@app.route('/chain', methods=['GET'])
def full_chain():
    """
    The entire chain is returned for verification
    """
    resp = {
        'chain': podchain.podchain,
        'length': len(podchain.podchain)
    }
    return jsonify(resp), 200

@app.route('/mine', methods=['GET'])
def mine():
    """
    Must calculate the PoW (proof of work), reward the miner, and add new block to podchain
    """
    # Get proof of work
    last_block = podchain.last_block
    last_proof = last_block['proof']
    proof = podchain.proof_of_work(last_proof)

    # Send reward based on proof
    # TODO: SEND REWARD BASED ON NUMBER OF TRANSACTIONS
    podchain.new_transaction("0", node_identifier, 1)

    # Add new block to the podchain!
    previous_hash = podchain.hash(last_block)
    block = podchain.new_block(proof, previous_hash)

    resp = {
        'message': "New Block Added to PodChain",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(resp), 200
  
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """
    A new transaction is added
    """
    data = request.get_json()

    # Ensure all data is sent correctly
    required = ['sender', 'recipient', 'amount']
    if not check_params(required, data.keys()):
        return {'message': 'Missing values'}, 400

    # Add a new Transaction
    index = podchain.new_transaction(data['sender'], data['recipient'], data['amount'])

    resp = {
        'message': f'Transaction added at index: {index}'
    }
    return jsonify(resp), 201

@app.route('/nodes/add', methods=['POST'])
def add_node():
    """
    Adds a node to the distributed system by making local nodes aware of all other node addresses
    """
    data = request.get_json()
    # Retrieve the new list of given nodes
    nodes = data.get('nodes')
    if nodes is None:
        return {'message': 'Invalid or empty list of nodes'}, 400
    # Loop through all given nodes and add each to node set
    for node in nodes:
        podchain.add_node(node)

    resp = {
        'message': 'Successfully added new nodes',
        'total_nodes': list(podchain.nodes),
    }
    return jsonify(resp), 201

@app.route('/nodes/consensus', methods=['GET'])
def consensus():
    """
    Requests the blockchain to achieve consensus within nodes
    """
    # New chain is a boolean that says whether a new chain was adopted or not
    new_chain = podchain.achieve_consensus()

    if new_chain:
        resp = {
            'message': 'The local chain was replaced',
            'new_chain': podchain.chain
        }
    else:
        resp = {
            'message': 'The local chain is the leader',
            'chain': podchain.chain
        }

    return jsonify(resp), 200
# -------------------------------------------------
#  EVERYTHING ABOVE UNTIL MARKER IS FOR BLOCKCHAIN
# -------------------------------------------------

# --------------------------------------------------
#  EVERYTHING BELOW UNTIL MARKER IS FOR APPLICATION
# --------------------------------------------------

sql = SQL()

@app.route('/podcasts', methods=['GET'])
def podcasts():
    """
    This will return all podcasts as a list in the below format
    {
        'id': uuid;
        'title': string;
        'media': base64;
        'posterKey': string;
        'date': DATE;
    }
    """
    resp = [{
            'id': id,
            'title': title,
            'posterKey': posterKey,
            'date': date
        } for id, title, posterKey, date in sql.select('Podcast')]
    return jsonify(resp), 200

@app.route('/podcasts/add', methods=['POST'])
def add_podcast():
    """
    This will add a podcast in the below format
    { 
        'id': uuid;
        'title': string;
        'media': base64;
        'posterKey': string;
        'date': DATE;
    }
    """
    data = request.get_json()
    required = ['title', 'media', 'posterKey']
    if data and not check_params(required, data.keys()):
        return jsonify({'message': 'Missing values!'}), 400

    podcast_id, date = sql.insert('Podcast', data)

    resp = {
        'message': 'The below was added as a podcast.',
        'podcast': {
            'id': podcast_id,
            'title': data['title'],
            'media': data['media'],
            'posterKey': data['posterKey'],
            'date': date
        }
    }

    return resp, 200

# --------------------------------------------------
#  EVERYTHING ABOVE UNTIL MARKER IS FOR APPLICATION
# --------------------------------------------------
if __name__ == '__main__':
    print(f'Starting server on port {argv[1]}')
    app.run(port=argv[1], debug=True)
