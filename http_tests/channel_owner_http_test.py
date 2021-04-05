import pytest
import requests
import json
from src import config
from src.error import AccessError, InputError

# registers a user and creates a dictionary of token and user_id. 
# it then returns the value at the token key
@pytest.fixture
def clear():
    requests.delete(config.url + "/clear/v1")

@pytest.fixture
def auth():
    resp = requests.post(config.url + "/auth/register/v2", params = {
        "email" : "boy@gmail.com", 
        "password": "password1", 
        "name_first": "Marc",
        "name_last": "Chee"
    })

    return resp.json()

# creates a channel using the auth fixture and returns the channel id
@pytest.fixture
def channel_create(auth):
    pub_channel1 = requests.post(config.url + "/channels/create/v2", params = {
        "token": auth["token"],
        "name": "pubChannel1",
        "is_public": True
    })
    pub_channel1_id = pub_channel1.json()["channel_id"]

    return pub_channel1_id

# registers two users and stores the results in a tuple
@pytest.fixture
def auth_two():
    resp1 = requests.post(config.url + "/auth/register/v2", params = {
        "email" : "aa@a.com", 
        "password": "password1", 
        "name_first": "Big",
        "name_last": "Boss"
    }).json()

    resp2 = requests.post(config.url + "/auth/register/v2", params = {
        "email" : "bb@b.com", 
        "password": "password2", 
        "name_first": "Marc",
        "name_last": "Chee"
    }).json()
    
    return (resp1, resp2)

@pytest.fixture
def auth_two_channel(auth_two):
    pub_channel = requests.post(config.url + "/channels/create/v2", params = {
        "token": auth_two[0]["token"],
        "name": "PubChannel",
        "is_public": True
    })
    pub_channel_id = pub_channel.json()["channel_id"]

    return pub_channel_id
# ------------------------------------------------------------------------------
# HTTP TESTS FOR CHANNEL_ADDOWNER_V1 AND CHANNEL_REMOVEOWNER_V1 
# WRITTEN BY GORDON  

# adds a new owner to the channel
def test_addowner_and_removeowner(clear, auth_two, auth_two_channel):
    details1 = requests.get(config.url + "/channel/details/v2", params = {
        "token": auth_two[0]["token"],
        "channel_id": channel_create
    }).json()

    length1 = len(details1["owner_members"])

    requests.post(config.url + "/channel/addowner/v1", params = {
        "token": auth_two[0]["token"],
        "channel_id": channel_create,
        "u_id": auth_two[1]["auth_user_id"]
    }).json()

    details2 = requests.get(config.url + "/channel/details/v2", params = {
        "token": auth_two[0]["token"],
        "channel_id": channel_create
    }).json()

    length2 = len(details2["owner_members"])

    assert length1 != length2

    requests.post(config.url + "/channel/removeowner/v1", params = {
        "token": auth_two[0]["token"],
        "channel_id": channel_create,
        "u_id": auth_two[1]["auth_user_id"]
    }).json()

    details3 = requests.get(config.url + "/channel/details/v2", params = {
        "token": auth_two[0]["token"],
        "channel_id": channel_create
    }).json()

    length3 = len(details3["owner_members"])

    assert length2 != length3
    assert length1 == length3

# error checking
# Input Error for invalid channel id
def test_invalid_channel_id_channel_addowner(clear, auth_two, auth_two_channel):
    assert requests.post(config.url + "/channel/addowner/v1", params = {
        "token": auth_two[0]["token"],
        "channel_id": 4,
        "u_id": auth_two[1]["auth_user_id"]
    }).status_code == 400

# Input Error for adding someone whos already an owner of that channel
def test_already_owner_channel_addowner(clear, auth_two, auth_two_channel):
    requests.post(config.url + "/channel/addowner/v1", params = {
        "token": auth_two[0]["token"],
        "channel_id": auth_two_channel,
        "u_id": auth_two[1]["auth_user_id"]
    })

    assert requests.post(config.url + "/channel/addowner/v1", params = {
        "token": auth_two[0]["token"],
        "channel_id": auth_two_channel,
        "u_id": auth_two[1]["auth_user_id"]
    }).status_code == 400

# Access Error for invalid token
def test_unauth_caller_channel_addowner(clear, auth_two, auth_two_channel):
    assert requests.post(config.url + "/channel/addowner/v1", params = {
        "token": "bad_token",
        "channel_id": auth_two_channel,
        "u_id": auth_two[1]["auth_user_id"]
    }).status_code == 404

