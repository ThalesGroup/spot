# Project: spot
# File   : satellite.py
# Author : Michel Nowak <michel.nowak@thalesgroup.com> 
# Date   : 16.10.2025

import numpy as np
from gymnasium import Env, spaces
import os
import ephem
import math
import logging
import json
import csv
import datetime as dt

import orekit
vm = orekit.initVM()
from orekit.pyhelpers import setup_orekit_curdir
orekit_data = os.environ.get("OREKIT_DATA")
setup_orekit_curdir(orekit_data)
from org.hipparchus.geometry.euclidean.threed import RotationConvention, RotationOrder, Vector3D
from org.orekit.attitudes import TargetPointing, LofOffset
from org.orekit.data import DataSource
from org.orekit.files.general import EphemerisFileParser
from org.orekit.bodies import OneAxisEllipsoid
from org.orekit.frames import FramesFactory, LOFType
from org.orekit.orbits import CartesianOrbit
from org.orekit.propagation import SpacecraftState
from org.orekit.propagation.analytical import Ephemeris
from org.orekit.time import AbsoluteDate, TimeScalesFactory, DateComponents
from org.orekit.utils import IERSConventions, Constants, PVCoordinates
from org.orekit.propagation.analytical.tle import TLE, TLEPropagator
from java.util import ArrayList

from spot.rl.environments.utils import datetime_to_absolutedate
from spot.rl.environments.utils import absolutedate_to_datetime
from spot.rl.environments.utils import compute_tmax

