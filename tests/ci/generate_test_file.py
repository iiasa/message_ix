import yaml

prefix = """
import ixmp
import message_ix

import numpy as np

from paths import dbpath
"""

setup_template = """
def test_{name}():
    mp = ixmp.Platform(dbpath, dbtype='HSQLDB')
    scen = message_ix.Scenario(mp, '{model}', '{scenario}')
    scen.solve(model='{solve}', solve_options={solve_options})
"""

test_template = """
    obs = {obs}
    exp = {exp}
    {test}
"""


def query(d, key, default):
    return d[key] if key in d else default


def main():
    text = prefix
    with open('scenarios.yaml', 'r') as f:
        for name, data in yaml.load(f).items():
            solve_options = query(data, 'solve_options', {})
            text += setup_template.format(
                name=name,
                model=data['model'],
                scenario=data['scenario'],
                solve=data['solve'],
                solve_options=solve_options,
            )
            for case in data['cases']:
                text += test_template.format(
                    obs=case['obs'],
                    exp=case['exp'],
                    test=case['test'],
                )
    with open('test_scenarios.py', 'w') as f:
        f.write(text)


if __name__ == '__main__':
    main()
