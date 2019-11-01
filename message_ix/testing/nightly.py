import os
from pathlib import Path
import shutil
import subprocess
import tarfile

import ixmp
import message_ix
import requests
import yaml


HERE = Path(__file__).resolve()
DBFOLDER = os.path.join(HERE, 'db')
DBPATH = os.path.join(DBFOLDER, 'scenarios')

PASSWORD = os.environ['MESSAGE_IX_CI_PW']
URL = 'https://data.ene.iiasa.ac.at/continuous_integration/scenario_db/'
USERNAME = os.environ['MESSAGE_IX_CI_USER']
FILENAME = 'db.tar.gz'


def download_db():
    r = requests.get(URL + FILENAME, auth=(USERNAME, PASSWORD))

    if r.status_code == 200:
        print('Downloading {} from {}'.format(FILENAME, URL))
        with open(FILENAME, 'wb') as out:
            for bits in r.iter_content():
                out.write(bits)
        print('Untarring {}'.format(FILENAME))
        tar = tarfile.open(FILENAME, "r:gz")
        tar.extractall()
        tar.close()
        os.remove(FILENAME)
    else:
        raise IOError(
            'Failed download with user/pass: {}/{}'.format(USERNAME, PASSWORD))


def download_license():
    filename = 'gamslice.txt'

    print(subprocess.check_output('which gams', shell=True).strip())

    localpath = os.path.dirname(
        subprocess.check_output(['which', 'gams']).strip())
    localpath = localpath.decode()  # py3

    r = requests.get(URL + filename, auth=(USERNAME, PASSWORD))

    if r.status_code == 200:
        outpath = os.path.join(localpath, filename)
        print('Downloading {} from {} to {}'.format(filename, URL, localpath))
        with open(outpath, 'wb') as out:
            for bits in r.iter_content():
                out.write(bits)
    else:
        raise IOError(
            'Failed download with user/pass: {}/{}'.format(USERNAME, PASSWORD))


def fetch_scenarios():
    mp = ixmp.Platform()
    with open('scenarios.yaml', 'r') as f:
        for name, data in yaml.load(f).items():
            scen = message_ix.Scenario(mp, data['model'], data['scenario'])
            scen.to_excel(name + '.xlsx')


def make_db():
    if os.path.exists(DBFOLDER):
        shutil.rmtree(DBFOLDER)

    mp = ixmp.Platform(DBPATH, dbtype='HSQLDB')
    with open('scenarios.yaml', 'r') as f:
        for name, data in yaml.load(f).items():
            scen = message_ix.Scenario(
                mp, data['model'], data['scenario'], version='new')
            message_ix.macro.init(scen)
            scen.read_excel(name + '.xlsx', add_units=True)
            scen.commit('saving')
    mp.close_db()


def upload_db():
    # TODO implement the following in Python
    # tar cvzf db.tar.gz db
    # scp db.tar.gz $1:/opt/data.ene.iiasa.ac.at/docs/continuous_integration/
    #   scenario_db/
    # rm db.tar.gz
    pass


def upload_license():
    # TODO implement the following in Python
    # scp $2 $1:/opt/data.ene.iiasa.ac.at/docs/continuous_integration/
    #   scenario_db/$(basename $2)
    pass
