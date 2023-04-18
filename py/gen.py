#!/usr/bin/env python3

from sympy import *


class CliffordAlgebra:
    e = Symbol("e")
    e_1 = Symbol("e_1")
    e_2 = Symbol("e_2")
    e_3 = Symbol("e_3")
    e_12 = Symbol("e_12")
    e_23 = Symbol("e_23")
    e_31 = Symbol("e_31")
    e_321 = Symbol("e_321")

    canonical_formes = {
        (1, 2, 3): (3, 2, 1),
        (1, 2): (1, 2),
        (1, 3): (3, 1),
        (2, 3): (2, 3),
        (1,): (1,),
        (2,): (2,),
        (3,): (3,),
        (): ()
    }

    canonical_symbols = {
        "e_321": e_321,
        "e_12": e_12,
        "e_31": e_31,
        "e_23": e_23,
        "e_1": e_1,
        "e_2": e_2,
        "e_3": e_3,
        "e": e
    }


class ElepticalArray:
    def __init__(self, indexes, negative=False):
        self.indexes = indexes
        self.negative = negative

    def __str__(self):
        return "ElepticalArray({},{})".format(self.indexes, "negative" if self.negative else "positive")

    def reorder_with_last(self, index, drop=False):
        return self.reorder_with_moving(index, len(self.indexes) - 1, drop)

    def reorder_with_first(self, index, drop=False):
        return self.reorder_with_moving(index, 0, drop)

    def reorder_with_moving(self, index, position, drop=False):
        if not index in self.indexes:
            raise Exception("Index not found")

        new_indexes = self.indexes.copy()
        new_indexes.remove(index)
        if not drop:
            new_indexes.insert(position, index)
        need_to_negate = (self.indexes.index(index) - position) % 2 == 1

        return ElepticalArray(new_indexes, not self.negative if need_to_negate else self.negative)

    def copy(self):
        return ElepticalArray(self.indexes.copy(), self.negative)

    def is_sorted(self):
        for i in range(len(self.indexes) - 1):
            if self.indexes[i] > self.indexes[i + 1]:
                return False
        return True

    def sorted(self):
        return self.sorted_as_template(sorted(self.indexes))

    def sorted_as_template(self, template):
        c = self.copy()
        sorted_indexes = template
        for idx in range(len(sorted_indexes)):
            c = c.reorder_with_moving(sorted_indexes[idx], idx)
        return c


class CliffordMulter:
    def __init__(self, eleptical_ones=[], dual_ones=[], negative=False):
        self.dual_ones = dual_ones
        self.eleptical_ones = ElepticalArray(eleptical_ones, negative)

    def commutate(self, other):
        for x in self.dual_ones:
            for y in other.dual_ones:
                return CliffordMulter()

        dual_ones = self.dual_ones + other.dual_ones

        indexes_common = set(self.eleptical_ones.indexes).intersection(
            set(other.eleptical_ones.indexes))

        a_eleptical = self.eleptical_ones
        b_eleptical = other.eleptical_ones

        for x in indexes_common:
            a_eleptical = a_eleptical.reorder_with_last(x, drop=True)
            b_eleptical = b_eleptical.reorder_with_first(x, drop=True)

        eleptical_ones = a_eleptical.indexes + b_eleptical.indexes
        negative = a_eleptical.negative != b_eleptical.negative

        eleptical_array = ElepticalArray(eleptical_ones, negative)
        eleptical_array = eleptical_array.sorted()
        eleptical_array_as_tuple = tuple(eleptical_array.indexes)
        canonical_form = CliffordAlgebra.canonical_formes[eleptical_array_as_tuple]
        eleptical_array = eleptical_array.sorted_as_template(canonical_form)

        return CliffordMulter(eleptical_array.indexes, dual_ones, eleptical_array.negative)

    def __str__(self):
        return "CliffordMulter(elep:{}, dual:{})".format(self.eleptical_ones, self.dual_ones)

    def symbol_name(self):
        if len(self.dual_ones) == 0 and len(self.eleptical_ones.indexes) == 0:
            return "e"

        es = "".join(f"{i}" for i in self.eleptical_ones.indexes)
        base = "e_"
        ds = "".join(f"{i}" for i in self.dual_ones)

        return base + ds + es

    def symbol(self):
        a = self.symbol_name()
        sign = -1 if self.eleptical_ones.negative else +1
        return CliffordAlgebra.canonical_symbols[f"{a}"] * sign


class CliffordGeometrySymbol(Symbol):
    def __new__(cls, name, *args, **kwargs):
        return super().__new__(cls, name, commutative=False)

    def __init__(self, name, ellipse, dual, negative=False):
        super().__init__()
        self.multer = CliffordMulter(ellipse, dual, negative)

    @staticmethod
    def from_multer(multer):
        name = multer.symbol_name()
        return CliffordGeometrySymbol(name, multer.eleptical_ones.indexes, multer.dual_ones, multer.eleptical_ones.negative)

    def __mul__(self, other):
        if isinstance(other, CliffordGeometrySymbol):
            multer = self.multer.commutate(other.multer)
            return CliffordGeometrySymbol.from_multer(multer)
        else:
            return super().__mul__(other)

    def __pow__(self, power, modulo=None):
        if power == 2:
            return self * self
        else:
            raise Exception("Not implemented")


alphabet = [
    CliffordMulter([]),
    CliffordMulter([1]),
    CliffordMulter([2]),
    CliffordMulter([3]),
    CliffordMulter([2, 3]),
    CliffordMulter([3, 1]),
    CliffordMulter([1, 2]),
    CliffordMulter([3, 2, 1])
]

for a in alphabet:
    print(a.symbol_name())
