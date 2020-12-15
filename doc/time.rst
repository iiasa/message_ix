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
The special value ``'year'`` represents the entire year.

Since a ``year`` element refers to the representative, final year within a period, using ``year`` and ``time`` together denotes *a portion of that specific year*.

Example 4
   In a Scenario with ``year`` elements [2000, 2002, 2004] and ``time`` elements [summer, winter]:

   - The ``year`` element ``2002`` refers to the period from 2001-01-01 to 2002-12-31 inclusive, which has a ``duration_period`` of 2 years.
   - The ``time`` element 'summer', **used alone**, refers to a portion of any year.
   - In a |MESSAGEix| parameter indexed by (``year``, ``time``, …), values with the key (``2002``, 'summer', ...) refer to the 'summer' portion of the final year (2002-01-01 to 2002-12-31) within the entire period (2001-01-01 to 2002-12-31) denoted by ``2002``.


Discounting
===========

The ``interest_rate`` in |MESSAGEix| is defined for a period of one year, therefore, for periods of more than a year, the discounting is performed in a cumulative manner. 

Example 5
   Using the same setup as Example 2:
   
   - Discounting for the element ``1010`` involves discounting for years ``1001``, ``1002``, ... , ``1010``.
   - Using the standard PV formula, we have that, for the year ``1001`` the discount factor would be :math:`(1 + interest_rate)^(1000 - 1001)`, for the year  ``1002`` the discount factor would be :math:`(1 + interest_rate)^(1000 - 1002)`, and so on.
   - Therefore, the period discount factor for the element ``1010`` is :math:`df_1010 = (1 + interest_rate)^(1000 - 1001) + (1 + interest_rate)^(1000 - 1002) + ... + (1 + interest_rate)^(1000 - 1010)`
   - Analogously, the period discount factor for the element ``1020`` is :math:`df_1020 = (1 + interest_rate)^(1000 - 1011) + (1 + interest_rate)^(1000 - 1012) + ... + (1 + interest_rate)^(1000 - 1020)`
   - So, if we have a cost of ``K_1010`` for the element ``1010``, its discounted value would be ``df_1010 * K_1010``, which means, all the years in  element ``1010`` have a representative cost of ``K_1010`` that is discounted up to the initial ``year`` of the setup, namely, the year ``1000``.
  
In practice, since the representative year of a period is always its final year, the actual calculation of the period discount factor within the model is performed backwards, i.e., starting from the final year of the period until the initial year. 
