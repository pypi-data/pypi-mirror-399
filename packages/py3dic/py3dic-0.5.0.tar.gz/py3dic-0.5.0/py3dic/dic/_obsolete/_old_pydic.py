#%%[markdown]
# this is a copy of the pydic file. 
# 
# For installation requirements check website


#%%[markdown]
#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of pydic, a free digital correlation suite for computing strain fields
#
# Author :  - Damien ANDRE, SPCTS/ENSIL-ENSCI, Limoges France
#             <damien.andre@unilim.fr>
#
# Copyright (C) 2017 Damien ANDRE
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Contributors : Ronan GARO (debugging + log strain), Laurent MAHEO (debugging + log strain)

# ====== INTRODUCTION
# Welcome to pydic a free python suite for digital image correlation.
# pydic allows to compute (smoothed or not) strain fields from a serie of pictures.
# pydic takes in account the rigid body transformation.

# Note that this file is a module file, you can't execute it.
# You can go to the example directory for usage examples.


import copy
import glob
import logging
import math
import os
import sys

import cv2
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.widgets import Button, RadioButtons, Slider

from ._old_dic_grid import OLD_grid
from ..core.core_calcs import compute_disp_and_remove_rigid_transform, compute_displacement,  remove_point_outside
from ..gui_selectors.cv2_area_selector import AreaSelectorCV2

# logging.basicConfig(level=logging.DEBUG)

def draw_opencv(image, 
          text:str=None, 
          point=None, 
          pointf=None, 
          grid:'OLD_grid'= None, # to display a grid,  must be a OLD_grid object
          scale:float=1, 
          p_color:tuple=(0, 255, 255), 
          l_color:tuple=(255, 120, 255), 
          gr_color:tuple=(255, 255, 255), 
          filename=None,
          *args, **kwargs):
     """A generic function used to draw opencv image. Depending on the arguments it plots 
     - grid
     - markers
     - lines
     - displacement

     Args:
         image (_type_): _description_
         text (str, optional): _description_. Defaults to None.
         point (_type_, optional): arg must be an array of (x,y) point. Defaults to None.
         pointf (_type_, optional): to draw lines between point and pointf, pointf  (must be an array of same lenght than the point array). Defaults to None.
         scale (int, optional): scaling parameter. Defaults to 1.
         p_color (tuple, optional): arg to choose the color of point in (r,g,b) format. Defaults to (0, 255, 255).
         l_color (tuple, optional): color of lines in (RGB). Defaults to (255, 120, 255).
         gr_color (tuple, optional): color of grid in (RGB). Defaults to (255, 255, 255).
         filename (_type_, optional): _description_. Defaults to None.
     """     
     
     if isinstance(image, str):
          image = cv2.imread(image, 0)

     if text is not None:
          image = cv2.putText(image, text, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 4)
      
     frame = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

     if point is not None:
          for pt in point:
               if not np.isnan(pt[0]) and not np.isnan(pt[1]):
                    x = int(pt[0])
                    y = int(pt[1])
                    frame = cv2.circle(frame, (x, y), 4, p_color, -1)

     # if 'pointf' in kwargs and 'point' in kwargs:
     if pointf is not None and point is not None:
          assert len(point) == len(pointf), 'bad size'
          for i, pt0 in enumerate(point):
               pt1 = pointf[i]
               if np.isnan(pt0[0])==False and np.isnan(pt0[1])==False and np.isnan(pt1[0])==False and np.isnan(pt1[1])==False :
                    disp_x = (pt1[0]-pt0[0])*scale
                    disp_y = (pt1[1]-pt0[1])*scale
                    frame = cv2.line(frame, (int(pt0[0]), int(pt0[1])), (int(pt0[0]+disp_x), int(pt0[1]+disp_y)), l_color, 2)

     if grid is not None:
          # I could just copy the grid to make sure no adjustment is made
          dic_grid = grid
          assert isinstance(dic_grid, OLD_grid), "grid should be OLD_grid"
          for i in range(dic_grid.size_x):
               for j in range(dic_grid.size_y):
                    if (dic_grid.is_valid_number(i,j)):
                         x = int(dic_grid.grid_x[i,j]) - int(dic_grid.disp_x[i,j]*scale)
                         y = int(dic_grid.grid_y[i,j]) - int(dic_grid.disp_y[i,j]*scale)
                         
                         if i < (dic_grid.size_x-1):
                              if (dic_grid.is_valid_number(i+1,j)):
                                   x1 = int(dic_grid.grid_x[i+1,j]) - int(dic_grid.disp_x[i+1,j]*scale)
                                   y1 = int(dic_grid.grid_y[i+1,j]) - int(dic_grid.disp_y[i+1,j]*scale)
                                   frame = cv2.line(frame, (x, y), (x1, y1), gr_color, 2)

                         if j < (dic_grid.size_y-1):
                              if (dic_grid.is_valid_number(i,j+1)):
                                   x1 = int(dic_grid.grid_x[i,j+1]) - int(dic_grid.disp_x[i,j+1]*scale)
                                   y1 = int(dic_grid.grid_y[i,j+1]) - int(dic_grid.disp_y[i,j+1]*scale)
                                   frame = cv2.line(frame, (x, y), (x1, y1), gr_color, 4)
     
     if filename is not None:
          cv2.imwrite(filename, frame)
          return

     cv2.namedWindow('image', cv2.WINDOW_NORMAL)
     cv2.resizeWindow('image', frame.shape[1], frame.shape[0])
     cv2.imshow('image',frame)
     cv2.waitKey(0)
     cv2.destroyAllWindows()


      
