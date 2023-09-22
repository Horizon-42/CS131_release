import numpy as np


def compress_image(image, num_values):
    """Compress an image using SVD and keeping the top `num_values` singular values.

    Args:
        image: numpy array of shape (H, W)
        num_values: number of singular values to keep

    Returns:
        compressed_image: numpy array of shape (H, W) containing the compressed image
        compressed_size: size of the compressed image
    """
    compressed_image = None
    compressed_size = 0

    # YOUR CODE HERE
    # Steps:
    #     1. Get SVD of the image
    #     2. Only keep the top `num_values` singular values, and compute `compressed_image`
    #     3. Compute the compressed size
    u, s, v = np.linalg.svd(image, full_matrices=False)
    # q: why do we need full_matrices=False
    # a: because we want to keep the original shape of the image
    #    if full_matrices=True, the shape of u will be (H, H), which is not what we want
    #    we want the shape of u to be (H, num_values)
    #    the same for v
    print(u.shape)
    print(s.shape)
    print(v.shape)
    s[num_values:] = 0
    compressed_image = u @ np.diag(s) @ v
    compressed_size = num_values * (u.shape[0] + v.shape[0] + 1)
    # 1. u.shape[0] is the number of rows of u
    #    v.shape[0] is the number of rows of v
    #    1 is the number of rows of s
    # 2. num_values is the number of values we keep
    #    we need to keep the top num_values singular values
    #    so we need to keep num_values rows of u, s, and v
    #    for each row of u, s, and v, we need to keep num_values values
    #    so we need to keep num_values columns of u, s, and v
    # END YOUR CODE

    assert compressed_image.shape == image.shape, \
        "Compressed image and original image don't have the same shape"

    assert compressed_size > 0, "Don't forget to compute compressed_size"

    return compressed_image, compressed_size
