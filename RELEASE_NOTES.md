
# Next Release

- [#99](https://github.com/iiasa/message_ix/pull/99): Fixing an error in the compuation of the auxiliary GAMS reporting variable `PRICE_EMISSION`
- [#89](https://github.com/iiasa/message_ix/pull/89): Fully implementing system reliability and flexibity considerations (cf. Sullivan)
- [#88](https://github.com/iiasa/message_ix/pull/88): Reformulated capacity maintainance constraint to ensure that newly installed capacity cannot be decommissioned within the same model period as it is built in
- [#84](https://github.com/iiasa/message_ix/pull/84): `message_ix.Scenariovintage_active_years()` now limits active years to those after the first model year or the years of a certain technology vintage
- [#82](https://github.com/iiasa/message_ix/pull/82): Introducing "add-on technologies" for mitigation options, etc.
- [#81](https://github.com/iiasa/message_ix/pull/81): Share constraints by mode added.
- [#80](https://github.com/iiasa/message_ix/pull/80): Share constraints by commodity/level added.
- [#78](https://github.com/iiasa/message_ix/pull/78): Bugfix: `message_ix.Scenario.solve()` uses 'MESSAGE' by default, but can be provided other model names
- [#77](https://github.com/iiasa/message_ix/pull/77): `rename()` function can optionally keep old values in the model (i.e., copy vs. copy-with-replace)
- [#74](https://github.com/iiasa/message_ix/pull/74): Activity upper and lower bounds can now be applied to all modes of a technology
- [#67](https://github.com/iiasa/message_ix/pull/67): Use of advanced basis in cplex.opt turned off by default to avoid conflicts with barrier method.
- [#65](https://github.com/iiasa/message_ix/pull/65): Bugfix for downloading tutorials. Now downloads current installed version by default.
- [#60](https://github.com/iiasa/message_ix/pull/60): Add basic ability to write and read model input to/from Excel
- [#59](https://github.com/iiasa/message_ix/pull/59): Added MacOSX CI support
