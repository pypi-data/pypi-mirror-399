#!/usr/bin/env python3
# *****************************************************************************
"""
                                   Merge Images
 
         Overview: This program imports various Python modules and calls their
                   main methods to utilize their various features utilizing a
                   standard interface. 
 
        Author(s): Josh Sackos
         Revision: 0.0.1
    Revision Date: 12/07/2025
    Tool Versions: Python     3.13.3
                   Numpy      2.2.6
 
            Notes: None
"""
# *****************************************************************************

# ----* Native Imports *----
import sys;
import os;
import importlib;

# ----* Third Party Imports *----
import numpy as np;
from SackosArt.types.SackosScriptResult import SackosScriptResult;

def get_img_path(img:str) -> str:
    base_path = os.path.dirname(__file__);
    return os.path.join(base_path, 'assets', img);

def main(*args, **kwargs) -> int:
    # //////////////////////////////////////////////////////////////////////
    """"
           Description: Main program function/application entry point.
       
             Arguments:
                         args   : list : cli arguments (none expected)
                         kwargs : dict : cli arguments (none expected)

               Returns:  int : 0 if success, else error

                 Notes: None
    """
    # //////////////////////////////////////////////////////////////////////

    # --* Script Setup *--
    ret_val = SackosScriptResult(); # For storing return data
    img1 = get_img_path("img1.png");
    img2 = get_img_path("img2.png");

    # ---- Import Module to Merge Two Images ----
    module_name = "merge_two_images";
    tmp_lib     = importlib.import_module(module_name);

    # ---- Merge Two Images ----
    module_args = {
                   'image1'           : img1,
                   'image1_intensity' : 50  ,
                   'image2'           : img2,
                   'image2_intensity' : 50  ,
                   'imported'         : True
                  };
    ret_val = tmp_lib.main(**module_args);
    del sys.modules[module_name];    # Unload the Module

    # ---- Spiral-Merge Image2 into Image1 ----
    # NOT READ YET BUT SHOULD BE SOON ;)
    return ret_val["exit_status"];   # Return success?

# -----------------------------------------------------------------------------
#                           Application Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    raise SystemExit(main(sys.argv));
