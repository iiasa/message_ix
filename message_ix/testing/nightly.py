from asyncio import get_event_loop
import logging
import os
from pathlib import Path
import subprocess
from tarfile import TarFile

from asyncssh import connect, scp
import click
import ixmp
import message_ix
import requests
import yaml


log = logging.getLogger(__name__)

HERE = Path(__file__).resolve()
DBFOLDER = os.path.join(HERE, 'db')
DBPATH = os.path.join(DBFOLDER, 'scenarios')


def _config():
    with open(HERE.parents[2] / 'ci' / 'nightly.yaml') as f:
        return yaml.load(f)


def download(path):
    auth = (os.environ['MESSAGE_IX_CI_USER'], os.environ['MESSAGE_IX_CI_PW'])

    cfg = _config()

    # Download database
    fn = cfg['filename']['data']
    url = cfg['http base'] + cfg['path'] + fn
    log.info('Downloading from {}'.format(url))

    r = requests.get(url, auth=auth)
    r.raise_for_status()

    data_path = path / fn
    with open(data_path, 'wb') as out:
        for bits in r.iter_content():
            out.write(bits)

    log.info('Untarring {}'.format(fn))
    with TarFile(data_path, 'r:gz') as tf:
        tf.extractall(path)

    data_path.unlink()

    # Download license
    gams_dir = Path(subprocess.check_output(['which', 'gams']).strip()).parent
    log.info('Located GAMS executable at {}'.format(gams_dir))

    fn = cfg['filename']['license']
    url = cfg['http base'] + cfg['path'] + fn
    log.info('Downloading from {}'.format(url))

    r = requests.get(url, auth=auth)
    r.raise_for_status()
    (gams_dir / fn).write_text(r.text)


def fetch_scenarios():
    mp = ixmp.Platform()
    with open('scenarios.yaml', 'r') as f:
        for name, data in yaml.load(f).items():
            scen = message_ix.Scenario(mp, data['model'], data['scenario'])
            scen.to_excel(name + '.xlsx')


def iter_scenarios():
    with open(HERE.parents[2] / 'tests' / 'data' / 'scenarios.yaml', 'r') as f:
        scenarios = yaml.load(f)

    for id, data in scenarios.items():
        yield id, (
            data['model'],
            data['scenario'],
            data['solve'],
            data.get('solve_options', {}),
            data['cases']
        )


def make_db(path):
    mp = ixmp.Platform(dbprops=path / 'scenarios', dbtype='HSQLDB')
    for id, data in iter_scenarios():
        scen = message_ix.Scenario(mp, data['model'], data['scenario'],
                                   version='new')
        message_ix.macro.init(scen)
        scen.read_excel(id + '.xlsx', add_units=True)
        scen.commit('saving')
    mp.close_db()

    # Pack the HSQLDB files into an archive
    cfg = _config()
    with TarFile(path / cfg['filename']['data'], 'w:gz') as tf:
        for fn in path.glob('scenarios*'):
            tf.add(fn)


def upload(path, username, password):
    get_event_loop().run_until_complete(_upload(path, username, password))


async def _upload(path, username, password):
    cfg = _config()
    async with connect(cfg['ssh']['host'], username=username,
                       password=password) as conn:
        target = (conn, cfg['ssh']['base'] + cfg['path'])
        await scp(path / cfg['filename']['data'], target)
        await scp(path / cfg['filename']['license'], target)
