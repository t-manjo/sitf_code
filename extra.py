"""
Program Name: extra
Copyright (c) 2024 Taishun MANJO

Authors: Taishun MANJO
Contact: manjo.taishun@spring8.or.jp

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

This code is the extra module for sitf code.
Required extra python package : tifffile, matplotlib, yaml
"""

import numpy as np

import tifffile

import matplotlib.pyplot as plt

import yaml

import sitf

def show_image(im):
  plt.imshow(im, cmap='Greys') # show image
  plt.show()

def save_tiff(im, name):
  tifffile.imsave(name, im)

def make_dict(header, data, data_s):
  sitf_dict = {}
  sitf_dict["nsel"] = header.nsel
  sitf_dict["epoch"] = header.epoch
  sitf_dict["filename"] = header.filename
  sitf_dict["general_desription"] = header.general_desription
  sitf_dict["npx"] = header.npx
  sitf_dict["npy"] = header.npy
  sitf_dict["roi_xmin"] = header.roi_xmin
  sitf_dict["roi_xmax"] = header.roi_xmax
  sitf_dict["roi_ymin"] = header.roi_ymin
  sitf_dict["roi_ymax"] = header.roi_ymax
  sitf_dict["nf_tot"] = header.nf_tot
  sitf_dict["nf_ne"] = header.nf_ne
  sitf_dict["mspf"] = header.mspf
  sitf_dict["realtime"] = header.realtime
  sitf_dict["n_th"] = header.n_th
  
  sitf_dict["border"] = header.border
  sitf_dict["ni"] = header.ni
  sitf_dict["iproc"] = header.iproc
  sitf_dict["selected_desription"] = header.selected_desription

  sitf_dict["nc_s"] = data_s.nc
  sitf_dict["npa_s"] = data_s.npa
  sitf_dict["xpa_s"] = data_s.xpa
  sitf_dict["ypa_s"] = data_s.ypa
  sitf_dict["va_s"] = data_s.va

  i = 1
  for data_i in data:
    sitf_dict["th_" + str(i)] = data_i.th
    sitf_dict["nopp_" + str(i)] = data_i.nopp
    sitf_dict["nc_" + str(i)] = data_i.nc
    sitf_dict["npa_" + str(i)] = data_i.npa
    sitf_dict["xpa_" + str(i)] = data_i.xpa
    sitf_dict["ypa_" + str(i)] = data_i.ypa
    sitf_dict["va_" + str(i)] = data_i.va
    sitf_dict["xbp_" + str(i)] = data_i.xbp
    sitf_dict["ybp_" + str(i)] = data_i.ybp
    i += 1

  return sitf_dict

def read_sitf_dict(f_in):
  #read sitf file in dictionary format (sitf_dict)
  #label in sitf file can be used to call value (e.g. sitf_dict["npa_s"] can call npa_s array)
  with open(f_in, "r") as f:
    sitf_list = f.readlines()
  
  sitf_dict = {}
  for temp1 in sitf_list:
    if temp1[0:2] != "# ":
      label = temp1.split(":")[0].split()
      if len(label) == 1: #detecting 1 label line (usually array data)
        if len(label[0]) > 6: # detecting "realtime" and "selected_desription" 
          if label[0] == "realtime":
            sitf_dict[label[0]] = float(temp1.split(":")[1].split()[0])
          elif label[0] == "#selected_desription":
            sitf_dict[label[0][1:]] = temp1.split(":")[1].split()[0]
          else:
            sitf_dict[label[0]] = temp1.split(":")[1].split()[0]
        else: #1 label -> npa, xpa, ypa, va, etc. array like
          str_line = temp1.split(":")[1].replace("[", "").replace("]", "")  #remove [] from text data
          if label[0][0:2] != "va": #check int arrya or float array (only va?)
            #int array
            data_array = np.empty([0], dtype=int)
            for temp in str_line.split():
              data_array = np.append(data_array, int(temp))
          else:
            #float array (va)
            data_array = np.empty([0], dtype=float)
            for temp in str_line.split():
              data_array = np.append(data_array, float(temp))
          sitf_dict[label[0]] = data_array
      elif label[0] == "#filename":
        sitf_dict[label[0][1:]] = temp1.split(":")[1].split()[0]
        sitf_dict[label[1]] = temp1.split(":")[1].split()[1]
      else: #some labels
        i = 0
        for l_temp in label:
          if isint(temp1.split(":")[1].split()[i]):
            sitf_dict[l_temp] = int(temp1.split(":")[1].split()[i])
          else:
            sitf_dict[l_temp] = float(temp1.split(":")[1].split()[i])
          i += 1
  
  #output
  print(sitf_dict)
  #print(sitf_dict["epoch"])
  #print(type(sitf_dict["epoch"]))  #numpy.ndarray
        
  return sitf_dict
        
def isint(str): #judge whether str is int
    try:
        int(str)
    except ValueError:
        return False
    else:
        return True
    
def save_yaml(dict, f_out):
  with open(f_out,'w')as f:
    yaml.dump(dict, f, default_flow_style=False, allow_unicode=True)