def build_grid(area, num_point, *args, **kwargs):
     """
     
     Args:
         area (_type_): _description_
         num_point (_type_): _description_

     Returns:
         _type_: _description_
     """    
     xmin = area[0][0]; xmax = area[1][0]; dx = xmax - xmin
     ymin = area[0][1]; ymax = area[1][1]; dy = ymax - ymin
     point_surface = dx*dy/num_point; point_line = math.sqrt(point_surface)
     ratio = 1. if not 'ratio' in kwargs else kwargs['ratio']
     num_x = int(ratio*dx/point_line) + 1
     num_y = int(ratio*dy/point_line) + 1
     grid_x, grid_y = np.mgrid[xmin:xmax:num_x*1j, ymin:ymax:num_y*1j]
     return OLD_grid(grid_x, grid_y, num_x, num_y)

def write_result(result_file, image, points):
     """used by init to write the data for a file.

     Args:
         result_file (_type_): _description_
         image (_type_): _description_
         points (_type_): _description_
     """     
     result_file.write(image + '\t')
     for p in points:
          result_file.write(str(p[0]) + ',' + str(p[1]) + '\t')
     result_file.write('\n')
    

# def remove_point_outside(points, area,  *args, **kwargs):
#      shape = 'box' if not 'shape' in kwargs else kwargs['shape']
#      # what is shape doing here?
#      xmin = area[0][0]
#      xmax = area[1][0]
#      ymin = area[0][1]
#      ymax = area[1][1]
#      res = []
#      for p in points:
#           x = p[0]; y = p[1]
#           if ((x >= xmin) and (x <= xmax) and (y >= ymin) and (y <= ymax)):
#                res.append(p)
#      return np.array(res)



