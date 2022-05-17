Video script: Installation
**************************

Introduction
============

.. note::

   Use a totally fresh install of Anaconda.
   This includes removing conda-forge from the channels list, so there is no warning message in Step 6.

   Open the install documentation at https://docs.messageix.org.
   Open https://github.com/iiasa/message_ix in a separate tab, for later.

Hello everybody and welcome to this video tutorial on the installation of MESSAGEix through Anaconda on Windows.

You can also find on the Installation page of the MESSAGEix documentation at docs dot messageix dot org, as it is shown here on the right side.
It is also linked in the description below.
While you are there, make sure to check the prerequisite knowledge and skills to use MESSAGEix, as this will not be covered in our tutorials.

That being said, let's jump straight into installing MESSAGEix through Anaconda.
At this point, we have already completed Steps 1 through 3, to install GAMS and add its PATH environment variable on the system.
We have also completed Step 4, installing Anaconda using the instructions linked from the page.
If you haven't completed these Steps 1 through 4 yet, you should read the documentation and instructions for those steps, complete them, and then come back to this video.

We begin with Step 5, opening the Anaconda Prompt from the Start Menu.

.. note::

   Do this.

In Step 6, we will first make sure that “conda forge” is used as the default channel to download and install packages, including message_ix and other packages that it requires.
Secondly, we set the channel priority to 'strict'.
This ensures that conda will select the latest version of message_ix from the "noarch" channel and ignore much older packages in OS-specific channels.

We copy the first command into the prompt and run it.

.. note::

   Do this.

This channel is now the top-priority or our default channel.

We then copy the second command into the prompt and run it.

.. note::

   Do this.

Now the channel priority is set to strict.
With that, we have completed Step 6, and we move on.

In the next steps, we will create and activate a new Anaconda “environment”, and use that to install MESSAGEix.
Conda allows us to have multiple environments, each with different Python packages and versions installed; the conda documentation explains this concept in complete detail.
For this video, we will do everything with just 1 environment.

Let's go through each step, one by one.
In Step 7, we create a new environment.
Note that the prompt shows us “base” in the parentheses at the left side here.

.. note::

   Use the mouse to highlight the ``(base)`` text at the left of the prompt.

This means that we are currently in the “base” environment.
For MESSAGEix, all we need to remember is that we cannot use the “base” environment; we must create and use a new one.
Let's do that, by typing conda create double-dash name and then "message_env", or copying the first command of Step 7.
"message_env" will be the name of our new environment, but we can also use any other name.

.. note::

   Type ``conda create --name message_env`` and hit [Enter].

We are prompted to say “yes” to creating this new environment, to be stored in this specific folder.
Now we see that the environment has been created, and we enter the next command from Step 7, "conda activate message_env", giving it the name of the environment we just created.

.. note::

   Do this.

And we see that we are now “in” this environment from the prompt.

.. note::

   Use the mouse to highlight the ``(message_env)`` text at the left of the prompt.

The next step is Step 8.
We enter the command "conda install message-ix".

.. note::

   Do this.

We see that it's now “solving” the environment.
It lists all the packages and dependencies that will be installed, which are required by MESSAGEix.
So, at the end of the list, confirm with “yes” and now we wait for all these packages to be installed.

To check that this process has picked out the latest version of MESSAGEix, we can type Ctrl+F and search for message-ix.
We can see that, first, it is one of the packages that will be installed, and second, the version matches the latest version shown in the documentation.
Currently this is version 3.3.0, but it may be a newer version as you watch this.
So in this case, we are OK.

.. note::

   Do this.
   Highlight message_ix and version number when searching for it
   Prepare https://github.com/iiasa/message_ix/releases in a browser window to quickly switch there for version control

We can also check that our default channel, that we set in Step 6, is being used: both message-ix and ixmp will be installed from the conda-forge channel.

.. note::

   Do this, highlighting with the mouse.

So far, so good!

At this point we must wait a few minutes for the packages to be downloaded and installed.
Depending on the machine, it can take more or less time; if we've already downloaded the packages previously, it can be faster.

So at this point, we have completed Step 8, and MESSAGEix—plus everything needed to use it—is installed.

Check the installation
======================

If we look again at the install instructions…

.. note::

   Change to the browser window where the install instructions appear.


…we can see that there are instructions for different ways of installing MESSAGEix, that are not covered in this video.
Since we have already installed using Anaconda, we can skip down to the section titled “Check that the installation was successful”.

To check this, we run two commands:
The first command is "message-ix show-versions":

.. note::

   Do this.

This is a way of accessing MESSAGEix from the command line, and it becomes available when the package is successfully installed.
"show-versions" is a specific command that—as the name implies—shows the versions of MESSAGEix, ixmp, GAMS, and other required and related packages.

By the way: when you experience an issue with MESSAGEix and you want to seek support via GitHub, it is very important to include the output of this command, because it includes essential information about your specific versions, operating system, etc.

The second command, "message-ix platform list", shows us a list of all the "platforms" that are configured on your system.
In the IIASA ECE program, for instance, this will include our central database that we used as a shared storage for our models and scenarios.

.. note::

   Do this.

