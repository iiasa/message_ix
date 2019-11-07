Tutorials
=========

To get started with |MESSAGEix|, the following tutorials are provided as
`Jupyter notebooks <https://jupyter.org/>`_, which combine code, sample output,
and explanatory text.

A static, non-interactive version of each notebook can be viewed online using
the links below. In order to execute the tutorial code or make modifications,
read the Preparation_ section, next.

Preparation
-----------

Getting tutorial files
~~~~~~~~~~~~~~~~~~~~~~

If you installed |MESSAGEix| from source, all notebooks are in the ``tutorial``
directory.

If you installed |MESSAGEix| using Anaconda, download the notebooks using the
``message-ix`` command-line program. In a command prompt::

    $ message-ix dl /path/to/tutorials

.. note::

   By default, the tutorials for your installed version of |MESSAGEix| are
   downloaded. To download a different version, add e.g. ``--tag 1.2.0`` to the
   above command. To download the tutorials from the development version,
   add ``--branch master``.

Running tutorials
~~~~~~~~~~~~~~~~~

Using Anaconda
..............

The ``nb_conda`` package is required. It should be installed by default with
Anaconda. If it was not, install it::

    $ conda install nb_conda

1. Open “Jupyter Notebooks” from Anaconda's “Home” tab (or directly if you have
   the option).

2. Choose and open a tutorial notebook.

3. Each notebook requires a *kernel* that executes code interactively. Check
   that the kernel matches your conda environment, and if necessary change
   kernels with the menu, e.g. `Kernel` → `Change Kernel` → `Python
   [conda root]`.

From the command line
.....................

1. Navigate to the tutorial folder. For instance, if ``message-ix dl`` was used
   above::

       $ cd /path/to/tutorials

2. Start the Jupyter notebook::

       $ jupyter notebook

Westeros Electrified
--------------------

This tutorial demonstrates how to model a very simple energy system, and then
uses it to illustrate a range of framework features.

1. `Build the baseline model <https://github.com/iiasa/message_ix/blob/master/tutorial/westeros/westeros_baseline.ipynb>`_.
2. `Introduce emissions <https://github.com/iiasa/message_ix/blob/master/tutorial/westeros/westeros_emissions_bounds.ipynb>`_ and a bound on the emissions.
3. `Limit emissions using a tax <https://github.com/iiasa/message_ix/blob/master/tutorial/westeros/westeros_emissions_taxes.ipynb>`_ instead of a bound.
4. `Represent both coal and wind electricity <https://github.com/iiasa/message_ix/blob/master/tutorial/westeros/westeros_firm_capacity.ipynb>`_, using a “firm capacity” formulation: each generation technology can supply some firm capacity, but the variable, renewable technology (wind) supplies less than coal.
5. Represent coal and wind electricity using a different, `“flexibility requirement” formulation <https://github.com/iiasa/message_ix/blob/master/tutorial/westeros/westeros_flexible_generation.ipynb>`_, wherein wind *requires* and coal *supplies* flexibility.
6. `Variablity in energy supply and demand <https://github.com/iiasa/message_ix/blob/master/tutorial/westeros/westeros_seasonality.ipynb>`_, by adding two sub-annual time steps (winter and summer).
7. `Use ixmp and message_ix reporting features <https://github.com/iiasa/message_ix/blob/master/tutorial/westeros/westeros_report.ipynb>`_ to post-process the raw results from a solved model.

Austrian energy system
----------------------

This tutorial demonstrates a stylized representation of a national electricity
sector model, with several fossil and renewable power plant types.

1. Prepare the base model version, in `Python <https://github.com/iiasa/message_ix/blob/master/tutorial/Austrian_energy_system/austria.ipynb>`__ or in `R <https://github.com/iiasa/message_ix/blob/master/tutorial/Austrian_energy_system/austria_reticulate.ipynb>`__.
2. Plot results, in `Python <https://github.com/iiasa/message_ix/blob/master/tutorial/Austrian_energy_system/austria_load_scenario.ipynb>`__ or in `R <https://github.com/iiasa/message_ix/blob/master/tutorial/Austrian_energy_system/austria_load_scenario_R.ipynb>`__.
3. `Run a single policy scenario <https://github.com/iiasa/message_ix/blob/master/tutorial/Austrian_energy_system/austria_single_policy.ipynb>`_.
4. Run multiple policy scenarios. This tutorial has two notebooks: `an introduction with some exercises <https://github.com/iiasa/message_ix/blob/master/tutorial/Austrian_energy_system/austria_multiple_policies.ipynb>`_ and `completed code for the exercises <https://github.com/iiasa/message_ix/blob/master/tutorial/Austrian_energy_system/austria_multiple_policies-answers.ipynb>`_.