def init(image_pattern, win_size_px, grid_size_px, result_file, area_of_interest=None, *args, **kwargs):
     """the init function is a simple wrapper function that allows to parse a 
          sequence of images. The displacements are computed and a result file is written

     Args:
         image_pattern (str): the path and pattern describing where your image are located 
         win_size_px (list):  the size in pixel of your correlation windows.Given as a (dx, dy) tuple
         grid_size_px (list): the size of your correlation grid. Given as a (dx, dy) tuple
         result_file (str): the name of the result file
         area_of_interest (list of two tuples, optional): gives the area of interset in 
               [(top left x,top left xy),(bottom right x, bottom right y)  ] format.
                 Defaults to None.
                         if you don't give this argument, a windows with the first image is displayed. 
                         You can pick in this picture manually your area of interest.

     Parsed kwargs:
          unstructured_grid=(val1,val2) : to let the 'goodFeaturesToTrack' opencv2 algorithm. Note that you can't use the 'spline' or the 'raw' interpolation method.
     """
     img_list = sorted(glob.glob(image_pattern))
     assert len(img_list) > 1, "there is not image in " + str(image_pattern)
     img_ref = cv2.imread(img_list[0], 0)
     
     # choose area of interset 
     if (area_of_interest is None):
          print("please pick your area of interest on the picture")
          print("Press 'c' to proceed")
          # area_of_interest = pick_area_of_interest(img_ref)
          areaSelector = AreaSelectorCV2(img_ref)
          area_of_interest = areaSelector.pick_area_of_interest()

     # init correlation grid
     area     = area_of_interest

     points   = []
     points_x = np.float64(np.arange(area[0][0], area[1][0], grid_size_px[0]))
     points_y = np.float64(np.arange(area[0][1], area[1][1], grid_size_px[1]))

     if 'unstructured_grid' in kwargs:
          block_size, min_dist = kwargs['unstructured_grid']
          feature_params = dict( maxCorners = 50000,
                                 qualityLevel = 0.01,
                                 minDistance = min_dist,
                                 blockSize = block_size)
          points = cv2.goodFeaturesToTrack(img_ref, mask = None, **feature_params)[:,0]
     elif 'deep_flow' in kwargs:
          points_x = np.float64(np.arange(area[0][0], area[1][0], 1))
          points_y = np.float64(np.arange(area[0][1], area[1][1], 1))
          for x in points_x:
               for y in points_y:
                    points.append(np.array([np.float32(x),np.float32(y)]))
          points = np.array(points)
     else: 
          for x in points_x:
               for y in points_y:
                    points.append(np.array([np.float32(x),np.float32(y)]))
          points = np.array(points)


     # ok, display
     points_in = remove_point_outside(points, area, shape='box')

     
     img_ref = cv2.imread(img_list[0], 0)
     img_ref = cv2.putText(img_ref, "Displaying markers... Press any buttons to continue", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),4)

     draw_opencv(img_ref, point=points_in)

     # compute grid and save it in result file
     f = open(result_file, 'w')
     xmin = points_x[0]; xmax = points_x[-1]; xnum = len(points_x)
     ymin = points_y[0]; ymax = points_y[-1]; ynum = len(points_y)
     f.write(str(xmin) + '\t' + str(xmax) + '\t' + str(int(xnum)) + '\t' + str(int(win_size_px[0])) + '\n')
     f.write(str(ymin) + '\t' + str(ymax) + '\t' + str(int(ynum)) + '\t' + str(int(win_size_px[1])) + '\n')

     # param for correlation 
     lk_params = dict( winSize  = win_size_px, maxLevel = 10,
                       criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))
     
     # parse all files and write results file
     point_to_process = points_in
     write_result(f, img_list[0], point_to_process)
     for i in range(len(img_list)-1):
          print('reading image {} / {} : "{}"'.format(i+1, len(img_list), img_list[i+1]))
          image_ref = cv2.imread(img_list[i], 0)
          image_str = cv2.imread(img_list[i+1], 0)
          
          if 'deep_flow' in kwargs:
               winsize_x = win_size_px[0]
               final_point = cv2.calcOpticalFlowFarneback(image_ref, image_str, None, 0.5, 3, winsize_x,
                                                          10, 5, 1.2, 0)
               # prev, next, flow, pyr_scale, levels, winsize, iterations,poly_n, poly_sigma
               index = 0
               ii_max = final_point.shape[0]
               jj_max = final_point.shape[1]

               for jj in range(jj_max):
                   for ii in range(ii_max):
                      #area     = [(0,0),(img_ref.shape[1],img_ref.shape[0])]
                      if (jj >= area[0][0] and jj < area[1][0] and
                          ii >= area[0][1] and ii < area[1][1]):
                          point_to_process[index] += final_point[ii,jj]
                          index += 1

               
          else:
               final_point, st, err = cv2.calcOpticalFlowPyrLK(image_ref, image_str, point_to_process, None, **lk_params)               
               #draw_opencv(image_ref, point=points_in, pointf=final_point, l_color=(0,255,0), p_color=(0,255,0))
               point_to_process = final_point
          write_result(f, img_list[i+1], point_to_process)
     f.write('\n')
     f.close()


