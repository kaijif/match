import pandas as pd
import requests
import stringdist
import inflection


class UTRPlayer:
    def __init__(self, data):
        self.__dict__.update({inflection.underscore(k): v for k, v in data.items()})
        self.name = self.display_name
        self.utr = self.singles_utr


def query_utr(player_name,return_all=False):
    cookies = {
        'jwt': 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJNZW1iZXJJZCI6IjM3MTE5MCIsImVtYWlsIjoiZnNqaWFuQGhvdG1haWwuY29tIiwiVmVyc2lvbiI6IjEiLCJEZXZpY2VMb2dpbklkIjoiNjYxNDAzMiIsIm5iZiI6MTYxOTU1NDM2MCwiZXhwIjoxNjIyMTQ2MzYwLCJpYXQiOjE2MTk1NTQzNjB9.oAUoOkin1XhtcPuzX6K2ezb7Ga6-MzrfWpcrd75268w',
    }
    payload = {
        'query': f'{player_name}'
    }
    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "cache-control": "max-age=0",
        "dnt": "1",
        "referer": "https://playtennis.usta.com/Competitions/triad-tennis-management/Tournaments/events/86B7BC30-1F13-400F-A596-B0AECAE67DEB",
        "sec-ch-ua": "\"Google Chrome\";v=\"89\", \"Chromium\";v=\"89\", \";Not A Brand\";v=\"99\"",
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-origin",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
    }
    utr_request = requests.get('https://app.myutr.com/api/v2/search/players', params=payload, cookies=cookies,
                               headers=headers)
    data = utr_request.json()
    for player_data in data['hits']:
        player_data = player_data['source']
        player_data['displayName'] =  ' '.join([name.strip() for name in player_data.pop('displayName').split(' ') if ' ' not in name and name])
    if data['total'] == 0:
        return None
    elif return_all:
        for player_data in data['hits']:
            player_data = player_data['source']
            player_data['displayName'] = ' '.join(
                [name.strip() for name in player_data.pop('displayName').split(' ') if ' ' not in name and name])
        return [UTRPlayer(player_data['source']) for player_data in data['hits']]
    else:
        if data['total'] == 1:
            return UTRPlayer(data['hits'][0]['source'])
        else:
            names = []
            for player_data in data['hits']:
                player_data = player_data['source']
                player_data['displayName'] = ' '.join(
                    [name.strip() for name in player_data.pop('displayName').split(' ') if ' ' not in name and name])
                names.append(player_data['displayName'])
            name_out = pd.DataFrame(
                [names, [stringdist.rdlevenshtein_norm(player_name.upper(), name.upper()) for name in names]]).transpose().sort_values(
                1).reset_index()[0][0]
            for player_data in data['hits']:
                player_data = player_data['source']
                if player_data['displayName'] == name_out:
                    return UTRPlayer(player_data)

