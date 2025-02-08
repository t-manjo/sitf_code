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

* write_sitf_file(header[^2], sitf data of each threshold, selected sitf data, filename, Overwrite_flag (default is true))

  This function outputs the sitf file. If the same name file has already existed, the file is usually overwritten. If the user sets up the Overwrite_flag to False, the user can avoid overwriting.

* read_sitf_file(sitf file name)

  This function reads the sitf file. The return values are header, sitf data of each threshold, selected sitf data.

  [^1]: sitf data is defined as the class. Member valuables are nc(number of counts), npa(array with number of positive pixels), xpa, ypa(array with x/y values of all positive pixels), va(array with intensity values of all positive pixels), th(threshold value), nopp(number of positive pixels), xbp, and ybp(array with x/y values of all bad pixels).
  [^2]: Header is also defines as the class. Member valuables are nsel(number of selected pixels), epoch(creation time), filename, npx, npy(number of pixels in full detector for x/y direction), roi_xmin, roi_xmax, roi_xmin, roi_ymax(minimum/maximum index of ROI (Region of Interest) for x/y direction), nf_tot(number of frames processed), nf_ne(number of "non-empty" frames where at least one pixel for one threshold has data), mspf(ms per frame), and realtime(realtime for data collection).
