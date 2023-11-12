#!/usr/bin/env python3.12
# -*- coding: utf-8 -*-
"""Algoritmo di Gauss"""
from dataclasses import dataclass
from itertools import chain
from typing import Any, Iterable, Iterator, Literal, Self, cast, overload, override


def indices(len: int, i: int | slice | Iterable[int | slice]) -> tuple[int, ...]:
    if isinstance(i, int):
        return (i, )
    if isinstance(i, slice):
        return tuple(range(*i.indices(len)))
    return tuple(chain.from_iterable([indices(len, j) for j in i]))


type R = float
type C = complex

class Vector[K: (R, C)]:
    """Un vettore di dimensione {n}"""
    # --- Attributes ---
    __slots__ = ("__v", "orient")
    __v: list[K]
    orient: Literal["h", "v"]

    # --- Constructors ---

    def __init__(self, items: Iterable[K] = (), /, *, orient: Literal["h", "v"] = "h") -> None:
        self.__v = [*items]
        self.orient = orient

    @classmethod
    def fill(cls, k: K, len: int, /) -> Self:
        return cls([k]*len)

    @classmethod
    def null(cls, len: int, /) -> Self:
        """The null vector."""
        return cls.fill(0, len)

    def copy(self, /, *, orient: Literal["h", "v", None] = None) -> Self:
        return type(self)(self.__v).reorient(orient or self.orient)

    # --- Converters ---

    def as_complex(self: "Vector[R]", /) -> "Vector[C]":
        """Interpret this (real) vector as a complex vector."""
        return self  # type: ignore

    def mat(self, /) -> "Matrix[K]":
        """Convert this vector to a matrix."""
        match self.orient:
            case "h":
                return Matrix.from_rows([self])
            case "v":
                return Matrix.from_cols([self])

    # --- Misc mutating methods ---

    def reorient(self, orient: Literal["h", "v", None] = None, /) -> Self:
        if orient is not None:
            self.orient = orient
        return self

    # --- Iterators ----

    def i(self, /) -> Iterator[int]:
        yield from range(len(self))

    def __iter__(self, /) -> Iterator[K]:
        yield from self.__v

    # --- Standard functions ---

    def __bool__(self, /) -> bool:
        """self != Vector.null(len(self))"""
        return self.__v != [0]*len(self)

    def __len__(self, /) -> int:
        return len(self.__v)

    @override
    def __repr__(self, /) -> str:
        return "[" + "\t".join(map(repr, self.__v)) + "\t]"

    # --- Comparison operators ---

    @override
    def __eq__(self, other: Any, /) -> bool:
        if not isinstance(other, type(self)):
            return False
        return len(self) == len(other) and all([x == y for x, y in zip(self, other)])

    # --- Arithmetic operators ---

    def __add__(self, v: Self) -> Self:
        return type(self)([x1 + x2 for x1, x2 in zip(self.__v, v, strict=True)])

    def __mul__(self, k: K) -> Self:
        return type(self)([x*k for x in self.__v])

    def __neg__(self, /) -> Self:
        return self * cast(K, -1)  # type: ignore

    def __pos__(self, /) -> Self:
        return self

    def __sub__(self, m: Self, /) -> Self:
        return self + (-m)  # type: ignore

    def __truediv__(self, k: K, /) -> Self:
        return self * (1/k)  # type: ignore

    # --- Concatenation operators ----

    def __or__(self, v: K | Self, /) -> Self:
        """Concatenate `v` to the right."""
        if isinstance(v, Matrix):
            return NotImplemented
        return type(self)(self.__v + vec(v).__v)

    def __ror__(self, v: K | Self, /) -> Self:
        """Concatenate `v` to the left."""
        return type(self)(vec(v).__v + self.__v)

    # --- Item access / Slicing operators ---

    @overload
    def __getitem__(self, key: int, /) -> K: ...
    @overload
    def __getitem__(self, key: slice, /) -> Self: ...
    @overload
    def __getitem__(self, key: Iterable[int | slice], /) -> Self: ...
    def __getitem__(self, key: int | slice | Iterable[int | slice], /) -> Self | K:
        if isinstance(key, int):
            return self.__v[key]
        return type(self)([self.__v[i] for i in indices(len(self), key)], orient=self.orient)

    @overload
    def __setitem__(self, key: int, val: K, /) -> None: ...
    @overload
    def __setitem__(self, key: slice, val: Iterable[K], /) -> None: ...
    def __setitem__(self, key: int | slice, val: K | Iterable[K], /) -> None:
        for i, x in zip(indices(len(self), key), vec(val)):
            self.__v[i] = x


def vec[K: (R, C)](v: K | Vector[K] | Iterable[K], /) -> Vector[K]:
    """Convert to Vector[K]."""
    if isinstance(v, Vector):
        return v
    if isinstance(v, int | float | complex):
        return Vector((v,))
    return Vector(v)


