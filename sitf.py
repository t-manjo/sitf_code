"""
Program Name: sitf
Copyright (c) 2024 Taishun MANJO

Authors: Taishun MANJO
Contact: manjo.taishun@spring8.or.jp

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

sparse image text format saving of 2D detector output
Designed to process many frames of sparse image data in, e.g. nominally identical conditions, and save all
the data to one file, possibly with processing
IOt is assumed that the frame rate will be high so that we try to keep the processing of
each frame relatively fast.  
However, the writing and reading of the sitf file is assumes to be done only occasionally so is not so optimized
"""


import os
import sys
import time

import numpy as np

import time #for checking the working speed of the function

np.set_printoptions(linewidth=sys.maxsize, formatter={'int': '{:5d}'.format, 'float': '{:5.1f}'.format})

class SitfData(): #sitf data structure
  def __init__(self):
    self.nc = 0                             #number of counts
    self.npa = np.empty([0], dtype=int)     #array with number of selected pixels in each frames
    self.xpa = np.empty([0], dtype=int)     #array with x values of all selected pixels in frame order
    self.ypa = np.empty([0], dtype=int)     #array with y values of all selected pixels in frame order
    self.va = np.empty([0], dtype=int)      #array with intensity values of all selected pixels in frame order
    self.th = 0.0                           #threshold value
    self.nopp = 0                           #number of positive pixels
    self.xbp = np.empty([0], dtype=int)     #array with y values of all bad pixels
    self.ybp = np.empty([0], dtype=int)     #array with y values of all bad pixels
    
  def print_method(self):   # for testing only
    print(self.nc, self.npa, self.xpa, self.ypa, self.va)
    print(self.th, self.nopp, self.xbp, self.ybp)

class HeaderData(): #header structure
  def __init__(self):
    self.nsel = 0                           #number of selected pixels
    self.epoch = 0.0                        #creation time
    self.filename = "test"                  #filename
    self.general_desription = "none"        #general description
    self.npx = 0                            #number of pixels in full detector for x direction
    self.npy = 0                            #number of pixels in full detector for y direction
    #define regions saved in sitf files relative to full detector
    self.roi_xmin = 0                       #minimum index of ROI (Region of Interest) for x direction
    self.roi_xmax = 0                       #maximum index of ROI (Region of Interest) for x direction
    self.roi_ymin = 0                       #minimum index of ROI (Region of Interest) for y direction
    self.roi_ymax = 0                       #maximum index of ROI (Region of Interest) for x direction
    self.nf_tot = 0                         #number of frames processed
    self.nf_ne = 0                          #number of "non-empty" frames where at least one pixel for one threshold has data
    self.mspf = 0.0                         #ms per frame
    self.realtime = 0.0                     #realtime for data collection
    self.nth = 0                            # number of threshold
    # optional user-defined variables for possble processing to get selected pixels
    self.border = 0.0                       #
    self.ni = 0                             #number of images in this file (number of threshold + 1(selected))
    self.iproc = 0                          #processing used to select pixels
    self.selected_desription = "none"           #optional description for selected


# process_one_threshold
def process_one_threshold(threshold, im_in, bpx, bpy):
  """process_one_threshold(threshold, im, bpx, bpy)   Process 2D im array for some threshold, with bad pixesl given by bpx,bpy. 
  This:  removes bad pixels, selects positive pixels, makes arrays of positions and values
  """
  data = SitfData() #initialize

  data.th = threshold
  data.xbp = bpx
  data.ybp = bpy

  # im[[bpx,bpy]] = 0  # set bad pixels to zero  AB Guess much faster loop
  im = im_in.copy()
  im[bpx,bpy] = 0
    
  #all = np.where(im > 16) #test
  all = np.where(im > 0) #usual
  data.xpa = all[0]
  data.ypa = all[1]
  data.va = im[data.xpa, data.ypa]
  data.nc = int(data.va.sum())
  data.nopp = len(data.va)

  return data

