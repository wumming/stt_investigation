import numpy as np
import matplotlib.pyplot as plt
import scipy.linalg as la

import tensorly as tl
import itertools

import TensorToolbox.multilinalg as mla
import TensorToolbox as DT
from TensorToolbox.core import STT
import SpectralToolbox
import progressbar

class PICGaussian:
    def __init__(self, covariance_type, hp, y_noise):
        self.hp = hp
        self.sigma_n = y_noise
        self.covariance_type = covariance_type

        # Related to PITC blocking
        self.centers = None
        self.clusterStarts = None
        self.clusterLengths = None

        # Related to GP training
        self.Km = None

        if covariance_type == 'RBF':
            # Hyperparameters:
            # hp[0]: sigma_rbf (value in covariance)
            self.covariance = lambda x, y: np.exp(-0.5 / (hp[0] ** 2) * la.norm(x - y) ** 2)

    def getClosestBlockIdx(self, x):
        '''
        Returns the index of the block that this point belongs to.

        :param x:
        :return:
        '''
        # Assuming there is at least 1 center
        cc = 0
        for j in range(len(self.centers)):
            if (la.norm(self.centers[j] - x) < la.norm(self.centers[cc] - x)):
                cc = j

        return cc

    def getBlocks(self, X, y, numBlocks):
        '''
        Place the input points into groups.

        :param X: The input points
        :return: Blocked off points
        '''

        # Currently, select the blocks randomly. Will implement FPC in the future
        self.centers = X[np.random.choice(np.array(range(len(X))), replace=False, size=numBlocks)]
        self.clusterLengths = np.zeros(len(self.centers), dtype=int)

        clusterPoints = []
        clusterTargets = []
        for i in range(len(self.centers)):
            clusterPoints.append([])
            clusterTargets.append([])

        # Now rearrange the data to correspond with the blocks
        for i in range(len(X)):
            cc = self.getClosestBlockIdx(X[i])

            clusterPoints[cc].append(X[i])
            clusterTargets[cc].append(y[i])
            self.clusterLengths[cc] += 1

        X = np.concatenate(clusterPoints)
        y = np.concatenate(clusterTargets)
        self.clusterStarts = np.concatenate(([0], np.cumsum(self.clusterLengths, dtype=int)))

        return X, y

    def computePIC(self, X, y, induced):
        '''
        Use Woodbury's matrix inversion lemma to compute the low-rank inverse, implementing PITC
        for use in PIC

        :param X: Input x points
        :param y: Targets
        :param induced: Inducing input locations

        :return: p, defined as in the paper
        '''
        self.X = X
        self.induced = induced
        self.Knm = np.matrix(np.zeros((len(X), len(induced))))
        self.Km = np.matrix(np.zeros((len(induced), len(induced))))

        for i in range(len(self.Km)):
            for j in range(len(self.Km)):
                self.Km[i, j] = self.covariance(induced[i], induced[j])

        self.Kminv = la.inv(self.Km)

        for i in range(len(X)):
            for j in range(len(induced)):
                self.Knm[i, j] = self.covariance(X[i], induced[j])

        blocks = [np.zeros((self.clusterLengths[i], self.clusterLengths[i])) for i in range(len(self.clusterLengths))]

        # Compute the blocks

        for i in range(len(self.clusterStarts)-1):
            # Compute the block produced by Kn
            for j in range(self.clusterStarts[i], self.clusterStarts[i+1]):
                for k in range(self.clusterStarts[i], self.clusterStarts[i + 1]):
                    blocks[i][j - self.clusterStarts[i], k - self.clusterStarts[i]] = self.covariance(X[j], X[k])

            # Subtract off the block Qn
            partial = self.Knm[self.clusterStarts[i]: self.clusterStarts[i + 1]]
            blocks[i] -= np.matmul(np.matmul(partial, self.Kminv), partial.transpose())

            # Add the diagonal y-noise term
            for j in range(self.clusterLengths[i]):
                blocks[i][j, j] += self.sigma_n ** 2

            # Invert each of the blocks to get A^{-1}... hooray
            blocks[i] = la.inv(blocks[i])

        # Now perform the inversion using Woodbury's Lemma to compute the vector p
        Ainv = la.block_diag(*blocks)

        self.pvec = (Ainv - Ainv * self.Knm * la.inv(self.Km + self.Knm.transpose() * Ainv * self.Knm) * self.Knm.transpose() * Ainv) * y
        self.pvec_augmented = self.Kminv * self.Knm.transpose() * self.pvec

        self.wBlocks = []
        self.wM = np.zeros((len(self.induced), 1))

        for i in range(len(self.centers)):
            Kmb = np.matrix(np.zeros(((len(induced), self.clusterLengths[i]))))

            for j in range(len(induced)):
                for k in range(self.clusterLengths[i]):
                    Kmb[j, k] = self.covariance(induced[j], X[self.clusterStarts[i] + k])

            wB = self.Kminv * Kmb * self.pvec[self.clusterStarts[i] : self.clusterStarts[i+1]]
            self.wBlocks.append(wB)
            self.wM += wB

    def train(self, X, y, induced):
        # For now, just use the cluster points as the induced inputs...
        print("Computing PITC approximation...")
        self.computePIC(X, y, induced)

    def predict_pitc(self, X):
        kst = np.zeros((len(X), len(self.Km)))

        for i in range(len(X)):
            for j in range(len(self.Km)):
                kst[i, j] = self.covariance(X[i], self.induced[j])

        return kst * self.pvec_augmented

    def predict_pic(self, X):
        predictions = np.zeros(len(X))
        variances = np.zeros(len(X))

        kstM = np.matrix(np.zeros((1, len(self.induced))))

        for i in range(len(X)):
            # Compute covariances with the inducing inputs
            for j in range(len(self.Km)):
                kstM[0, j] = self.covariance(X[i], self.induced[j])

            # Find the closest block
            cc = self.getClosestBlockIdx(X[i])
            kstB = np.matrix(np.zeros((1, self.clusterLengths[cc])))

            # Compute covariances with the points in the block
            for j in range(self.clusterLengths[cc]):
                kstB[0, j] = self.covariance(X[i], self.X[self.clusterStarts[cc] + j])

            # predictions[i] = self.wM - self.wBlocks[cc]
            predictions[i] = kstM * (self.wM - self.wBlocks[cc]) + kstB * self.pvec[self.clusterStarts[cc] : self.clusterStarts[cc+1]]

        return predictions


def test_univariate():
    gp = PICGaussian('RBF', [2.0], 0.2)

    X = np.array([[i * 0.1] for i in range(0, 150)])
    y = np.array(np.sin(X.transpose()) + np.random.normal(0, scale=0.15, size=len(X)).transpose())[0]

    blockedX, blockedY = gp.getBlocks(X, y, 20)
    blockedY = np.matrix(blockedY).transpose()

    induced_inputs = blockedX[np.random.choice(np.array(range(len(blockedX))), replace=False, size=15)]

    colors = []
    for i in range(len(gp.clusterStarts)-1):
        for j in range(gp.clusterLengths[i]):
            colors.append(i)

    gp.train(blockedX, blockedY, induced_inputs)

    X_pred = np.array([i * 0.01 for i in range(-50, 1500)])
    predictions = gp.predict_pic(X_pred)

    plt.scatter(X_pred, predictions, s=0.02)
    plt.scatter(X, y, c=colors)
    plt.show()

if __name__ == '__main__':
    test_univariate()