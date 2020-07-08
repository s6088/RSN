import datetime
import json
import requests
from django.shortcuts import render,redirect

CONNECTED_NODE_ADDRESS = "http://127.0.0.1:8002"

votes = []


def fetch_votes():
    get_chain_address = "{}/chain".format(CONNECTED_NODE_ADDRESS)
    response = requests.get(get_chain_address,  headers={'Content-Type': 'application/json'},)
    if response.status_code == 200:
        content = []
        chain = json.loads(response.content)

        for block in chain["chain"]:
            for tx in block["transactions"]:
                tx["index"] = block["index"]
                tx["hash"] = block["previous_hash"]
                content.append(tx)

        global votes
        votes = sorted(content, key=lambda k: k['timestamp'], reverse=True)


def home_view(request):
    fetch_votes()
    context = {
        'votes':votes,
        'node_address':CONNECTED_NODE_ADDRESS,
        'readable_time':timestamp_to_string
    }
    return render(request, "index.html", context)


def submit_vote(request):
    voter = request.POST.get('voter')
    candidate = request.POST.get('candidate')

    vote_object = {
        'candidate': candidate,
        'content': voter,
    }

    new_tx_address = "{}/new_transaction".format(CONNECTED_NODE_ADDRESS)
    response = requests.post(new_tx_address,  headers={'Content-Type': 'application/json'}, json=vote_object)
    
    return redirect('/')


def timestamp_to_string(epoch_time):
    return datetime.datetime.fromtimestamp(epoch_time).strftime('%H:%M')
