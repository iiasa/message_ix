import os
import requests
import subprocess

username = os.environ['MESSAGE_IX_CI_USER']
password = os.environ['MESSAGE_IX_CI_PW']

url = 'https://data.ene.iiasa.ac.at/continuous_integration/scenario_db/'
filename = 'gamslice.txt'

print(subprocess.check_output('which gams', shell=True).strip())

localpath = os.path.dirname(subprocess.check_output(['which', 'gams']).strip())
try:
    localpath = localpath.decode()  # py3
except:
    pass  # py2

r = requests.get(url + filename, auth=(username, password))

if r.status_code == 200:
    outpath = os.path.join(localpath, filename)
    print('Downloading {} from {} to {}'.format(filename, url, localpath))
    with open(outpath, 'wb') as out:
        for bits in r.iter_content():
            out.write(bits)
else:
    raise IOError(
        'Failed download with user/pass: {}/{}'.format(username, password))
