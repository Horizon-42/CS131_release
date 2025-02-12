"""
CS131 - Computer Vision: Foundations and Applications
Assignment 8
Author: Donsuk Lee (donlee90@stanford.edu)
Date created: 09/2017
Last modified: 12/02/2017
Python Version: 3.5+
"""

import numpy as np
from skimage.transform import pyramid_gaussian
from skimage.filters import sobel_h, sobel_v, gaussian
from skimage.feature import corner_harris, corner_peaks


def lucas_kanade(img1, img2, keypoints, window_size=5):
    """ Estimate flow vector at each keypoint using Lucas-Kanade method.

    Args:
        img1 - Grayscale image of the current frame. Flow vectors are computed
            with respect to this frame.
        img2 - Grayscale image of the next frame.
        keypoints - Keypoints to track. Numpy array of shape (N, 2).
        window_size - Window size to determine the neighborhood of each keypoint.
            A window is centered around the current keypoint location.
            You may assume that window_size is always an odd number.
    Returns:
        flow_vectors - Estimated flow vectors for keypoints. flow_vectors[i] is
            the flow vector for keypoint[i]. Numpy array of shape (N, 2).

    Hints:
        - You may use np.linalg.inv to compute inverse matrix
    """
    assert window_size % 2 == 1, "window_size must be an odd number"

    flow_vectors = []
    w = window_size // 2

    # Compute partial derivatives
    Iy, Ix = np.gradient(img1)
    It = img2 - img1

    # For each [y, x] in keypoints, estimate flow vector [vy, vx]
    # using Lucas-Kanade method and append it to flow_vectors.
    for y, x in keypoints:
        # Keypoints can be loacated between integer pixels (subpixel locations).
        # For simplicity, we round the keypoint coordinates to nearest integer.
        # In order to achieve more accurate results, image brightness at subpixel
        # locations can be computed using bilinear interpolation.
        y, x = int(round(y)), int(round(x))

        # YOUR CODE HERE
        A_x = Ix[y-w:y+w+1, x-w:x+w+1].flatten()
        A_y = Iy[y-w:y+w+1, x-w:x+w+1].flatten()
        A = np.vstack((A_x, A_y)).T
        b = -It[y-w:y+w+1, x-w:x+w+1].flatten()
        v = np.linalg.inv(A.T @ A) @ A.T @ b
        flow_vectors.append([v[1], v[0]])
        # END YOUR CODE

    flow_vectors = np.array(flow_vectors)

    return flow_vectors


def iterative_lucas_kanade(img1, img2, keypoints,
                           window_size=9,
                           num_iters=7,
                           g=None):
    """ Estimate flow vector at each keypoint using iterative Lucas-Kanade method.

    Args:
        img1 - Grayscale image of the current frame. Flow vectors are computed
            with respect to this frame.
        img2 - Grayscale image of the next frame.
        keypoints - Keypoints to track. Numpy array of shape (N, 2).
        window_size - Window size to determine the neighborhood of each keypoint.
            A window is centered around the current keypoint location.
            You may assume that window_size is always an odd number.
        num_iters - Number of iterations to update flow vector.
        g - Flow vector guessed from previous pyramid level.
    Returns:
        flow_vectors - Estimated flow vectors for keypoints. flow_vectors[i] is
            the flow vector for keypoint[i]. Numpy array of shape (N, 2).
    """
    assert window_size % 2 == 1, "window_size must be an odd number"

    # Initialize g as zero vector if not provided
    if g is None:
        g = np.zeros(keypoints.shape)

    flow_vectors = []
    w = window_size // 2

    # Compute spatial gradients
    Iy, Ix = np.gradient(img1)

    for y, x, gy, gx in np.hstack((keypoints, g)):
        v = np.zeros(2)  # Initialize flow vector as zero vector
        y1 = int(round(y))
        x1 = int(round(x))

        # TODO: Compute inverse of G at point (x1, y1)
        # YOUR CODE HERE
        G = np.zeros((2, 2))
        G[0, 0] = np.sum(Ix[y1-w:y1+w+1, x1-w:x1+w+1]**2)
        G[0, 1] = np.sum(Ix[y1-w:y1+w+1, x1-w:x1+w+1]
                         * Iy[y1-w:y1+w+1, x1-w:x1+w+1])
        G[1, 0] = G[0, 1]
        G[1, 1] = np.sum(Iy[y1-w:y1+w+1, x1-w:x1+w+1]**2)
        # END YOUR CODE

        # iteratively update flow vector
        for k in range(num_iters):
            vx, vy = v
            # Refined position of the point in the next frame
            y2 = int(round(y+gy+vy))
            x2 = int(round(x+gx+vx))

            # TODO: Compute bk and vk = inv(G) x bk
            # YOUR CODE HERE
            if y2-w < 0 or y2+w+1 > img2.shape[0] or x2-w < 0 or x2+w+1 > img2.shape[1]:
                break
            Ik = img1[y1-w:y1+w+1, x1-w:x1+w+1] - \
                img2[y2-w:y2+w+1, x2-w:x2+w+1]
            bk = np.array([np.sum(Ik*Ix[y1-w:y1+w+1, x1-w:x1+w+1]),
                           np.sum(Ik*Iy[y1-w:y1+w+1, x1-w:x1+w+1])])
            vk = np.linalg.inv(G) @ bk

            # END YOUR CODE

            # Update flow vector by vk
            v += vk

        vx, vy = v
        flow_vectors.append([vy, vx])

    return np.array(flow_vectors)


