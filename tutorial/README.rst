Tutorials
---------

To get started with a stylized energy system model implemented in |MESSAGEix|,
the following tutorials are provided as `Jupyter <https://jupyter.org/>`_
notebooks. These can be viewed online using the links below.

In order to run the tutorials, `install Jupyter <https://jupyter.org/install>`_.
If you installed the model from source, the notebook files are in the `tutorial` directory.

https://github.com/iiasa/message_ix/blob/master/tutorial/


Westeros Electrified
====================

The Westeros example consists of a suite of tutorials that present the smallest possible energy system to illustrate a range of framework features.

1. `Baseline <https://github.com/iiasa/message_ix/blob/v1.1.0/tutorial/westeros/westeros_baseline.ipynb>`_
2. `Introducing emissions <https://github.com/iiasa/message_ix/blob/v1.1.0/tutorial/westeros/westeros_emissions_bounds.ipynb>`_ and a bound on the emissions.
3. `Taxing emissions <https://github.com/iiasa/message_ix/blob/v1.1.0/tutorial/westeros/westeros_emissions_taxes.ipynb>`_.
4. `Representing both coal and wind electricity using a firm capacity formulation <https://github.com/iiasa/message_ix/blob/v1.1.0/tutorial/westeros/westeros_firm_capacity.ipynb>`_, wherein each generation technology can supply some firm capacity, but the variable, renewable technology (wind) less than coal.
5. Representing coal and wind electricity using a different, `flexibility requirement formulation <https://github.com/iiasa/message_ix/blob/v1.1.0/tutorial/westeros/westeros_flexible_generation.ipynb>`_, wherein wind *requires* and coal *supplies* flexibility.

Austrian energy system
======================

This tutorial generates a stylized representation of a national electricity sector model with several fossil and renewable power plant types.

1. Base model version prepared in `Python <https://github.com/iiasa/message_ix/blob/26cc08f31e2741d2fd60f3493264e654987cc6b1/tutorial/Austrian_energy_system/austria.ipynb>`_ and in `R <https://github.com/iiasa/message_ix/blob/v1.1.0/tutorial/Austrian_energy_system/austria_reticulate.ipynb>`_.
2. `Plot results <https://github.com/iiasa/message_ix/blob/v1.1.0/tutorial/Austrian_energy_system/austria_load_scenario.ipynb>`_ using Python.
3. `Plot results in R <https://github.com/iiasa/message_ix/blob/v1.1.0/tutorial/Austrian_energy_system/austria_load_scenario_R.ipynb>`_.
4. `Running a single policy scenario <https://github.com/iiasa/message_ix/blob/v1.1.0/tutorial/Austrian_energy_system/austria_single_policy.ipynb>`_
5. Running multiple policy scenarios. This tutorial has two notebooks: `an introduction with some exercises <https://github.com/iiasa/message_ix/blob/v1.1.0/tutorial/Austrian_energy_system/austria_multiple_policies.ipynb>`_ and `completed code for the exercises <https://github.com/iiasa/message_ix/blob/v1.1.0/tutorial/Austrian_energy_system/austria_multiple_policies-answers.ipynb>`_
