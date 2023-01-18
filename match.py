import sys, os, click
import pandas as pd
from datetime import timedelta
from datetime import datetime
from openpyxl import load_workbook
from Dependencies.libusta.ranking_ripper import update_ranking_tables
from Dependencies.libutr.utr_api_api import query_utr,utr_login
from Dependencies.libusta.new_tourn_query import query_tourn
from Dependencies.libusta.query_player_ranking import query_usta_ranking

@click.command()
@click.option('-u', '--update_tables', is_flag=True, help='Flag to update ranking tables.')
@click.option('-d','--debug', is_flag=True, help='Flag to enable debug logging')
@click.option('-b','--boy',is_flag=True,help='Flag to only pull down Boys')
@click.option('-g','--girl',is_flag=True,help='Flag to only pull down Girls')
@click.option('-s', '--sections', multiple=True ,help='Sections to rank, if any')
@click.argument('target_site',required=True,type=str)
def main(target_site,update_tables,debug,boy,girl,sections):
    with open('Dependencies/LOG.txt', 'w') as file:
        file.write(f'Used @ {datetime.now()}')
    pd.options.mode.chained_assignment = None
    with open('Dependencies/date_last_updated.txt', 'r') as file:
        date = file.read()
    date = datetime.strptime(date, '%Y-%m-%d')
    if update_tables or datetime.today() - date > timedelta(7):
        update_ranking_tables()
        with open('Dependencies/date_last_updated.txt', 'w') as file:
            file.write(datetime.today().strftime('%Y-%m-%d'))

    click.secho(f'Getting tournament information...', fg='white', bg='green')
    tourn, tourn_name = query_tourn(target_site)
    if debug:
        tourn.to_csv(f'Dependencies/debug/tourn_{datetime.now()}.txt')
    ind = 1
    cookie = utr_login()
    if cookie == 'No login':
        return
    base = pd.DataFrame()
    if boy:
        tourn = tourn[tourn['Gender'] == 'M']
        tourn = tourn.set_index(pd.Series(list(range(1, len(tourn.index) + 1))))
    if girl:
        tourn = tourn[tourn['Gender'] == 'F']
        tourn = tourn.set_index(pd.Series(list(range(1, len(tourn.index) + 1))))

    print(tourn)

    for player in tourn['Player name'].tolist():
        click.secho(f'Looking up info for {player}', fg='white', bg='green')
        utr = query_utr(player, cookies=cookie)
        if debug:
            utr.to_csv(f'Dependencies/debug/utr_{utr[0]}_{datetime.now()}.txt')
        usta = query_usta_ranking(player.upper(), tourn['Events'][ind])
        utr['USTA rank'] = usta[0]
        utr['Player Location'] = usta[1]
        utr['Event'] = tourn['Events'][ind]
        utr['Section'] = usta[2]
        base = pd.concat([base, utr])
        ind += 1
    base = base.reset_index(drop=True)
    base = base.drop_duplicates()
    kaiji_summary = pd.DataFrame()
    kairrie_summary = pd.DataFrame()
    current_time = datetime.now().strftime('%m.%d.%Y %H.%M.%S')
    tourn_name = tourn_name[:64]
    out_name = f'Rosters/{tourn_name}/{tourn_name} Roster {current_time}.xlsx'
    os.makedirs(f'Rosters/{tourn_name}', exist_ok=True)
    with pd.ExcelWriter(out_name) as writer:
        click.secho('Writing.', nl=False,fg='white', bg='green')
        for div in list(base['Event'].unique()):
            kairrie = query_utr('Kairrie Fu',cookies=cookie)
            click.secho('.', nl=False,fg='white', bg='green')
            kairrie['USTA rank'] = query_usta_ranking('Kairrie Fu'.upper(), div)[0]
            kairrie['Event'] = div
            kairrie['Player Location'] = 'Greenville, NC'
            kairrie['Section'] = 'Southern'
            click.secho('.', nl=False,fg='white', bg='green')
            per_base = base[base['Event'] == div]
            if kairrie['USTA rank'] != 'NaN':
                per_base = pd.concat([per_base, kairrie])
            kaiji = query_utr('Kaiji Fu',cookies=cookie)
            kaiji['USTA rank'] = query_usta_ranking('Kaiji Fu'.upper(), div)[0]
            kaiji['Event'] = div
            kaiji['Player Location'] = 'Greenville, NC'
            kaiji['Section'] = 'Southern'
            click.secho('.', nl=False,fg='white', bg='green')
            if kaiji['USTA rank'] != 'NaN':
                per_base = pd.concat([per_base, kaiji])
            per_base.rename(
                {
                    'singlesUtr': 'Singles UTR',
                    'name': 'Name',
                    'USTA rank': 'USTA Rank'
                }, axis=1, inplace=True
            )
            numeric = pd.to_numeric(per_base['USTA Rank'].replace('NaN', 99999))
            per_base['USTA Rank'] = numeric
            per_base = per_base.sort_values(by='USTA Rank')
            per_base['USTA Rank'] = per_base['USTA Rank'].replace(99999, 'Not Found')
            per_base = per_base.replace('NaN', 'Not Found')
            per_base = per_base.drop_duplicates()
            per_base['Position'] = [num + 1 for num in range(len(per_base.index))]
            if 'Kaiji Fu' in per_base['Name'].values:
                kaiji_summary = pd.concat([kaiji_summary, per_base[per_base['Name'] == 'Kaiji Fu']])
            if 'Kairrie Fu' in per_base['Name'].values:
                kairrie_summary = pd.concat([kaiji_summary, per_base[per_base['Name'] == 'Kairrie Fu']])
            per_base = per_base.reset_index()
            utr_per_base = per_base.copy()
            utr_per_base['Singles UTR'] = utr_per_base['Singles UTR'].replace('Not Found', -1)
            utr_per_base = utr_per_base.sort_values('Singles UTR',ascending=False,ignore_index=True)
            utr_per_base['Singles UTR'] = utr_per_base['Singles UTR'].replace(-1, 'Not Found')
            utr_per_base['Position'] = pd.Series(list(range(1,len(utr_per_base.index.tolist())+1)))
            utr_per_base_to_write = utr_per_base.copy()
            utr_numeric = pd.to_numeric(utr_per_base['USTA Rank'].replace('Not Found', 99999))
            utr_per_base['USTA Rank'] = utr_numeric
            utr_per_base = utr_per_base.sort_values(by='USTA Rank')
            utr_per_base['USTA Rank'] = utr_per_base['USTA Rank'].replace(99999, 'Not Found')
            utr_per_base = utr_per_base.replace('NaN', 'Not Found')
            utr_per_base = utr_per_base.drop_duplicates()
            utr_per_base = utr_per_base.reset_index()
            per_base = per_base.reset_index()
            per_base['UTR Position'] = utr_per_base['Position']
            per_base = per_base[['Position','UTR Position', 'Name', 'USTA Rank', 'Singles UTR', 'Player Location','Section']]
            per_base.to_excel(writer, sheet_name=div, index=False)
            utr_per_base_to_write = utr_per_base_to_write[['Position', 'Name', 'Event', 'USTA Rank', 'Singles UTR', 'Player Location', 'Section']]
            utr_per_base_to_write.to_excel(writer, sheet_name=div + '(UTR)', index=False)
            if sections:
                sections = list(sections)
                for section in sections:
                    if section in per_base['Section'].values:
                        section_roster = per_base[per_base['Section'] == section]
                        section_roster = section_roster.sort_values(by='USTA Rank')
                        if div.startswith('Boy'):
                            sheet_name = div[:9] + f'({section})'
                        else:
                            sheet_name = div[:10] + f'({section})'
                        section_roster = section_roster.rename(columns={'Position':'Overall Ranking'})
                        section_rankings = []
                        for num in range(1, len(section_roster.index) + 1):
                            section_rankings.append(num)
                        section_roster = section_roster.reset_index()
                        section_roster['Section Ranking'] = pd.Series(section_rankings)
                        section_roster = section_roster.set_index('Section Ranking')
                        section_roster = section_roster[['Overall Ranking','Name','USTA Rank','Singles UTR', 'Player Location']]
                        section_roster.to_excel(writer,sheet_name=sheet_name)
                    else:
                        pass
        if not kaiji_summary.empty:
            kaiji_summary = kaiji_summary.sort_values('Event')
            kaiji_summary['Recommended'] = kaiji_summary['Event'] == 'Boys\' 14 & Under Singles'
            kaiji_summary = kaiji_summary[['Position', 'Name', 'Event', 'USTA Rank', 'Singles UTR', 'Recommended']]
            kaiji_summary.to_excel(writer, sheet_name='Kaiji\'s Summary', index=False)
        if not kairrie_summary.empty:
            kairrie_summary = kairrie_summary.sort_values('Event')
            kairrie_summary['Recommended'] = kairrie_summary['Event'] == 'Girls\' 18 & Under Singles'
            kairrie_summary = kairrie_summary[['Position', 'Name', 'Event', 'USTA Rank', 'Singles UTR', 'Recommended']]
            kairrie_summary.to_excel(writer, sheet_name='Kairrie\'s Summary', index=False)
    wb = load_workbook(out_name)
    for sheet in wb.worksheets:
        if '(' in sheet.title and 'UTR' not in sheet.title:
            sheet.column_dimensions['A'].width = 20
            sheet.column_dimensions['B'].width = 20
            sheet.column_dimensions['C'].width = 40
            sheet.column_dimensions['E'].width = 10
            sheet.column_dimensions['F'].width = 30
        elif 'Summary' not in sheet.title and '(UTR)' not in sheet.title:
            sheet.column_dimensions['B'].width = 20
            sheet.column_dimensions['C'].width = 30
            sheet.column_dimensions['E'].width = 10
            sheet.column_dimensions['F'].width = 30
            sheet.column_dimensions['G'].width = 30
        elif 'Summary' not in sheet.title and '(UTR)' in sheet.title:
            sheet.column_dimensions['B'].width = 30
            sheet.column_dimensions['D'].width = 10
            sheet.column_dimensions['E'].width = 30
            sheet.column_dimensions['F'].width = 30
            sheet.column_dimensions['G'].width = 30
        elif 'Summary' in sheet.title:
            sheet.column_dimensions['B'].width = 30
            sheet.column_dimensions['C'].width = 30
            sheet.column_dimensions['E'].width = 10
            sheet.column_dimensions['F'].width = 15
        else:
            print('One of the sheets had an invalid name')

    wb.save(out_name)
    print('')
    click.secho('Done!', fg='white', bg='green')


main()
