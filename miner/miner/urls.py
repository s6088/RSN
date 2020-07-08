from django.contrib import admin
from django.urls import re_path

from .views import * 

urlpatterns = [
    re_path(r'^new_transaction$', new_transaction, name='new_transaction'),
    re_path(r'^chain$', get_chain, name='get_chain'),
    re_path(r'^mine$', mine_unconfirmed_transactions, name='mine_unconfirmed_transactions'),
    # re_path(r'^register_node$', register_new_peers, name='register_new_peers'),
    # re_path(r'^register_with$', register_with_existing_node, name='register_with_existing_node'),
    # re_path(r'^add_block$', verify_and_add_block, name='verify_and_add_block'),
    # re_path(r'^pending_tx$', get_pending_tx, name='get_pending_tx'),
    # re_path(r'^add_block$', verify_and_add_block, name='verify_and_add_block'),
    # re_path(r'^add_block$', verify_and_add_block, name='verify_and_add_block'),
    # re_path(r'^add_block$', verify_and_add_block, name='verify_and_add_block'),
]
