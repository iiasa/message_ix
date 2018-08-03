
# Next Release

- [#84](https://github.com/iiasa/message_ix/pull/84): `message_ix.Scenariovintage_active_years()` now limits active years to those after the first model year
- [#78](https://github.com/iiasa/message_ix/pull/78): Bugfix: `message_ix.Scenario.solve()` uses 'MESSAGE' by default, but can be provided other model names
- [#77](https://github.com/iiasa/message_ix/pull/77): `rename()` function can optionally keep old values in the model (i.e., copy vs. copy-with-replace)
- [$67](https://github.com/iiasa/message_ix/pull/67): Use of advanced basis in cplex.opt turned off by default to avoid conflicts with barrier method.
- [#65](https://github.com/iiasa/message_ix/pull/65): Bugfix for downloading tutorials. Now downloads current installed version by default.
- [$60](https://github.com/iiasa/message_ix/pull/60): Add basic ability to write and read model input to/from Excel
- [$59](https://github.com/iiasa/message_ix/pull/59): Added MacOSX CI support
