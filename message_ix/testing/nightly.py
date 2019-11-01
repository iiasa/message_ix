import os
import requests
import tarfile

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
    pass


def generate_test_file():
    pass


def fetch_scenarios():
    pass


def make_db():
    pass


def upload_db():
    pass


def upload_license():
    pass