def read_dic_file(result_file, *args, **kwargs):
     """the read_dic_file is a simple wrapper function that allows to parse a dic 
     file (given by the init() function) and compute the strain fields. The displacement fields 
     can be smoothed thanks to many interpolation methods. A good interpolation method to do this 
     job is the 'spline' method. After this process, note that a new folder named 'pydic' is 
     created into the image directory where different results files are written. 

     These results are:
     - 'disp' that contains images where the displacement of the correlation windows are highlighted. 
          You can apply a scale to amplify these displacements.
     - 'grid' that contains images where the correlation grid is highlighted. You 
     can apply a scale to amplify the strain of this grid.
     - 'marker' that contains images  where the displacement of corraleted markers are highlighted
     - 'result' where you can find raw text file (csv format) that constain the computed displacement
     and strain fields of each picture.

     * required argument:
     - the first arg 'result_file' must be a result file given by the init() function
     * optional named arguments:
     - 'interpolation' the allowed vals are 'raw', 'spline', 'linear', 'delaunnay', 'cubic', etc... 
     a good value is 'raw' (for no interpolation) or spline that smooth your data.
     - 'save_image ' is True or False. Here you can choose if you want to save the 'disp', 'grid' and 
     'marker' result images
     - 'scale_disp' is the scale (a float) that allows to amplify the displacement of the 'disp' images
     - 'scale_grid' is the scale (a float) that allows to amplify the 'grid' images
     - 'meta_info_file' is the path to a meta info file. A meta info file is a simple csv file 
     that contains some additional data for each pictures such as time or load values.
     - 'strain_type' should be 'green_lagrange' '2nd_order' or 'log'. Default value is cauchy (or engineering) strains. You 
     can switch to log or 2nd order strain if you expect high strains. 
     - 'rm_rigid_body_transform' for removing rigid body displacement (default is true)
     """
     grid_list = [] # saving grid here
     # treat optional args
     interpolation= 'raw' if not 'interpolation' in kwargs else kwargs['interpolation']
     save_image   = True if not 'save_image' in kwargs else kwargs['save_image']
     scale_disp   = 4. if not 'scale_disp' in kwargs else float(kwargs['scale_disp'])
     scale_grid   = 25. if not 'scale_grid' in kwargs else float(kwargs['scale_grid'])
     strain_type  = 'green_lagrange' if not 'strain_type' in kwargs else kwargs['strain_type']
     rm_rigid_body_transform = True if not 'rm_rigid_body_transform' in kwargs else kwargs['rm_rigid_body_transform']
     
     # read meta info file
     meta_info = {}
     # if 'meta_info_file' in kwargs:
     if  kwargs.get('meta_info_file', None) is not None:
          print('read meta info file', kwargs['meta_info_file'], '...')
          with open(kwargs['meta_info_file']) as f:
               lines = f.readlines()
               header = lines[0]
               field = header.split()
               for l in lines[1:-1]:
                    val = l.split()
                    if len(val) > 1:
                         dictionary = dict(zip(field, val))
                         meta_info[val[0]] = dictionary
     
                
     # first read grid
     with open(result_file) as f:
          head = f.readlines()[0:2]
     (xmin, xmax, xnum, win_size_x) = [float(x) for x in head[0].split()]
     (ymin, ymax, ynum, win_size_y) = [float(x) for x in head[1].split()]
     win_size = (win_size_x, win_size_y)
     
     grid_x, grid_y = np.mgrid[xmin:xmax:int(xnum)*1j, ymin:ymax:int(ynum)*1j]
     mygrid = OLD_grid(grid_x, grid_y, int(xnum), int(ynum))

     # the results
     point_list = []
     image_list = []
     disp_list = []

     # parse the result file
     with open(result_file) as f:
          res = f.readlines()[2:-1]
          for line in res:
               val = line.split('\t')
               image_list.append(val[0])
               point = []
               for pair in val[1:-1]:
                    (x,y) = [float(x) for x in pair.split(',')]
                    point.append(np.array([np.float32(x),np.float32(y)]))
               point_list.append(np.array(point))
               grid_list.append(copy.deepcopy(mygrid))
     f.close()
               
     # compute displacement and strain
     for i, mygrid in enumerate(grid_list):
          print("compute displacement and strain field of", image_list[i], "...")
          disp = None
          if rm_rigid_body_transform:
               print("remove rigid body transform")
               disp = compute_disp_and_remove_rigid_transform(point_list[i], point_list[0])
          else:
               print("do not remove rigid body transform")
               disp = compute_displacement(point_list[i], point_list[0])
          mygrid.add_raw_data(win_size, image_list[0], image_list[i], point_list[0], point_list[i], disp)
          
          disp_list.append(disp)
          mygrid.interpolate_displacement(point_list[0], disp, method=interpolation)

          if (strain_type == 'green_lagrange'):
               mygrid.compute_strain_field()
          elif (strain_type =='2nd_order'):
               mygrid.compute_strain_field_DA()
          elif (strain_type =='log'):
               mygrid.compute_strain_field_log()
          else:
               print("please specify a correct strain_type : 'green_lagrange', 'cauchy-eng', '2nd_order' or 'log'")
               print("exiting...")
               sys.exit(0)

          # write image files
          if (save_image):
               mygrid.draw_marker_img()
               mygrid.draw_disp_img(scale_disp)
               mygrid.draw_grid_img(scale_grid)
               if win_size_x == 1 and win_size_y == 1 : 
                    mygrid.draw_disp_hsv_img()

          if not kwargs.get("unit_test_mode", False):
               # write result file
               mygrid.write_result()

          # add meta info to grid if it exists
          if (len(meta_info) > 0):
               img = os.path.basename(mygrid.image)
               #if not meta_info.has_key(img):
               if img not in meta_info.keys():
                    print("warning, can't affect meta deta for image", img)
               else:
                    mygrid.add_meta_info(meta_info.get(img))
                    print('add meta info', meta_info.get(img))
     return grid_list
                    
          


