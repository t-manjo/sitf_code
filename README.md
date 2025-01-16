# OUTLINE

**sitf(sparse image text format)** is a new file format for sparse image data. This format compresses data without losing information while improving human readability and contributing to more efficient use of storage.

# How to use
## input data
* Threshold value (real (float) type)

* Image array(numpy 2D array, [x pixel $\times$ y pixel])

* Bad pixel array for x (numpy array)

* Bad pixel array for y (numpy array)

## function
* process_one_threshold(Threshold value, Image array, Bad pixel array for x, Bad pixel array for y)

  This function translates from image array to sitf data lists. The return value is sitf data[^1].

  [^1]: sitf data is defined as the class. Member valuables are nc(number of counts), npa(array with number of positive pixels), xpa, ypa(array with x/y values of all positive pixels), va(array with intensity values of all positive pixels), th(threshold value), nopp(number of positive pixels), xbp, and ybp(array with x/y values of all bad pixels).
