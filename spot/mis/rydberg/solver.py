# File   : solver.py
# Project: spot
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.03.2026

import qoolqit
import pulser
from pulser.devices import AnalogDevice, MockDevice
from pulser_pasqal.backends import EmuMPSBackend

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
            username=manager.username,
            password=manager.password,
            project_id=manager.project_id,
        )
        return connection

    def get_backend(self, seq):
        """ backend_type : "local_emulator", "emu_mps_remote_emulator", "fresnel_can1"
        """
        if self.backend_type == "local_emulator":
            backend = pulser.backends.QutipBackendV2(seq)

        elif self.backend_type=="emu_mps_remote_emulator":

            config = pulser.backend.BackendConfig(
                default_num_shots=self.num_shots)
            backend = pulser.backends.EmuMPSBackend(
                seq,
                connection,
                config)

        elif self.backend_type == "fresnel_can1":

            config = pulser.backend.BackendConfig(
                default_num_shots=self.num_shots)
            backend = pulser.backends.QPUBackend(
                seq,
                connection,
                config=config)

        return backend

    def get_device(self):
        """ Gets device
        """
        if self.backend_type=="local_emulator" or "emu_mps_remote_emulator":
            # device = replace(AnalogDevice.to_virtual(), max_radial_distance=900)
            device = MockDevice

        elif self.bakcend_type=="fresnel_can1":
            device = qoolqit.devices.Device(
                    pulser_device=self.get_connection().fetch_available_devices()["FRESNEL_CAN1"])
        return device