@dataclass(slots=True, frozen=True)
class _MatrixWithoutOperator[K: (R, C)]:
    matrix: "Matrix[K]"

    def __getitem__(self, key: tuple[int | slice | Iterable[int | slice], int | slice | Iterable[int | slice]]) -> "Matrix[K]":
        i, j = key
        m = self.matrix.m
        n = self.matrix.n
        return self.matrix[
            # select all but the given indices
            tuple(set(range(m)) - set(indices(m, i))),
            tuple(set(range(n)) - set(indices(n, j))),
        ]


class Matrix[K: (R, C)]:
    """Una matrice {m}x{n}"""
    # --- Attributes & Properties ---
    data: list[list[K]]

    @property
    def m(self, /) -> int:
        return len(self.data)

    @property
    def n(self, /) -> int:
        if not self.data:
            return 0
        return len(self.data[0])

    @property
    def T(self, /) -> Self:
        return type(self)(zip(*self.data))

    # --- Constructors ---

    def __init__(self, rows: Iterable[Iterable[K]] = (), /) -> None:
        self.data = [[*r] for r in rows]

    @classmethod
    def from_rows(cls, rows: Iterable[Iterable[K]]) -> Self:
        return cls(rows)

    @classmethod
    def from_cols(cls, cols: Iterable[Iterable[K]]) -> Self:
        return cls(cols).T  # type: ignore

    @classmethod
    def fill(cls, k: K, m: int, n: int | None = None, /) -> Self:
        return cls([[k]*m]*(m if n is None else n))

    @classmethod
    def null(cls, m: int, n: int | None = None, /) -> Self:
        return cls.fill(0, m, n)

    @classmethod
    def Id(cls, n: int, /) -> Self:
        return cls([[0]*i+[1]+[0]*(n-i-1) for i in range(n)])  # type: ignore

    def copy(self, /) -> Self:
        return type(self)(self.data)

    # --- Converters ---

    def as_complex(self: "Matrix[R]", /) -> "Matrix[C]":
        """Interpret this (real) matrix as a complex matrix."""
        return self  # type: ignore

    # --- Misc mutating methods ---

    def swap_rows(self, r1: int, r2: int, /) -> None:
        """Swap two rows."""
        self.data[r1], self.data[r2] = self.data[r2], self.data[r1]

    def swap_cols(self, c1: int, c2: int, /) -> None:
        """Swap two columns."""
        self[:,c1], self[:,c2] = self[:,c2], self[:,c1]

    # --- Iterators ----

    def i(self, /) -> Iterator[int]:
        """Iterator on row indices."""
        yield from range(self.m)

    def j(self, /) -> Iterator[int]:
        """Iterator on column indices."""
        yield from range(self.n)

    def ij(self, /) -> Iterator[tuple[int, int]]:
        """Iterator on (row, col) indices."""
        for i in range(self.m):
            for j in range(self.n):
                yield i, j

    def rows(self, /) -> Iterator[Vector[K]]:
        return (Vector(row, orient="h") for row in self.data)

    def cols(self, /) -> Iterator[Vector[K]]:
        return (Vector(col, orient="v") for col in self.T.data)

    def __iter__(self, /) -> Iterator[Vector[K]]:
        return self.cols()

    # --- Standard functions ---

    def __bool__(self, /) -> bool:
        """self != Matrix.null(self.m, self.n)"""
        return self.data != [[0]*self.m]*self.n

    @override
    def __repr__(self, /) -> str:
        if self.m == 0:
            return "[]"
        if self.m == 1:
            return "[" + "\t".join(map(repr, self.data[0])) + "\t]"
        return "\n".join([
            "⎡" + "\t".join(map(repr, self.data[ 0])) + "\t⎤", *[
            "⎢" + "\t".join(map(repr, self.data[ i])) + "\t⎢" for i in range(1, self.m - 1)],
            "⎣" + "\t".join(map(repr, self.data[-1])) + "\t⎦",
        ])

    # --- Comparison operators ---

    @override
    def __eq__(self, other: Any, /) -> bool:
        if not isinstance(other, type(self)):
            return False
        return self.data == other.data

    # --- Arithmetic operators ---

    def __add__(self, m: Self, /) -> Self:
        return type(self)([[x1 + x2 for x1, x2 in zip(r1, r2, strict=True)] for r1, r2 in zip(self.data, m.data, strict=True)])

    def __mul__(self, k: K, /) -> Self:
        return type(self)([[x * k for x in row] for row in self.data])

    def __neg__(self, /) -> Self:
        return self * cast(K, -1)  # type: ignore

    def __pos__(self, /) -> Self:
        return self

    def __sub__(self, m: Self, /) -> Self:
        return self + (-m)  # type: ignore

    def __truediv__(self, k: K, /) -> Self:
        return self * (1/k)  # type: ignore

    def __matmul__(self, other: Self, /) -> Self:
        if other.m != (n := self.n):
            raise ValueError("Matrix multiplication between these two matrices is undefined.")
        new = type(self).null(self.m, other.n)
        for i, j in zip(self.i(), other.j()):
            new[i, j] = cast(K, sum(self[i,k] * other[k,i] for k in range(n)))
        return new

    # --- Concatenation operators ----

    def __or__(self, m: Self | Vector[K], /) -> Self:
        """Concatenate `m` to the right."""
        return type(self).from_cols([*self.cols(), *mat(m, vec="v").cols()])

    def __ror__(self, m: Self | Vector[K], /) -> Self:
        """Concatenate `m` to the left."""
        return type(self).from_cols([*mat(m, vec="v").cols(), *self.cols()])

    def __and__(self, x: Self | Vector[K], /) -> Self:
        """Concatenate `m` below."""
        return type(self).from_rows([*self.rows(), *mat(x, vec="h").rows()])

    def __rand__(self, x: Self | Vector[K], /) -> Self:
        """Concatenate `m` above."""
        return type(self).from_rows([*mat(x, vec="h").rows(), *self.rows()])

    # --- Item access / Slicing operators ---

    @overload
    def __getitem__(self, key: tuple[int, int], /) -> K: ...
    @overload
    def __getitem__(self, key: tuple[int, slice | Iterable[int | slice]], /) -> Vector[K]: ...
    @overload
    def __getitem__(self, key: tuple[slice | Iterable[int | slice], int], /) -> Vector[K]: ...
    @overload
    def __getitem__(self, key: tuple[slice | Iterable[int | slice], slice | Iterable[int | slice]], /) -> Self: ...
    def __getitem__(
        self,
        key: tuple[
            int | slice | Iterable[int | slice],  # i
            int | slice | Iterable[int | slice],  # j
        ],
    /) -> K | Vector[K] | Self:
        """self[*key]"""
        ki, kj = key
        if isinstance(ki, int):
            return Vector(self.data[ki], orient="h")[kj]  # returns either a vector or an item
        if isinstance(kj, int):
            return self.T[kj,ki].reorient("v")  # it's gonna be a vector
        # here we should return a matrix
        return type(self)([[self.data[i][j] for j in indices(self.n, kj)] for i in indices(self.m, ki)])

    @overload
    def __setitem__(self, key: tuple[int, int], value: K, /) -> None: ...
    @overload
    def __setitem__(self, key: tuple[slice, int], value: Iterable[K], /) -> None: ...
    @overload
    def __setitem__(self, key: tuple[int, slice], value: Iterable[K], /) -> None: ...
    @overload
    def __setitem__(self, key: tuple[slice, slice], value: Iterable[Iterable[K]], /) -> None: ...
    def __setitem__(
        self,
        key: tuple[int | slice, int | slice],
        value: K | Iterable[K] | Iterable[Iterable[K]],
    /) -> None:
        """self[*key] = value"""
        ki, kj = key
        for i, row in zip(indices(self.m, ki), mat(value)):
            for j, x in zip(indices(self.n, kj), row):
                self.data[i][j] = x

    @property
    def without(self, /) -> _MatrixWithoutOperator[K]:
        return _MatrixWithoutOperator(self)