def pyramid_lucas_kanade(img1, img2, keypoints,
                         window_size=9, num_iters=7,
                         level=2, scale=2):
    """ Pyramidal Lucas Kanade method

    Args:
        img1 - same as lucas_kanade
        img2 - same as lucas_kanade
        keypoints - same as lucas_kanade
        window_size - same as lucas_kanade
        num_iters - number of iterations to run iterative LK method
        level - Max level in image pyramid. Original image is at level 0 of
            the pyramid.
        scale - scaling factor of image pyramid.

    Returns:
        d - final flow vectors
    """

    # Build image pyramids of img1 and img2
    pyramid1 = tuple(pyramid_gaussian(img1, max_layer=level, downscale=scale))
    pyramid2 = tuple(pyramid_gaussian(img2, max_layer=level, downscale=scale))

    # Initialize pyramidal guess
    g = np.zeros(keypoints.shape)

    d = np.zeros(keypoints.shape)
    for L in range(level, -1, -1):
        # YOUR CODE HERE
        d = iterative_lucas_kanade(
            pyramid1[L], pyramid2[L], keypoints=keypoints/(scale**L), window_size=window_size, num_iters=num_iters, g=g)
        g = scale * (g + d)
        # END YOUR CODE

    d = g + d
    return d


def compute_error(patch1, patch2):
    """ Compute MSE between patch1 and patch2

        - Normalize patch1 and patch2
        - Compute mean square error between patch1 and patch2

    Args:
        patch1 - Grayscale image patch of shape (patch_size, patch_size)
        patch2 - Grayscale image patch of shape (patch_size, patch_size)
    Returns:
        error - Number representing mismatch between patch1 and patch2
    """
    assert patch1.shape == patch2.shape, 'Differnt patch shapes'
    error = 0
    # YOUR CODE HERE
    p1_norm = (patch1-patch1.min())/(patch1.max()-patch1.min())
    p2_norm = (patch2-patch2.min())/(patch2.max()-patch2.min())
    error = np.mean((p1_norm - p2_norm)**2)
    # print(error)
    # END YOUR CODE
    return error


def track_features(frames, keypoints,
                   error_thresh=1.5,
                   optflow_fn=pyramid_lucas_kanade,
                   exclude_border=5,
                   **kwargs):
    """ Track keypoints over multiple frames

    Args:
        frames - List of grayscale images with the same shape.
        keypoints - Keypoints in frames[0] to start tracking. Numpy array of
            shape (N, 2).
        error_thresh - Threshold to determine lost tracks.
        optflow_fn(img1, img2, keypoints, **kwargs) - Optical flow function.
        kwargs - keyword arguments for optflow_fn.

    Returns:
        trajs - A list containing tracked keypoints in each frame. trajs[i]
            is a numpy array of keypoints in frames[i]. The shape of trajs[i]
            is (Ni, 2), where Ni is number of tracked points in frames[i].
    """

    kp_curr = keypoints
    trajs = [kp_curr]
    patch_size = 3  # Take 3x3 patches to compute error
    w = patch_size // 2  # patch_size//2 around a pixel

    for i in range(len(frames) - 1):
        I = frames[i]
        J = frames[i+1]
        flow_vectors = optflow_fn(I, J, kp_curr, **kwargs)
        kp_next = kp_curr + flow_vectors

        new_keypoints = []
        for yi, xi, yj, xj in np.hstack((kp_curr, kp_next)):
            # Declare a keypoint to be 'lost' IF:
            # 1. the keypoint falls outside the image J
            # 2. the error between points in I and J is larger than threshold

            yi = int(round(yi))
            xi = int(round(xi))
            yj = int(round(yj))
            xj = int(round(xj))
            # Point falls outside the image
            if yj > J.shape[0]-exclude_border-1 or yj < exclude_border or\
               xj > J.shape[1]-exclude_border-1 or xj < exclude_border:
                continue

            # Compute error between patches in image I and J
            patchI = I[yi-w:yi+w+1, xi-w:xi+w+1]
            patchJ = J[yj-w:yj+w+1, xj-w:xj+w+1]
            error = compute_error(patchI, patchJ)
            if error > error_thresh:
                continue

            new_keypoints.append([yj, xj])

        # print('Number of keypoints:', kp_curr.shape[0])
        # print('Number of lost keypoints:',
        #       kp_curr.shape[0] - len(new_keypoints))

        kp_curr = np.array(new_keypoints)
        trajs.append(kp_curr)

    return trajs


def IoU(bbox1, bbox2):
    """ Compute IoU of two bounding boxes

    Args:
        bbox1 - 4-tuple (x, y, w, h) where (x, y) is the top left corner of
            the bounding box, and (w, h) are width and height of the box.
        bbox2 - 4-tuple (x, y, w, h) where (x, y) is the top left corner of
            the bounding box, and (w, h) are width and height of the box.
    Returns:
        score - IoU score
    """
    x1, y1, w1, h1 = bbox1
    x2, y2, w2, h2 = bbox2
    score = 0

    # YOUR CODE HERE
    pass
    # END YOUR CODE

    return score
