#!/usr/bin/env python3
# *****************************************************************************
"""
                                   Merge Images
 
         Overview: This program imports 2 JPEG images using OpenCV-4, extracts
                   the raw pixel data, merges the two images together with
                   variable pixel intensities for each respective image.
 
        Author(s): Josh Sackos
         Revision: 0.0.1
    Revision Date: 12/07/2025
    Tool Versions: Python     3.13.3
                   OpenCV 4   4.11.0
                   Numpy      2.2.6
 
            Notes: Still need to account for pixel value overflow.
"""
# *****************************************************************************

# ----* Native Imports *----
import sys
import os

# ----* Third Party Imports *----
import numpy as np
import cv2
from SackosArt.types.SackosScriptResult import SackosScriptResult


def main(*args, **kwargs) -> SackosScriptResult:
    # //////////////////////////////////////////////////////////////////////
    """
           Description: Main program function/application entry point.
             Arguments:
                         args : list : Command-line arguments
       
                                       args[0] = image1 path
                                       args[1] = image1 pixel intensity
                                       args[2] = image2 path
                                       args[3] = image2 pixe2 intensity

                         kwargs : dict : Same as Command-line arguments
                                         but in dictionary form. Key/Value
                                         pairs will be interpreted left to
                                         right and only values extracted.

                                         NOTE: kwargs not used if args
                                               is used and vice versa.
       
                         Example Arguments:
                                            args[0] = georgy_feet.jpg
                                            args[1] = 50
                                            args[2] = georgy_flower.jpg
                                            args[3] = 75

               Returns:  dict : {'exit_status':int}  : System Exit Status
                                {'result':np.ndarray}: Merged OpenCV 4 Img

                 Notes: Returns a dict containing the result/merged image
                        numpy array. (Allows for uniform interface between
                        unrelated Python modules)
    """
    # //////////////////////////////////////////////////////////////////////

    # --* Script Setup *--
    ret_val = SackosScriptResult(); # For storing return data

    # ---- Process CLI Arguments ----
    isCLI          = False if "imported" in kwargs.keys() else True;
    args           = args[0] if isCLI else [];
    # Convert dictionary kwargs to list style since it was already written :P
    for i, (key, val) in enumerate(kwargs.items()):
        if i >= 4:
            break;
        args.append(val);

    # Data should be in list form ready for use now. This isn't always
    # necessary. I just don't have a lot of time right now since i'm working
    # fulltime. Cheers!
    file1          = args[0];
    img1_intensity = (((args[1] % 100)/100.0) if args[1] != 100 else 1.0) \
                     if ( args[1] > 1.0 ) else ( args[1] );
    fname1         = os.path.abspath(file1).replace('\\', '/').split('/')[-1];
    file2          = args[2];
    img2_intensity = (((args[3] % 100)/100.0) if args[3] != 100 else 1.0) \
                     if ( args[3] > 1.0 ) else ( args[3] );
    fname2         = os.path.abspath(file2).replace('\\', '/').split('/')[-1];
    
    # ----- Import Images -----
    try:
        img1  = cv2.imread(file1, cv2.IMREAD_COLOR);
        img2  = cv2.imread(file2, cv2.IMREAD_COLOR);
    except:
        print("ERROR: Could not open images, aborting...");
        return {'exit_status':-1};

    # ----- Resize Images -----
    img1_scaled = cv2.resize(img1, None, fx=0.25, fy=0.25, \
                             interpolation=cv2.INTER_AREA);
    img2_scaled = cv2.resize(img2, None, fx=0.25, fy=0.25, \
                             interpolation=cv2.INTER_AREA);

    # ----- Create Destination Matrix -----
    img = np.zeros(img1_scaled.shape, dtype=np.uint8);

    # ----- Merge Both Images -----
    img[:, :, 0] = (img1_scaled[:, :, 0]*img1_intensity) + \
                   (img2_scaled[:, :, 0]*img2_intensity);
    img[:, :, 1] = (img1_scaled[:, :, 1]*img1_intensity) + \
                   (img2_scaled[:, :, 1]*img2_intensity);
    img[:, :, 2] = (img1_scaled[:, :, 2]*img1_intensity) + \
                   (img2_scaled[:, :, 2]*img2_intensity);
    ret_val['result'] = img;

    # ----- Show Merged Image -----
    showImage("Merged Image" , img);
    
    # ---- Save Image ----
    fname1 = fname1.replace('.jpg', '').replace('.png', '').replace('.gif', '');
    fname2 = fname2.replace('.jpg', '').replace('.png', '').replace('.gif', '');

    save_path = '/'.join(os.path.abspath(file1).replace('\\', '/').split("/")\
                [0:-1]) + '/' + fname1 + "_" + fname2 + '.jpg';
    
    cv2.imwrite(save_path, img);

    # ---- Wait for Keypress ----
    cv2.waitKey(0);

    # ---- Return success command-line, and image if imported by module ----
    ret_val['exit_status'] = 0;
    return ret_val;

def showImage(wTitle, img) -> None:
    # //////////////////////////////////////////////////////////////////////
    """
            Description: Displays numpy matrix as an image via OpenCV
                         imshow().
    
              Arguments:
                         wTitle : str     : Window title
                         img    : ndarray : Numpy matrix
    
                Returns: None
    """
    # //////////////////////////////////////////////////////////////////////
    cv2.imshow(wTitle, img);
    return;

# -----------------------------------------------------------------------------
#                           Application Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    try:
        args    = sys.argv[1:5];
        args[0] = args[0].replace('\\', '/'); # Use unix filepath separator
        args[1] = float(args[1]);             # Convert intensity to integer
        args[2] = args[2].replace('\\', '/'); # Use unix filepath separator
        args[3] = float(args[3]);             # Convert intensity to integer

    except:
        print("Invalid arguments. Expected Command Line Arguments:");
        print("\targs[0] = image1 path"                            );
        print("\targs[1] = image1 pixel intensity"                 );
        print("\targs[2] = image2 path"                            );
        print("\targs[3] = image2 pixel intensity"                 );
        raise SystemExit(-1); # Return error

#    raise SystemExit(main(args, imported=True)[0]);
    raise SystemExit(main(args)['exit_status']);
