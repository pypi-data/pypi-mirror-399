#!/usr/bin/env python3
# *****************************************************************************
"""
                           CoordCylindrical Class
 
         Overview: None
 
        Author(s): Josh Sackos
         Revision: 0.0.1
    Revision Date: 12/25/2025
    Tool Versions: Python     3.13.3
                   Numpy      2.2.6
 
            Notes: None
"""
# *****************************************************************************

# ----* Native Imports *----
import sys
import os

# ----* Third Party Imports *----
import numpy as np
import CoordSys

class CoordCylindrical(CoordSys):
    # ======================================================================
    """
       Description: Mathematical implementation of the Cylindrical
                    coordinate system.

        Attributes: version : Current version of class.

          Examples: None
           Related: None
    """
    # ======================================================================

    # ++++ Class Variables ++++
    version = 0.1;

    def __init__(self):
        # ///////////////////////////////////////////////////////////////
        """
             Description: Class constructor
               Arguments: None
                 Returns: None
                   Notes: None
        """
        # ///////////////////////////////////////////////////////////////

        # ---- Initialize Instance Variables ----
        self.version   = CoordCylindrical.version;
        self.coord_sys = "Cylindrical";

        return;

# -----------------------------------------------------------------------------
#                           Application Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    raise SystemExit(0);
