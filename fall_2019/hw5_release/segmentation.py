"""
CS131 - Computer Vision: Foundations and Applications
Assignment 5
Author: Donsuk Lee (donlee90@stanford.edu)
Date created: 09/2017
Last modified: 09/25/2018
Python Version: 3.5+
"""

import numpy as np
import random
from scipy.spatial.distance import squareform, pdist
from skimage.util import img_as_float

# Clustering Methods


def kmeans(features, k, num_iters=100):
    """ Use kmeans algorithm to group features into k clusters.

    K-Means algorithm can be broken down into following steps:
        1. Randomly initialize cluster centers
        2. Assign each point to the closest center
        3. Compute new center of each cluster
        4. Stop if cluster assignments did not change
        5. Go to step 2

    Args:
        features - Array of N features vectors. Each row represents a feature
            vector.
        k - Number of clusters to form.
        num_iters - Maximum number of iterations the algorithm will run.

    Returns:
        assignments - Array representing cluster assignment of each point.
            (e.g. i-th point is assigned to cluster assignments[i])
    """

    N, D = features.shape

    assert N >= k, 'Number of clusters cannot be greater than number of points'

    # Randomly initalize cluster centers
    idxs = np.random.choice(N, size=k, replace=False)
    centers = features[idxs]
    assignments = np.zeros(N, dtype=np.uint32)

    for n in range(num_iters):
        # YOUR CODE HERE
        origin_assignments = np.copy(assignments)
        for i in range(N):
            feat = features[i]
            nearest = 0
            min_dist = np.linalg.norm(feat-centers[0])
            for j in range(1, k):
                dist = np.linalg.norm(feat-centers[j])
                if dist < min_dist:
                    min_dist = dist
                    nearest = j
            assignments[i] = nearest
        if np.all(origin_assignments == assignments):
            break
        for j in range(k):
            # 注意 求均值需要指定维度
            centers[j] = np.mean(features[assignments == j], axis=0)
        # END YOUR CODE

    return assignments


def kmeans_fast(features, k, num_iters=100):
    """ Use kmeans algorithm to group features into k clusters.

    This function makes use of numpy functions and broadcasting to speed up the
    first part(cluster assignment) of kmeans algorithm.

    Hints
    - You may find np.repeat and np.argmin useful

    Args:
        features - Array of N features vectors. Each row represents a feature
            vector.
        k - Number of clusters to form.
        num_iters - Maximum number of iterations the algorithm will run.

    Returns:
        assignments - Array representing cluster assignment of each point.
            (e.g. i-th point is assigned to cluster assignments[i])
    """

    N, D = features.shape

    assert N >= k, 'Number of clusters cannot be greater than number of points'

    # Randomly initalize cluster centers
    idxs = np.random.choice(N, size=k, replace=False)
    centers = features[idxs]
    assignments = np.zeros(N, dtype=np.uint32)

    for n in range(num_iters):
        # YOUR CODE HERE
        new_ass = np.argmin(
            np.linalg.norm(np.repeat(features[:, np.newaxis, :], k, axis=1)-centers, axis=2), axis=1)
        if np.all(new_ass == assignments):
            break
        assignments = new_ass
        for j in range(k):
            # 注意 求均值需要指定维度
            centers[j] = np.mean(features[assignments == j], axis=0)
        # END YOUR CODE

    return assignments


def hierarchical_clustering(features, k):
    """ Run the hierarchical agglomerative clustering algorithm.

    The algorithm is conceptually simple:

    Assign each point to its own cluster
    While the number of clusters is greater than k:
        Compute the distance between all pairs of clusters
        Merge the pair of clusters that are closest to each other

    We will use Euclidean distance to define distance between clusters.

    Recomputing the centroids of all clusters and the distances between all
    pairs of centroids at each step of the loop would be very slow. Thankfully
    most of the distances and centroids remain the same in successive
    iterations of the outer loop; therefore we can speed up the computation by
    only recomputing the centroid and distances for the new merged cluster.

    Even with this trick, this algorithm will consume a lot of memory and run
    very slowly when clustering large set of points. In practice, you probably
    do not want to use this algorithm to cluster more than 10,000 points.

    Args:
        features - Array of N features vectors. Each row represents a feature
            vector.
        k - Number of clusters to form.

    Returns:
        assignments - Array representing cluster assignment of each point.
            (e.g. i-th point is assigned to cluster assignments[i])
    """

    N, D = features.shape

    assert N >= k, 'Number of clusters cannot be greater than number of points'

    # Assign each point to its own cluster
    assignments = np.arange(N, dtype=np.uint32)
    centers = np.copy(features)
    n_clusters = N

    while n_clusters > k:
        # YOUR CODE HERE
        dist = squareform(pdist(centers))
        np.fill_diagonal(dist, np.inf)
        min_idx = np.argmin(dist)
        min_idx = np.unravel_index(min_idx, dist.shape)
        assignments[assignments == min_idx[1]] = min_idx[0]
        centers[min_idx[0]] = np.mean(
            features[assignments == min_idx[0]], axis=0)
        centers = np.delete(centers, min_idx[1], axis=0)
        assignments[assignments > min_idx[1]] -= 1
        n_clusters -= 1
        # END YOUR CODE

    return assignments