# Access Error for a caller that is not apart of the channel
def test_bad_caller_channel_addowner(clear, auth_two, auth_two_channel):
    new_id = requests.post(config.url + "/auth/register/v2", params = {
        "email" : "a1b2c3@gmail.com", 
        "password": "passw0rd", 
        "name_first": "Monster",
        "name_last": "Cat"
    }).json()
    
    assert requests.post(config.url + "/channel/addowner/v1", params = {
        "token": new_id["token"],
        "channel_id": auth_two_channel,
        "u_id": auth_two[1]["auth_user_id"]
    }).status_code == 404

    requests.post(config.url + "/channel/join/v2", params = {
        "token": new_id["token"],
        "channel_id": auth_two_channel,
    })

    assert requests.post(config.url + "/channel/addowner/v1", params = {
        "token": new_id["token"],
        "channel_id": auth_two_channel,
        "u_id": auth_two[1]["auth_user_id"]
    }).status_code == 404

# Input Error for invalid target user
def test_invalid_user_channel_addowner(clear, auth_two, auth_two_channel):
    assert requests.post(config.url + "/channel/addowner/v1", params = {
        "token": auth_two[0]["token"],
        "channel_id": auth_two_channel,
        "u_id": 4
    }).status_code == 400

#-------------------------------------------------------------------------------
# Input Error for invalid channel id
def test_invalid_channel_id_channel_removeowner(
    clear, auth_two, auth_two_channel):
    requests.post(config.url + "/channel/addowner/v1", params = {
        "token": auth_two[0]["token"],
        "channel_id": auth_two_channel,
        "u_id": auth_two[1]["auth_user_id"]
    })

    assert requests.post(config.url + "/channel/removeowner/v1", params = {
        "token": auth_two[0]["token"],
        "channel_id": 4,
        "u_id": auth_two[1]["auth_user_id"]
    }).status_code == 400

# Input Error for removing someone who isn't an owner
def test_not_owner_channel_removeowner(clear, auth_two, auth_two_channel):
    new_id = requests.post(config.url + "/auth/register/v2", params = {
        "email" : "a1b2c3@gmail.com", 
        "password": "passw0rd", 
        "name_first": "Monster",
        "name_last": "Cat"
    }).json()

    assert requests.post(config.url + "/channel/removeowner/v1", params = {
        "token": auth_two[0]["token"],
        "channel_id": auth_two_channel,
        "u_id": new_id["auth_user_id"]
    }).status_code == 400

# Input Error for removing someone who is the sole owner of a channel
def test_single_owner_channel_removeowner(clear, auth_two):
    new_channel = requests.post(config.url + "/channels/create/v2", params = {
        "token": auth_two["token"],
        "name": "NewChannel",
        "is_public": True
    })
    new_channel_id = new_channel.json()["channel_id"]

    assert requests.post(config.url + "/channel/removeowner/v1", params = {
        "token": auth_two[0]["token"],
        "channel_id": new_channel_id,
        "u_id": auth_two[1]["auth_user_id"]
    }).status_code == 400

# Input Error for trying to removing an invalid user 
def test_invalid_user_channel_removeowner(clear, auth_two, auth_two_channel):
    assert requests.post(config.url + "/channel/removeowner/v1", params = {
        "token": auth_two[0]["token"],
        "channel_id": auth_two_channel,
        "u_id": 4
    }).status_code == 400

# Access Error for unauthorised caller 
def test_unauth_caller_channel_removeowner(clear, auth_two, auth_two_channel):
    assert requests.post(config.url + "/channel/removeowner/v1", params = {
        "token": "bad_token",
        "channel_id": auth_two_channel,
        "u_id": auth_two[1]["auth_user_id"]
    }).status_code == 404

# Access Error for caller not being apart of the channel
def test_bad_caller_channel_removeowner(clear, auth_two, auth_two_channel):
    new_id = requests.post(config.url + "/auth/register/v2", params = {
        "email" : "a1b2c3@gmail.com", 
        "password": "passw0rd", 
        "name_first": "Monster",
        "name_last": "Cat"
    }).json()

    assert requests.post(config.url + "/channel/removeowner/v1", params = {
        "token": new_id["token"],
        "channel_id": auth_two_channel,
        "u_id": auth_two[1]["auth_user_id"]
    }).status_code == 404
