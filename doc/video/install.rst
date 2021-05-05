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


Captions of first attempt YouTube video
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

1
00:00:00,640 --> 00:00:06,560
Hello everybody and welcome to
this video tutorial on the installation

2
00:00:06,560 --> 00:00:10,880
of MESSAGEix through Anaconda. This
video

3
00:00:10,880 --> 00:00:14,240
follows up on a request of one of our
September

4
00:00:14,240 --> 00:00:19,279
workshop participants that suggested
that a video tutorial

5
00:00:19,279 --> 00:00:23,519
going through the installation steps of
the MESSAGEix framework would be

6
00:00:23,519 --> 00:00:29,039
very useful. So,
let's start with the with the process

7
00:00:29,039 --> 00:00:33,440
the first thing to do it would be opening an Anaconda

8
00:00:33,440 --> 00:00:40,000
prompt and also be sure
that you've already installed GAMS and

9
00:00:40,000 --> 00:00:43,680
Anaconda adding their path environment variables

10
00:00:43,680 --> 00:00:47,760
to Windows. So as we can see here

11
00:00:47,760 --> 00:00:54,559
we are now in the environment base
and we will go we will have to go to the

12
00:00:54,559 --> 00:00:58,879
MESSAGEix installation page that we've
already shared

13
00:00:58,879 --> 00:01:06,960
and start following
the installation steps. So, the first

14
00:01:06,960 --> 00:01:13,840
thing to do is to ensure that
Conda Forge is your

15
00:01:13,840 --> 00:01:18,799
default channel where to
download the

16
00:01:18,799 --> 00:01:26,320
the packages from, so we will
run this command.

17
00:01:26,320 --> 00:01:32,640
And yes, Anaconda it's already
in our channel's list and is moving like it

18
00:01:32,640 --> 00:01:37,200
to the top of the priorities, to the top priority.

19
00:01:37,200 --> 00:01:43,840
Now we will just have to
start with the rest of the steps in this

20
00:01:43,840 --> 00:01:47,439
case it would be just
creating a new environment, activating it

21
00:01:47,439 --> 00:01:52,000
and then installing MESSAGEix.
So, let's go

22
00:01:52,000 --> 00:01:58,960
one by one: conda create
--name and we can just choose whatever

23
00:01:58,960 --> 00:02:04,000
name we want for the environment
in this case we will choose ws1-env

24
00:02:04,000 --> 00:02:11,680
(dash env).
So now we'll have to wait so

25
00:02:11,680 --> 00:02:15,440
we will say yes to creating this
new

26
00:02:15,440 --> 00:02:18,879
this new environment which will be
stored in this

27
00:02:18,879 --> 00:02:23,840
specific folder

28
00:02:23,920 --> 00:02:29,280
OK, so the environment has just been
created so we will now just activate it

29
00:02:29,280 --> 00:02:33,519
again with conda activate

30
00:02:34,080 --> 00:02:40,400
workshop one environment (ws1-env)
and we see that now we are inside of the

31
00:02:40,400 --> 00:02:43,680
environment so
between parentheses that's the

32
00:02:43,680 --> 00:02:47,120
environment name.
So then the next step would be

33
00:02:47,120 --> 00:02:52,400
conda install
message-ix

34
00:02:54,560 --> 00:02:57,120
We will see

35
00:02:57,840 --> 00:03:01,920
that it's now solving environment and
will list all the packages and

36
00:03:01,920 --> 00:03:04,159
dependencies
that will be installed that are

37
00:03:04,159 --> 00:03:07,920
dependencies of MESSAGEix.

38
00:03:08,159 --> 00:03:11,801
So, we will say 'yes', at the end,
and now we will wait for all

39
00:03:14,800 --> 00:03:18,800
these packages to be installed.
Just for a simple check we can just

40
00:03:18,800 --> 00:03:25,440
always Ctrl + F
and look for message-ix

41
00:03:27,040 --> 00:03:30,560
and we see that is it is one of the
packages that is being studied

42
00:03:30,560 --> 00:03:34,080
with version 3.1.0 so it's the latest
version