If you've just installed MESSAGEix for the first time, you will see a platform that's named "local".
This is stored in a specific file on your system, and the path is shown here.
It also shows us that "local" is the default platform.

Another thing we can do, in order to check where Anaconda, our environment, and MESSAGEix are, is run the command "conda info".

.. note::

   Do this.

This shows us the directories where these have been placed.
We can copy this path and paste it into Windows Explorer to open the "anaconda3" folder.

.. note::

   Do this.

And within this folder, we can navigate:

- first to "envs", which means "environments",
- then, to the folder named "message_env", matching the name of the environment we created earlier,
- then to "Lib", followed by "site-packages".

.. note::

   Do this.

In this folder, we have one folder per Python package that has been installed in this specific environment.
If we have other environments, different to "messager_env", the corresponding "site-pacakges" folder will have different folders, with different other packages.

.. note::

   Find and select the message_ix folder.

If we are curious to look at the source code that MESSAGEix runs, for instance the actual GAMS files with the core linear program formulation, we can look at the files in this directory, specifically, the subdirectory message_ix/model/.

.. note::

   Show these files in Windows Explorer.

Another place to look is on GitHub directly:

.. note::

   Switch to a browser tab with https://github.com/iiasa/message_ix.
   Navigate into the "message_ix/model/" folder.

Equally, the code for the ixmp package, that handles the data storage underlying MESSAGEix, can also be found in "site-packages".


Download and start tutorials
============================

We've now installed and checked the installation of MESSAGEix.
The last thing we will cover in this video, and the first thing you will probably want to do if you are a new user, is to download and run the MESSAGEix tutorials.

Our team has developed a very rich set of example models that give you an introduction to the use of MESSAGEix, ixmp, and some of the many capabilities of the framework.

Complete information about these tutorials is available in the documentation…

.. note::

   Go to documentation, navigate to page about “Tutorials”.

…here on this page.

So we will cover the instructions under “Getting tutorial files” and “Running tutorials using Anaconda”.

The first step is to download the tutorial files.
Since these are a kind of learning aid, they are not automatically installed with the Python and GAMS code for MESSAGEix.
This is why we need to download them.

The "message-ix" program we already used has a command "dl" that does this for us.
We only need to choose a specific folder or directory where we want the downloaded tutorials to be placed.
In this case, let's put them into the Document folder—but they can also be placed anywhere else.
We use Windows Explorer to navigate to the Document folder, and then we copy the full path.

.. note::

   Do this.

Next, with that same environment "message_env" active, we run the command "message-ix dl " and then paste the path we just copied.

.. note::

    Do this.

We see that it receives some data and unzips it into that specific folder.
It is a very quick process, so we already see that this folder has appeared, and if we double-click on it, then we see the folder where our tutorials are stored in.

.. note::

   Do this.

The tutorials are in the form of Jupyter notebooks.
Remember - understanding and working with Jupyter notebooks is one of the prerequisite skills for learning MESSAGEix, these are listed in the documentation.
This video does not cover this.

The last thing we need to do in order to run the tutorials, is to install the "nb_conda" package for being able to run Jupyter.
So what we do is copy this command and paste it in out Anaconda Prompt and run it.

.. note::

   Do this.

It collects again some package meta data and solves the environment.
Here, please answer also with "Yes", so the specific packages can be downloaded.

As such, we want to start the Jupyter notebook server and use this to open the tutorials.
In order to do this, we want to switch the current working directory to this tutorial folder.
We again use Windows Explorer to copy the tutorials path, and then, in the Anaconda Prompt, we use the "cd" or "change directory" command, to move into that folder.

.. note::

   Do this.

Next, we run the command "jupyter notebook" to start Jupyter.

.. note::

   Do this.

A browser tab is automatically opened.
This shows the list of files and subfolders in this folder.
(If we "cd" to a different folder before running "jupyter notebook", we would see different files.)

As a last step, let's open one tutorial notebook, for the “Westeros baseline” tutorial.
We do this by clicking on the “Westeros” directory, and then on the file “westeros_baseline.ipynb.”

So a new browser tab opens with the tutorial.
The first thing we will need to check is that the “Kernel” which runs the notebook code is associated with the environment where we earlier installed MESSAGEix.
To do that, we click on “Kernel” in the menu, then “Change Kernel.”
An asterisk (\*) shows which environment is currently active.
As we can see, it appears by "message_env", so we know that this notebook is running in the correct environment.

We can then select the first cell and check that it runs correctly.
To do so, select the cell and hit Ctrl + Enter.

.. note::

   Do this.

The cell runs correctly, including the line "import ixmp".
This is a confirmation that ixmp (and MESSAGEix) are installed correctly, and can be loaded and used by the Python code in this tutorial notebook.

Conclusion
==========

And with that we've reached the end of this video.
Thank you for watching.
Please read the documentation and explore the tutorials to learn more about the capabilities of the MESSAGEix framework, the ixmp platform, and how to use them in research.


.. Captions of first attempt YouTube video
.. ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. This video follows up on a request of one of our September workshop participants that suggested that a video tutorial going through the installation steps of the MESSAGEix framework would be very useful.
