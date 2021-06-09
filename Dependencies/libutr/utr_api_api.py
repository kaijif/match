import pandas as pd
import requests
import stringdist
import json

def utr_login():
    auth_data = json.loads('{"email":"fsjian@hotmail.com","password":"Netmaker99"}')
    auth_headers = {
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
    auth = requests.post('https://app.universaltennis.com/api/v1/auth/login',json=auth_data,headers=auth_headers)
    cookies = {'jwt':auth.headers['jwt-token']}
    return cookies

def query_utr(player_name, cookies, cookies_number=1):
    cookies2 = None
    data_out = []
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
    if cookies_number == 1:
        utr_request = requests.get('https://app.myutr.com/api/v2/search/players', params=payload, cookies=cookies,
                                   headers=headers)
    else:
        utr_request = requests.get('https://app.myutr.com/api/v2/search/players', params=payload, cookies=cookies_2,
                                   headers=headers)
    utr_response = utr_request.json()
    for player in utr_response['hits']:
        data_out.append(player['source'])
    included_keys = ["displayName", "singlesUtr", "display"]
    clean_data_out = []
    for player in data_out:
        clean_dict = {k: v for k, v in player.items() if k in included_keys}
        clean_dict['name'] = ' '.join(
            [name.strip() for name in clean_dict.pop('displayName').split(' ') if ' ' not in name and name])
        if clean_dict['name'].upper() == player_name.upper():
            clean_data_out.append(clean_dict)
    out = pd.DataFrame(clean_data_out)
    if not out.empty:
        out = out[['name', 'singlesUtr']]
    elif utr_response['total'] != 0:
        names = []
        for player in data_out:
            clean_dict = {k: v for k, v in player.items() if k in included_keys}
            clean_dict['name'] = ' '.join(
                [name.strip() for name in clean_dict.pop('displayName').split(' ') if ' ' not in name and name])
            names.append(clean_dict['name'])
        name_out = pd.DataFrame(
            [names, [stringdist.rdlevenshtein_norm(player_name, name) for name in names]]).transpose().sort_values(
            1).reset_index()[0][0]
        clean_data_out = []
        for player in data_out:
            clean_dict = {k: v for k, v in player.items() if k in included_keys}
            clean_dict['name'] = ' '.join(
                [name.strip() for name in clean_dict.pop('displayName').split(' ') if ' ' not in name and name])
            if clean_dict['name'].upper() == name_out.upper():
                clean_data_out.append(clean_dict)
        out = pd.DataFrame(clean_data_out)
        out = out[['name', 'singlesUtr']]
    else:
        out = pd.DataFrame([player_name, 'NaN']).transpose()
        out.columns = ['name', 'singlesUtr']

    out = out[['name', 'singlesUtr']]
    out = out.sort_values(by='singlesUtr', ascending=False).iloc[0]
    return out


if __name__ == '__main__':
    print(query_utr(input('Player name: ')))
