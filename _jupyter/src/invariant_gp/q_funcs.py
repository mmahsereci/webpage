import numpy as np
from typing import Callable

def Q_nfold_rotation(N: int, D: int):
    """n fold rotation"""
    if D == 2:
        delta_alpha = 2 * np.pi / N
        Q = np.zeros([N, D, D])
        for n in range(N):
            alpha = n * delta_alpha
            Qn = np.array([[np.cos(alpha), -np.sin(alpha)],
                           [np.sin(alpha), np.cos(alpha)]])
            Q[n, :, :] = Qn
        return Q
    else:
        raise ValueError('dimension not supported')


def Q_identities(N: int, D: int):
    """only identities"""
    Q = np.zeros([N, D, D])
    for n in range(N):
        Q[n, :, :] = np.eye(D)
    return Q


def Q_permutation(N: int, D: int):
    if D == 1:
        raise ValueError('D must be >1')
    elif D == 2:
        Q = np.zeros([2, D, D])
        Q[0, :, :] = np.eye(D)
        Q[1, :, :] = np.array([[0, 1], [1, 0]])
        return Q
    else:
        raise ValueError('dimension not supported')


def Q_y_and_x_flip(N: int, D: int):
    """flip each axis individually"""
    if D == 1:
        Q = np.zeros([2, D, D])
        Q[0, :, :] = np.eye(D)
        Q[1, :, :] = np.array([[-1]])
        return Q
    elif D == 2:
        Q = np.zeros([3, D, D])
        Q[0, :, :] = np.eye(D)
        Q[1, :, :] = np.array([[ 1, 0], [0, -1]])
        Q[2, :, :] = np.array([[-1, 0], [0,  1]])
        return Q
    else:
        raise ValueError('dimension not supported')


def Q_point_mirror_and_y_and_x_flip(N: int, D: int):
    """flip each axis individually + all at once"""
    if D == 1:
        Q = np.zeros([2, D, D])
        Q[0, :, :] = np.eye(D)
        Q[1, :, :] = np.array([[-1]])
        return Q
    elif D == 2:
        Q = np.zeros([4, D, D])
        Q[0, :, :] = np.eye(D)
        Q[1, :, :] = np.array([[-1, 0], [0, -1]])
        Q[2, :, :] = np.array([[ 1, 0], [0, -1]])
        Q[3, :, :] = np.array([[-1, 0], [0,  1]])
        return Q
    else:
        raise ValueError('dimension not supported')


def Q_point_mirror(N: int, D: int):
    """flip all axis"""
    if D == 1:
        Q = np.zeros([2, D, D])
        Q[0, :, :] = np.eye(D)
        Q[1, :, :] = np.array([[-1]])
        return Q
    elif D == 2:
        Q = np.zeros([2, D, D])
        Q[0, :, :] = np.eye(D)
        Q[1, :, :] = np.array([[-1, 0], [0, -1]])
        return Q
    else:
        raise ValueError('dimension not supported')


def Q_y_mirror(N: int, D: int):
    """flip one axis if 2D and 1 axis of 1D"""
    if D == 1:
        Q = np.zeros([2, D, D])
        Q[0, :, :] = np.eye(D)
        Q[1, :, :] = np.array([[-1]])
        return Q
    elif D == 2:
        Q = np.zeros([2, D, D])
        Q[0, :, :] = np.eye(D)
        Q[1, :, :] = np.array([[-1, 0], [0, 1]])
        return Q
    else:
        raise ValueError('dimension not supported')


def A_nfold(func: Callable, x: np.ndarray, N: int, D: int):
    """

    :param func: one of the Q functions
    :param x: generator of the set of invariant locations
    :param N: number of invariant locations
    :param D: dimensionality
    :return: invariant locations generted by x shape (N, D), invariant transformations, shape (num_invariances, D, D)
    """
    Q = func(N, D)
    N = Q.shape[0]
    A = np.zeros([N, D])
    for n in range(N):
        A[n, :] = Q[n, :, :] @ x
    return A, Q