# Pixel-Level Features
def color_features(img):
    """ Represents a pixel by its color.

    Args:
        img - array of shape (H, W, C)

    Returns:
        features - array of (H * W, C)
    """
    H, W, C = img.shape
    img = img_as_float(img)
    features = np.zeros((H*W, C))

    # YOUR CODE HERE
    features = img.reshape((H*W, C))
    # END YOUR CODE

    return features


def color_position_features(img):
    """ Represents a pixel by its color and position.

    Combine pixel's RGB value and xy coordinates into a feature vector.
    i.e. for a pixel of color (r, g, b) located at position (x, y) in the
    image. its feature vector would be (r, g, b, x, y).

    Don't forget to normalize features.

    Hints
    - You may find np.mgrid and np.dstack useful
    - You may use np.mean and np.std

    Args:
        img - array of shape (H, W, C)

    Returns:
        features - array of (H * W, C+2)
    """
    H, W, C = img.shape
    color = img_as_float(img)
    features = np.zeros((H*W, C+2))

    # YOUR CODE HERE
    color = color.reshape((H*W, C))
    color = (color - np.mean(color, axis=0)) / np.std(color, axis=0)
    y, x = np.mgrid[0:H, 0:W]
    y = y.reshape((H*W, 1))
    y = (y - np.mean(y, axis=0)) / np.std(y, axis=0)
    x = x.reshape((H*W, 1))
    x = (x - np.mean(x, axis=0)) / np.std(x, axis=0)
    features = np.hstack((color, y, x))
    # features = (features - np.mean(features, axis=0)) / \
    #     np.std(features, axis=0)
    # END YOUR CODE

    return features


def my_features(img):
    """ Implement your own features

    Args:
        img - array of shape (H, W, C)

    Returns:
        features - array of (H * W, C)
    """
    features = None
    # YOUR CODE HERE
    import cv2
    color = img_as_float(img)
    H, W, C = color.shape
    color = color.reshape((H*W, C))
    color = (color - np.mean(color, axis=0)) / np.std(color, axis=0)
    # gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    gray = np.mean(img, axis=2)
    gray = gray.astype(np.float32)
    grad_x = np.gradient(gray, axis=1)
    grad_y = np.gradient(gray, axis=0)
    grad_x = grad_x.reshape((H*W, 1))
    grad_x = (grad_x - np.mean(grad_x, axis=0)) / np.std(grad_x, axis=0)
    grad_y = grad_y.reshape((H*W, 1))
    grad_y = (grad_y - np.mean(grad_y, axis=0)) / np.std(grad_y, axis=0)
    features = np.hstack((color, grad_x, grad_y))
    # END YOUR CODE
    return features


def sift_features(img):
    """ Extracts SIFT features from the image.

    You should use the default value of the parameters for this function.

    Args:
        img - array of shape (H, W, C)

    Returns:
        features - array of (N, 128)
    """
    import cv2
    sift = cv2.SIFT_create()
    gray = np.mean(img*255, axis=2, dtype=np.uint8)
    _, features = sift.detectAndCompute(gray, None)
    return features


# Quantitative Evaluation
def compute_accuracy(mask_gt, mask):
    """ Compute the pixel-wise accuracy of a foreground-background segmentation
        given a ground truth segmentation.

    Args:
        mask_gt - The ground truth foreground-background segmentation. A
            logical of size H x W where mask_gt[y, x] is 1 if and only if
            pixel (y, x) of the original image was part of the foreground.
        mask - The estimated foreground-background segmentation. A logical
            array of the same size and format as mask_gt.

    Returns:
        accuracy - The fraction of pixels where mask_gt and mask agree. A
            bigger number is better, where 1.0 indicates a perfect segmentation.
    """

    accuracy = None
    # YOUR CODE HERE
    TP = np.sum(np.logical_and(mask_gt, mask))
    TN = np.sum(np.logical_and(np.logical_not(mask_gt), np.logical_not(mask)))
    accuracy = (TP + TN) / (mask_gt.shape[0] * mask_gt.shape[1])
    # END YOUR CODE

    return accuracy


def evaluate_segmentation(mask_gt, segments):
    """ Compare the estimated segmentation with the ground truth.

    Note that 'mask_gt' is a binary mask, while 'segments' contain k segments.
    This function compares each segment in 'segments' with the ground truth and
    outputs the accuracy of the best segment.

    Args:
        mask_gt - The ground truth foreground-background segmentation. A
            logical of size H x W where mask_gt[y, x] is 1 if and only if
            pixel (y, x) of the original image was part of the foreground.
        segments - An array of the same size as mask_gt. The value of a pixel
            indicates the segment it belongs.

    Returns:
        best_accuracy - Accuracy of the best performing segment.
            0 <= accuracy <= 1, where 1.0 indicates a perfect segmentation.
    """

    num_segments = np.max(segments) + 1
    best_accuracy = 0

    # Compare each segment in 'segments' with the ground truth
    for i in range(num_segments):
        mask = (segments == i).astype(int)
        accuracy = compute_accuracy(mask_gt, mask)
        best_accuracy = max(accuracy, best_accuracy)

    return best_accuracy
