EUPS for PFS
------------

Overview
^^^^^^^^

PFS software products are all stored as git repositories under
``https://github.com/Subaru-PFS``.  They are installed and run as ``EUPS``
products on a local machine.

The purpose of ``EUPS`` is to maintain multiple versions of
products. If a given product depends on others, the version numbers of
all are saved together.

The tool to install PFS git products into an ``EUPS`` tree is
``pfsinstall``. Give it a list of products and git tags, and it will
install them in order, using the git tag as the EUPS tag::

  pfsinstall ics_config:1.4.0

After which you arrange for version 1.40 of ``ics_config`` to be used
with ``EUPS``\'s ``setup`` command::

  setup -v ics_config 1.4.0

Note that you had to specify the version. ``EUPS`` also maintains a
"current" version, which is the one which is used if no version is
specified. ``pfs_install -c `` sets the current version if you want::

  pfsinstall -c ics_config:1.4.0

after which ``setup -v ics_config`` will give you version 1.40.

Since it sets up basic rules, ``ics_config`` is a bit special. Among
other things it does not depend on any other products. But most PFS
products do. The actor library is in the ``tron_actorcore`` product,
for instance. You can chose which ``tron_actorcore`` library you build
and run against. ``pfsinstall`` installs each of the
``product:version`` on its command line in order, and uses the
following rules to select the other products:

#. if a product depends on one earlier on the command line, it will
   depend on the command line version::

     pfsinstall tron_actorcore:1.7.0 ics_mcsActor:1.4.0

#. if a product depends on one which was set up before ``pfsinstall``
   was invoked, it will depend on the setup version::

     setup tron_actorcore 1.6.4
     pfsinstall ics_mcsActor:1.4.0

#. if a product depends on one which has a ``current`` version, it will
   depend on the ``current`` version::

     pfsinstall ics_config:1.4.0

Common development practice
^^^^^^^^^^^^^^^^^^^^^^^^^^^

A common development pattern is for a programmer to be actively
working on live git versions of one or a few products, but to also use
installed versions of other products. Actor programmers probably want
to use the latest installed version of ``tron_actorcore``, for
instance.

One mechanism to get the right environment is to run ``setup -v -r .``
in the top-level of the git directory for your working product. This
configures the git version for your product and the current versions
of any dependencies. This is usually sufficient for programming on
actors.

If you need to override the version of a lower-level product you can
specify it and leave the others alone, with ``setup -j $PRODUCT
$VERSION``. 

A couple of products are almost always left as live git versions, and
should not (yet) be frozen with ``pfsinstall``. The ``ics_actorkeys``
product is the obvious one. For that, ``git clone ics_actorkeys``
in a development directory and declare that current to EUPS (cd into
the git directory, then ``eups declare -v -c -r . ics_actorkeys
live``. You can then ``git fetch; git rebase``, etc. to get new
versions.

``ics_config`` can also be such a product. Obviously all products get
tagged for production.

Common development standards
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Please use MAJOR.MINOR.REVISION git and EUPS tags. ``2.3.0``, for
instance. Always having all three parts is good. Change MAJOR when the
external API changes in an incompatible way, or you want to highlight
a large architectural change. Change REVISION for bug fixes. Make a git
tag with ``git tag -a 1.2.3`` then push it with ``git push -t``

Git branches should be handled roughly as in the `LSST branching model
<https://developer.lsst.io/processes/workflow.html#git-branching>`_
though we are much less formal about reviews and CI. The branch naming
and merging, and the commit best-practices sections are useful. 

Basic EUPS commands
^^^^^^^^^^^^^^^^^^^

``eups list``

    List all eups products and versions.

``eups list tron_actorcore``

    List all versions of a single product.

``eups list -s``

    List the currently set up versions.

``eups list -c``

    List the "current" versions

``setup -v $PRODUCT``

    Sets up the "current" version of a product.

``setup -v -r .``

    Setup the product whose top-level directory you are in.

``unsetup $PRODUCT``

    Remove whatever changes setting up ``$PRODUCT`` made to the environment.

``eups declare -c $PRODUCT $VERSION``

    Declare that a given version of a product is the "current" version.

``eups declare [-c] -r $DIR $PRODUCT $VERSION``

    Declare that the given directory contains the given version of the
    given product. Note several things:

    * ``-r .`` is a common idiom.

    * The ``$DIR`` must contain a ``ups`` directory and a
      ``ups/$PRODUCT.table`` table file.

    * In this case, version dependencies on other products are not
      frozen.

Basic EUPS internals
^^^^^^^^^^^^^^^^^^^^

For a product named ``$PRODUCT`` to be an ``EUPS`` product, the top
level directory must contain a ``ups`` directory, and that must
contain a ``$PRODUCT.table`` "table" file.

The table file contains instructions for modifying the process
environment and for specifying dependencies on other products. The
most common are::

  # Prepend our bin/ directory to the PATH environment variable
  pathPrepend(PATH, ${PRODUCT_DIR}/bin)

  # Prepend our python/ directory to the python search path
  pathPrepend(PYTHONPATH, ${PRODUCT_DIR}/python)

  # Set an environment variable
  envSet(MYENVVAR, 'some value')

and for dependencies::

  setupRequired(tron_actorcore)
  setupOptional(some_product_name)

When ``pfsinstall`` runs, it installs the product into a directory
inside the $EUPS_PATH directory tree. For example,``ics_xcuActor
1.7.2`` would be put into ``$EUPS_PATH/Linux64/ics_xcuActor/1.7.2/``.
It also adds the versions of the dependencies to the table file; the
installed version from the last example would be written as::

  setupRequired(tron_actorcore 1.7.0)

This is how versions are permanently frozen: the executables are
copied into an internal tree and the version numbers are explicitly
written.
