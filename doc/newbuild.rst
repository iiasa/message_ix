Building a new model
********************

Before starting
===============
- What questions do I want to answer with my model?
  - Influences model structure -> Develop a Reference Energy System (RES).
  - What data do I require and in what format is the data?
  - Single or multiple collabortors/developers?

There are countless ways to structure an energy model.
There is no single correct structure not is their a single right way to structure the underlying process of building an energy model.
There are however several aspects to take into consideration, prior to commencing the modeling exercise.

#. Question 1. What question do I want to answer with the model?

   Building an energy model requires a careful balance in the level of detail represented.
   The number of demand sectors or technologies, the geographical as well as the temporal resolution are just a few examples where the level of detail plays a particularly important role.
   The reason for this is because they act as multiplicators to each other, hence they can quickly increase the model complexity.
   A concrete research question or outline for the analysis which is to be undertaken, helps to focus on detailing those aspects of the model relevant to answering the question.
   If for example the goal is to understand the effects of a policy, which increases the share of renewables in the electricity generation mix, on fuel mix in the transport sector, then attention can be given to detailing the transport sector and therewith associated fuel generation processes. The industrial, residential or commercial sectors may be depicted at a more aggregate level.
   A helpful approach to structuring the model is to develop a "Reference Energy System" (RES). In addition to guiding the model development process, the RES is also a very useful reference in the future to help document the model.
   
#. Question 2. What data is available and in what format?

   Having used the RES to structure the overall model layout, it will also be useful in identifying input data requirements.
   The data used as input to the model is critical in determining the results.
   The data used across different model aspects will not always come from a single source. Naming conventions, data formats, granularity or the time point at which the data was compiled can vary.
   Possibly data availability will also influence the model structure.
   Ideally sourcing data, cross checking the data for consistency and possibly identifying alternative methods or assumptions to compensate data gaps should largely be completed prior to commencing the modelling work.

#. Question 3. Who will be developing/using the model?

   Additional requirements may arise depending on the number of people developing the model or the future users.
   On the one hand, the detail in the documentation of the model can differ, the coding style used in scripts to 

   


- Familiarize yourself with the documentation of MESSAGEix.
  - Documentation of functions and code.
  - Searching page for information.
  - Use of messageix-discussions.
  - Other documentation:
    - MESSAGEix-GLOBIOM.
    - SA National model paper.
    - ..other material supplied as part of WS preparation..

- Are there any requirements which require me to look at additional resources?
  - Stackoverflow.
  - Software specific pages.

Exploration using tutorials
===========================
- Tutorials to explore features of MESSAGEix.
- Start with modifying existing tutorial and add complexity step by step.
  - Solve and validate.
  - Add documentation on underlying process.
  - Add Reporting.
  - Repeat process with each additional layer of complexity.

Example of workflow
-------------------
#. Step 1. Create a simplified single region model. A single or mutliple scripts can be used to:
    #. Create a new single region model with 10 timesteps e.g. 1990, 1995, 2000, 2005, 2015, 2020, 2025, 2030, 2040, 2050.
    #. Add technologies with underlying techno-echonomic parametrization. Eventually these can be read from a file containing raw technology data, which is formatted and add subsequentially added to the model. 
    #. Add demands to the model. 
    #. Calibrated historic capacity and activity for all historical timesteps based on the currently available data sets. 
    #. **Solve model; verify results; add reporting; add documentation**

#. Step 2. Extend model by adding CO2 emissions:
    #. Add CO2 emissions for technologies in the model. 
    #. **Solve model; verify results; add reporting; add documentation**

#. Step 3. Extend model by adding other GHG emissions:
    #. Add other GHG emissions for technologies in the model.
    #. Test model by adding an emissions constraint/tax.
    #. **Solve model; verify results; add reporting; add documentation**

#. Step 4. Extend time-horizon granularity
    #. Add additional timesteps 2035 and 2045 
    #. **Solve model; verify results; add reporting; add documentation**
         
#. Step 5. Add other regions 
    #. Add another region.
    #. Add import/export from/to new region.
    #. **Solve model; verify results; add reporting; add documentation**

Model transition
================

The migration of a "model" from an existing modelling platform, such as ANSWER-TIMES to MESSAGEix, can be accomplished in several different ways. Broadly a differentiation can be made between two general approaches: 

#. "Export and re-import": Data is is exported from the source platform, formatted and subsequently import to the destination platform.

#. "Re-build": Raw model data is used to build a new model in the destination platform. 

Each of the approaches have pros and cons. Steps from each of approaches can be combined to create a hybrid approach. But before providing details on how the process can be realized technically, there are a few considerations to be made when transitioning from a modelling platform to another. 

