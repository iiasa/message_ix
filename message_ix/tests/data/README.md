# Nightly Tests

Nightly tests are run based on the `scenario.yaml` file, which contains the scenario specifics and expected objective values.

# Generating observed values

If a change has been made either upstream or to related code (e.g., the GAMS formulation), expected objective values
may also change. You can regenerate those values with

```
$ python generate_nightly_test_values.py
```

Running this assumes you are within the IIASA network and able to connect to the `ixmp_dev` database.

It creates a new YAML file called `scenario_obs.yaml` with a value 'obs' containing the observed objective function value for each scenario. If there is an error, the error message is provided instead.