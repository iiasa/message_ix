import yaml

prefix = """
import ixmp
import message_ix

import numpy as np

from paths import dbpath
"""

template = """
def test_{name}():
    mp = ixmp.Platform(dbpath, dbtype='HSQLDB')
    scen = message_ix.Scenario(mp, '{model}', '{scenario}')
    scen.solve(model='{solve}')
    obs = {obs}
    exp = {exp}
    {test}
"""


def main():
    text = prefix
    with open('scenarios.yaml', 'r') as f:
        for name, data in yaml.load(f).items():
            text += template.format(
                name=name,
                model=data['model'],
                scenario=data['scenario'],
                solve=data['solve'],
                obs=data['obs'],
                exp=data['exp'],
                test=data['test'],
            )
    with open('test_scenarios.py', 'w') as f:
        f.write(text)


if __name__ == '__main__':
    main()
