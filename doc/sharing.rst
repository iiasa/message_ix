Sharing tools, projects and publications
****************************************

We invite you to share your tools, projects and/or publications which are using the |MESSAGEix| framework.
To do so, please check first :doc:`contributing` and add your material as follows.

1. Add the citation of your tool/project/paper in BibTeX format to *message_ix/doc/references.bib*.

2. Add a figure representing your tool/project/paper into the directory *message_ix/doc/_static/tools_figures*, *message_ix/doc/_static/projects_figures* or *message_ix/doc/_static/publication_figures*.

   As a naming convention we make use of the DOI where possible. Use everything after https://doi.org/ and use "-" instead of "/".
   For example if your DOI is https://doi.org/10.1016/j.scs.2021.103257 the name of your figure would be *10.1016-j.scs.2021.103257.jpeg*.
   The ending .jpeg can also be .png or else.

3. Add your tool/project/paper to the respective file.

   You can add the description to your tool/project to *message_ix/doc/tools.rst* or *message_ix/doc/project.rst* with the following.
   The description to your publication, you can add to the respective REsT files of the different categories in directory *message_ix/doc/publications*.
   You can add your paper to as many categories as you think fits to the topic.

   - Please add the name of your tool/project/paper underlined by "-".
   - Then add your figure with the following::

        .. figure:: ../_static/publication_figures/The_name_of_your_figure.The_ending_of_your_figure
           :width: 250px
           :align: right
   - Add the citation as follows::

        :cite:ct:`Kikstra2021`
   - Add the first max. 311 characters of the abstract/description of your tool/project/paper followed by::

        ... :doc:`Read more →<The_name_of_your_tool/project/paper>`

4. (Optional for publications) Add new category

   - If a category is not listed, which represents your paper best, feel free to add an additional REsT file under *message_ix/doc/publications* underlining the heading with "=".
   - Link then the *publications.rst* file under *Topic* or *Scope* (or any heading) with the following::

        - :doc:`publications/name_of_the_file_with_new_category`

