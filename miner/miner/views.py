from django.shortcuts import render, redirect
from .util import *
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt


blockchain = Blockchain()
blockchain.create_genesis_block()
peers = set()


@csrf_exempt
def new_transaction(request):
    tx_data =  json.loads(request.body.decode('utf8').replace("'", '"'))
    tx_data["timestamp"] = time.time()
    blockchain.add_new_transaction(tx_data)
    return HttpResponse(status=200)



def get_chain(request):
    chain_data = []
    print(len(blockchain.chain))
    for block in blockchain.chain:
        chain_data.append(block.__dict__)
    content = {"length": len(chain_data),
                       "chain": chain_data,
                       "peers": list(peers)}
    
    return JsonResponse(content, safe=False)



def mine_unconfirmed_transactions(request):
    result = blockchain.mine()
    if not result:
        return HttpResponse("No transactions to mine")
    else:
        chain_length = len(blockchain.chain)
        consensus()
        if chain_length == len(blockchain.chain):
            announce_new_block(blockchain.last_block)
        return HttpResponse("Block #{} is mined.".format(blockchain.last_block.index))



def register_new_peers():
    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400
    peers.add(node_address)
    return get_chain()


# @app.route('/register_with', methods=['POST'])
def register_with_existing_node():

    node_address = request.get_json()["node_address"]
    if not node_address:
        return "Invalid data", 400

    data = {"node_address": request.host_url}
    headers = {'Content-Type': "application/json"}

    # Make a request to register with remote node and obtain information
    response = requests.post(node_address + "/register_node",
                             data=json.dumps(data), headers=headers)

    if response.status_code == 200:
        global blockchain
        global peers
        # update chain and the peers
        chain_dump = response.json()['chain']
        blockchain = create_chain_from_dump(chain_dump)
        peers.update(response.json()['peers'])
        return "Registration successful", 200
    else:
        # if something goes wrong, pass it on to the API response
        return response.content, response.status_code


def create_chain_from_dump(chain_dump):
    generated_blockchain = Blockchain()
    generated_blockchain.create_genesis_block()
    for idx, block_data in enumerate(chain_dump):
        if idx == 0:
            continue  # skip genesis block
        block = Block(block_data["index"],
                      block_data["transactions"],
                      block_data["timestamp"],
                      block_data["previous_hash"],
                      block_data["nonce"])
        proof = block_data['hash']
        added = generated_blockchain.add_block(block, proof)
        if not added:
            raise Exception("The chain dump is tampered!!")
    return generated_blockchain



# @app.route('/add_block', methods=['POST'])
def verify_and_add_block():
    block_data = request.get_json()
    block = Block(block_data["index"],
                  block_data["transactions"],
                  block_data["timestamp"],
                  block_data["previous_hash"],
                  block_data["nonce"])

    proof = block_data['hash']
    added = blockchain.add_block(block, proof)

    if not added:
        return "The block was discarded by the node", 400

    return "Block added to the chain", 201



#@app.route('/pending_tx')
def get_pending_tx():
    return json.dumps(blockchain.unconfirmed_transactions)


def consensus():
    global blockchain
    longest_chain = None
    current_len = len(blockchain.chain)

    for node in peers:
        response = requests.get('{}chain'.format(node))
        length = response.json()['length']
        chain = response.json()['chain']
        if length > current_len and blockchain.check_chain_validity(chain):
            current_len = length
            longest_chain = chain

    if longest_chain:
        blockchain = longest_chain
        return True

    return False


def announce_new_block(block):
    for peer in peers:
        url = "{}add_block".format(peer)
        headers = {'Content-Type': "application/json"}
        requests.post(url,
                      data=json.dumps(block.__dict__, sort_keys=True),
                      headers=headers)

