.. highlight:: shell

============
Contributing
============

Contributions are welcome, and they are greatly appreciated! Every little bit
helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

For all types of contributions, it is favorable to use GitHub and its features
to keep communication in a central place and for everyone to see. However,
you are always welcome to contact timskovjacobsen@gmail.com for inquiries
about the project.

Report Bugs
-----------

Report bugs at https://github.com/timskovjacobsen/conctools/issues.

If you are reporting a bug, please include:

* Your operating system name and version.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
--------

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help
wanted" is open to whoever wants to implement it.

Implement Features
------------------

Look through the GitHub issues for features. Anything tagged with
"enhancement" and "help wanted" is open to whoever wants
to implement it.

Write Documentation
-------------------

``conctools`` could always use more documentation, whether as part of the
official ``conctools`` docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
---------------

The best way to send feedback is to file an issue at https://github.com/timskovjacobsen/conctools/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* Remember that this is a volunteer-driven project and that contributions
  are welcome :)

Help Getting Started
--------------------

If you are new to Git, GitHub or coding in general, look for issues tagged
with "good first issue". The tag denotes that particular issue to belong
to the easy difficulty level so implement.

Get Started!
------------

Ready to contribute? Here's how to set up ``conctools`` for local development.

1. Fork the ``conctools`` repo on GitHub.
2. Clone your fork locally::

    git clone git@github.com:your_name_here/conctools.git

3. Install your local copy into a *virtualenv*. Assuming you have *virtualenvwrapper* installed, this is how you set up your fork for local development::

    mkvirtualenv conctools
    cd conctools/
    python setup.py develop

4. Create a branch for local development::

    git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and
   the tests, including testing other Python versions with tox::

    flake8 conctools tests
    python setup.py test or pytest
    tox

   To get flake8 and tox, just pip install them into your virtualenv.

6. Commit your changes and push your branch to GitHub::

    git add .
    git commit -m "Your detailed description of your changes."
    git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring, and add the
   feature to the list in README.rst.
3. The pull request should work for Python 3.5, 3.6, 3.7 and 3.8, and PyPy.
   Check https://travis-ci.org/timskovjacobsen/conctools/pull_requests 
   and make sure that the tests pass for all supported Python versions.

.. |Anchor| replace:: How to Contribute to an Open Source Project on GitHub
.. _Anchor: https://egghead.io/series/how-to-contribute-to-an-open-source-project-on-github

You can learn how to make your first Pull Request from |Anchor|_


Tips
----

To run a subset of tests::

 pytest tests.test_conctools


Deploying
---------

A reminder for the maintainers on how to deploy.
Make sure all your changes are committed (including an entry in HISTORY.rst).
Then run::

 bump2version patch # possible: major / minor / patch
 git push
 git push --tags

Travis will then deploy to PyPI if tests pass.
