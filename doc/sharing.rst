Sharing publications, projects, and tools
*****************************************

We invite you to share your publication, project, and/or tool created using the |MESSAGEix| framework.
To do so, please first read the steps at :ref:`contrib-pr`.

.. note:: If you are unfamiliar with development using Git and GitHub, you can instead `open an issue <https://github.com/iiasa/message_ix/issues/new>`_ containing all of the information mentioned below.

In your branch/pull request, make the following additions:

1. **Add the citation** of your publication/project/tool to the file :file:`doc/references.bib`.

   Use BibTeX format.
   Give the entry a key like ``surname-2021``, using the lead author's name and the year of publication.

2. **Add a figure** representing your publication/project/tool in the directory :file:`doc/_static/usage_figures/`.

   If possible, construct the file name using either the BibTeX entry key (above) or the DOI.

   For example: the URL https://doi.org/10.1016/j.scs.2021.103257 contains the DOI ``10.1016/j.scs.2021.103257``.
   Replace the ``/`` character with ``-``, and append the appropriate file extension for your image, like :file:`.jpeg`, :file:`.png`, etc.
   This might yield a file name like: :file:`doc/_static/usage_figures/10.1016-j.scs.2021.103257.jpeg`

3. **Add your publication/project/tool to the documentation sources**, specifically the existing file :file:`doc/usage.rst`.
   Use the existing entries as a template.

   - Use the same level of heading as the other entries in the same section.
   - For publications, use the full title as the heading.
   - Add your figure from (2) above with the ReST code like:

     .. code-block:: rest

        .. figure:: ../_static/usage_figures/your-pub-DOI.ext
           :width: 250px
           :align: right

   - Add the citation:

     .. code-block:: rest

        :cite:ct:`surname-2021`

   - In case of a publication, add bullet points to describe the spatial scope/resolution, keywords, and key ways in which |MESSAGEix| was used in the publication.
   - In case of a tool, add bullet points to describe the development goal and the key features, and link the code location (e.g. GitHub repository).
     If there is a publication that *describes* this tool, you can also include a citation per step (1) above and abstract (below).
   - Add the first max. 75 characters of the abstract/description of your publication/project/tool, followed by a link to an external location.

     .. code-block:: rest

        This paper analyses energy in Country X… `Read more →<https://doi.org/your-pub-DOI>`__

     - For publications, use the DOI URL if possible.
     - For tools, use the code or documentation URL.
