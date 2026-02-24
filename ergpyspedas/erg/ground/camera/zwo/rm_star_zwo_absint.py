import numpy as np
from scipy.signal import medfilt2d as median


def rm_star_zwo_absint(
    img0, 
    img_size=1408
    ):
    """
    Remove star lights with a median filter.
    
    @img0: input the image data
    @img_size: input image size
    @return: output the image data that remove the star lights
    """
    # ---Median filter size:
    width = 3

    # ---Calculate the image data median values:
    img0 = img0.astype(float)
    med_img = median(img0, width)

    # ---Deviation of the raw image from the median value:
    star_img = img0 - med_img

    # ---Calculate the mean and standard deviation for an image sample,
    # ---constrained between pix_0 and pix_1:
    pix_0 = int(img_size / 2 - img_size / 4)
    pix_1 = int(img_size / 2 + img_size / 4 - 1)
    res_mean = np.nanmean(star_img[pix_0:pix_1, pix_0:pix_1])
    res_std = np.nanstd(star_img[pix_0:pix_1, pix_0:pix_1])

    # ---Calculate the threshold of the star lights,
    # ---which is the sum of the mean and standard deviation:
    star_threshold = res_mean + res_std

    # ---Identify the number of non-star light positions with less than threshold values:
    non_star_pos = np.where(star_img < star_threshold)

    # ---The number of non-star light positions is not zero -->
    # ---the image value is zero at the star light positions:
    if len(non_star_pos) != 0:
        star_img[non_star_pos] = 0

    # ---Subtract the star lights from the raw image data:
    img_out = img0 - star_img

    return img_out
