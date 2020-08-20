Add model years to an existing Scenario
=======================================

Description
-----------

This tool adds new modeling years to an existing :class:`message_ix.Scenario` (hereafter "reference scenario"). For instance, in a scenario define with::

    history = [690]
    model_horizon = [700, 710, 720]
    sc_ref.add_horizon(
        year=history + model_horizon,
        firstmodelyear=model_horizon[0]
    )

…additional years can be added after importing the add_year function::

    from message_ix.tools.add_year import add_year
    sc_new = message_ix.Scenario(mp, sc_ref.model, sc_ref.scenario,
                                 version='new')
    add_year(sc_ref, sc_new, [705, 712, 718, 725])

At this point, ``sc_new`` will have the years [700, 705, 710, 712, 718, 720, 725], and original or interpolated data for all these years in all parameters.


The tool operates by creating a new empty Scenario (hereafter "new scenario") and:

- Copying all **sets** from the reference scenario, adding new time steps to relevant sets (e.g., adding 2025 between 2020 and 2030 in the set ``year``)
- Copying all **parameters** from the reference scenario, adding new years to relevant parameters, and calculating missing values for the added years.

Features
~~~~~~~~

- It can be used for any MESSAGE scenario, from tutorials, country-level, and global models.
- The new years can be consecutive, between existing years, and/or after the model horizon.
- The user can define for what regions and parameters the new years should be added. This saves time when adding the new years to only one parameter of the reference scenario, when other parameters have previously been successfully added to the new scenario.

Usage
-----

The tool can be used either:

1. Directly from the command line::

    $ message-ix \
        --platform default
        --model MESSAGE_Model \
        --scenario baseline \
        add-years
        --years_new 2015,2025,2035,2045

   For the full list of input arguments, run::

    $ message-ix add-years --help

2. By calling the function :meth:`~message_ix.tools.add_year.add_year` from a Python script.


Technical details
-----------------

1. An existing scenario is loaded and the desired new years are specified.
2. A new (empty) scenario is created for adding the new years.
3. The new years are added to the relevant sets, ``year`` and ``type_year``.

   - The sets ``firstmodelyear``, ``lastmodelyear``, ``baseyear_macro``, and ``initializeyear_macro`` are modified, if needed.
   - The set ``cat_year`` is modified for the new years.

4. The new years are added to the index sets of relevant parameters, and the missing data for the new years are calculated based on interpolation of adjacent data points. The following steps are applied:

   a. Each non-empty parameter is loaded from the reference scenario.
   b. The year-related indexes (0, 1, or 2) of the parameter are identified.
   c. The new years are added to the parameter, and the missing data is calculated based on the number of year-related indexes. For example:

      - The parameter ``inv_cost`` has index ``year_vtg``, to which the new years are added.
      - The parameter ``output`` has indices ``year_act`` and ``year_vtg``. The new years are added to *both* of these dimensions.
   d. Missing data is calculated by interpolation.
   e. For parameters with 2 year-related indices (e.g. ``output``), a final check is applied so ensure that the vintaging is correct. This step is done based on the lifetime of each technology.

5. The changes are committed and saved to the new scenario.

.. warning::
   The tool does not ensure that the new scenario will solve after adding the
   new years. The user needs to load the new scenario, check some key
   parameters (like bounds) and solve the new scenario.

API reference
-------------

.. automodule:: message_ix.tools.add_year
   :members:
