User guidelines and notice
**************************

We ask that you take the following four actions whenever you:

- **use** the |MESSAGEix| framework, |ixmp|, or any model(s) you have built using these tools
- to **produce** any scientific publication, technical report, website, or other **publicly-available material**.

The aim of this request is to ensure good scientific practice and collaborative development of the platform.

1. Understand the code license
==============================

Use the most recent version of |MESSAGEix| from the Github repository.
Specify clearly which version (e.g. release tag, such as ``v1.1.0``, or commit hash, such as ``26cc08f``) you have used, and whether you have made any modifications to the code.
To retrieve this information from the command line, use ``git describe --tags``, which will show you the version, number of commits since then, and the hash of your current commit.
Note that the commit hash does not include the preceeding ``-g``.

Read and understand the file ``LICENSE``; in particular, clause 7 (“Disclaimer of Warranty”), which states:

    Unless required by applicable law or agreed to in writing, Licensor provides the Work (and each Contributor provides its Contributions) on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied, including, without limitation, any warranties or conditions of TITLE, NON-INFRINGEMENT, MERCHANTABILITY, or FITNESS FOR A PARTICULAR PURPOSE. You are solely responsible for determining the appropriateness of using or redistributing the Work and assume any risks associated with Your exercise of permissions under this License.

.. _notice-cite:

2. Cite the scientific publication
==================================

Cite, at minimum, the following manuscript:

  | Daniel Huppmann, Matthew Gidden, Oliver Fricko, Peter Kolp, Clara Orthofer, Michael Pimmer, Nikolay Kushin, Adriano Vinca, Alessio Mastrucci, Keywan Riahi, and Volker Krey.
  | "The MESSAGEix Integrated Assessment Model and the ix modeling platform".
  | *Environmental Modelling & Software* 112:143-156, 2019.
  | doi: `10.1016/j.envsoft.2018.11.012`_
  | electronic pre-print available at `pure.iiasa.ac.at/15157/`_.

You should also cite the software project itself. The data for citing both the manuscript and the software can be found in the citation file :file:`CITATION.cff`.
You can use `the official cff tools <https://github.com/citation-file-format/citation-file-format#tools-to-work-with-citationcff-files-wrench>`__ to export the data to BibTeX and other formats.

In addition, you may:

- **Cite the code via Zenodo**.
  The DOI `10.5281/zenodo.4005684 <https://doi.org/10.5281/zenodo.4005684>`_ represents *all* versions of the :mod:`message_ix` code, and will always resolve to the latest version.
  At that page, you can also choose a different DOI in order to cite one specific version; for instance, `10.5281/zenodo.4005685 <https://doi.org/10.5281/zenodo.4005685>`_ to cite v3.1.0.
  Zenodo also provides citation export in BibTeX and other formats.
- Include a link, e.g. in a footnote, to the online documentation at https://docs.messageix.org.

3. Use the naming convention for new model instances
====================================================

For any new model instance under the |MESSAGEix| framework, choose a name of
the form "MESSAGEix [xxx]" or "MESSAGEix-[xxx]", where [xxx] is replaced by:

- the institution or organization developing the model,
- the name of a country/region represented in the model, or
- a similar identifier.

For example, the national model for South Africa developed by Orthofer et al. [1] is named "MESSAGEix South Africa".

Ensure there is no naming conflict with existing versions of the |MESSAGEix| model family.
When in doubt, contact the IIASA ECE Program at <message_ix@iiasa.ac.at> for a list of existing model instances.

4. Give notice of publication
=============================

E-mail <message_ix@iiasa.ac.at> with notice of any new or pending publication.

Optional: Add your tool, project or publication to this documentation
---------------------------------------------------------------------

To make your usage of |MESSAGEix| visible, add it to the :doc:`usage` page of this documentation, in the :ref:`tools`, :ref:`projects` or :ref:`publications` section.
See :doc:`sharing` for details.

References
----------

  | [1] Clara Orthofer, Daniel Huppmann, and Volker Krey (2019).
  |     "South Africa's shale gas resources - chance or challenge?"
  |     Frontiers in Energy Research 7:20. doi: `10.3389/fenrg.2019.00020`_

..  _`10.1016/j.envsoft.2018.11.012`: https://doi.org/10.1016/j.envsoft.2018.11.012
.. _`pure.iiasa.ac.at/15157/`: https://pure.iiasa.ac.at/15157/
.. _`10.3389/fenrg.2019.00020`: https://doi.org/10.3389/fenrg.2019.00020
