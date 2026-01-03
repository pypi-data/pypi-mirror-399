from ctypes import c_uint32
from .types import lst_dec_2d_t

class Matrix:
    def __init__(self, rows: c_uint32, cols: c_uint32, init_mat: lst_dec_2d_t | None = None):
        """
        initialize rows*cols matrix with init_mat 2D list elements.

        :param rows: matrix rows count.
        :param cols: matrix cols count.
        :param init_mat: initial rows*cols 2D Decimal values for matrix elements; or None as default for zero matrix.
        """
        pass