class SatelliteEnvironment(Env):
    """ Satellite gym environment
    """
    def __init__(self, shift_day=0):
        """ Initializer
        """
        self.date = dt.datetime(2026, 3, 9,0,0,0,0) + dt.timedelta(days=int(shift_day))
        self.initial_date = self.date
        self.observation_shape = (1)
        self.observation_space = spaces.Box(
                low=np.array([-30/180*np.pi]),
                high=np.array([30/180*np.pi]),
                dtype=np.float64)
        self.action_space = spaces.Box(
                low=np.array([-np.pi, -np.pi, -np.pi]),
                high=np.array([np.pi, np.pi, np.pi]),
                dtype=np.float64)
        self.elapsed_time = 0
        self.current_step = 0
        self.delta_t = 1 # seconds
        self.pitch= 0
        self.yaw= 0
        self.roll= 0
        self.pitches = []
        self.yaws= []
        self.rolls= []
        self.requests_status = []
        self.map = None
        self.night = None
        self.completed_slots = []
        self.requests = []
        self.precomputed_trajectory = False
        # Logging configuration
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        date_strftime_format = "%d-%b-%y %H:%M:%S"
        self.output_file_name = "satellite.listing"
        logging.basicConfig(filename=self.output_file_name,
                            filemode='w',
                            datefmt=date_strftime_format,
                            level=logging.INFO,
                            format='%(asctime)s | %(name)s | %(message)s')

        self.logger = logging.getLogger('satellite')

        self.reset()

    def init_from_tle(self, tle_string):
        """
        """
        self.precomputed_trajectory = True
        self.logger.info("Computing trajectory from TLE")
        tle = TLE(tle_string[0], tle_string[1])

        tle_propagator = TLEPropagator.selectExtrapolator(tle)
        tle_orbit_cart = tle_propagator.getInitialState().getOrbit()
        eme_frame = FramesFactory.getEME2000()

        states = ArrayList()

        self.initial_date = self.date
        date = datetime_to_absolutedate(self.date)
        end_date = datetime_to_absolutedate(self.date + dt.timedelta(days=1))

        cdate = date 
        positions= []
        current_state = tle_propagator.propagate(cdate)
        for date_index in range(0, 60*60*24):
            current_state = tle_propagator.propagate(cdate)

            states.add(current_state)

            earth = OneAxisEllipsoid(
                    Constants.WGS84_EARTH_EQUATORIAL_RADIUS,
                    Constants.WGS84_EARTH_FLATTENING,
                    FramesFactory.getITRF(IERSConventions.IERS_2010, False));

            position = earth.transform(
                    current_state.getPosition(),
                    eme_frame,
                    current_state.getDate());

            positions.append(position)
            cdate = cdate.shiftedBy(1.)
        self.positions = []

        for sat_pos in positions:
            self.positions.append([
                sat_pos.getLongitude()*180/np.pi, 
                sat_pos.getLatitude()*180/np.pi]) 
        self.eph = Ephemeris(states, 8)

    def reset(self):
        """ resets the environment
        """
        self.elapsed_time = 0
        self.current_step = 0
        self.state = np.random.rand(1)
        self.requests_success = np.zeros(len(self.requests))
        self.requests_in_range = np.zeros(len(self.requests))
        self.requests_in_shade = np.zeros(len(self.requests))
        self.requests_status = np.zeros(len(self.requests))

    def step(self, action):
        """ Step: moves the satellite
        """
        self.current_step += 1

        # increment date with delta_t
        self.date += dt.timedelta(seconds=self.delta_t)

        # given the action given by the agent, change the orientation of the
        # satellite
        self.roll= action[0]
        self.pitch= action[1]
        self.yaw = action[2]

        # TODO update the reard given the action taken
        reward = 0.

        # record positions of the satellite
        self.current_position = self.positions[self.elapsed_time]

        # update requests in shade status
        self.update_requests_in_shade()
        
        # check if request is in range and in daylight
        self.update_requests_in_range()

        # update request status
        self.update_requests_status()

        next_state = np.random.rand(1)

        done = False

        self.elapsed_time += self.delta_t

        return next_state, reward, done

    def update_requests_in_range(self):
        """ Checks if request is in range and not in shade
        """
        sat_pos = self.current_position

        max_range = 10# degrees on earth latitude and longitude

        for i, request in enumerate(self.requests):
            lon, lat = request[0], request[1]

            x_sat_min = sat_pos[0] - max_range
            x_sat_max = sat_pos[1] + max_range

            y_sat_min = sat_pos[0]- max_range
            y_sat_max = sat_pos[1]+ max_range

            self.requests_in_range[i] = 0
            if x_sat_min <= lon and \
               lon <= x_sat_max and \
               y_sat_min <= lat and \
               lat <= y_sat_max:
                   if not self.requests_in_shade[i]:
                       self.requests_success[i] = 1
                       self.requests_in_range[i] = 1

    def update_requests_status(self):
        """ Updates request satatus
            0 in shade and not accomplished
            1 not in shade and not accomplished
            2 in shade and accomplished
        """
        for i in range(len(self.requests)):
            if not self.requests_in_shade[i]:
                if self.requests_success[i]:
                    self.requests_status[i] = 2
                else:
                    self.requests_status[i] = 1
            else:
                if self.requests_success[i]:
                    self.requests_status[i] = 2
                else:
                    self.requests_status[i] = 0
    

    def update_requests_in_shade(self):
        """ updates booleans to tell if request is in shade or not
        """
        pos = self.current_position
        o = ephem.Observer()
        o.long = pos[0]
        o.lat = pos[1]
        o.date = self.date
        s = ephem.Sun()
        s.compute(o)

        for request_id, request in enumerate(self.requests):
            if s.alt > 0:
                self.requests_in_shade[request_id] = 1
            else:
                self.requests_in_shade[request_id] = 0

    def compute_data_take_opportunity(self, requests):
        """ Computes data take opportunity
        """
        start_date = self.date
        self.requests = requests

        requests_dtos = np.zeros((len(self.requests), 2))
        dtos_finished = np.zeros(len(self.requests))
        dtos_started = np.zeros(len(self.requests))

        self.reset()

        self.logger.info("Computing data take opportunity")

        while(self.elapsed_time < 60*60*24):
            self.step([0., 0., 0.])

            for i in range(len(self.requests)):
                if self.requests_in_range[i]:
                    if not dtos_started[i]:
                        requests_dtos[i][0] = (self.date - start_date) / dt.timedelta(seconds=1)
                        dtos_started[i] = 1
                if dtos_started[i] and not self.requests_in_range[i]:
                    if not dtos_finished[i]:
                        requests_dtos[i][1] = (self.date - start_date) / dt.timedelta(seconds=1)
                        dtos_finished[i] = 1

        for i in range(len(self.requests)):
            if not dtos_finished[i]:
                requests_dtos[i][1] = (self.date - start_date) / dt.timedelta(seconds=1)

        return requests_dtos

    def pointing_to_attitude(self, current_date, target):
         """
         Compute the satellite attitude when pointing to a target point on Earth
    
         :param eph: the satellite orbit (Orekit Ephemeris object)
         :param current_date: the time of computing
         :param target: the geodetic point on Earth (Orekit GeodeticPoint object)
         :return: the Euler attitude angles (Roll Pitch and Yaw) in the Local Orbital Frame [in radians]
         """
    
         # Transform geodetic point to ITRF
         itrf = FramesFactory.getITRF(IERSConventions.IERS_2010, True)
         earth_shape = OneAxisEllipsoid(Constants.WGS84_EARTH_EQUATORIAL_RADIUS, Constants.WGS84_EARTH_FLATTENING, itrf)
         itrf_point = earth_shape.transform(target)
    
         # Target pointing law in ITRF
         target_law = TargetPointing(self.eph.getFrame(), earth_shape.getBodyFrame(), itrf_point)
    
         # Satellite attitude at currentDate when pointing to target
         target_attitude = target_law.getAttitude(self.eph, current_date, self.eph.getFrame())
    
         # Get roll, pitch, yaw angles corresponding to this pointing law
         lof_aligned_law = LofOffset(self.eph.getFrame(), LOFType.VVLH)  # Nadir pointing law
         lof_aligned_rot = lof_aligned_law.getAttitude(self.eph, current_date, self.eph.getFrame()).getRotation()
         roll_pitch_yaw = target_attitude.getRotation().compose(lof_aligned_rot.revert(),
                                                                RotationConvention.VECTOR_OPERATOR).revert    ()
         angles = roll_pitch_yaw.getAngles(RotationOrder.XYZ, RotationConvention.VECTOR_OPERATOR)
    
         return angles

    def get_acquisition_duration(self, distance, initialDate, initialPoint):
        """
        """
        # Initialisations
        alt = 550_000  # altitude in meters
        SATELLITE_SPEED = 4.4  # in km/s
        RE = 6378137.0  # WGS84_EARTH_EQUATORIAL_RADIUS in meters
    
        # Get pitch angle at date t
        angles = self.pointing_to_attitude(initialDate, initialPoint)
        pitch = angles[1]
    
        # Sat-target distance
        cos_pitch = math.cos(pitch)
        term1 = (RE + alt) * cos_pitch
        term2 = math.sqrt(RE * RE - ((RE + alt) * (RE + alt)) * (1 - cos_pitch * cos_pitch))
        lsp = term1 - term2
        cosac = term2 / RE
    
        # Guidance duration (duration in seconds)
        guidanceDuration = distance / (SATELLITE_SPEED * 1000.0) / (lsp / (alt * cosac))
        guidanceDuration = round(guidanceDuration)  # Round to the closest second
        return guidanceDuration

    def get_maneuver_duration(self, initial_euler_angles, final_euler_angles):
        """
        Compute the maneuver duration to rally two attitudes
    
        :param initial_euler_angles: Initial Euler attitude angles (Roll Pitch and Yaw) in the Local Orbital Frame [in radians]
        :param final_euler_angles: Final Euler attitude angles (Roll Pitch and Yaw) in the Local Orbital Frame [in radians]
        :return: the maneuver duration [in seconds]
        """
    
        t_man = []
        for i in range(len(initial_euler_angles)):
            delta_angle = abs(final_euler_angles[i] - initial_euler_angles[i])
            t_man.append(compute_tmax(math.degrees(delta_angle), i))
    
        # Computation of the global duration = maximum between the roll, pitch and yaw duration
        if t_man[0] >= t_man[1]:
            if t_man[2] >= t_man[0]:
                duration = t_man[2]
            else:
                duration = t_man[0]
        else:
            if t_man[2] >= t_man[1]:
                duration = t_man[2]
            else:
                duration = t_man[1]
    
        # Round to nearest dt_aocs
        dt_aocs = 0.125
        duration = math.ceil(duration / dt_aocs) * dt_aocs
    
        return duration