def mat[K: (R, C)](
    m: K | Vector[K] | Iterable[K] | Matrix[K] | Iterable[Iterable[K]],
    /, *, vec: Literal["v", "h", None] = None
) -> Matrix[K]:
    if isinstance(m, Matrix):
        return m  # type: ignore
    if isinstance(m, Vector):
        return cast(Vector[K], m).copy(orient=vec).mat()
    if isinstance(m, int | float | complex):
        return Matrix(((m,),))
    it = [*m]
    if (not it) or isinstance(it[0], Iterable):
        return Matrix[K](it)  # type: ignore
    return Matrix.from_cols([it])  # type: ignore


def gauss[K: (R, C)](M: Matrix[K], /) -> Matrix[K]:
    # Se la matrice è nulla, abbiamo finito
    if not M:
        return M
    # Se la prima colonna è nulla, ignorala
    if not M[:,0]:
        return M[:,0] | gauss(M[:,1:])
    # Fintanto che il primo elemento è uno 0, scambia la prima riga con un'altra
    i = 1
    while not M[0,0]:
        M.swap_rows(0, i)
        i += 1
    # Ora il primo elemento è sicuramente un perno. Sottraiamo le volte necessarie ogni riga
    r = M[0,:]/M[0,0]
    for i in range(1, M.m):
        M[i,:] -= r * M[i,0]
    # Ora la prima colonna è tutta di zeri (a parte il perno): procedi senza prima riga e prima colonna
    return M[0,:] & (M[1:,0] | gauss(M[1:,1:]))


m1 = Matrix([
    [1,  0,  0, 0],
    [0,  1,  1, 5],
    [1, -1,  0, 0],
    [1,  1, -1, 2],
])
