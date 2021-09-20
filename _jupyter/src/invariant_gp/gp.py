# Warning: this code only works for certain Qs. It is wrong otherwise and very hacky.
# I do not reccomend using it otherwise.

import numpy as np

from typing import Tuple
from scipy.special import erf
from scipy.linalg import lapack, cholesky
from scipy.optimize import minimize

from emukit.quadrature.kernels import QuadratureKernel
from emukit.quadrature.kernels.quadrature_rbf import QuadratureRBFLebesgueMeasure
from emukit.quadrature.interfaces import IBaseGaussianProcess, IStandardKernel
from emukit.quadrature.kernels.integration_measures import IsotropicGaussianMeasure

# from utils.reporting import info

# Todo: remove later
import sys
import code
#code.interact(local=locals())


class RBF(IStandardKernel):
    """
    Interface for an RBF kernel
    Inherit from this class to wrap your standard rbf kernel.

    .. math::
        k(x, x') = \sigma^2 e^{-\frac{1}{2}\frac{\|x-x'\|^2}{\lambda^2}},

    where :math:`\sigma^2` is the `variance' property and :math:`\lambda` is the lengthscale property.
    """

    def __init__(self, lengthscale=1., variance=1.):
        self._lengthscale = lengthscale
        self._variance = variance

    @property
    def lengthscale(self) -> float:
        return self._lengthscale

    @property
    def variance(self) -> float:
        return self._variance

    @lengthscale.setter
    def lengthscale(self, value):
        self._lengthscale = value

    @variance.setter
    def variance(self, value):
        self._variance = value

    def K(self, x1: np.ndarray, x2: np.ndarray) -> np.ndarray:
        """
        The kernel k(x1, x2) evaluated at x1 and x2

        :param x1: first argument of the kernel
        :param x2: second argument of the kernel
        :returns: kernel evaluated at x1, x2
        """
        scaled_diff = (x1[None, :, :] - x2[:, None, :]) / self.lengthscale
        exp_term = np.exp(-0.5 * (scaled_diff ** 2).sum(axis=2).T)
        return self._variance * exp_term

    def dK_dtheta(self, x1: np.ndarray, x2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        returns a pair ( dk/dtheta_1(x1, x2), dk/dtheta_2(x1, x2) ),
          where lengthscale = exp(theta_1 / 2),
                variance = exp(theta_2)
        (the exponentiantion is done is order to make sure both variance and lengthscale are positive.)

        :param x1: first argument of the kernel
        :param x2: second argument of the kernel
        :returns: kernel gradients evaluated at x1, x2
        """
        K = self.K(x1, x2)
        dK_dtheta_1 = - K * np.log(K / self.variance)
        dK_dtheta_2 = K
        return dK_dtheta_1, dK_dtheta_2

    def dK_dx1(self, x1: np.ndarray, x2: np.ndarray) -> np.ndarray:
        """
        gradient of the kernel wrt x1 evaluated at pair x1, x2.
        We use the scaled squared distance defined as:

        ..math::

            r^2(x_1, x_2) = \sum_{d=1}^D (x_1^d - x_2^d)^2/\lambda^2

        :param x1: first argument of the kernel, shape = (n_points N, input_dim)
        :param x2: second argument of the kernel, shape = (n_points M, input_dim)
        :return: the gradient of the kernel wrt x1 evaluated at (x1, x2), shape (input_dim, N, M)
        """
        K = self.K(x1, x2)
        scaled_vector_diff = (x1.T[:, :, None] - x2.T[:, None, :]) / self.lengthscale ** 2
        dK_dx1 = - K[None, ...] * scaled_vector_diff
        return dK_dx1

    def dKdiag_dx(self, x: np.ndarray) -> np.ndarray:
        """
        gradient of the diagonal of the kernel (the variance) v(x):=k(x, x) evaluated at x

        :param x: argument of the kernel, shape (n_points M, input_dim)
        :return: the gradient of the diagonal of the kernel evaluated at x, shape (input_dim, M)
        """
        num_points, input_dim = x.shape
        return np.zeros((input_dim, num_points))


class InvariantQuadratureRBFLebesgueMeasure(QuadratureKernel):
    """
    Works only with QuadratureRBFLebesgueMeasure
    """

    def __init__(self, qkernel: QuadratureRBFLebesgueMeasure, Q: np.ndarray):
        super().__init__(kern=qkernel.kern,
                         integral_bounds=qkernel.integral_bounds.bounds,
                         measure=None)
        self.Q = Q
        self._QQ = self._get_QQ()
        self.num_invariances = Q.shape[0]
        self.qkern = qkernel

    @property
    def lengthscale(self):
        return self.qkern.kern.lengthscale

    @lengthscale.setter
    def lengthscale(self, value):
        self.qkern.kern.lengthscale = value

    @property
    def variance(self):
        return self.qkern.kern.variance

    @variance.setter
    def variance(self, value):
        self.qkern.kern.variance = value

    def _get_QQ(self) -> np.ndarray:
        """shape (num_invariances^2, D, D)"""
        N = self.Q.shape[0]
        return np.array([self.Q[i, :, :].T @ self.Q[j, :, :] for i in range(N) for j in range(N)])

    def K(self, x1: np.ndarray, x2: np.ndarray) -> np.ndarray:
        K = np.zeros([x1.shape[0], x2.shape[0]])
        x2_trans = self._QQ @ x2.T
        for ii in range(self._QQ.shape[0]):
            #sys.stdout.write("\r" + str(i) + ', ' + str(round(100 * i / self._QQ.shape[0], 2)))
            #sys.stdout.flush()
            K += self.qkern.K(x1, x2_trans[ii, :, :].T)
        return K

    def dK_dtheta(self, x1: np.ndarray, x2: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        returns a pair ( dk/dtheta_1(x1, x2), dk/dtheta_2(x1, x2) ),
          where lengthscale = exp(theta_1 / 2),
                variance = exp(theta_2)
        (the exponentiantion is done is order to make sure both variance and lengthscale are positive.)

        :param x1: first argument of the kernel
        :param x2: second argument of the kernel
        :returns: kernel gradients evaluated at x1, x2
        """
        dK_dtheta_1 = np.zeros([x1.shape[0], x2.shape[0]])
        dK_dtheta_2 = np.zeros([x1.shape[0], x2.shape[0]])

        x2_trans = self._QQ @ x2.T
        for ii in range(self._QQ.shape[0]):
            dK_dtheta_1_tmp, dK_dtheta_2_tmp = self.qkern.kern.dK_dtheta(x1, x2_trans[ii, :, :].T)
            dK_dtheta_1 += dK_dtheta_1_tmp
            dK_dtheta_2 += dK_dtheta_2_tmp

        return dK_dtheta_1, dK_dtheta_2

    def K_diag(self, x: np.ndarray) -> np.ndarray:
        diagK = np.zeros([x.shape[0], 1])
        for ii in range(self._QQ.shape[0]):
            diagK += self._K_diag_ij(x, self._QQ[ii, :, :])[0]
        return diagK

    def _K_diag_ij(self, x: np.ndarray, QQij: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        m = np.eye(x.shape[1]) - QQij
        diff = (x @ m.T) / (np.sqrt(2) * self.lengthscale)
        return self.variance * np.exp(-np.sum(diff ** 2, axis=1))[:, np.newaxis], m

    # the following methods are integrals of a quadrature kernel
    def qK(self, x2: np.ndarray) -> np.ndarray:
        """
        Kernel with the first component integrated out aka. kernel mean

        :param x2: remaining argument of the once integrated kernel, shape (n_points N, input_dim)
        :returns: kernel mean at location x2, shape (1, N)
        """
        qK = np.zeros([1, x2.shape[0]])
        x2_trans = self._QQ @ x2.T
        for ii in range(self._QQ.shape[0]):
            qK += self.qkern.qK(x2_trans[ii, :, :].T)
        return qK

    def Kq(self, x1: np.ndarray) -> np.ndarray:
        """
        Kernel with the second component integrated out aka. kernel mean

        :param x1: remaining argument of the once integrated kernel, shape (n_points N, input_dim)
        :returns: kernel mean at location x1, shape (N, 1)
        """
        return self.qK(x1).T

    def qKq(self) -> float:
        """
        Kernel integrated over both arguments x1 and x2

        :returns: double integrated kernel
        """
        # Todo: only works for QQ=diag
        qKq = 0
        for ii in range(self._QQ.shape[0]):
            qKq += self._qKq_ij(self._QQ[ii, :, :])
        return self.variance * qKq * self.lengthscale ** (2 * self._QQ.shape[1])

    def _z(self, a: np.ndarray, b: np.ndarray, QQ: np.ndarray) -> np.ndarray:
        """scaled vector diff with for a and QQ b"""
        return self.qkern._scaled_vector_diff(a, np.dot(QQ, b))

    def _qKq_ij(self, QQij: np.ndarray) -> np.ndarray:
        lower_bounds = self.integral_bounds.lower_bounds.squeeze()
        upper_bounds = self.integral_bounds.upper_bounds.squeeze()

        zbb = self._z(upper_bounds, upper_bounds, QQij)
        zaa = self._z(lower_bounds, lower_bounds, QQij)
        zab = self._z(lower_bounds, upper_bounds, QQij)
        zba = self._z(upper_bounds, lower_bounds, QQij)

        termbb = - np.sqrt(np.pi) * zbb * erf(zbb) - np.exp(-zbb ** 2)
        termaa = - np.sqrt(np.pi) * zaa * erf(zaa) - np.exp(-zaa ** 2)
        termab = + np.sqrt(np.pi) * zab * erf(zab) + np.exp(-zab ** 2)
        termba = + np.sqrt(np.pi) * zba * erf(zba) + np.exp(-zba ** 2)

        detQQij = np.linalg.det(QQij)

        qKqij = (termaa + termbb + termba + termab).prod() / detQQij
        return qKqij

    # the following methods are gradients of a quadrature kernel
    def dK_dx1(self, x1: np.ndarray, x2: np.ndarray) -> np.ndarray:
        """
        gradient of the kernel wrt x1 evaluated at pair x1, x2

        :param x1: first argument of the kernel, shape = (n_points N, input_dim)
        :param x2: second argument of the kernel, shape = (n_points M, input_dim)
        :return: the gradient of the kernel wrt x1 evaluated at (x1, x2), shape (input_dim, N, M)
        """
        N, D = x1.shape
        M = x2.shape[0]
        x2_trans = self._QQ @ x2.T

        grad = np.zeros([D, N, M])
        for ii in range(self._QQ.shape[0]):
            grad += self.qkern.dK_dx1(x1, x2_trans[ii, :, :].T)
        return grad

    def dK_dx2(self, x1: np.ndarray, x2: np.ndarray) -> np.ndarray:
        """
        gradient of the kernel wrt x2 evaluated at pair x1, x2
        Note that it is the transposed gradient wrt x1 evaluated at (x2, x1), i.e., the arguments are switched.

        :param x1: first argument of the kernel, shape = (n_points N, N, input_dim)
        :param x2: second argument of the kernel, shape = (n_points N, M, input_dim)
        :return: the gradient of the kernel wrt x2 evaluated at (x1, x2), shape (input_dim, N, M)
        """
        return np.transpose(self.dK_dx1(x1=x2, x2=x1), (0, 2, 1))

    def dKdiag_dx(self, x: np.ndarray) -> np.ndarray:
        """
        gradient of the diagonal of the kernel (the variance) v(x):=k(x, x) evaluated at x

        :param x: argument of the kernel, shape = (n_points M, input_dim)
        :return: the gradient of the diagonal of the kernel evaluated at x, shape (input_dim, M)
        """
        M, D = x.shape
        grad = np.zeros([D, M])
        for ii in range(self._QQ.shape[0]):
            diagK, m = self._K_diag_ij(x, self._QQ[ii, :, :])
            grad += - (diagK * (x @ (m.T @ m))).T
        return grad / self.lengthscale ** 2

    def dqK_dx(self, x2: np.ndarray) -> np.ndarray:
        """
        gradient of the kernel mean (integrated in first argument) evaluated at x2

        :param x2: N points at which to evaluate, shape = (n_points N, N, input_dim)
        :return: the gradient with shape (input_dim, N)
        """
        N, D = x2.shape
        grad = np.zeros([D, N])
        x2_trans = self._QQ @ x2.T
        for i in range(self.num_invariances):
            for j in range(self.num_invariances):
                grad += self._QQ[i, :, :].T @ self.qkern.dqK_dx(x2_trans[i, :, :].T)
                #grad += self.qkern.dqK_dx(x2_trans[i, :, :].T) # @ (self.Q[i, :, :].T @ self.Q[j, :, :])
        return grad

    def dKq_dx(self, x1: np.ndarray) -> np.ndarray:
        """
        gradient of the kernel mean (integrated in second argument) evaluated at x1
        :param x1: N points at which to evaluate, shape = (n_points N, N, input_dim)
        :return: the gradient with shape (N, input_dim)
        """
        return self.dqK_dx(x1).T


class InvariantQuadratureRBFIsoGaussMeasure(InvariantQuadratureRBFLebesgueMeasure):
    """
    Works only with IsotropicGaussianMeasure
    """

    def __init__(self, qkernel: QuadratureRBFLebesgueMeasure, measure: IsotropicGaussianMeasure, Q: np.ndarray):
#        super().__init__(kern=qkernel.kern, measure=None)
        super(InvariantQuadratureRBFLebesgueMeasure, self).__init__(kern=qkernel.kern, integral_bounds=None, measure=measure)
        self.Q = Q
        self._QQ = self._get_QQ()
        self.num_invariances = Q.shape[0]
        self.qkern = qkernel
        self.measure = measure
        self.input_dim = measure.num_dimensions

    def qKq(self) -> float:
        """
        Kernel integrated over both arguments x1 and x2

        :returns: double integrated kernel
        """
        # Todo: only works for QQ=diag
        qKq = 0

        factor = (2 * self.measure.variance / self.lengthscale ** 2 + 1) ** (self.input_dim / 2)

        for ii in range(self._QQ.shape[0]):
            qKq += self._qKq_ij(self._QQ[ii, :, :])
        return (self.variance / factor) * qKq

    def _z(self, a: np.ndarray, b: np.ndarray, QQ: np.ndarray, scale: float=None) -> np.ndarray:
        """scaled vector diff with for a and QQ b"""
        if scale is None:
            scale = self.lengthscale

        return self.qkern._scaled_vector_diff(a, np.dot(QQ, b), scale)

    def _qKq_ij(self, QQij: np.ndarray) -> np.ndarray:
        scale = np.sqrt(self.lengthscale ** 2 + 2 * self.measure.variance)
        scaled_vector_diff = self._z(self.measure.mean, self.measure.mean, QQij, scale)
#        scaled_vector_diff = self._scaled_vector_diff(QQij @ self.measure.mean, self.measure.mean, scale)

        qKqij = np.exp(- np.sum(scaled_vector_diff ** 2, axis=0))
        return qKqij


class InvariantBaseGaussianProcess(IBaseGaussianProcess):

    def __init__(self, kern: InvariantQuadratureRBFLebesgueMeasure, X, Y, noise_free: bool = True):
        """
        :param kern: a quadrature kernel
        :param noise_free: if False, the observation noise variance will be treated as a model parameter,
        if True it is set to 1e-10, defaults to True
        """
        super().__init__(kern=kern)
        #  Todo: hyper can not be adapted atm.
        # Todo: noise free not done
        self._observation_noise_variance = 1e-6
        self._X = X
        self._Y = Y
        self.G, self.lower_chol, self.woodbury_vector = self._get_posterior_quantities()

    @property
    def X(self) -> np.ndarray:
        return self._X

    @property
    def Y(self) -> np.ndarray:
        return self._Y

    @property
    def observation_noise_variance(self) -> float:
        """
        Gaussian observation noise variance
        :return: The noise variance from some external GP model
        """
        return self._observation_noise_variance

    @observation_noise_variance.setter
    def observation_noise_variance(self, value: float):
        if value < 0:
            raise ValueError('Observation noise variance cannot be negative. {} given.', value)
        self._observation_noise_variance = value

    def _get_posterior_quantities(self):
        G = self.kern.K(self.X, self.X) + self.observation_noise_variance * np.eye(self.X.shape[0])
        try:
            lower_chol = cholesky(G).T
        except:
            print('get_posterior quantoties')
            raise np.linalg.LinAlgError
            #code.interact(local=locals())
            #np.linalg.LinAlgError as e:
            #print('\nLengthscale: %s\nVariance: %s' % (self.kern.qkern.kern._lengthscale, self.kern.qkern.kern._variance))
            #info('\nLengthscale: %s\nVariance: %s' % (self.kern.qkern.kern._lengthscale, \
            #                                       self.kern.qkern.kern._variance))
            #info('X = %s' % self._X)
            #info('G = %s' % G)
            #raise e
        woodbury_vector = self.solve_linear(self.Y, lower_chol)
        return G, lower_chol, woodbury_vector

    def set_params(self, kern_lengthscale: float=None, kern_variance: float=None, noise_variance: float=None) -> None:
        if any([kern_lengthscale, kern_variance, noise_variance]) <=0:
            raise ValueError('paramters must be positive. {}', [kern_lengthscale, kern_variance, noise_variance])
        if kern_lengthscale is not None:
            self.kern.lengthscale = kern_lengthscale
        if kern_variance is not None:
            self.kern.variance = kern_variance
        if noise_variance is not None:
            self.observation_noise_variance = noise_variance
        self.G, self.lower_chol, self.woodbury_vector = self._get_posterior_quantities()

    def set_data(self, X: np.ndarray, Y: np.ndarray) -> None:
        """
        Sets training data in model
        :param X: New training features
        :param Y: New training outputs
        """
        self._X = X
        self._Y = Y
        self.G, self.lower_chol, self.woodbury_vector = self._get_posterior_quantities()

    def predict(self, X_pred: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predictive mean and covariance at the locations X_pred

        :param X_pred: points at which to predict, with shape (number of points, dimension)
        :return: Predictive mean, predictive variances shapes (num_points, 1) and (num_points, 1)
        """
        KxX = self.kern.K(X_pred, self.X)
        schur = np.reshape((KxX.T * self.solve_linear(KxX.T)).sum(axis=0), [X_pred.shape[0], 1])
        return KxX @ self.woodbury_vector, self.kern.K_diag(X_pred) - schur

    def predict_with_full_covariance(self, X_pred: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predictive mean and covariance at the locations X_pred

        :param X_pred: points at which to predict, with shape (num_points, input_dim)
        :return: Predictive mean, predictive full covariance shapes (num_points, 1) and (num_points, num_points)
        """
        KxX = self.kern.K(X_pred, self.X)
        schur = self._symmetrize(KxX @ self.solve_linear(KxX.T))
        return KxX @ self.woodbury_vector, self.kern.K(X_pred, X_pred) - schur

    def solve_linear(self, z: np.ndarray, lower_chol=None) -> np.ndarray:
        """
        Solve the linear system G(X, X)x=z for x.
        G(X, X) is the Gram matrix :math:`G(X, X) = K(X, X) + \sigma^2 I`, of shape (num_dat, num_dat) and z is a
        matrix of shape (num_dat, num_obs).

        :param z: a matrix of shape (num_dat, num_obs)
        :return: the solution to the linear system G(X, X)x = z, shape (num_dat, num_obs)
        """
        if lower_chol is None:
            lower_chol = self.lower_chol
        return lapack.dtrtrs(lower_chol.T, (lapack.dtrtrs(lower_chol, z, lower=1)[0]), lower=0)[0]

    def graminv_residual(self) -> np.ndarray:
        """
        The inverse Gram matrix multiplied with the mean-corrected data

        ..math::

            (K_{XX} + \sigma^2 I)^{-1} (Y - m(X))

        where the data is given by {X, Y} and m is the prior mean and sigma^2 the observation noise

        :return: the inverse Gram matrix multiplied with the mean-corrected data with shape: (number of datapoints, 1)
        """
        return self.woodbury_vector

    def _negative_log_marginal_likelihood_helpers(self):
        K = self.kern.K(self.X, self.X) + np.eye(self.X.shape[0]) * (self.observation_noise_variance + 1e-6)
        try:
            lower_chol = np.linalg.cholesky(K)
        except:
            print('_neg_helper')
            raise np.linalg.LinAlgError
            #code.interact(local=locals())
        log_det = 2. * np.sum(np.log(np.diag(lower_chol)))
        woodbury_vector = self.solve_linear(self.Y, lower_chol)  # G^{-1}Y
        return K, lower_chol, log_det, woodbury_vector

    def _negative_log_marginal_likelihood(self) -> float:
        K, lower_chol, log_det, woodbury_vector = self._negative_log_marginal_likelihood_helpers()
        log_2_pi = np.log(2 * np.pi)
        return 0.5 * self.Y.size * log_2_pi + 0.5 * log_det + 0.5 * np.sum(woodbury_vector * self.Y)

    def _negative_log_marginal_likelihood_grads(self) -> Tuple[float, float]:
        K, lower_chol, log_det, woodbury_vector = self._negative_log_marginal_likelihood_helpers()
        dK_dtheta_1, dK_dtheta_2 = self.kern.dK_dtheta(self.X, self.X)

        df_dtheta_1 = .5 * np.trace(- woodbury_vector @ woodbury_vector.T @ dK_dtheta_1 +
                                    self.solve_linear(dK_dtheta_1, lower_chol))
        df_dtheta_2 = .5 * np.trace(- woodbury_vector @ woodbury_vector.T @ dK_dtheta_2 +
                                    self.solve_linear(dK_dtheta_2, lower_chol))

        return df_dtheta_1, df_dtheta_2

    def _nlml_regularized(self, theta: np.ndarray, theta0: np.ndarray, gamma: float):
        """l2 regularization of lengthscale"""
        value = self._negative_log_marginal_likelihood()

        # lengthscale
        diff = theta[0] - theta0[0]
        return value + 0.5 * gamma * diff ** 2

    def _nlml_regularized_grad(self, theta: np.ndarray, theta0: np.ndarray, gamma: float):
        """l2 regularization of lengthscale"""
        grad_theta_1, grad_theta_2 = self._negative_log_marginal_likelihood_grads()

        # lengthscale
        grad_theta_1 += gamma * (theta[0] - theta0[0])
        return grad_theta_1, grad_theta_2

    def optimize(self) -> None:
        """ Optimize the hyperparameters of the GP """

        def theta_to_vars(theta):
            """convert opt params to lengthscale and variance"""
            theta1 = theta[0]
            theta2 = theta[1]
            if np.isnan(np.exp(theta1 / 2)):
                print('isnan 0')
                code.interact(local=locals())
            if np.isnan(np.exp(theta2)):
                print('isnan 1')
                code.interact(local=locals())
            return np.array([np.exp(theta1 / 2), np.exp(theta2)])

        def vars_to_theta(lamb, variance):
            """convert lengthscale and variance to opt params"""
            return np.array([2 * np.log(lamb), np.log(variance)])

        def get_lamb_zero(bounds):
            """lengthscale we regularize towards"""
            diff = np.array([b[1] - b[0] for b in bounds])
            lamb_max = diff.max()
            return lamb_max / 30.

        # regularization

        if self.kern.integral_bounds:
            bounds = self.kern.integral_bounds.bounds
        else:
            bounds = [(x, y) for (x, y) in zip(self.kern.measure.mean - 4 *self.kern.measure.variance ** (1/2),
                          self.kern.measure.mean + 4 *self.kern.measure.variance ** (1/2))]

        lamb0 = get_lamb_zero(bounds)

        var0 = 1  # Will be disregarded
        gamma = 0.1
        theta0 = vars_to_theta(lamb0, var0)

        def optimize_fcn_and_grad(theta):
            if theta[0]==0 or theta[1]==0:
                # print('opt fcn  0')
                theta = vars_to_theta(self.kern.lengthscale, self.kern.variance)
                # code.interact(local=locals())

            if np.isnan(theta[0]) or np.isinf(theta[0]):
                #print('opt fcn isnan 0')
                theta = vars_to_theta(self.kern.lengthscale, self.kern.variance)
                #code.interact(local=locals())

            if np.isnan(theta[1]) or np.isinf(theta[1]):
                print('opt fcn isnan 1')
                theta = vars_to_theta(self.kern.lengthscale, self.kern.variance)
                #code.interact(local=locals())
            lengthscale, variance = theta_to_vars(theta)
            self.set_params(kern_lengthscale=lengthscale,
                            kern_variance=variance)

            # Todo: switch regularizer here
            func = lambda theta: self._negative_log_marginal_likelihood()
            dfunc = lambda theta: self._negative_log_marginal_likelihood_grads()

            # Todo: this uses global vars theta0 and gamma (this is ugly)
            #func = lambda theta: self._nlml_regularized(theta, theta0, gamma)
            #dfunc = lambda theta: self._nlml_regularized_grad(theta, theta0, gamma)

            value = func(theta)
            theta_1_grad, theta_2_grad = dfunc(theta)
            grad = np.array([theta_1_grad, theta_2_grad])
            return value, grad

        def optimize_fcn(theta):
            return optimize_fcn_and_grad(theta)[0]

        def optimize_fcn_grads(theta):
            return optimize_fcn_and_grad(theta)[1]

        diff = np.array([b[1] - b[0] for b in bounds])
        ub_lengthscale = diff.max()
        lb_lengthscale = 10**-5
        lb_variance = 10**-5
        ub_variance = 1

        #lb_theta1, lb_theta2 = vars_to_theta(lb_lengthscale, lb_variance)
        #ub_theta1, ub_theta2 = vars_to_theta(ub_lengthscale, ub_variance)
        #opt_bounds = [(lb_theta1, ub_theta1), (lb_theta2, ub_theta2)]

        lengthscale_old = self.kern.lengthscale
        variance_old = self.kern.variance

        res = minimize(optimize_fcn,
                       vars_to_theta(self.kern.lengthscale, self.kern.variance),
                       jac=optimize_fcn_grads,
                       method='L-BFGS-B',
                       options={'maxcor': 3, 'disp': False})
                       #options={'maxcor': 3, 'maxiter': 100, 'disp': False})
                       #options={'gtol': 1e-6, 'disp': True},
                       #bounds=opt_bounds)

        lengthscale, variance = theta_to_vars(res.x)

        #print('lambi, vari:\t {},\t {}, \t {}'.format(lengthscale, variance, self._negative_log_marginal_likelihood()))
        #info('Optimal pars: \n\tlengthscale %s \n\tvariance %s' % (np.sqrt(lengthscale_sq), variance))

        self.set_params(kern_lengthscale=lengthscale, kern_variance=variance)

    @staticmethod
    def _symmetrize(A: np.ndarray) -> np.ndarray:
        return 0.5 * (A + A.T)
