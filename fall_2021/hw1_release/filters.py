"""
CS131 - Computer Vision: Foundations and Applications
Assignment 1
Author: Donsuk Lee (donlee90@stanford.edu)
Date created: 07/2017
Last modified: 10/16/2017
Python Version: 3.5+
"""

import numpy as np


def conv_nested(image, kernel):
    """A naive implementation of convolution filter.

    This is a naive implementation of convolution using 4 nested for-loops.
    This function computes convolution of an image with a kernel and outputs
    the result that has the same shape as the input image.

    Args:
        image: numpy array of shape (Hi, Wi).
        kernel: numpy array of shape (Hk, Wk). Dimensions will be odd.

    Returns:
        out: numpy array of shape (Hi, Wi).
    """
    Hi, Wi = image.shape
    Hk, Wk = kernel.shape
    out = np.zeros((Hi, Wi))

    ### YOUR CODE HERE
    h_s = Hk//2
    w_s = Wk//2
    
    for hi in range(Hi):
        for wi in range(Wi):
            for hk in range(-h_s, -h_s+Hk):
                for wk in range(-w_s, -w_s+Wk):
                    if hi-hk >=0 and hi-hk<Hi and wi-wk>=0 and wi-wk<Wi:
                        out[hi,wi]+=kernel[hk+h_s,wk+w_s]*image[hi-hk, wi-wk]
    ### END YOUR CODE

    return out

def zero_pad(image, pad_height, pad_width):
    """ Zero-pad an image.

    Ex: a 1x1 image [[1]] with pad_height = 1, pad_width = 2 becomes:

        [[0, 0, 0, 0, 0],
         [0, 0, 1, 0, 0],
         [0, 0, 0, 0, 0]]         of shape (3, 5)

    Args:
        image: numpy array of shape (H, W).
        pad_width: width of the zero padding (left and right padding).
        pad_height: height of the zero padding (bottom and top padding).

    Returns:
        out: numpy array of shape (H+2*pad_height, W+2*pad_width).
    """

    H, W = image.shape
    out = None

    ### YOUR CODE HERE
    out = np.zeros((H+2*pad_height, W+2*pad_width))
    out[pad_height:H+pad_height, pad_width:W+pad_width] = image
    ### END YOUR CODE
    return out


def conv_fast(image, kernel):
    """ An efficient implementation of convolution filter.

    This function uses element-wise multiplication and np.sum()
    to efficiently compute weighted sum of neighborhood at each
    pixel.

    Hints:
        - Use the zero_pad function you implemented above
        - There should be two nested for-loops
        - You may find np.flip() and np.sum() useful

    Args:
        image: numpy array of shape (Hi, Wi).
        kernel: numpy array of shape (Hk, Wk). Dimensions will be odd.

    Returns:
        out: numpy array of shape (Hi, Wi).
    """
    Hi, Wi = image.shape
    Hk, Wk = kernel.shape
    out = np.zeros((Hi, Wi))

    ### YOUR CODE HERE
    h_s = Hk//2
    w_s = Wk//2
    print(h_s,w_s)
    print(Hk, Wk)
    
    image_with_pad = zero_pad(image, h_s, w_s)
    kernel = np.flip(kernel)

    for hi in range(h_s,h_s+Hi):
        for wi in range(w_s,w_s+Wi):
            out[hi-h_s,wi-w_s] = np.sum(kernel[:,:]*image_with_pad[hi-h_s:hi-h_s+Hk,wi-w_s:wi-w_s+Wk])
            
    ### END YOUR CODE

    return out

def cross_correlation(f, g):
    """ Cross-correlation of image f and template g.

    Hint: use the conv_fast function defined above.

    Args:
        f: numpy array of shape (Hf, Wf).
        g: numpy array of shape (Hg, Wg).

    Returns:
        out: numpy array of shape (Hf, Wf).
    """

    out = None
    ### YOUR CODE HERE
    Hi, Wi = f.shape
    Hk, Wk = g.shape
    out = np.zeros((Hi, Wi))

    ### YOUR CODE HERE
    h_s = Hk//2
    w_s = Wk//2
    print(h_s,w_s)
    print(Hk, Wk)
    
    image_with_pad = zero_pad(f, h_s, w_s)

    for hi in range(h_s,h_s+Hi):
        for wi in range(w_s,w_s+Wi):
            out[hi-h_s,wi-w_s] = np.sum(g[:,:]*image_with_pad[hi-h_s:hi-h_s+Hk,wi-w_s:wi-w_s+Wk])
    ### END YOUR CODE

    return out

def zero_mean_cross_correlation(f, g):
    """ Zero-mean cross-correlation of image f and template g.

    Subtract the mean of g from g so that its mean becomes zero.

    Hint: you should look up useful numpy functions online for calculating the mean.

    Args:
        f: numpy array of shape (Hf, Wf).
        g: numpy array of shape (Hg, Wg).

    Returns:
        out: numpy array of shape (Hf, Wf).
    """

    out = None
    ### YOUR CODE HERE
    g_mean = np.mean(g)
    out = cross_correlation(f, g-g_mean)
    ### END YOUR CODE

    return out

def normalized_cross_correlation(f, g):
    """ Normalized cross-correlation of image f and template g.

    Normalize the subimage of f and the template g at each step
    before computing the weighted sum of the two.

    Hint: you should look up useful numpy functions online for calculating 
          the mean and standard deviation.

    Args:
        f: numpy array of shape (Hf, Wf).
        g: numpy array of shape (Hg, Wg).

    Returns:
        out: numpy array of shape (Hf, Wf).
    """
    from matplotlib import pyplot as plt

    out = None
    ### YOUR CODE HERE
    g = g.astype(float)
    f = f.astype(float)
    g_norm = (g-np.mean(g))/np.std(g)
    
    ### YOUR CODE HERE
    Hi, Wi = f.shape
    Hk, Wk = g.shape
    out = np.zeros((Hi, Wi))

    ### YOUR CODE HERE
    h_s = Hk//2
    w_s = Wk//2
    print(h_s,w_s)
    print(Hk, Wk)
    
    image_with_pad = zero_pad(f, h_s, w_s)

    for hi in range(h_s,h_s+Hi):
        for wi in range(w_s,w_s+Wi):
            patch_mean = np.mean(image_with_pad[hi-h_s:hi-h_s+Hk,wi-w_s:wi-w_s+Wk])
            patch_std = np.std(image_with_pad[hi-h_s:hi-h_s+Hk,wi-w_s:wi-w_s+Wk])
            out[hi-h_s,wi-w_s] = np.sum(g_norm[:,:]*(image_with_pad[hi-h_s:hi-h_s+Hk,wi-w_s:wi-w_s+Wk]-patch_mean)/patch_std)
    ### END YOUR CODE

    return out

    ### END YOUR CODE

    return out
