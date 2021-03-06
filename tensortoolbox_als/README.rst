==============
Tensor Toolbox
==============

The Tensor Toolbox provides functionalities for the decomposition of tensors in tensor-train format [1] and spectral tensor-train format [2].

The toolbox provides the following tools:

* TT-svd

* TT-cross

* TT-dmrg

* TT-vectors

* TT-matrices

* Quatics TT-vectors/matrices (cross and dmrg)

* TT-integration

* Basic operations in TT format

* Multi-linear algebra in TT format (Steepest descent, CG and GMRES)

* STT-construction

* STT-projection/interpolation

* STT for single quantities and for fields

Status
======

`PyPi <https://pypi.python.org/pypi/TensorToolbox/>`_:

.. image:: http://southpacific.no-ip.org:8080/buildStatus/icon?job=pypi-TensorToolbox
   :target: http://southpacific.no-ip.org:8080/buildStatus/icon?job=pypi-TensorToolbox

`LaunchPad <https://launchpad.net/tensortoolbox>`_:

.. image:: http://southpacific.no-ip.org:8080/buildStatus/icon?job=TensorToolbox
   :target: http://southpacific.no-ip.org:8080/buildStatus/icon?job=TensorToolbox

`TestPyPi <https://testpypi.python.org/pypi/TensorToolbox/>`_:

.. image:: http://southpacific.no-ip.org:8080/buildStatus/icon?job=testpypi-TensorToolbox
   :target: http://southpacific.no-ip.org:8080/buildStatus/icon?job=testpypi-TensorToolbox

Installation
============

Make sure to have the latest version of pip installed:

   $ pip install --upgrade pip

Automatic installation
----------------------

You can first try the out-of-the-box installation using

   $ pip install TensorToolbox

If this doesn't work, proceed with the step by step installation

Step-by-step installation
-------------------------

For everything to go smooth, I suggest that you first install some dependencies separately: `numpy <https://pypi.python.org/pypi/numpy>`_, `scipy <https://pypi.python.org/pypi/scipy>`_, `matplotlib <https://pypi.python.org/pypi/matplotlib>`_ can be installed by:

    $ pip install numpy scipy matplotlib

If you need MPI support in the TensorToolbox, you need to have an MPI back-end installed on your machine and add the right path on the ``$LD_LIBRARY_PATH``, so that `mpi4py <https://pypi.python.org/pypi/mpi4py/>`_ can link to it. You should install `mpi4py <https://pypi.python.org/pypi/mpi4py/>`_ manually by

   $ pip install mpi4py

TensorToolbox now stores data in both `cPickle <https://docs.python.org/2/library/pickle.html>`_ files and `hd5 <http://www.hdfgroup.org/>`_ through the python package `h5py <http://www.h5py.org/>`_. You need then to have the necessary library package ``libhdf5`` and ``libhdf5-dev``, or similar on your machine. Click `here <http://docs.h5py.org/en/latest/build.html>`_ for more detailed information about the manual installation of `h5py <http://www.h5py.org/>`_.

Once the ``hdf5`` dependency is satisfied, we can proceed further. The package depends on `Cython <https://pypi.python.org/pypi/Cython/>`_ and requires to link to an mpi backend, and find the file `mpi.h`. In order to manually solve the dependencies do:

    $ pip install cython
    
    $ C_INCLUDE_PATH=<path-to-mpi.h-folder> pip install h5py

When everything is set, you can install the ``TensorToolbox`` using:

    $ pip install TensorToolbox

Some users might want to install the toolbox *without MPI* support. This is possible, but not through the ``pip`` command:

     $ pip download TensorToolbox

     $ cd /pth/to/downloaded/files

     $ tar xzf TensorToolbox-x.x.x.tar.gz

     $ cd TensorToolbox-x.x.x

     $ python setup.py install --without-mpi4py


Test Installation
=================
You can test whether all the functionalities work by running the unit tests.

    >>> import TensorToolbox
    >>> TensorToolbox.RunUnitTests(maxprocs=None)

where ``maxprocs`` defines the number of processors to be used if MPI support is activated. Be patient. The number of unit tests grows with the number of functionalities implemented in the software.


Examples
========
Examples can be found inside the package. To find them, download the source:

     $ pip download TensorToolbox
     
     $ cd /pth/to/downloaded/files
     
     $ tar xzf TensorToolbox-x.x.x.tar.gz
     
     $ cd TensorToolbox-x.x.x
     
     $ cd Examples


References
==========
[1] Oseledets, I. (2011). Tensor-train decomposition. SIAM Journal on Scientific Computing, 33(5), 2295–2317. Retrieved from http://epubs.siam.org/doi/pdf/10.1137/090752286

[2] Bigoni, D. and Marzouk, Y.M. and Engsig-Karup, A.P. (2014) Spectral tensor-train decomposition. (Submitted) ArXiv: http://arxiv.org/abs/1405.5713


Change Log
==========

1.0.2:
  * Fixed bug in TensorWrapper

1.0.1:
  * Fixed TensorWrapper unit tests

1.0.0:
  * Added support for Python3. Updated interface to SpectralToolbox 0.2.0.
