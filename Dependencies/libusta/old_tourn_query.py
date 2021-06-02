import pandas as pd
from selenium import webdriver
import time


# noinspection PyTypeChecker
def query_tourn(site):
    driver = webdriver.Chrome()
    driver.get(site)
    time.sleep(3)
    tourn_name = driver.find_element_by_xpath('//*[@id="tournaments"]/div/div/div/div[1]/div/div[1]/h1').text
    list_of_tables = pd.DataFrame()
    driver.find_element_by_xpath('//*[@id="cookie-bar"]/p/a[2]').click()
    if 'Acceptance lists' in driver.page_source:
        div = 1
        while div < 20:
            driver.find_element_by_xpath(
                '//*[@id="tournaments"]/div/div/div/div[3]/div/div/div/div/div/div/div').click()
            try:
                driver.find_element_by_xpath(f'//*[@id="menu-"]/div[3]/ul/li[{int(div)}]').click()
            except:
                break
            if 'Main draw' not in driver.page_source:
                div += 1
            else:
                name = driver.find_element_by_xpath(
                    '//*[@id="tournaments"]/div/div/div/div[3]/div/div/div/div/div/div/div').text
                table = pd.read_html(driver.page_source)[2].drop('Position', axis=1)
                table['Events'] = [name for _ in range(len(table.index))] if not name.endswith('Doubles') else ['NaN'
                                                                                                                for _ in
                                                                                                                range(
                                                                                                                    len(table.index))]
                list_of_tables = list_of_tables.append(table)
                div += 1
        driver.close()
        processed = list_of_tables
        processed['Player name'].apply(lambda x: x.upper())
        processed = processed[processed['Events'] != 'NaN']
        processed = processed.set_index(pd.Series([ind for ind in range(1, len(processed.index) + 1)]))
    else:
        list_of_tables = pd.read_html(driver.page_source)[2]
        processed = list_of_tables.drop(['Unnamed: 3', 'Unnamed: 4'], axis=1)
        processed = processed[processed.nunique(1) > 1]
        extras = pd.DataFrame()
        new_li = []
        ind = 0
        for events in processed['Events'].tolist():
            if len(events.split(',')) == 1:
                if events.endswith('Doubles'):
                    new_li.append('NaN')
                    continue
                else:
                    new_li.append(events)
                    continue
            if '/' in events:
                new_li.append('NaN')
                continue

            if len(events.split(',')) > 2:
                cand_events = []
                for event in events.split(','):
                    if event.endswith('Doubles'):
                        pass
                    elif event.endswith('Singles'):
                        cand_events.append(event)
                new_li.append(sorted(cand_events, reverse=True)[0].lstrip())
                for cand_event in cand_events[1:]:
                    extras = extras.append(pd.DataFrame(processed['Player name'][ind], cand_event))
                continue

            if len(events.split(',')) == 2 and events.split(', ')[0].endswith('Singles') and events.split(', ')[
                1].endswith('Singles'):
                new_li.append(sorted(events.split(','))[0].lstrip())
                for cand_event in sorted(events.split(',')):
                    extras = extras.append(pd.DataFrame(processed['Player name'][ind], cand_event.lstrip()))
                continue

            for event in events.split(','):
                if event.endswith('Doubles'):
                    pass
                elif event.endswith('Singles'):
                    new_li.append(event.lstrip())
        processed.append(extras)
        names = []
        for name in processed['Player name']:
            name = name.split(', ')
            name.reverse()
            name = [name_part.lower().capitalize() for name_part in name]
            sep = ' '
            name = sep.join(name)
            names.append(name)
        processed['Player name'] = names
        processed['Events'] = new_li
        processed = processed[processed['Events'] != 'NaN']
        processed = processed.set_index(pd.Series([ind for ind in range(1, len(processed.index) + 1)]))
        driver.close()
    return processed, tourn_name

if __name__ == '__main__':
    print(query_tourn(input('Site: ')))