The goal of the "Export and re-import" transition method is to, as closely as possible, replicate the current model (modelled in source platform) in the new framework (MESSAGEix). This process will require the (1) current data to be exported to some sort of file-format compatible with the new model. (2) The exported data then requires formatting and adjustments to account for any requirements by the new framework to which the data will be uploaded. (3) The adjusted data is then added/imported into the new framework. In the case of transitioning from ANSWER-TIMES to MESSAGEix, exporting data to an xlsx file, in the format required by MESSAGEix, would be a possibility. The excel can then be imported using the `read_excel()` function (see link). 

There are some considerations to be made when deciding on the most suitable approach to switching to a different modelling framework. 

#. Legacy issues: As is the case for most models, the current version to be migrated will be a product having been developed over a longer time period.  Different modellers/users will have worked with the model.  Modelling approaches are different from user to user so notations and use of equations may not always be consistent. Software used to generate input data will have changed and hence the format of input data may have altered. This means that there are certain model aspects which have been inherited over time, some of which should possibly be re-implemented or possibly omitted when transitioning the model between frameworks. 

#. User friendliness and transparency: The fact that the current model is a product which has been developed over time, also menas that there are probably some desirable improvements that will want to be undertaken to make the model more transparent and user-friendly.  This can be achieved by shuffling around the "reference energy system" or possibly by making use of new features available in the new framework. 

#. Modularizing features: Models can incorporate features which were developed for a certain purpose but are not necessarily used as part of the core model. Therefore, the core model could be slimmed down.  The additional features can be implemented as "modules" which are essentially additional model features that can be used in conjunction with the core model to provide additional detailed incites for certain policy analysis. 

#. Data adjustments: Input data requirements may be different for the two frameworks.  This means that the current model data may need to be supplemented in the transition process. Further adjustments may also be required as the data "structure" from one model may not necessarily "solve" in another model.  

#. Verification and validation: Despite input data being very similar for models, a verification and validation process will be required to ensure that the new results make sense. An important aspect of this process is the size of the model for which the verification is being carried out. 

The following should be noted on the "Export and re-import" process: 

#. It is not guaranteed that the "export and re-import" process will yield transitioning to a new platform faster. The source model structure, the available resources as well as the modellers firmness with both the old and the new platform will play a decisive role. While the "upfront" investments may be lower, there are tasks that follow the initial import, which may be more difficult to resolve once the initial model has been set up and the "new" version will have been adopted for new projects/research. 

#. While "export and re-import" may result in faster transfer of the model to the new platform, there are also numerous process outside the "platform" that define the actual model. This can be in the form of linkages to other models, but also in the form of workflows that feed the model with data, model documentation, reporting of results. The bigger the model, the bigger the task, the longer it will take to complete individual tasks.  

#. The "export and re-import" process should be considered a once-in-a-lifetime process. This means that when modelling data is updated in the future, the data will need to be updated in the MESSAGEix framework directly, as opposed to being first updated in ANSWER-TIMES, which is the transitioned using the "export and re-import" process into the MESSAGEix framework. This implies, that any existing scripts used to calibrate or update data in the framework, will need to be reworked irrespective of the approach used to transition data. 

#. Lastly, when "importing" data into the model, users make use of automated functions that ease the process, but at the same time, if not already firm with the new platform, the learning process of using the new platform will be less effective. 

Therefore, the suggestion would be to structure the transition process with the aim of already or eventually using raw input data. This means, that wherever possible, raw input data should be processed and fed into the new platform.

.. _fig-newbuild_transfer:
.. figure:: /_static/newbuild_transfer.png
   :width: 500px
   :align: center

   Overview of model transition process options.

For example, if the techno-economic data (investment costs, variable operating and maintenance cost, efficiency etc.) is being read from a csv file and added to the current framework using a script, then the script importing the data could be modified to import data into the new framework (see Workflow 2 in above figure) as opposed to exporting the techno economic data from the old framework and re-importing this into the new framework (see Workflow 1 in above figure). 

If for example it is too challenging or inefficient at the moment to use `add_par()` or `add_set()` functions, then the xlsx import function can be used temporarily, yet the underlying scripts and workflows should aim to eventually transition to using the purpose-built functions designed to carry out these specific tasks. 

Initially what the "finished" model should look like in terms of the RES, but also in terms of various non-framework specific aspects or interactions should be established prior to starting the transition process. Splitting the transition process into manageable chunks is the next step.  By concentrating on smaller tasks, the verification and validation of the results is more manageable, the reporting can be established for these small steps and workflows can be established so that they can be repeated in the future. In addition, documentation and even tests can be written to accompany the scripts and processes. So, having a workflow that builds the model essentially from scratch will provide more flexibility in the future. 