43
00:03:34,080 --> 00:03:38,159
So we are OK. And it's been installed from
Conda Forge

44
00:03:38,159 --> 00:03:43,040
the same with the ixmp: also ixmp is

45
00:03:43,040 --> 00:03:47,340
installed at the version 3.1.0 from
Conda Forge.

46
00:03:47,340 --> 00:03:51,760
So, apparently, so far so good.
We will have to wait for the

47
00:03:51,760 --> 00:03:56,080
installation of all of these
packages which will take depending of

48
00:03:56,080 --> 00:04:00,879
course on the machine
two to three minutes it usually

49
00:04:00,879 --> 00:04:04,879
takes some time to downloading some of
the packages but in this case

50
00:04:04,879 --> 00:04:10,799
it's been fast because I already
downloaded them in a previous

51
00:04:10,799 --> 00:04:17,440
test of the installation. So now we have
both packages so both ixmp and

52
00:04:17,440 --> 00:04:21,199
message-ix installed to check where
exactly have they

53
00:04:21,199 --> 00:04:24,960
been installed we can always check:
'where conda' command

54
00:04:24,960 --> 00:04:31,840
it will show us where the
executable is and so

55
00:04:31,840 --> 00:04:36,240
we will just have to copy this this part
of the directory that is showing

56
00:04:36,240 --> 00:04:40,320
so we will have to locate the anaconda 3
folder

57
00:04:40,320 --> 00:04:44,240
and it will be just a matter of opening

58
00:04:44,240 --> 00:04:51,919
the Windows explorer,
type the the path in here

59
00:04:51,919 --> 00:04:57,120
and now we will be in
the anaconda3 folder. So,

60
00:04:57,120 --> 00:05:03,280
now we will have to look for the
envs folder

61
00:05:03,280 --> 00:05:07,360
and within the envs folder we will have
all the environments

62
00:05:07,360 --> 00:05:12,700
that we have created and in our case
this workshop one environment (ws1-env)

63
00:05:12,700 --> 00:05:17,039
so we will have to open this
folder

64
00:05:17,039 --> 00:05:21,360
and within this folder we will have to
go to lib

65
00:05:21,360 --> 00:05:27,199
and then within lib, the famous
folder I've already mentioned in the

66
00:05:27,199 --> 00:05:31,840
workshop which is
'site-packages' and within site-packages

67
00:05:31,840 --> 00:05:36,960
we will have one folder per Python
package that we have installed in this

68
00:05:36,960 --> 00:05:40,080
specific environment so other
environments

69
00:05:40,080 --> 00:05:44,479
different to ws1-env
will have other lists of folders here

70
00:05:44,479 --> 00:05:48,720
with different other packages.
So, we can see that we have ixmp here

71
00:05:48,720 --> 00:05:54,080
with all of its files and Python files
and we will also

72
00:05:54,080 --> 00:05:59,039
see that there is message_ix

73
00:05:59,840 --> 00:06:05,039
and yeah with all of its subfolders
and Python files

74
00:06:05,039 --> 00:06:10,960
When we were talking about where the
GAMS model files are it's in the

75
00:06:10,960 --> 00:06:15,120
specific folder called
model and within the folder model we

76
00:06:15,120 --> 00:06:19,199
will have also the
folder MESSAGE which will eventually

77
00:06:19,199 --> 00:06:24,000
lead us to all the
GAMS files that are used to run and

78
00:06:24,000 --> 00:06:28,000
solve the MESSAGEix model

79
00:06:28,080 --> 00:06:34,960
So, now that we know where
we have installed

80
00:06:35,039 --> 00:06:41,440
these packages we will go back to the
message_ix folder

81
00:06:41,440 --> 00:06:44,800
and we will just copy this this path
here

82
00:06:44,800 --> 00:06:48,080
because I want the tutorials to be
installed in this

83
00:06:48,080 --> 00:06:51,440
specific folder.
But of course we could also

84
00:06:51,440 --> 00:06:55,919
move it to the Desktop or to another any
other specific folder

