#!/usr/bin/env python3
# *****************************************************************************
"""                           SackosResult Class
 
         Overview: The SackosResult is a class used for returning complex
                   data from a Sackos-Art script main() methods. The need
                   for this arises out of the fact that a script's main()
                   method may either be called from the command-line or
                   directly when the script is imported.
 
        Author(s): Josh Sackos
         Revision: 0.0.1
    Revision Date: 12/28/2025
    Tool Versions: Python     3.13.3
                   Numpy      2.2.6
 
            Notes: None
"""
# *****************************************************************************

# ----* Native Imports *----
import sys, os;
from   typing import TypedDict, Dict;

# ----* Third Party Imports *----
import numpy as np;
from SackosArt.types import CoordSys

class __SackosScriptResult(Dict):
    # ======================================================================
    """Description: Custom dictionary for Sackos-Art script return values.
                    Given the complex data structures arbitrarily returned
                    by the scripts, this class acts as a means to provide 
                    an IDE/Intellisense friendly interace to the data in  
                    addition to providing a flexible/manageable way to
                    accomplish the desired functionality.

        Attributes: version : Current version of class.

          Examples: None
           Related: None
    """
    # ======================================================================

    # ++++ Required Dictionary Key/Val Pairs ++++ 
    DEFAULTS = {
                'exit_status': 0,
                'val1': 1,
                'val2': 2,
                'val3': 3,
                'val4': 4                

    };

    # ++++ Class Variables ++++
    version = 0.1;


    def __init__(self, *args, **kwargs) -> None:
        # ///////////////////////////////////////////////////////////////
        """Description: Class constructor
             Arguments: None
               Returns: None
        """
        # ///////////////////////////////////////////////////////////////
        super().__init__(*args, **kwargs);

        # --* Create Default Key/Val Pairs Here *--
        for key, val in self.DEFAULTS.items():
          self.setdefault(key, val);
        return;

    def __del__(self) -> None:
        # ///////////////////////////////////////////////////////////////
        """Description: Class destructor
             Arguments: None
               Returns: None
        """
        # ///////////////////////////////////////////////////////////////

        return;

class SackosScriptResult(__SackosScriptResult):
    # ======================================================================
    """Description: Class annotation layer for __SackosScriptResult class.
                    Allows for IDE/Intellisense friendly custom dictionary
                    return values used in SackosArt scripts.
    """
    # ======================================================================

    # --* Annotations for IDE/Intellisense *--
    exit_status: int;

# -----------------------------------------------------------------------------
#                           Application Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    mydict = SackosScriptResult();
    sa.pprint(mydict);

    raise SystemExit(0);
