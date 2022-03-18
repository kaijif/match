import requests
import pandas as pd
import json
import click


def update_ranking_tables():
    token = 'Bearer ' + requests.post('https://www.usta.com/etc/usta/nologinjwt.nljwt.json').json()['access_token']
    headers = {'Authorization': token}
    gens = ['M', 'F']
    dis_gens = {'M': 'Boys\'', 'F': 'Girls\''}
    ages = [12, 14, 16, 18]
    for gen in gens:
        for age in ages:
            outs = []
            keep_going = True
            num = 1
            while keep_going:
                click.secho(f'Updating {dis_gens[gen]} {age} & under Singles, {num}% done.\r', nl=False,fg='white', bg='green')
                json_data = json.loads(
                    '{"pagination":{"pageSize":100,"currentPage":1},"selection":{"catalogId":"JUNIOR_NULL_' + gen + '_STANDING_Y' + str(
                        age) + '_UNDER_NULL_NULL_NULL"}}')
                json_data['pagination']['currentPage'] = num
                r = requests.post('https://services.usta.com/v1/dataexchange/rankings/search/public', json=json_data,
                                  headers=headers)
                if not r.json()['data']:
                    break
                for out in r.json()['data']:
                    cleaned_out = list(out.values())[:7]
                    cleaned_out.append(list(out.values())[7]['name'])
                    outs.append(cleaned_out)
                num += 1
            outs = pd.DataFrame(outs)
            outs.columns = ['Name', 'UAID', 'City', 'State', 'Trend', 'Points', 'ranks','Section']
            outs = outs[['Name', 'City', 'State', 'Points', 'ranks','Section']]
            outs['City, State'] = outs['City'] + ', ' + outs['State']
            outs = outs.drop('City', 1)
            outs = outs.drop('State', 1)
            natl_ranks = []
            for rank in outs["ranks"]:
                natl_ranks.append(rank["national"])
            outs["Rank"] = pd.Series(natl_ranks)
            outs = outs.drop("ranks", 1)
            outs = outs.set_index('Rank')
            outs.to_csv(f'Dependencies/tables/{dis_gens[gen]} {age} & under Singles.csv', encoding='utf-8',errors='replace')



if __name__ == '__main__':
    update_ranking_tables()