def select_common(* sitf):
  data_s = SitfData()  #selected
  data_s = sitf[0]  #initialized by first data

  for i in range(1, len(sitf)): #threshold loop (th2 th3 th4...)
    data_t = SitfData() #temp data
    for j in range(data_s.nopp):
      for k in range(sitf[i].nopp):
        if data_s.xpa[j] == sitf[i].xpa[k] and data_s.ypa[j] == sitf[i].ypa[k]:
          data_t.xpa = np.append(data_t.xpa, data_s.xpa[j])
          data_t.ypa = np.append(data_t.ypa, data_s.ypa[j])
          data_t.va = np.append(data_t.va, data_s.va[j])
          data_t.nopp += 1
    
    data_t.nc = int(data_t.va.sum())
    data_s = data_t #update selected pixel sitf
  
  return data_s

def select_diff(* sitf):
  """possible routine to choose selected pixels.  Eg.  th1-th2 or fancier routine """
  data_s = SitfData()  #selected
  data_s = sitf[0]  #initialized by first data

  for i in range(1, len(sitf)): #threshold loop (th2 th3 th4...)
    data_t = SitfData() #temp data
    for j in range(data_s.nopp):
      diff_flag = 0
      for k in range(sitf[i].nopp):
        if data_s.xpa[j] == sitf[i].xpa[k] and data_s.ypa[j] == sitf[i].ypa[k]:
          diff_flag = 1

      if diff_flag == 0:
        data_t.xpa = np.append(data_t.xpa, data_s.xpa[j])
        data_t.ypa = np.append(data_t.ypa, data_s.ypa[j])
        data_t.va = np.append(data_t.va, data_s.va[j])
        data_t.nopp += 1
    
    data_t.nc = int(data_t.va.sum())
    data_s = data_t #update selected pixel sitf

  return data_s

def append_data(data, sitf_temp):
  """ adds a frame to arrays """
  data.npa = np.append(data.npa, sitf_temp.nopp)
  data.xpa = np.append(data.xpa, sitf_temp.xpa)
  data.ypa = np.append(data.ypa, sitf_temp.ypa)
  data.va = np.append(data.va, sitf_temp.va)
  data.nc += sitf_temp.nc

