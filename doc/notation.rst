Notation
********

This page explains the notation used in this mathematical formulation section of the documentation, using the following example:

.. math::

   & \forall \, c, h, \ l \notin L^{\text{RES}} \cup L^{\text{REN}} \cup L^{\text{STOR}}, n = n^D = n^O, y = y^A: \\&
   \sum_{h m n^L t ; y^V \leq y}{\left(
     \output
     \cdot \text{duration_time_rel}_{h^1=h^D;h^2=h}
     \cdot \text{ACT}_{h m n^L t y^A y^V}
   \right)} \\&
   - \sum_{h m n^L t; y^V \leq y}{\left(
     \text{input}_{c h h^O l m n^L n^O t y^A y^V}
     \cdot \text{duration_time_rel}_{h^1=h^O;h^2=h}
     \cdot \text{ACT}_{h m n^L t y^A y^V}
   \right)} \\&
   + \text{STOCK_CHG}_{c h l n y} \\&
   + \sum_{s}{\left(
      \left( \text{land_output}_{c h l n s y} - \text{land_input}_{c h l n s y} \right)
     \cdot \text{LAND}_{n s y}
   \right)} \\&
   - \text{demand_fixed}_{c h l n y} \\&
   = \\&
   \text{COMMODITY_BALANCE}_{c h l n y}

- The equality (=) or inequality (< or >) relation is on a line by itself.
  This allows to distinguish the **left- and right-hand sides** of the expression.
- The first line begins with the "for all …" symbol (:math:`\forall`) and gives:

  - The **dimensionality** of the equation or inequality, via a list of **indices** (in alphabetical order).
    In some cases, this is equivalent to the dimensionality of a single term on either side.
    In the example above, this is COMMODITY_BALANCE.
    Where both sides are more complicated, the first line informs about the dimensionality.
  - Any **conditions or restrictions** on the set members to which the indices apply.
    Implicitly, indices without condition may take any value from their corresponding set.
    In the example above:

    - Index :math:`l` must be in the union of certain other sets.
    - The indices :math:`y` (for parameters/variables with a dimension named "year") must always align with indices :math:`y^A` (for parameters/variables with a dimension named "year_active").
    - Likewise, :math:`n`, :math:`n^D` (node_dest), and :math:`n^O` (node_origin) must all be aligned
    - The other indices are unconstrained, so implicitly :math:`c \in C` and :math:`h \in H`.

- References to items (exogenous **parameters** or endogenous **variables**) include:

  - The **name** in roman (upright) text.
    Parameter names are always lower case, for instance 'output'.
    Variables names are always upper case, for instance 'ACT'.

  - Its **dimensionality** as a right subscript with an alphabetical list of indices.
    These:

    - Always exactly restate the dimensionality of the item given elsewhere in this documentation.
      That is, the indices do indicate aggregation or other operations.
    - *May* express an alignment or restriction of indices, *if and only if* this is particular to one reference of the parameter/variable.
      Otherwise, these are expressed in the first line, as described above.
      In the above example, 'duration_time_rel' has indices :math:`h^1, h^2`, but these are aligned differently in the two places it is used in the equation.
    - Facilitate understanding of alignment and broadcasting between elements of parameters/variables with different dimensionality.

- Indices are always exactly one character, for instance 'y'.
  If a parameter or variable is indexed more than once by the same set, all but 0 or 1 occurrence of the same base has a right superscript, for instance :math:`y^A` and :math:`y^V`.
  These correspond to different **dimension- or index names** given in the "sets and parameters" page of the documentation; for instance :math:`y^A` is always the dimension/index name "year_active", referring to a member of :math:`Y^A \subseteq Y`.
- In both the left- and right-hand sides:

  - Individual additive terms are shown on separate lines.
  - Operands for operations like summation, if including multiple terms, are enclosed in parentheses.

LateX source
============

The following describes the usage of LaTeX markup to **write** equations.
Users who are only *reading* the documentation to aid usage of :mod:`message_ix` do not need to read these instructions.

…
