Years, periods, and time slices
*******************************

This page describes how time-related concepts are represented in the |MESSAGEix| framework and stored in |ixmp|.

Years and periods
=================

The ``year`` set—in a :class:`message_ix.Scenario` and in the |MESSAGEix| model formulation—is used to index parameter dimensions with the names "year", "year_act", "year_vtg", etc.
Elements in this set are **representative years** within a **period** of time.
|MESSAGEix| treats periods as contiguous, but ``year`` elements need not be consecutive.
The representative year is always the *final* year of the corresponding period.

Example 1
   In a Scenario with consecutive ``year`` elements [1984, 1985, 1986, ...], the element ``1985`` refers to the period from 1985-01-01 to 1985-12-31, inclusive.

Example 2
   In a Scenario with non-consecutive ``year`` elements [1000, 1010, 1020, ...]:

   - the element ``1000`` refers to a period that ends 1000-12-31, i.e. at the end of the calendar year 1000.
   - the element ``1010`` refers to a period that ends 1010-12-31, i.e. at the end of the calendar year 1010.
   - the element ``1010`` therefore refers to the period from 1001-01-01 to 1010-12-31, inclusive.

The parameter ``duration_period`` stores the **duration** of each period, measured in years, indexed by elements from the ``year`` set.
|MESSAGEix| only supports ``year`` set elements that can be represented as integers, and therefore periods with durations that are a whole number of years.

Other parameters may be **aligned** to the start or end of periods.

Example 3
   A Scenario has ``year`` elements [1000, 1010, 1020, 1030, ...], and a technology parameterized with ``technical_lifetime`` value of 20 years for the key ``year_vtg=1010``.

   - Capacity associated with this technology is constructed at the *beginning* of the period denoted by ``1010``, i.e. as of 1001-01-01.
   - By the end of this period, 1010-12-31, this technology has operated for 10 years.
   - The next period, labelled ``1020``, ends in 1020-12-31.
     By this date, the technology has operated for 20 years, equal to its technical lifetime.
   - The following period, labelled ``1030``, begins on 1021-01-01.
     The capacity created in ``year_vtg=1010`` is beyond its technical lifetime, and unavailable in this period.

Time slices
===========

The ``time`` set is used to index parameter dimensions with the names "time", "time_origin", "time_dest", etc.
These are variously referred to as “(sub-annual) time slices”, “time steps”, or other names.
Elements in this set are labels for **portions of a single year**.
The special value ``'Year'`` represents the entire year.

Since a ``year`` element refers to the representative, final year within a period, using ``year`` and ``time`` together denotes *a portion of that specific year*.

Example 4
   In a Scenario with ``year`` elements [2000, 2002, 2004] and ``time`` elements [summer, winter]:

   - The ``year`` element ``2002`` refers to the period from 2001-01-01 to 2002-12-31 inclusive, which has a ``duration_period`` of 2 years.
   - The ``time`` element 'summer', **used alone**, refers to a portion of any year.
   - In a |MESSAGEix| parameter indexed by (``year``, ``time``, …), values with the key (``2002``, 'summer', ...) refer to the 'summer' portion of the final year (2002-01-01 to 2002-12-31) within the entire period (2001-01-01 to 2002-12-31) denoted by ``2002``.

Duration of sub-annual time slices
----------------------------------
The duration of each sub-annual time slice should be defined relative to the whole year, with a value between 0 and 1, using the parameter ``duration_time``.
For example, in a model with four seasons with the same length, ``duration_time`` of each season will be 0.25.
Please note that the duration of time slices does not need to be equal to each other.
This information is needed to calculate capacity of a technology that is active in different time slices.
Time slices can be represented at different temporal levels, using the sets ``lvl_temporal`` and ``map_temporal_hierarchy``.
This helps introducing a flexible temporal resolution, e.g., by representing some technologies at finer time resolution while others at ``Year``.
When there are more than one temporal levels, e.g., "year", "season", "month", "day", etc., ``duration_time`` is defined for time slices at each **temporal level** separately.
The sum of ``duration_time`` of time slices at each temporal level must be equal to 1.
For example, in a model with 4 time slices as "season" and 10 time slices as "day" under each "season", ``duration_time`` of each "season" and "day" can be specified as 0.25 and 0.025, respectively.

By default, the unit of ``ACT`` is treated per year in the GAMS formulation for different time slices.
This means values reported in time slice "Year" and "month" both have the same unit (e.g., GWa).
However, the user can report the values across parameters and variables with different units relative to the length of the full year.
For example, the user can report ``ACT`` in units of "GWa" and "GWh" for time slices of "Year" and "hour", respectively, in the same model.
To activate this feature, the parent time slice for which the relative units are desired should be specified by set ``time_relative``.
This will ensure that parameter ``duration_time_rel`` is effective.
Otherwise, this parameter is filled by value of 1, meaning that the units will be treated uniformly across different sub-annual time slices.

Discounting
===========

The ``interest_rate`` in |MESSAGEix| is defined for a period of one year, therefore, for periods of more than a year, the discounting is performed in a cumulative manner.

Example 5
   Using the same setup as Example 2:

   - Discounting for the element ``1010`` involves discounting for years ``1001``, ``1002``, ... , ``1010``.
   - Using the standard PV formula, we have that, for the year ``1001`` the discount factor would be :math:`(1 + \text{interest_rate})^{1000 - 1001}`, for the year  ``1002`` the discount factor would be :math:`(1 + \text{interest_rate})^{1000 - 1002}`, and so on.
   - Therefore, the period discount factor for the element ``1010`` is :math:`\text{df}_{1010} = (1 + \text{interest_rate})^{1000 - 1001} + ... + (1 + \text{interest_rate})^{1000 - 1010}`
   - Analogously, the period discount factor for the element ``1020`` is :math:`\text{df}_{1020} = (1 + \text{interest_rate})^{1000 - 1011} + ... + (1 + \text{interest_rate})^{1000 - 1020}`
   - So, if we have a cost of ``K_1010`` for the element ``1010``, its discounted value would be ``df_1010 * K_1010``, which means, all the years in  element ``1010`` have a representative cost of ``K_1010`` that is discounted up to the initial ``year`` of the setup, namely, the year ``1000``.

In practice, since the representative year of a period is always its final year, the actual calculation of the period discount factor within the model is performed backwards, i.e., starting from the final year of the period until the initial year.
