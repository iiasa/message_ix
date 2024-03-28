Developing tutorials
********************

Developers *and users* of the |MESSAGEix| framework are welcome to contribute **tutorials**, according to the following guidelines.
Per the license and CLA, tutorials will become part of the message_ix test suite and will be publicly available.

Developers **must** ensure new features (including :py:`message_ix.tools` submodules) are fully documented.
This can be done via the API documentation (this site) and, optionally, a tutorial.
These have complementary purposes:

- The API documentation (built using Sphinx and ReadTheDocs) must completely, but succinctly, *describe the arguments and behaviour* of every class and method in the code.
- Tutorials serve as *structured learning exercises* for the classroom or self-study.
  The intended learning outcome for each tutorial is that students understand how the model framework API may be used for scientific research, and can begin to implement their own models or model changes.


Code and writing style
======================

- Python and R code in notebooks: follow all points of the :ref:`code-style` for message_ix.
- Only commit 'bare' Jupyter notebooks: clear all cell output before committing.
  Notebooks will be run and rendered when the documentation is generated.
- Add a line to :file:`message_ix/tests/test_tutorials.py`, so that the parametrized test function runs the tutorial (as noted at :pull:`196`).
- Optionally, use Jupyter notebook slide-show features so that the tutorial can be viewed as a presentation.
- When relevant, provide links to publications or sources that provide greater detail for the methodology, data, or other packages used.
- Providing the mathematical formulation in the tutorial itself is optional.
- Framework specific variables and parameters or functions must be in italic.
- Relevant figures, tables, or diagrams should be added to the tutorial if these can help users to understand concepts.

  - Place rendered versions of graphics in a directory with the tutorial (see `Location`_ below).
    Use SVG, PNG, JPG, or other web-ready formats.


Structure
=========

Generally, a tutorial should have the following elements or sections.

- Tutorial introduction:

  - The general overview of tutorial.
  - The intended learning outcome.
  - An explanation of which features are covered.
  - Reference and provide links to any tutorials that are interlinked or part of a series.

- Description of individual steps:

  - A brief explanation of the step.
  - A link to any relevant mathematical documentation.

- Modeling results and visualizations:

  - Model outputs and post-processing calculations in tutorials should demonstrate usage of the :doc:`message_ix.report module </reporting>`.
  - Plots to depict results should use `pyam <https://github.com/IAMconsortium/pyam/>`_.
  - Include a brief discussion of insights from the results, in line with the learning objectives.

- Exercises: include self-test questions, small activities, and exercises at the end of a tutorial so that users (and instructors, if any) can check their learning.


Location
========

Place notebooks in an appropriate location:

:file:`tutorial/name.ipynb``
   Stand-alone tutorial.

:file:`tutorial/example/example_baseline.ipynb`
   Group of tutorials named “example.”
   Each notebook's file name begins with the group name, followed by a name
   beginning with underscores.
   The group name can refer to a specific RES shared across multiple tutorials.
   Some example names include::

       <group>_baseline.ipynb

       <group>_basic.ipynb  # Basic modeling features, e.g.:
       <group>_emmission_bounds.ipynb
       <group>_emission_taxes.ipynb
       <group>_fossil_resources.ipynb

       <group>_adv.ipynb  # Advanced modeling features, e.g.:
       <group>_addon_technologies.ipynb
       <group>_share_constraints.ipynb

       <group>_renewables.ipynb  # Features related to renewable energy, e.g.:
       <group>_firm_capacity.ipynb
       <group>_flexible_generation.ipynb
       <group>_renewable_resources.ipynb
