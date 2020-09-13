Video script: Installation
**************************

.. note::

   Use a totally fresh install of Anaconda.
   This includes removing conda-forge from the channels list, so there is no warning message in Step 6.

   Open the install documentation at https://docs.messageix.org.

This video describes the installation of MESSAGEix using Anaconda on Windows.

Here, we are looking at the Installation page of the MESSAGEix documentation at docs dot messageix dot org.
At this point, we have already completed Steps 1 through 3, to install GAMS and add its PATH environment variable on the system.
We have also completed Step 4, installing Anaconda using the instructions linked from this page.

We begin with Step 5, opening the Anaconda Prompt from the Start Menu.

.. note::

   Do this.

In Step 6, we will make sure that “conda forge” is used as the default channel to download and install packages, including message_ix and other packages that depend on it.
We copy this command into the prompt and run it.

.. note::

   Do this.

Next, in Step 7, we create a new “environment”.
Note that the prompt shows us “base” in parentheses at the left here.

.. note::

   Use the mouse to highlight the ``(base)`` text at the left of the prompt.

This means that we are currently in the “base” environment.
Conda allows us to have multiple environments, each with different Python packages and versions installed; the conda documentation explains this concept in complete detail.
For MESSAGEix, all we need to remember is that we cannot use the “base” environment; we must create and use a new one.

[…etc.…]