85
00:06:55,919 --> 00:07:01,360
So, let's continue with the in
with the procedure, which first of all

86
00:07:01,360 --> 00:07:06,560
will be
message-ix dl

87
00:07:06,560 --> 00:07:11,599
and then we will just have to copy here
the the path

88
00:07:12,000 --> 00:07:16,080
we will see that it will be retrieving
some data and

89
00:07:16,080 --> 00:07:20,400
unzipping it into that specific folder.

90
00:07:20,639 --> 00:07:23,680
It's a very quick process and yeah we
will see that

91
00:07:23,680 --> 00:07:30,080
this folder has appeared
in this in here so we will just have to

92
00:07:30,080 --> 00:07:32,880
double click on it
and then we will find this Tutorial

93
00:07:32,880 --> 00:07:37,600
folder where all the different tutorials are present.

94
00:07:37,600 --> 00:07:46,000
So, now it would be
nice to, again, copy the path

95
00:07:46,000 --> 00:07:52,400
of this specific folder
in the tutorial folder and so we will

96
00:07:52,400 --> 00:07:58,400
just move there with: 'cd' and then the path.
It will just

97
00:07:58,400 --> 00:08:01,759
move the current working directory to
this specific one

98
00:08:01,759 --> 00:08:06,639
You see, we are already here, and here we
will just have to

99
00:08:06,639 --> 00:08:12,639
type jupyter notebook. But, before doing that
we will have to install the nb_conda

100
00:08:12,639 --> 00:08:16,800
package as I've shown in

101
00:08:16,800 --> 00:08:20,640
in today's workshop presentation. So,
we will proceed to

102
00:08:20,640 --> 00:08:31,039
conda install nb_ronda
And this package, I repeat, it's for being

103
00:08:31,039 --> 00:08:35,519
able to manage different environments and to run

104
00:08:35,519 --> 00:08:40,080
Jupyter notebooks
in different environments. So, it's asking

105
00:08:40,080 --> 00:08:45,680
us that these two packages will be
installed we will say 'yes'

106
00:08:53,760 --> 00:08:58,000
We have installed nb_conda so now
we are ready as I was saying before to

107
00:08:58,000 --> 00:09:02,880
just write:
jupyter notebook

108
00:09:02,880 --> 00:09:09,040
and it will open a
web browser tab

109
00:09:09,040 --> 00:09:12,399
with the working directory into this
folder so we will

110
00:09:12,399 --> 00:09:17,519
able to access the the tutorials very easily.

111
00:09:17,519 --> 00:09:22,220
So, here we are this
is the Jupyter notebook

112
00:09:22,220 --> 00:09:26,000
we are seeing here all the folders I was
mentioning before

113
00:09:26,000 --> 00:09:29,360
So, we'll try just to open we'll quickly
open

114
00:09:29,360 --> 00:09:35,200
the 'westeros baseline' tutorial
and the first thing we will need to check is

115
00:09:35,200 --> 00:09:38,480
that we are using the right Kernel which is

116
00:09:38,480 --> 00:09:42,640
associated to the right environment
so we will have to go and click on

117
00:09:42,640 --> 00:09:47,120
Kernel, Change Kernel
and we will see that there is a an

118
00:09:47,120 --> 00:09:55,920
asterisk (*) in the Conda environment that we are using.
In this case it's shown in the

119
00:09:55,920 --> 00:10:00,560
(ws1-env) so we know that
we are in the correct

120
00:10:00,560 --> 00:10:04,000
environment so we are using Jupyter
notebook in the correct

121
00:10:04,000 --> 00:10:07,680
environment. I'll quickly just move to
the first cell

122
00:10:07,680 --> 00:10:14,560
to check that we can import pandas
and ixmp correctly. So, after trying

123
00:10:14,560 --> 00:10:24,560
that the cell we run works, this is
a confirmation that MESSAGEix was installed successfully

124
00:10:24,560 --> 00:10:28,300
and, therefore, this is the end of our tutorial for today.

125
00:10:28,300 --> 00:10:33,680
Thank you very much for your attention.
