import yaml

import ixmp
import message_ix


def main():
    mp = ixmp.Platform()
    with open('scenarios.yaml', 'r') as f:
        for name, data in yaml.load(f).items():
            scen = message_ix.Scenario(mp, data['model'], data['scenario'])
            scen.to_excel(name + '.xlsx')


if __name__ == '__main__':
    main()
