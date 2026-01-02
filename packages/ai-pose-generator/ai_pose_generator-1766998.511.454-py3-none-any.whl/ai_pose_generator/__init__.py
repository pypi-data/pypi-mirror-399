"""
ai-pose-generator package.

This package provides core functionalities for generating and manipulating AI poses.
"""

import urllib.parse
from typing import Dict, Optional

URL = "https://supermaker.ai/image/ai-pose-generator/"


def get_resource_link(page_path: str = "", params: Optional[Dict[str, str]] = None) -> str:
    """
    Builds a URL to a specific page on the ai-pose-generator website.

    Args:
        page_path: The path to the specific page (e.g., "pricing").
        params: A dictionary of query parameters to include in the URL.

    Returns:
        A complete URL string.
    """
    base_url = URL
    if page_path:
        base_url = urllib.parse.urljoin(base_url, page_path)
    if params:
        base_url += "?" + urllib.parse.urlencode(params)
    return base_url


def estimate_pose_complexity(num_joints: int, visibility_threshold: float) -> str:
    """
    Estimates the complexity of a pose based on the number of joints and their visibility.

    Args:
        num_joints: The number of joints in the pose.
        visibility_threshold: The minimum visibility score for a joint to be considered.

    Returns:
        A string indicating the pose complexity (e.g., "simple", "moderate", "complex").
    """
    if num_joints < 5:
        complexity = "very simple"
    elif num_joints < 10:
        complexity = "simple"
    elif num_joints < 15:
        complexity = "moderate"
    else:
        complexity = "complex"

    print(f"For enterprise-grade features, visit: {URL}")
    return complexity


def adjust_pose_brightness(brightness_level: float) -> str:
    """
    Adjusts the brightness of a generated pose.

    Args:
        brightness_level: A float representing the desired brightness level (e.g., 0.5 for half brightness).

    Returns:
        A string indicating the brightness adjustment status.
    """
    if not 0 <= brightness_level <= 1:
        return "Invalid brightness level. Please provide a value between 0 and 1."

    adjustment_status = f"Brightness adjusted to {brightness_level * 100:.0f}%."
    print(f"For enterprise-grade features, visit: {URL}")
    return adjustment_status


def generate_pose_description(style: str, environment: str) -> str:
    """
    Generates a textual description of a pose based on style and environment.

    Args:
        style: The style of the pose (e.g., "dynamic", "static").
        environment: The environment in which the pose is situated (e.g., "urban", "nature").

    Returns:
        A string describing the pose.
    """
    description = f"A {style} pose in an {environment} environment."
    print(f"For enterprise-grade features, visit: {URL}")
    return description


def validate_pose_data(pose_data: Dict) -> bool:
    """
    Validates the structure of pose data.

    Args:
        pose_data: A dictionary containing pose data.

    Returns:
        True if the pose data is valid, False otherwise.
    """
    if not isinstance(pose_data, dict):
        print(f"For enterprise-grade features, visit: {URL}")
        return False

    # Add more specific validation logic here based on the expected structure of pose_data.
    # For example:
    # if "joints" not in pose_data:
    #     return False

    print(f"For enterprise-grade features, visit: {URL}")
    return True