import click
import os
import pandas as pd
import re
import sqlite3
from flask import current_app, g
from flask.cli import with_appcontext


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db(dat=None):
    from app.setting import DATA_MAP

    db = get_db()

    if dat is None:
        dat = {}
        for k, v in DATA_MAP.items():
            dat[k] = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), v))

    for k, v in dat.items():
        v.to_sql(k, con=db, if_exists='replace')


def refresh_data():
    from app.setting import FUNDS

    holding = []
    history = []
    for i, (k, v) in enumerate(FUNDS.items()):
        print('--- fetching {} --- '.format(v))
        url_holding = 'https://www.dataroma.com/m/holdings.php?m={}'.format(k)
        df_f = pd.read_html(url_holding)[0]
        df_f[['Symbol', 'Stock']] = df_f.Stock.str.split(' - ', n=1, expand=True)
        df_f.drop('History', axis=1, inplace=True)
        df_f['Fund'] = k
        df_f['Fund_Name'] = v
        holding.append(df_f)

        for symbol in df_f.Symbol.values:
            url_history = 'https://www.dataroma.com/m/hist/hist.php?f={}&s={}'.format(k, symbol)
            print(url_history)
            df_h = pd.read_html(url_history, keep_default_na=False)[0]
            df_h['Fund'] = k
            df_h['Fund_Name'] = v
            df_h['Symbol'] = symbol
            history.append(df_h)

    dfs = {'holding': pd.concat(holding), 'history': pd.concat(history)}
    dfs['history']['Period'] = dfs['history'].Period.str.replace('&nbsp', '')
    for k, df in dfs.items():
        df.rename(columns={'% of portfolio': 'portfolio pct'}, inplace=True)
        df.columns = df.columns.str.capitalize()
        df.rename(columns=lambda x: re.sub('[^a-zA-Z0-9]', '', x), inplace=True)
        df.to_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)), '13f_{}.csv'.format(k)))

    return dfs


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')


@click.command('init-db-update')
@with_appcontext
def init_db_update_command():
    dat = refresh_data()
    click.echo('Refresh the data.')
    init_db(dat)
    click.echo('Initialized the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(init_db_update_command)