def write_sitf_file(header, data, data_s, fname_out, overwrite_flag=True):
  """write sitf file - default will overwrite - option to not overwrite"""
  if not overwrite_flag:
    if os.path.exists(fname_out):
      print("Error in 'write_sitf_file'.")
      print("File '" + fname_out + "' now exists.")
      print("You choose not to overwrite.")
      input("Push enter key to exit\n")
      exit()

  header.epoch = time.time()
  if header.filename == "test" or header.filename != fname_out:
    header.filename = fname_out

  #make output line
  header.n_th = len(data)
  label_d = {"th":["n_th"], "nopp":["nsel"], "nc":["nc_s"]}
  value_d = {"th":[str(header.n_th)], "nopp":[str(header.nsel)], "nc":[str(data_s.nc)]}
  i = 1
  for data_i in data:
    label_d["th"].append("th_" + str(i))
    label_d["nopp"].append("nopp_" + str(i))
    label_d["nc"].append("nc_" + str(i))

    value_d["th"].append(str(data_i.th))
    value_d["nopp"].append(str(data_i.nopp))
    value_d["nc"].append(str(data_i.nc))
    i+=1

  ll = []
  ll.append("#filename general_desription : {0:s} {1:s}".format(header.filename, header.general_desription))
  ll.append("nsel epoch : {0:d} {1:.3f}".format(header.nsel, header.epoch))
  ll.append("npx npy roi_xmin roi_xmax roi_ymin roi_ymax : {0:d} {1:d} {2:d} {3:d} {4:d} {5:d}".format(header.npx, header.npy, header.roi_xmin, header.roi_xmax, header.roi_ymin, header.roi_ymax))
  ll.append("nf_tot nf_ne mspf : {0:d} {1:d} {2:.1f}".format(header.nf_tot, header.nf_ne, header.mspf))
  ll.append("realtime : {0:.3f}".format(header.realtime))
  ll.append(" ".join(label_d["th"]) + " : " + " ".join(value_d["th"]))
  ll.append(" ".join(label_d["nopp"]) + " : " + " ".join(value_d["nopp"]))
  ll.append(" ".join(label_d["nc"]) + " : " + " ".join(value_d["nc"]))
  ll.append("#selected_desription : {0:s}".format(header.selected_desription))
  ll.append("ni iproc border : {0:d} {1:d}  {2:.1f}".format(header.ni, header.iproc, header.border))
  ll.append("# selected nsel = {0:d} nc_s = {1:s}".format(header.nsel, str(data_s.nc)))
  ll.append("npa_s : "+str(data_s.npa))
  ll.append("xpa_s : "+str(data_s.xpa))
  ll.append("ypa_s : "+str(data_s.ypa))
  ll.append("va_s  : "+str(data_s.va))
  i = 1
  for data_i in data:
    ll.append("# th_" + str(i) + " = " + str(str(data_i.th)) + " with " + str(data_i.nopp) + " positive pixels and " + str(data_i.nc) + " counts")
    ll.append("npa_" + str(i) + " : "+str(data_i.npa))
    ll.append("xpa_" + str(i) + " : "+str(data_i.xpa))
    ll.append("ypa_" + str(i) + " : "+str(data_i.ypa))
    ll.append("va_" + str(i) + "  : "+str(data_i.va))
    i += 1  
  ll.append("# bad_pixel_maps")
  i = 1
  for data_i in data:
    ll.append("xbp_" + str(i) + " : "+str(data_i.xbp))
    ll.append("ybp_" + str(i) + " : "+str(data_i.ybp))
    i += 1

  outstr = ' \n'.join(ll)
  with open(header.filename, "w") as f:
    f.write(outstr)

def read_sitf_file(f_in):
  """read_sitf_file(f_in) - read sitf file"""
  #read all from f_in.sitf
  with open(f_in, "r") as f:
    sitf_list = f.readlines()
  
  #header data assignment
  header = HeaderData() #initialize
  #1st line
  i = 0
  l_temp = sitf_list[i][1:] #delete "#"
  values = l_temp.split(":")[1].split()
  header.filename = values[0]
  header.general_desription = values[1]
  #next line
  i+=1
  values = sitf_list[i].split(":")[1].split()
  header.nsel = int(values[0])
  header.epoch = float(values[1])
  #next line
  i+=1
  values = sitf_list[i].split(":")[1].split()
  header.npx = int(values[0])
  header.npy = int(values[1])
  header.roi_xmin = int(values[2])
  header.roi_xmax = int(values[3])
  header.roi_ymin = int(values[4])
  header.roi_ymax = int(values[5])
  #next line
  i+=1
  values = sitf_list[i].split(":")[1].split()
  header.nf_tot = int(values[0])
  header.nf_ne = int(values[1])
  header.mspf = float(values[2])
  #next line
  i+=1
  values = sitf_list[i].split(":")[1].split()
  header.realtime = float(values[0])
  #next line
  i+=1
  values = sitf_list[i].split(":")[1].split()
  all = []
  sel = SitfData()
  header.n_th = int(values[0])
  for j in range(header.n_th):
    temp1 = SitfData()
    temp1.th = float(values[j + 1])
    all.append(temp1)
  #next line
  i+=1
  values = sitf_list[i].split(":")[1].split()
  for j in range(header.n_th):
    all[j].nopp = int(values[j + 1])
  #next line
  i+=1
  values = sitf_list[i].split(":")[1].split()
  sel.nc = float(values[0])
  for j in range(header.n_th):
    all[j].nc = float(values[j + 1])
  #next line
  i+=1
  l_temp = sitf_list[i][1:] #delete "#"
  values = sitf_list[i].split(":")[1].split()
  header.selected_desription = values[0]
  #next line
  i+=1
  values = sitf_list[i].split(":")[1].split()
  header.ni = int(values[0])
  header.iproc = int(values[1])
  header.border = float(values[2])
  #next line
  i+=1
  #skip comment line
  #next line
  i+=1
  sel.npa = array_from_strline(sitf_list[i])
  #next line
  i+=1
  sel.xpa = array_from_strline(sitf_list[i])
  #next line
  i+=1
  sel.ypa = array_from_strline(sitf_list[i])
  #next line
  i+=1
  sel.va = array_from_strline(sitf_list[i])
  for j in range(header.n_th):
    i+=1
    #skip comment line
    i+=1
    all[j].npa = array_from_strline(sitf_list[i])
    #next line
    i+=1
    all[j].xpa = array_from_strline(sitf_list[i])
    #next line
    i+=1
    all[j].ypa = array_from_strline(sitf_list[i])
    #next line
    i+=1
    all[j].va = array_from_strline(sitf_list[i])
  #next line
  i+=1
  #skip comment line
  for j in range(header.n_th):
    i+=1
    all[j].xbp = array_from_strline(sitf_list[i])
    i+=1
    all[j].ybp = array_from_strline(sitf_list[i])

  return header, all, sel

