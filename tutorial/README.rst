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
   downloaded. To download a different version, add e.g. ``--tag v1.2.0`` to
   the above command. To download the tutorials from the development version,
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

#. Build the baseline model (`westeros_baseline.ipynb`_).

#. Add extra detail and constraints to the model

   #. Emissions

      #. Introduce emissions and a bound on the emissions
         (`westeros_emissions_bounds.ipynb`_).
      #. Introduce taxes on emissions (`westeros_emissions_taxes.ipynb`_).

   #. Represent both coal and wind electricity using a “firm capacity”
      formulation (`westeros_firm_capacity.ipynb`_): each generation technology
      can supply some firm capacity, but the variable, renewable technology
      (wind) supplies less than coal.
   #. Represent coal and wind electricity using a different, “flexibility
      requirement” formulation (`westeros_flexible_generation.ipynb`_), wherein
      wind *requires* and coal *supplies* flexibility.
   #. Variablity in energy supply and demand by adding sub-annual time steps,
      e.g. winter and summer (`westeros_seasonality.ipynb`_).

#. After the MESSAGE model has solved, use the :mod:`.message_ix.reporting`
   module to ‘report’ results, e.g. do post-processing, plotting, and other
   calculations (`westeros_report.ipynb`_).

.. _westeros_baseline.ipynb:            https://github.com/iiasa/message_ix/blob/v3.0.0/tutorial/westeros/westeros_baseline.ipynb
.. _westeros_emissions_bounds.ipynb:    https://github.com/iiasa/message_ix/blob/v3.0.0/tutorial/westeros/westeros_emissions_bounds.ipynb
.. _westeros_emissions_taxes.ipynb:     https://github.com/iiasa/message_ix/blob/v3.0.0/tutorial/westeros/westeros_emissions_taxes.ipynb
.. _westeros_firm_capacity.ipynb:       https://github.com/iiasa/message_ix/blob/v3.0.0/tutorial/westeros/westeros_firm_capacity.ipynb
.. _westeros_flexible_generation.ipynb: https://github.com/iiasa/message_ix/blob/v3.0.0/tutorial/westeros/westeros_flexible_generation.ipynb
.. _westeros_seasonality.ipynb:         https://github.com/iiasa/message_ix/blob/v3.0.0/tutorial/westeros/westeros_seasonality.ipynb
.. _westeros_report.ipynb:              https://github.com/iiasa/message_ix/blob/v3.0.0/tutorial/westeros/westeros_report.ipynb


Austrian energy system
----------------------

This tutorial demonstrates a stylized representation of a national electricity
sector model, with several fossil and renewable power plant types.

#. Prepare the base model version, in Python (`austria.ipynb`_) or in R
   (`austria_reticulate.ipynb`_).
#. Plot results, in Python (`austria_load_scenario.ipynb`_) or in R
   (`austria_load_scenario_R.ipynb`_).
#. Run a single policy scenario (`austria_single_policy.ipynb`_).
#. Run multiple policy scenarios. This tutorial has two notebooks: an
   introduction with some exercises (`austria_multiple_policies.ipynb`_) and
   completed code for the exercises
   (`austria_multiple_policies-answers.ipynb`_).

.. _austria.ipynb:                           https://github.com/iiasa/message_ix/blob/v3.0.0/tutorial/Austrian_energy_system/austria.ipynb
.. _austria_reticulate.ipynb:                https://github.com/iiasa/message_ix/blob/v3.0.0/tutorial/Austrian_energy_system/austria_reticulate.ipynb
.. _austria_load_scenario.ipynb:             https://github.com/iiasa/message_ix/blob/v3.0.0/tutorial/Austrian_energy_system/austria_load_scenario.ipynb
.. _austria_load_scenario_R.ipynb:           https://github.com/iiasa/message_ix/blob/v3.0.0/tutorial/Austrian_energy_system/austria_load_scenario_R.ipynb
.. _austria_single_policy.ipynb:             https://github.com/iiasa/message_ix/blob/v3.0.0/tutorial/Austrian_energy_system/austria_single_policy.ipynb
.. _austria_multiple_policies.ipynb:         https://github.com/iiasa/message_ix/blob/v3.0.0/tutorial/Austrian_energy_system/austria_multiple_policies.ipynb
.. _austria_multiple_policies-answers.ipynb: https://github.com/iiasa/message_ix/blob/v3.0.0/tutorial/Austrian_energy_system/austria_multiple_policies-answers.ipynb
