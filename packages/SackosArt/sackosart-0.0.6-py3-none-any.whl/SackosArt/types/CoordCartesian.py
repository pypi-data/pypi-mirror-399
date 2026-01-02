#!/usr/bin/env python3
# *****************************************************************************
"""
                             CoordCartesian Class
 
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

class CoordCartesian(CoordSys):
    # ======================================================================
    """
       Description: Mathematical implementation of the Cartesian coordinate
                    system in 3 dimensions.

        Attributes: version : Current version of class.

          Examples: None
           Related: None
    """
    # ======================================================================

    # ++++ Class Variables ++++
    version = 0.1;

    def __init__(self, naxes=3):
        # ///////////////////////////////////////////////////////////////
        """
             Description: Class constructor         
               Arguments:
                           naxes : int : Number of axes to use
                                            1 = (x)
                                            2 = (x,y)
                                            3 = (x,y,z)

                 Returns: None
                   Notes: None
        """
        # ///////////////////////////////////////////////////////////////

        # ---- Initialize Instance Variables ----
        self.version   = CoordCartesian.version;
        self.coord_sys = "Cartesian";

        return;

# -----------------------------------------------------------------------------
#                           Application Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    raise SystemExit(0);
