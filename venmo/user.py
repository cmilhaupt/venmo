'''
User module.
'''
import json

import requests

import venmo


def id_from_username(username):
    for u in search(username):
        if u['username'].lower() == username.lower():
            return u['id']
    return None


def print_search(query):
    print(json.dumps(search(query), indent=4))


def search(query):
    venmo.auth.ensure_access_token()
    response = requests.get(
        venmo.settings.USERS_URL,
        params={
            'limit': 5,
            'query': query,
        },
        headers={
            'Authorization': 'Bearer {}'.format(venmo.auth.get_access_token())
        },
    )
    users = response.json()['data']
    results = []
    for u in users:
        results.append({
            'id': u['id'],
            'username': u['username'],
            'display_name': u['display_name'],
            'profile_picture_url': u['profile_picture_url'],
        })
    return results

def get_profile_id():
    response = venmo.singletons.session().get(venmo.settings.PROFILE_URL)
    return response.json()['data']['user']['id']

def feed(limit=10):
    venmo.auth.ensure_access_token()
    user_id = get_profile_id()
    response = venmo.singletons.session().get(venmo.settings.FEED_URL + user_id + "?limit=" + str(limit))
    response_dict = response.json()
    for i,d in enumerate(response_dict['data']):
        print("Transaction #" + str(i + 1))
        if d['type'] == 'transfer':
            print("    Transfered $" + str(d['transfer']['amount']) + " to '" +
                d['transfer']['destination']['name'] + "' on " +
                d['transfer']['date_requested'].split('T')[0])
        elif d['type'] == 'payment':
            if d['payment']['actor']['id'] == user_id:
                print("    You paid " + d['payment']['target']['user']['display_name'] + " $" +
                    str(d['payment']['amount']) + " on " +
                    d['date_created'].split('T')[0])
            else:
                print("    " + d['payment']['actor']['display_name'] + " paid you $" +
                    str(d['payment']['amount']) + " on " + 
                    d['date_created'].split('T')[0])
        else:
            print("    You paid " + d['authorization']['merchant']['display_name'] + " $" +
                str((d['authorization']['amount']/100.0)) + " on " +
                    d['date_created'].split('T')[0])
        print()
