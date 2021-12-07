Sharing tools, projects and publications
****************************************

We invite you to share your publications, tools and/or projects which are using the |MESSAGEix| framework.
To do so, please check first :doc:`contributing` and add your material as follows.

**1. Add the citation of your publication/tool/project in BibTeX format to message_ix/doc/references.bib.**

**2. Add a figure representing your publication/tool/project into the directory message_ix/doc/_static/usage_figures.**

   As a naming convention we make use of the DOI where possible. Use everything after https://doi.org/ and use "-" instead of "/".
   For example if your DOI is https://doi.org/10.1016/j.scs.2021.103257 the name of your figure would be *10.1016-j.scs.2021.103257.jpeg*.
   The ending .jpeg can also be .png or else.

**3. Add your publication/tool/project message_ix/doc/usage.rst.**

   - Please add the name of your publication/tool/project underlined by "~" under the respective heading.
   - Then add your figure with the following::

        .. figure:: ../_static/publication_figures/The_name_of_your_figure.The_ending_of_your_figure
           :width: 250px
           :align: right

   - Add the citation as follows::

        :cite:ct:`Kikstra2021`

   - In case of a publication, add bullet points which describes the region, keywords and the usage of |MESSAGEix|.
   - In case of a tool, add bullet points which describes the development goal and the output, and link the GitHub repository.
   - Add the first max. 75 characters of the abstract/description of your publication/tool/project followed by::

        ... :doc:`Read more →<The_name_of_your_tool/project/paper>`

