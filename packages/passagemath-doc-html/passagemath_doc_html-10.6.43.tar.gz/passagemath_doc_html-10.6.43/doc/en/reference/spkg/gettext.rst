.. _spkg_gettext:

gettext: Internationalization/localization infrastructure
=========================================================

Description
-----------

The GNU gettext utilities provide a framework to produce multi-lingual messages.


License
-------

GPLV2+


Type
----

standard


Dependencies
------------



Version Information
-------------------

package-version.txt::

    0.26

Installation commands
---------------------

.. tab:: Sage distribution:

   .. CODE-BLOCK:: bash

       $ sage -i gettext

.. tab:: mingw-w64:

   .. CODE-BLOCK:: bash

       $ sudo pacman -S ${MINGW_PACKAGE_PREFIX}-gettext


If the system package is installed, ``./configure`` will check if it can be used.
