# OUTLINE

**sitf(sparse image text format)** is a new file format for sparse image data. This format balances readability and storage efficiency, significantly reducing data storage requirements.

# How to use
## input data
* Threshold value (real (float) type)

* Image array(numpy 2D array, [x pixel $\times$ y pixel])

* Bad pixel array for x (numpy array)

* Bad pixel array for y (numpy array)

## function
* process_one_threshold(Threshold value, Image array, Bad pixel array for x, Bad pixel array for y)
