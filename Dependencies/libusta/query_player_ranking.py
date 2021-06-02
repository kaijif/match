import pandas as pd


def query_usta_ranking(name, div):
    df = pd.read_csv(f'Dependencies/tables/{div}.csv', index_col='Rank')
    df['Name'] = df['Name'].str.upper()
    out = [df[df['Name'] == name].index.tolist()[0]] if len(df[df['Name'] == name].index.tolist()) >= 2 else df[
        df['Name'] == name].index.tolist() if df[df['Name'] == name].index.tolist() else ['NaN']
    out.append(df[df['Name'] == name]['City, State'].tolist()[0]) if df[df['Name'] == name][
        'City, State'].tolist() else out.append('NaN')
    return out


if __name__ == '__main__':
    print(query_usta_ranking(input('Name: '), input('Div: ')))