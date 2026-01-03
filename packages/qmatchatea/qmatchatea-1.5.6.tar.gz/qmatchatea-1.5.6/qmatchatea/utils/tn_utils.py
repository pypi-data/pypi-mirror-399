# This code is part of qmatchatea.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE.txt file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
I/O functions for tensors and mps (list of tensors).
Furthermore, the class :py:class:`QCOperators` for handling operators is provided.

Functions and classes
---------------------

"""

# pylint: disable=too-many-branches

import numpy as np
from qtealeaves import read_tensor
from qtealeaves.operators import TNOperators

__all__ = ["write_tensor", "write_mps", "read_mps", "QCOperators"]


def write_tensor(tensor, dest, cmplx=True, sparse=False):
    """
    Write a tensor stored in a numpy matrix to a file. Conversion
    to column major is taken care of here.

    **Arguments**

    tensor : np.ndarray
        Tensor to be written to the file.

    dest : str, or filehandle
        If string, file will be created or overwritten. If filehandle,
        then data will be written there.

    sparse: bool
        If True write the tensor in a sparse format, i.e. each row is written as
        idx elem
        where idx is the position of the element elem in the tensor vector
    """
    if isinstance(dest, str):
        fh = open(dest, "w+")
    elif hasattr(dest, "write"):
        fh = dest
    else:
        raise TypeError("`dest` for `write_tensor` neither str nor writeable.")

    # Number of links
    fh.write("%d \n" % (len(tensor.shape)))

    # Dimensions of links
    dl = " ".join(list(map(str, tensor.shape)))
    fh.write(dl + "\n")

    # Now we need to transpose
    tensor_colmajor = np.reshape(tensor, -1, order="F")
    if sparse:
        nonzero = np.nonzero(tensor_colmajor)[0]  # index of nonzero element
        tensor_colmajor = tensor_colmajor[nonzero]
        nonzero += 1  # from python to fortran indexing
        fh.write(f"{len(nonzero)} \n")

    for ii, elem in enumerate(tensor_colmajor):
        if cmplx:
            if sparse:
                fh.write(
                    "%d (%30.15E, %30.15E)\n"
                    % (nonzero[ii], np.real(elem), np.imag(elem))
                )
            else:
                fh.write("(%30.15E, %30.15E)\n" % (np.real(elem), np.imag(elem)))
        else:
            if sparse:
                fh.write("%d %30.15E\n" % (nonzero[ii], np.real(elem)))
            else:
                fh.write("%30.15E\n" % (np.real(elem)))
            imag_part = np.imag(elem)
            if np.abs(imag_part) > 1e-14:
                raise TypeError("Writing complex valued tensor as real valued tensor.")

    if isinstance(dest, str):
        fh.close()

    return


def read_mps(filename, cmplx=True):
    """Read an MPS from a given file.
    Reads in column-major order but the output is in row-major.

    This function was used to exchange the MPS with the Fortran
    backend (thus the different ordering), which is now deprecated.

    Parameters
    ----------
    filename: str
            PATH to the file
    cmplx: bool, optional
            If True the MPS is complex, real otherwise. Default to True

    Returns
    -------
    mps: list
            list of np.array in row-major order
    """
    mps = []
    with open(filename, "r") as fh:
        num_sites = int(fh.readline())
        for _ in range(num_sites):
            tens = read_tensor(fh, cmplx=cmplx)
            mps.append(tens)

    return mps


def write_mps(filename, mps, cmplx=True):
    """Write an MPS to file.
    The tensor is written in Fortran-like indexing, i.e. the MPS tensors
    will be converted from row-major into column-major order.

    This function was used to exchange the MPS with the Fortran
    backend (thus the different ordering), which is now deprecated.

    Parameters
    ----------
    filename: str
            PATH to the file
    mps: list
            List of tensors forming the mps
    cmplx: bool, optional
            If True the MPS is complex, real otherwise. Default to True

    Returns
    -------
    None
    """
    with open(filename, "w") as fh:
        fh.write(str(len(mps)) + " \n")
        for tens in mps:
            write_tensor(tens, fh, cmplx=cmplx)

    return None


class QCOperators(TNOperators):
    """
    Class to store and save to file operators. To add an operator to the list use
    self['op_name'] = op_tensor.

    It starts with the pauli operators already defined, with keywords "X","Y","Z"
    """

    def __init__(self):
        TNOperators.__init__(self)
        pauli_matrices = {
            "Z": np.array([[1, 0], [0, -1]]),
            "X": np.array([[0, 1], [1, 0]]),
            "Y": np.array([[0, -1j], [1j, 0]]),
            "I": np.array([[1, 0], [0, 1]]),
        }
        for key, val in pauli_matrices.items():
            self[key] = val