def array_from_strline(strline):
  """make array from sitf file. delete "[]" from sitf file line. This is subroutine for read_sitf_file"""
  label = strline.split(":")[0] #before ":"
  list_line = strline.split(":")[1].replace("[", "").replace("]", "") #after ":" 
  if label[0:2] != "va":
    #int array
    data_array = np.empty([0], dtype=int)
    for temp in list_line.split():
      data_array = np.append(data_array, int(temp))
  else:
    #float array (for va)
    data_array = np.empty([0], dtype=float)
    for temp in list_line.split():
      data_array = np.append(data_array, float(temp))

  return data_array
    
def sitf_to_image_array(header, sitf):
  """make image array from sitf file"""
  image = np.zeros((header.npx, header.npy), dtype=int)
  if sitf.npa.sum() > 0 and len(sitf.xpa) == len(sitf.ypa) and sitf.va.sum() > 0.0:
    for i in range(len(sitf.xpa)):
      image[sitf.xpa[i], sitf.ypa[i]] += sitf.va[i]
  return image

def add_image_array(image, sitf):
  if sitf.npa.sum() > 0 and len(sitf.xpa) == len(sitf.ypa) and sitf.va.sum() > 0.0:
    for i in range(len(sitf.xpa)):
      image[sitf.xpa[i], sitf.ypa[i]] += sitf.va[i]
  return image

def combine_sitf(datadir,string1,string2):
  """combine multiple sitfs to single sitf """
  if not os.path.exists(datadir): 
    print("Directory not found in combine_sitf!!! ",datadir)
    exit()
  
  lof = os.listdir(datadir)  # list of files
  lopt =  [f for f in lof if string1 in f] # list of possibilities
  lop =  [f for f in lopt if string2 in f] # list of possibilities
  nopf = len(lop)
  if nopf < 1:
    print(f'Combine Error. No files containing {string1,string2}. EXIT')
    exit()
  else:
    print(f'Found {nopf} files containing {string1,string2}.  Attempting to combine theses.')
    sitf = SitfData()
    header_first, all_first, sel_first = read_sitf_file(datadir + "/" + lop[0])
    temp_im = np.zeros((header_first.npx, header_first.npy), dtype=int)
    for f in lop:
      fin = datadir + "/" + f
      header_sitf, all_sitf, sel_sitf = read_sitf_file(fin)
      temp_im = add_image_array(temp_im, sel_sitf)
    
    all = np.where(temp_im > 0)
    sitf.xpa = all[0]
    sitf.ypa = all[1]
    sitf.va = temp_im[sitf.xpa, sitf.ypa]
    sitf.npa = np.append(sitf.npa, len(sitf.va))

  return sitf
