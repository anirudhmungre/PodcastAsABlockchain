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
guesses = dict()
PRIZE = 100.0

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

@app.route('/mine/cheat', methods=['GET'])
def mine_cheat():
    last_block = podchain.last_block
    last_proof = last_block['proof']
    proof = podchain.proof_of_work(last_proof)

    previous_hash = podchain.hash(last_block)
    block = podchain.new_block(proof, previous_hash)
    podchain.new_transaction('0', node_identifier, PRIZE)

    resp = {
        'message': f'You found the solution! New block added to the PodChain!',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(resp), 200


@app.route('/mine', methods=['POST'])
def mine():
    """
    Must calculate the PoW (proof of work), reward the miner, and add new block to podchain
    """
    global guesses, PRIZE
    data = request.get_json()

    # Ensure all data is sent correctly
    required = ['publicKey', 'guess']
    if not check_params(required, data.keys()):
        return {'message': 'Missing values'}, 400
    
    # Add a guess to the public key of the user who submitted it
    if data['publicKey'] in guesses:
        guesses[data['publicKey']] += 1
    else:
        guesses[data['publicKey']] = 0

    # Get previous blocks solution
    last_block = podchain.last_block
    last_proof = last_block['proof']
    # proof = podchain.proof_of_work(last_proof)
    solved = podchain.valid_solution(last_proof, data['guess'])
    if solved:
        # Send reward based on proof
        # TODO: SEND REWARD BASED ON NUMBER OF TRANSACTIONS
        # podchain.new_transaction("0", node_identifier, 1)

        # Add new block to the podchain!
        previous_hash = podchain.hash(last_block)
        block = podchain.new_block(data['guess'], previous_hash)

        # Divy up prizes
        prize_for_solver = PRIZE * 0.2
        prize_for_donators = PRIZE * 0.5
        prize_for_miners = PRIZE * 0.3

        # Separate prize for solver
        podchain.new_transaction('0', data['publicKey'], prize_for_solver)
        print(f"For SOLVING: Sending {prize_for_solver} PodCoin to {data['publicKey']}")

        # Separate prize for other miners
        total_guesses = float(sum(guesses.values()))
        for userKey, amount in guesses.items():
            portion_won = prize_for_miners * (amount/total_guesses)
            podchain.new_transaction('0', userKey, portion_won)
            print(f'For MINING: Sending {portion_won} PodCoin to {userKey}')
        # Reset the guesses
        guesses = dict()

        # Separate prize for donators
        donators = dict()
        for t in block['transactions']:
            if t['sender'] != '0':
                if t['sender'] in donators:
                    donators[t['sender']] += t['amount']
                else:
                    donators[t['sender']] = t['amount']

        total_donated = float(sum(donators.values()))
        for userKey, amount in donators.items():
            portion_won = prize_for_donators * (amount/total_donated)
            podchain.new_transaction('0', userKey, portion_won)
            print(f'For DONATION: Sending {portion_won} PodCoin to {userKey}')
        
        # Achieve consensus because new block now available
        podchain.achieve_consensus()

        resp = {
            'message': f"You found the solution! Block {block['index']} added to the PodChain! You have been sent {prize_for_solver} plus a portion of the mining prize!",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash']
        }

        return jsonify(resp), 200
    else:
        resp = {
            'message': 'Incorrect value! New block was not mined!',
            'guess': data['guess']
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
    succesful = podchain.new_transaction(data['sender'], data['recipient'], data['amount'])
     
    # True if transaction succesful
    if succesful:
        resp = {
            'message': f"{data['amount']} PodCoin Sent Succesfully!"
        }
        return jsonify(resp), 201
    else:
        resp = {
            'message': f"Not enough funds. Only {podchain.get_amount(data['sender'])}"
        }
        return jsonify(resp), 400

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

# ----------------------------------------------
#  EVERYTHING BELOW UNTIL MARKER IS FOR WALLETS
# ----------------------------------------------

@app.route('/wallets/add', methods=['POST'])
def add_wallet():
    """
    Adds a new wallet to the blockchain
    """
    data = request.get_json()

    # Ensure all data is sent correctly
    required = ['publicKey']
    if not check_params(required, data.keys()):
        return {'message': 'Missing values'}, 400
    
    added = podchain.add_wallet(data['publicKey'])
    if added:
        return {'message': 'Wallet succesfully added!', 'publicKey': data['publicKey']}, 201
    else:
        return {'message': 'Wallet already exists!', 'publicKey': data['publicKey']}, 409

@app.route('/wallets/amount', methods=['POST'])
def get_amount():
    """
    Gets the amount of PodCoin in the given wallet
    """
    data = request.get_json()

    # Ensure all data is sent correctly
    required = ['publicKey']
    if not check_params(required, data.keys()):
        return {'message': 'Missing values'}, 400
    
    amount = podchain.get_amount(data['publicKey'])
    if amount == -1:
        return {'message': 'Wallet does not exist! Please add wallet!', 'publicKey': data['publicKey'], 'amount': amount}, 404 
    else:
        return {'message': 'PodCoin wallet amount refreshed!', 'publicKey': data['publicKey'], 'amount': amount}, 200

# ----------------------------------------------
#  EVERYTHING ABOVE UNTIL MARKER IS FOR WALLETS
# ----------------------------------------------

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
            'media': media,
            'posterKey': posterKey,
            'date': date
        } for id, title, media, posterKey, date in sql.select('Podcast')]
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
