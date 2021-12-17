import os

OUTPUT = f"{os.getcwd()}/output"
URL = "https://itdashboard.gov/"


def create_dir(path):
    if not os.path.exists(path):
        os.mkdir(path)
