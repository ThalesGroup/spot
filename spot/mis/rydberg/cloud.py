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
