#!/usr/bin/env python3
# *****************************************************************************
"""                            CoordSys Class
 
         Overview: Implementation of the CoordSys parent class that is used
                   for defining new coordinate systems for use in the
                   Sackos-Art software.
 
        Author(s): Josh Sackos
         Revision: 0.0.1
    Revision Date: 12/25/2025
    Tool Versions: Python     3.13.3
                   Numpy      2.2.6
 
            Notes: None
"""
# *****************************************************************************

# ----* Native Imports *----
import sys;
import os;

# ----* Third Party Imports *----
import numpy as np;
import matplotlib.pyplot as plt;
import math;
import SackosArt as sa;

class CoordSys():
    # ======================================================================
    """Description: Parent class for coordinate systems used by
                    Sackos-Art software.

        Attributes: version : Current version of class.

          Examples: None
           Related: None
    """
    # ======================================================================

    # ++++ Class Variables ++++
    version = 0.1;

    def __init__(self) -> None:
        # ///////////////////////////////////////////////////////////////
        """Description: Class constructor
             Arguments: None
               Returns: None
        """
        # ///////////////////////////////////////////////////////////////
        self.pi = math.pi;

        return;

    def __del__(self) -> None:
        # ///////////////////////////////////////////////////////////////
        """Description: Class destructor
             Arguments: None
               Returns: None
        """
        # ///////////////////////////////////////////////////////////////

        return;

    def plot(self, data, system):
        # ///////////////////////////////////////////////////////////////
        """Description: 
             Arguments: 
               Returns:
        """
        # ///////////////////////////////////////////////////////////////
        system = system.lower();
        fig    = plt.figure();

        # --* Polar Plot *--
        if system == 'polar':
            r     = [x for x,y in data];
            theta = [y for x,y in data];
            plt.polar(theta, r, marker='o');
        
        # --* Cartesian Plot *--
        elif system == 'cartesian':
            x = [x1 for x1,y1 in data];
            y = [y1 for x1,y1 in data];
            plt.plot(x,y, marker='p');
        
        # --* Cylindrical Plot *--
        elif system == 'cylindrical':
          pass;

        # --* Spherical Plot *--
        elif system == 'spherical':
          pass;

        # --* Handle mouse clicks for data points *--
        def onclick(event):
            if event.xdata is not None and event.ydata is not None:
                print(f"Clicked at: ({event.xdata:.3f}, {event.ydata:.3f})")
        fig.canvas.mpl_connect('button_press_event', onclick)


        # --* Show Plot *--
        plt.show();

        return;

    def rad2deg(self,
                rads  : np.ndarray[float] | float,
                reduce: bool=True
        ) -> list[float] | float:
        # ///////////////////////////////////////////////////////////////
        """Description: Converts rad to degrees.
             Arguments: 
                        rads   : Converts radian value(s) to degrees
                        reduce : Mod degree values so no result exceeds
                                 360° 
                                       -> True  = Reduce values
                                       -> False = Preserve value 

               Returns: rad value(s) in degrees
        """
        # ///////////////////////////////////////////////////////////////
        degrees = rads*(180.0/self.pi);
        return( (degrees % 360.0) if reduce else degrees );

    def deg2rad(self,
                degs  : np.ndarray[float] | float,
                reduce: bool=True
        ) -> np.ndarray[float] | float:
        # ///////////////////////////////////////////////////////////////
        """Description: Converts degrees to rad.
             Arguments: 
                        degs   : Degree value(s) to convert.
                        reduce : Mod degree values so no
                                 result exceeds 2π.
                                     -> True  = Reduce values
                                     -> False = Preserve value 

               Returns: rad value in degrees
        """
        # ///////////////////////////////////////////////////////////////
        rad = (degs*(self.pi/180.0));
        return( (rad % (2*self.pi)) if reduce else rad );

    def cart2polar(self,
                   coords: list[tuple[float,float]]
        ) -> list[tuple[float,float]]:
        # ///////////////////////////////////////////////////////////////
        """Description: Converts Cartesian coordinates to Polar
                        coordinates.
             Arguments: 
                        coords : List of (x,y) tuples to be converted to
                        polar coordinate.

               Returns:  Polar coordinate equivalent tuples
                         in the form of (r,θ).
                         
                         NOTE: θ = rad
        """
        # ///////////////////////////////////////////////////////////////
        return [(math.sqrt((x**2+y**2)),math.atan2(y,x)) for x,y in coords];

    def polar2cart(self,
                   coords: list[tuple[float,float]]
        ) -> list[tuple[float,float]]:
        # ///////////////////////////////////////////////////////////////
        """Description: Converts Polar coordinates to Cartesian
                        coordinates.
             Arguments: 
                        coords : List of (r,θ) polar tuples to be
                                 converted to Cartesian coordinates. 
                                 
                                 NOTE: θ = radian.

               Returns: Cartesian coordinate equivalent tuples in the
                        form of (x,y).
        """
        # ///////////////////////////////////////////////////////////////
        return [(r*math.cos(θ),r*math.sin(θ)) for r,θ in coords];

# -----------------------------------------------------------------------------
#                           Application Entry Point
# -----------------------------------------------------------------------------
if __name__ == "__main__":

    reduce        = False;
    coordsys_inst = CoordSys();

    # --* Cartesian Example *--
    cart_coords = [
                    (  math.sqrt (2)/2 ,  math.sqrt(2)/2 ), # Quadrant 1 @ 45°
                    ( -math.sqrt (2)/2 ,  math.sqrt(2)/2 ), # Quadrant 2 @ 135°
                    ( -math.sqrt (2)/2 , -math.sqrt(2)/2 ), # Quadrant 3 @ 225°
                    (  math.sqrt (2)/2 , -math.sqrt(2)/2 )  # Quadrant 4 @ 315°
    ];

    polar_coords = coordsys_inst.cart2polar(cart_coords);
#    coordsys_inst.plot(polar_coords, system='polar');

    # --* Polar Example *--
    polar_coords = [
                    (  1 ,    math.pi /4.0 ), # Quadrant 1 @ 45°
                    (  1 , (3*math.pi)/4.0 ), # Quadrant 2 @ 135°
                    (  1 , (5*math.pi)/4.0 ), # Quadrant 3 @ 225°
                    (  1 , (7*math.pi)/4.0 )  # Quadrant 4 @ 315°
    ];
    cart_coords = coordsys_inst.polar2cart(polar_coords);
#    coordsys_inst.plot(cart_coords, system='cartesian');

    raise SystemExit(0);
