Contact Us
----------
Join the KM3Pipe channel here: https://chat.km3net.de/channel/km3pipe


Filing Bugs or Feature Requests
-------------------------------

Please **always** create an issue when you encounter any bugs, problems or
need a new feature. Emails and private messages are not meant to communicate
such things!

Use the appropriate template and file a new issue here:
https://git.km3net.de/km3py/km3io/issues

You can browse all the issues here: https://git.km3net.de/km3py/km3io/-/issues

Please follow the instructions in the templates to provide all the
necessary information which will help other people to understand the
situation.

Improve km3io
---------------

Check out our KanBan board https://git.km3net.de/km3py/km3io/-/boards,
which shows all the open issues in three columns:

- *discussion*: The issues which are yet to be discussed (e.g. not clear how to proceed)
- *todo*: Issues tagged with this label are ready to be tackled
- *doing*: These issues are currently "work in progress". They can however be
  put tossed back to *todo* column at any time if the development is suspended.

Here is the recommended workflow if you want to improve km3io. This is a
standard procedure for collaborative software development, nothing exotic!

Feel free to contribute ;)

Make a Fork of km3io
~~~~~~~~~~~~~~~~~~~~~~

You create a fork (your full own copy of the
repository), change the code and when you are happy with the changes, you create
a merge request, so we can review, discuss and add your contribution.
Merge requests are automatically tested on our GitLab CI server and you
don't have to do anything special.

Go to http://git.km3net.de/km3py/km3io and click on "Fork".

After that, you will have a full copy of km3io with write access under an URL
like this: ``http://git.km3net.de/your_git_username/km3io``

Clone your Fork to your PC
~~~~~~~~~~~~~~~~~~~~~~~~~~

Get a local copy to work on (use the SSH address `git@git...`, not the HTTP one)::

    git clone git@git.km3net.de:your_git_username/km3io.git

Now you need to add a reference to the original repository, so you can sync your
own fork with the km3io repository::

    cd km3io
    git remote add upstream git@git.km3net.de:km3py/km3io.git


Keep your Fork Up to Date
~~~~~~~~~~~~~~~~~~~~~~~~~

To get the most recent commits (including all branches), run::

    git fetch upstream

This will download all the missing commits and branches which are now accessible
using the ``upstream/...`` prefix::

    $ git fetch upstream
    From git.km3net.de:km3py/km3io
     * [new branch]        gitlab_jenkins_ci_test -> upstream/gitlab_jenkins_ci_test
     * [new branch]        legacy                 -> upstream/legacy
     * [new branch]        master                 -> upstream/master


If you want to update for example your **own** ``master`` branch
to contain all the changes on the official ``master`` branch of km3io,
switch to it first with::

    git checkout master

and then merge the ``upstream/master`` into it::

    git merge upstream/master

Make sure to regularly ``git fetch upstream`` and merge changes to your own branches.

Push your changes to Gitlab regularly
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Make sure to keep your fork up to date on the GitLab server by pushing
all your commits regularly using::

    git push


Install in Developer Mode
~~~~~~~~~~~~~~~~~~~~~~~~~

km3io can be installed in ``dev-mode``, which means, it links itself to your
site-packages and you can edit the sources and test them without the need
to reinstall km3io all the time. Although you will need to restart any
``python``, ``ipython`` or ``jupyter``-notebook (only the kernel!) if you
imported km3io before  you made the changes.

Go to your own fork folder (as described above) and check out the branch you
want to work on::

    git checkout master  # the main development branch (should always be stable)
    make install-dev


Running the Test Suite
~~~~~~~~~~~~~~~~~~~~~~

Make sure to run the test suite first to see if everything is working
correctly::

    $ make test

This should give you a green bar, with an output like this::

    $ make test
    py.test --junitxml=./reports/junit.xml -o junit_suite_name=km3io tests
    =========================================== test session starts ===========================================
    platform linux -- Python 3.8.5, pytest-5.3.5, py-1.8.1, pluggy-0.13.1
    rootdir: /home/tgal/Dev/km3io
    plugins: flake8-1.0.4, pylint-0.15.0, cov-2.8.1
    collected 126 items

    tests/test_gseagen.py .....                                                                         [  3%]
    tests/test_km3io.py .                                                                               [  4%]
    tests/test_offline.py ................................s.............                                [ 41%]
    tests/test_online.py ...................................                                            [ 69%]
    tests/test_tools.py .......................................                                         [100%]

    ----------------------- generated xml file: /home/tgal/Dev/km3io/reports/junit.xml ------------------------
    =============================== 125 passed, 1 skipped, 4 warnings in 6.54s ================================


Run the tests every time you make changes to see if you broke anything! It usually
takes just a few seconds and ensures that you don't break existing code. It's
also an easy way to spot syntax errors ;)

You can also start a script which will watch for file changes and retrigger
a test suite run every time for you. It's a nice practice to have a terminal
open running this script to check your test results continuously::

    make test-loop

Time to Code
~~~~~~~~~~~~

We develop new features and fix bugs on separate branches and merge them
back to ``master`` when they are stable. Merge requests (see below) are also
pointing towards this branch.

If you are working on your own fork, you can stay on your own ``master`` branch
and create merge requests from that.

Code Style
~~~~~~~~~~

Make sure to run ``black`` over the code, which ensures that the code style
matches the one we love and respect. We have a tool which makes it easy::

    make black

Create a Merge Request (aka Pull Request)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Go to https://git.km3net.de/km3py/km3io/merge_requests/new and select
your source branch, which contains the changes you want to be included in km3io
and select the ``master`` branch as target branch.

That's it, the merge will be accepted if everything is OK ;)

If you want to join the km3io dev-team, let us know!:)
