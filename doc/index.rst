The |MESSAGEix| framework
*************************

|MESSAGEix| is a systems-optimization modelling framework developed by the |IIASA| Energy, Climate, and Environment (ECE) Program [#rename]_ since the 1970s.

This is the documentation for :mod:`message_ix`,
a Python package that ties together all components of the framework.
:mod:`message_ix` is free and open source software,
licensed under the `Apache 2.0 license`_.

- :mod:`message_ix` supports creation and use of *any* energy-system model with the MESSAGE core equations.
  One *specific* model is “MESSAGEix-GLOBIOM”,
  a global model instance used in IIASA ECE Program research and sometimes informally called “MESSAGE”.
  MESSAGEix-GLOBIOM is documented as part of the separate :mod:`message_ix_models` package,
  in particular on the page “:doc:`message-ix-models:global/index`”.
- For peer-reviewed academic literature about |MESSAGEix| and specific models and applications,
  see :ref:`section 2 of the “User guidelines and notice” page <notice-cite>`,
  the :doc:`Usage <usage>` page,
  and again the :doc:`MESSAGEix-GLOBIOM <message-ix-models:global/index>` page in the message_ix_models documentation.

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
- :doc:`Usage <usage>` of |MESSAGEix| in academic publications, research projects, and derived tools.

.. toctree::
   :hidden:
   :caption: Getting started

   prereqs
   framework
   install
   tutorials
   Publications, projects, and tools <usage>

.. figure:: _static/ix_features.svg
   :width: 360px
   :align: center

   Features of ``ixmp``, ``message_ix``, and related packages :cite:`Huppmann-2018`


.. _core:

Mathematical specification
==========================

These pages provide comprehensive description of variables and equations
in the GAMS implementation of MESSAGE that is included with and used via :mod:`message_ix`.

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
   :caption: Mathematical specification

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

Everyone is encouraged to use |MESSAGEix| to develop energy system and integrated assessment models!
Developing a valid, scientific model requires careful use of the framework features.
This section provides guidelines for how to make some common model design choices.

- :doc:`efficiency`
- :doc:`tools/add_year`
- :doc:`reporting`
- :doc:`debugging`
- :doc:`macro`
- :doc:`notice` describes how to cite the framework and software in published research.
- :doc:`sharing` explains how to add your |MESSAGEix| applications to the :doc:`Usage <usage>` page in these docs.

.. toctree::
   :hidden:
   :caption: Developing MESSAGEix models
   :glob:

   efficiency
   tools/*
   reporting
   debugging
   macro
   notice
   sharing

Reference and development
=========================

- :doc:`api`
- :doc:`rmessageix`
- :doc:`whatsnew` —release history and migration/upgrade notes.
- :doc:`contributing` —we welcome enhancements to the framework itself that enable new features across all models.
  You can learn more about how we handle these contributions in :file:`GOVERNANCE.md` (`on GitHub <https://github.com/iiasa/message_ix/blob/main/GOVERNANCE.md>`__ or included with the source code)  [#osguides]_
- :doc:`bibliography`

.. toctree::
   :hidden:
   :caption: Reference & development

   api
   rmessageix
   whatsnew
   contributing
   bibliography

.. _help:

Community and support
=====================

We aim to maintain a healthy community for developers and users of MESSAGEix; thus we expect everyone to follow our **Code of Conduct**, which you can find in :file:`CODE_OF_CONDUCT.md` (`on GitHub <https://github.com/iiasa/message_ix?tab=coc-ov-file>`__  or included with the source code). [#osguides]_

You can also:

.. _newsletter:

- Read or join existing `discussions <https://github.com/iiasa/message_ix/discussions>`_ on GitHub, or start a new one with your MESSAGEix usage question.
- Search `current issues <https://github.com/iiasa/message_ix/issues?q=is:issue>`_, or open a new one to report a bug in the code.
- Subscribe to the **MESSAGEix Community Newsletter** by filling `this form <https://iiasa.ac.at/signup>`__ and ticking the box for "MESSAGEix-Community".
  At least once a year, we update all subscribers on the latest research and ongoing projects regarding MESSAGEix and invite you to our annual `Community Meeting <https://iiasa.ac.at/search?search_api_fulltext=MESSAGEix+Community+Meeting>`__.
- See our security policy in :file:`SECURITY.md` (`on GitHub <https://github.com/iiasa/message_ix?tab=security-ov-file>`_ or included with the source code). [#osguides]_
- Read answers to some not-so-:doc:`‘frequently’ asked questions <faq>`.
- Check the older message_ix Google Group, either `online <https://groups.google.com/d/forum/message_ix>`_ or via e-mail at <message_ix@googlegroups.com>.

.. toctree::
   :hidden:
   :caption: Community & support

   Code of conduct <https://github.com/iiasa/message_ix?tab=coc-ov-file#readme>
   Discussions <https://github.com/iiasa/message_ix/discussions>
   faq

.. _`MESSAGEix-GLOBIOM documentation`: http://data.ene.iiasa.ac.at/message-globiom/
.. _`Apache 2.0 license`: https://github.com/iiasa/message_ix/blob/main/LICENSE

.. [#rename] Known as the “Energy Program” until 2020-12-31.
.. [#osguides] `Our usage <https://github.com/iiasa/message_ix/community>`_ of files like CODE_OF_CONDUCT, GOVERNANCE, SECURITY, and SUPPORT follows the `Open Source Guides <https://opensource.guide/>`_ recommendations.
