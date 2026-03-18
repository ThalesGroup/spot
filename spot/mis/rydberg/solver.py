# File   : solver.py
# Project: spot
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.03.2026

from dataclasses import replace
import qoolqit
import pulser
from pulser.devices import AnalogDevice, MockDevice
from pulser_pasqal import PasqalCloud
from pulser_pasqal.backends import EmuMPSBackend

from qubosolver.config import SolverConfig, QPU, RemoteEmulator

from spot.mis.solver import Solver
from spot.mis.rydberg.cloud import PasqalCloudManager



class RydbergSolver(Solver):
    """
    """
    def __init__(self, params):
        """
        """
        super().__init__(params=params)
        self.num_shots = 100
        self.backend_type = params.get("backend_type", "local_emulator")

    def get_connection(self, device_name="FRESNEL_CAN1"):
        """ return connection via pasqal cloud
        """
        manager = PasqalCloudManager()

        connection = PasqalCloud(
            project_id=manager.project_id,
            username=manager.username,
            password=manager.password,
        )
        return connection

    def get_backend(self, seq):
        """ get backend for pulse solver
        """
        if self.backend_type == "local_emulator":
            backend = pulser.backends.QutipBackendV2(seq)

        elif self.backend_type=="emu_mps_remote_emulator":

            backend = pulser.backends.EmuMPSBackend(
                seq,
                connection=self.get_connection())

        elif self.backend_type == "fresnel_can1":

            backend = pulser.backends.QPUBackend(
                seq,
                connection=self.get_connection())

        return backend

    def get_device(self):
        """ Gets device for pulse solver
        """
        if self.backend_type=="local_emulator":
            device = MockDevice
        elif self.backend_type=="emu_mps_remote_emulator":
            device = AnalogDevice
        elif self.backend_type=="fresnel_can1":
            device = self.get_connection().fetch_available_devices()["FRESNEL_CAN1"]
        return device

    def get_qubo_backend(self):
        """
        """
        return QPU(connection=self.get_connection(), runs=self.num_shots)

    def get_qubo_device(self):
        """
        """
        if self.backend_type=="emu_mps_remote_emulator":
            device = replace(AnalogDevice.to_virtual(), max_radial_distance=900)
            device = RemoteEmulator(
                 backend_type = EmuMPSBackend,
                 connection = self.get_connection()
             )
        elif self.backend_type=="fresnel_can1":
            device = qoolqit.devices.Device(
                    pulser_device=self.get_connection().fetch_available_devices()["FRESNEL_CAN1"])
        return device



