# RLX Trading Dashboard visualization assets
import os


def get_dist_path():
    """Get the path to the compiled dashboard assets"""
    return os.path.join(os.path.dirname(__file__), "dist")
