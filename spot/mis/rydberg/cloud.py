# File   : cloud.py
# Project: spot
# Author : Michel Nowak <michel.nowak@thalesgroup.com>
# Date   : 16.03.2026
#
# Copyright 2026 Thales
#
# Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import os
from pasqal_cloud import SDK


class PasqalCloudManager():
    """
    """
    def __init__(self):
        """
        """
        self.project_id = os.environ.get("PASQAL_CLOUD_PROJECT_ID")
        self.username = os.environ.get("PASQAL_CLOUD_USERNAME")
        self.password = os.environ.get("PASQAL_CLOUD_PASSWORD")

    def build_sdk(self):
        self.sdk= SDK(
                username=self.username,
                password=self.password,
                project_id=self.project_id)
                
    def get_jobs(self):
        """
        """
        print(self.sdk.get_jobs())

    def cancel_jobs(self):
        """
        """
        self.sdk.cancel_jobs()
