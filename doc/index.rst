The |MESSAGEix| framework
*************************

.. figure:: _static/ix_features.png
   :width: 320px
   :align: right

   The |ixmp| (:cite:`huppmann_messageix_2018`)

|MESSAGEix| is a versatile, dynamic systems-optimization modelling framework developed by the |IIASA| Energy, Climate, and Environment (ECE) Program [#rename]_ since the 1980s.

This is the documentation for :mod:`message_ix`, a Python package that ties together all components of the framework.
:mod:`message_ix` and :mod:`ixmp` are free and open source, licensed under the `APACHE 2.0 open-source license`_.

- For the scientific reference of the framework, see Huppmann et al. (2019) :cite:`huppmann_messageix_2018`.
- For an overview and recent publications related to the specific |MESSAGEix|-GLOBIOM global model instance used at the IIASA ECE Program, see the `MESSAGEix-GLOBIOM documentation`_.


.. _getting-started:

Getting started
===============

.. NB this ReST pattern is repeated throughout this file:

   1. List of :doc:`...` links, followed by
   2. .. toctree:: directive with :hidden:, containing the same links.

   This overcomes limitations of toctree, allowing introductory paragraphs, and different titles in this page than in the sidebar.

Modeling using |MESSAGEix| requires domain knowledge, understanding of certain research methods, and scientific computing skills.

- :doc:`prereqs` gives a list of these items for formal and self-guided learning.

Then, continue with the:

- :doc:`framework` detailed description and feature list.
- :doc:`install` of the software and essential dependencies.
- :doc:`tutorials` for new users that demonstrate the basic features of the framework.

.. toctree::
   :hidden:
   :caption: Getting started

   prereqs
   framework
   install
   tutorials




.. _core:

Mathematical specification
==========================

These pages provide comprehensive description of the variables and equations in
the core MESSAGEix mathematical implementation.

- :doc:`model/MESSAGE/sets_maps_def`
- :doc:`time`
- :doc:`model/MESSAGE/parameter_def`
- :doc:`model/MESSAGE/model_core`
- :doc:`model/MESSAGE/model_solve`
- :doc:`model/MESSAGE/reporting`
- :doc:`model/MESSAGE/scaling_investment_costs`
- :doc:`model/MACRO/macro_core`

.. toctree::
   :hidden:
   :caption: Mathematical Specification

   model/MESSAGE/sets_maps_def
   time
   model/MESSAGE/parameter_def
   model/MESSAGE/model_core
   model/MESSAGE/model_solve
   model/MESSAGE/reporting
   model/MESSAGE/scaling_investment_costs
   model/MACRO/macro_core


.. _guide:

Developing |MESSAGEix| models
=============================

Developing a valid, scientific |MESSAGEix| model requires careful use of the framework features.
This section provides guidelines for how to make some common model design choices.

- :doc:`efficiency`
- :doc:`tools/add_year`
- :doc:`reporting`
- :doc:`debugging`
- :doc:`macro`

.. toctree::
   :hidden:
   :caption: Developing MESSAGEix models
   :glob:

   efficiency
   tools/*
   reporting
   debugging
   macro


Using, getting help, and contributing
=====================================

Everyone is encouraged to use the framework to develop energy system and integrated assessment models!

- :doc:`api`
- :doc:`rmessageix`
- :doc:`whatsnew` —release history and migration/upgrade notes.
- :doc:`notice` —including how to properly cite the framework and software in scientific research.
- :doc:`contributing` —we welcome enhancements to the framework itself that enable new features across all models.
- :doc:`faq`
- :doc:`bibliography`

.. toctree::
   :hidden:
   :caption: Help & reference

   api
   rmessageix
   whatsnew
   notice
   contributing
   faq
   bibliography

.. _help:

Have a question? Check…

- …on GitHub:

  - Join an existing `discussion <https://github.com/iiasa/message_ix/discussions>`_ or start a new one with your question.
  - Search `current issues <https://github.com/iiasa/message_ix/issues?q=is:issue>`_, or open a new one to report a bug in the code.

- …the :doc:`faq`.
- …the message_ix Google Group, either `online <https://groups.google.com/d/forum/message_ix>`_ or via e-mail at <message_ix@googlegroups.com>.

.. _`MESSAGEix-GLOBIOM documentation`: http://data.ene.iiasa.ac.at/message-globiom/
.. _`APACHE 2.0 open-source license`: https://github.com/iiasa/message_ix/blob/master/LICENSE

.. [#rename] Known as the “Energy Program” until 2020-12-31.
