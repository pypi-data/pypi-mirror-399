from ctypes import c_uint32
from .types import lst_dec_1d_t


class Vector:
    def __init__(self, rows: c_uint32, init_vec: lst_dec_1d_t | None = None):
        """
        initialize a rows count vector and init_vec list

        :param rows: vector rows count.
        :param init_vec: initial values for vector; or None as default for zero vector.
        """
        pass