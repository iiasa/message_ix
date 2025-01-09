Tutorials
*********

To get started with |MESSAGEix|, the following tutorials are provided as
`Jupyter notebooks <https://jupyter.org/>`_, which combine code, sample output,
and explanatory text.

A static, non-interactive version of each notebook can be viewed online using
the links below. In order to execute the tutorial code or make modifications,
read the Preparation_ section, next.

Preparation
===========

The tutorials refer to terms and concepts from energy systems research (i.e.
how they are measured and modeled mathematically) and to scientific programming
languages and tools (i.e. Python/R language syntax and popular packages in
either language)—however, they **do not** provide a full introduction to these.
Read the :doc:`pre-requisite knowledge <prereqs>` documentation page for an
outline of things you should learn first, in order to fully understand the
tutorials.

Getting tutorial files
----------------------

If you installed |MESSAGEix| from source, all notebooks are in the ``tutorial``
directory.

If you installed |MESSAGEix| using Anaconda or :program:`pip`, download the
notebooks using the ``message-ix`` command-line program. In a command prompt::

    $ message-ix dl /path/to/tutorials

.. note::

   If you installed :mod:`message_ix` into a specific conda environment, that
   environment must be active in order for your system to find the
   ``message-ix`` command-line program, and also to run the Jupyter notebooks.
   Activate the environment `as described`_ in the conda documentation; for
   instance, if you used the name ``message_env``::

     $ conda activate message_env

.. _as described: https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#activating-an-environment

.. note::

   By default, the tutorials matching your installed version of |MESSAGEix| are
   downloaded. To download a different version, add e.g. ``--tag v1.2.0`` to
   the above command. To download the tutorials from the development version,
   add ``--branch main``.

Running tutorials
-----------------

Using Anaconda
~~~~~~~~~~~~~~

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
~~~~~~~~~~~~~~~~~~~~~

1. Navigate to the tutorial folder. For instance, if ``message-ix dl`` was used
   above::

       $ cd /path/to/tutorials

2. Start the Jupyter notebook::

       $ jupyter notebook

.. _tutorial-westeros:

Westeros Electrified
====================

The *Westeros Electrified* tutorial series demonstrates how to:

- create a minimal model that represents a very simple energy system,
- add extra detail / constraints to this representation, and
- post-process (analyze, visualize, or ‘report’) the results.

The following list groups the tutorials by topic.
For new or beginner users, the following sequence of six tutorials (also marked
with ⭐, below) requires the lowest amount of background knowledge and is
sufficient for a basic introduction:

    1 — 2.1 — 2.2 — 3.1 — 3.2.1

The remaining tutorials require deeper energy systems knowledge; greater
scientific programming skills; and/or relate to more advanced uses of the
framework, such as used in global research applications of |MESSAGEix|.

#. ⭐ Build the baseline model (:tut:`westeros/westeros_baseline.ipynb`).

#. Add extra detail and constraints to the model:

   #. ⭐ Emissions:

      #. Introduce emissions and a bound on the emissions
         (:tut:`westeros/westeros_emissions_bounds.ipynb`).
      #. Introduce taxes on emissions
         (:tut:`westeros/westeros_emissions_taxes.ipynb`).

   #. ⭐ Supply of resources:

      Add a fossil-resource supply curve for the coal power plant,
      (:tut:`westeros/westeros_fossil_resource.ipynb`).

   #. Renewables and integration constraints:

      #. Represent both coal and wind electricity using a “firm capacity”
         formulation (:tut:`westeros/westeros_firm_capacity.ipynb`): each
         generation technology can supply some firm capacity, but the variable,
         renewable technology (wind) supplies less than coal.
      #. Represent coal and wind electricity using a different, “flexibility
         requirement” formulation
         (:tut:`westeros/westeros_flexible_generation.ipynb`), wherein wind
         *requires* and coal *supplies* flexibility.
      #. Add a renewable-resource supply curve for the wind power plant,
         (:tut:`westeros/westeros_renewable_resource.ipynb`).

   #. Sub-annual time resolution:

      Represent variability in energy supply and demand by adding sub-annual
      time resolution, e.g. winter and summer
      (:tut:`westeros/westeros_seasonality.ipynb`).

   #. Constraints:

      #. Using share constraints to depict policies, i.e. require renewables to
         supply a certain share of total electricity generation
         (:tut:`westeros/westeros_share_constraint.ipynb`).
      #. Add soft constraints for activity related dynamic constraints
         (:tut:`westeros/westeros_soft_constraints.ipynb`

   #. Add-on technologies:

      Add the possibility of co-generation for the coal power plant, by
      allowing it to produce heat via a passout-turbine
      (:tut:`westeros/westeros_addon_technologies.ipynb`).

   #. Use parameters to represent the historical characteristics of the energy
      system (:tut:`westeros/westeros_historical_new_capacity.ipynb`).

   #. Modeling of a multi-node energy system and representing trade between nodes
      (:tut:`westeros/westeros_multinode_energy_trade.ipynb`).

#. Use other features of :mod:`message_ix` and :mod:`ixmp`:

   #. ⭐ After the MESSAGE model has solved, use the :mod:`.message_ix.report`
      module to ‘report’ results, e.g. do post-processing, plotting, and other
      calculations (:tut:`westeros/westeros_report.ipynb`).

      #. After familiarizing yourself with ‘reporting’, learn how to quickly assess
         variable flows by plotting Sankey diagrams
         (:tut:`westeros/westeros_sankey.ipynb`).

   #. Build the baseline scenario using data stored in Excel files to
      populate sets and parameters:

      #. ⭐ Export data to file and import the data to create a new scenario
         (:tut:`westeros/westeros_baseline_using_xlsx_import_part1.ipynb`).
      #. Import and combine data from multiple files to create a new scenario
         (:tut:`westeros/westeros_baseline_using_xlsx_import_part2.ipynb`).

.. _austria-tutorials:

Austrian energy system
======================

These tutorials demonstrate a stylized representation of a national electricity
sector model, with several fossil and renewable power plant types.

#. Prepare the base model version, in Python
   (:tut:`Austrian_energy_system/austria.ipynb`)
   or in R (:tut:`Austrian_energy_system/R_austria.ipynb`).
#. Plot results, in Python
   (:tut:`Austrian_energy_system/austria_load_scenario.ipynb`)
   or in R (:tut:`Austrian_energy_system/R_austria_load_scenario.ipynb`).
#. Run a single policy scenario
   (:tut:`Austrian_energy_system/austria_single_policy.ipynb`).
#. Run multiple policy scenarios. This tutorial has two notebooks:

  - an introduction with some exercises
    (:tut:`Austrian_energy_system/austria_multiple_policies.ipynb`), and
  - completed code for the exercises
    (:tut:`Austrian_energy_system/austria_multiple_policies-answers.ipynb`).


Code reference
==============

The module :mod:`message_ix.util.tutorial` contains some helper code used to simplify the tutorials; see also :func:`.report.operator.stacked_bar`.

.. currentmodule:: message_ix.util.tutorial

.. automodule:: message_ix.util.tutorial
   :members:
