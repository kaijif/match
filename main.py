import sys, os, smtplib, ssl, click
import pandas as pd
from datetime import timedelta
from datetime import datetime
from openpyxl import load_workbook
from Dependencies.libusta.ranking_ripper import update_ranking_tables
from Dependencies.libutr.utr_api_api import query_utr
from Dependencies.libusta.new_tourn_query import query_tourn
from Dependencies.libusta.query_player_ranking import query_usta_ranking
import yagmail

@click.command()
@click.option('-ut', '--update_tables', is_flag=True, help='Flag to update ranking tables.')
@click.option('-d','--debug', is_flag=True, help='Flag to enable debug logging')
@click.option('-b','--boy',is_flag=True,help='Flag to only pull down Boys')
@click.option('-g','--girl',is_flag=True,help='Flag to only pull down Girls')
@click.argument('target_site',required=True,type=str)
def main(target_site,update_tables,debug,boy,girl):
    with open('Dependencies/LOG.txt', 'w') as file:
        file.write(f'Used @ {datetime.now()}')
    pd.options.mode.chained_assignment = None
    click.secho('Billing...',fg='white', bg='green')
    with open('Dependencies/binary.txt') as file:
        receiver_email = file.read()
    smtp_server = "smtp.gmail.com"
    password = "$World123"
    message = f"""\
        Hi there, valued customer!

        We noticed that you used our program recently, at {datetime.now()}. As you know, our time is extremely valuable, and I spent a lot of it on designing this code. As such, I expect to be compensated for my efforts. Also, that's what it says in LICENSE.

        Please send 1(one) iPhone 12 Pro Max (512 GB of storage and Pacific Blue)(found here:https://www.apple.com/shop/buy-iphone/iphone-12-pro/6.7-inch-display-512gb-pacific-blue-unlocked) to Kaiji Fu before {datetime.now() + timedelta(days=7)}, or prepare to suffer the consequences.

        Cheers,
        Match 2.0 Development Team
    """
    yag = yagmail.SMTP({'matchbilling@gmail.com':'Match2.0 Billing'},'$World123')
    yag.send(to={receiver_email:'Valued Customer'},subject='Match2.0 Bill',contents=message)
    if update_tables:
        update_ranking_tables()

    click.secho(f'Getting tournament information...', fg='white', bg='green')
    tourn, tourn_name = query_tourn(target_site)
    if debug:
        tourn.to_csv(f'Dependencies/debug/tourn_{datetime.now()}.txt')
    ind = 1
    base = pd.DataFrame()
    with open('Dependencies/date_last_updated.txt', 'r') as file:
        date = file.read()
    date = datetime.strptime(date, '%Y-%m-%d')
    if datetime.today() - date > timedelta(7):
        update_ranking_tables()
        with open('Dependencies/date_last_updated.txt', 'w') as file:
            file.write(datetime.today().strftime('%Y-%m-%d'))

    if boy:
        tourn = tourn[tourn['Gender'] == 'M']
        tourn = tourn.set_index(pd.Series(list(range(1, len(tourn.index) + 1))))
    if girl:
        tourn = tourn[tourn['Gender'] == 'F']
        tourn = tourn.set_index(pd.Series(list(range(1, len(tourn.index) + 1))))

    print(tourn)
    for player in tourn['Player name'].tolist():
        click.secho(f'Looking up info for {player}', fg='white', bg='green')
        utr = query_utr(player, 1)
        if debug:
            utr.to_csv(f'Dependencies/debug/utr_{utr[0]}_{datetime.now()}.txt')
        usta = query_usta_ranking(player.upper(), tourn['Events'][ind])
        utr['USTA rank'] = usta[0]
        utr['Player Location'] = usta[1]
        utr['Event'] = tourn['Events'][ind]
        base = base.append(utr)
        ind += 1
    base = base.reset_index(drop=True)
    base = base.drop_duplicates()
    kaiji_summary = pd.DataFrame()
    kairrie_summary = pd.DataFrame()
    current_time = datetime.now().strftime('%m.%d.%Y %H.%M.%S')
    tourn_name = tourn_name[:64]
    out_name = f'{tourn_name}/{tourn_name} Roster {current_time}.xlsx'
    os.makedirs(f'{tourn_name}', exist_ok=True)
    with pd.ExcelWriter(f'Rosters/{out_name}') as writer:
        click.secho('Writing.', nl=False,fg='white', bg='green')
        for div in list(base['Event'].unique()):
            kairrie = query_utr('Kairrie Fu')
            click.secho('.', nl=False,fg='white', bg='green')
            kairrie['USTA rank'] = query_usta_ranking('Kairrie Fu'.upper(), div)[0]
            kairrie['Event'] = div
            kairrie['Player Location'] = 'Greenville, NC'
            click.secho('.', nl=False,fg='white', bg='green')
            per_base = base[base['Event'] == div]
            if kairrie['USTA rank'] != 'NaN':
                per_base = per_base.append(kairrie)
            kaiji = query_utr('Kaiji Fu')
            kaiji['USTA rank'] = query_usta_ranking('Kaiji Fu'.upper(), div)[0]
            kaiji['Event'] = div
            kaiji['Player Location'] = 'Greenville, NC'
            click.secho('.', nl=False,fg='white', bg='green')
            if kaiji['USTA rank'] != 'NaN':
                per_base = per_base.append(kaiji)
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
                kaiji_summary = kaiji_summary.append(per_base[per_base['Name'] == 'Kaiji Fu'])
            if 'Kairrie Fu' in per_base['Name'].values:
                kairrie_summary = kairrie_summary.append(per_base[per_base['Name'] == 'Kairrie Fu'])
            per_base = per_base[['Position', 'Name', 'USTA Rank', 'Singles UTR', 'Player Location']]
            per_base.to_excel(writer, sheet_name=div, index=False)
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
        if 'Summary' not in sheet.title:
            sheet.column_dimensions['B'].width = 30
            sheet.column_dimensions['D'].width = 10
            sheet.column_dimensions['E'].width = 30
        else:
            sheet.column_dimensions['B'].width = 30
            sheet.column_dimensions['C'].width = 30
            sheet.column_dimensions['E'].width = 10
            sheet.column_dimensions['F'].width = 15
    wb.save(out_name)
    print('')
    click.secho('Done!', fg='white', bg='green')


main()
