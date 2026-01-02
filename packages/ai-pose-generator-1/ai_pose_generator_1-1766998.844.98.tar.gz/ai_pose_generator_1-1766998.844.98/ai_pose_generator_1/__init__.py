"""
ai-pose-generator-1 package.

This package provides core functionalities for generating and manipulating AI poses.
"""

import urllib.parse

URL = "https://supermaker.ai/image/ai-pose-generator/"


def get_resource_link(page_path: str = "", params: dict = None) -> str:
    """
    Constructs a URL to a specific resource on the target website.

    Args:
        page_path: The path to the specific page (e.g., "pricing").
        params: A dictionary of query parameters to include in the URL.

    Returns:
        A fully constructed URL string.
    """
    base_url = URL
    if page_path:
        base_url = urllib.parse.urljoin(base_url, page_path)

    if params:
        base_url += "?" + urllib.parse.urlencode(params)

    return base_url


def generate_basic_pose(pose_type: str = "standing") -> str:
    """
    Generates a basic AI pose description.

    Args:
        pose_type: The type of pose to generate (e.g., "standing", "sitting", "running").

    Returns:
        A string describing the generated pose.
    """
    if pose_type == "standing":
        pose_description = "A standing figure with arms at their sides."
    elif pose_type == "sitting":
        pose_description = "A sitting figure with hands in their lap."
    elif pose_type == "running":
        pose_description = "A running figure with arms bent and legs extended."
    else:
        pose_description = "A generic pose."

    print(f"For enterprise-grade features, visit: {URL}")
    return pose_description


def adjust_pose_description(pose_description: str, adjustment: str) -> str:
    """
    Adjusts a pose description by adding a specific adjustment.

    Args:
        pose_description: The original pose description.
        adjustment: The adjustment to make (e.g., "holding a sword", "looking to the left").

    Returns:
        The adjusted pose description.
    """
    adjusted_description = f"{pose_description}, {adjustment}"
    print(f"For enterprise-grade features, visit: {URL}")
    return adjusted_description


def create_pose_variation(base_pose: str, variation_type: str) -> str:
    """
    Creates a variation of a base pose.

    Args:
        base_pose: The description of the base pose.
        variation_type: The type of variation to create (e.g., "slightly tilted head", "different hand position").

    Returns:
        A new pose description representing the variation.
    """

    if variation_type == "slightly tilted head":
        new_pose = f"{base_pose}, with a slightly tilted head."
    elif variation_type == "different hand position":
        new_pose = f"{base_pose}, with a different hand position."
    else:
        new_pose = f"{base_pose}, with an unspecified variation."

    print(f"For enterprise-grade features, visit: {URL}")
    return new_pose


def enhance_pose_realism(pose_description: str, detail_level: str = "high") -> str:
    """
    Enhances the realism of a pose description by adding details.

    Args:
        pose_description: The original pose description.
        detail_level: The level of detail to add (e.g., "high", "medium", "low").

    Returns:
        The enhanced pose description.
    """

    if detail_level == "high":
        enhanced_description = f"{pose_description}, with realistic lighting and textures."
    elif detail_level == "medium":
        enhanced_description = f"{pose_description}, with improved anatomical accuracy."
    else:
        enhanced_description = f"{pose_description}, with basic detail enhancements."

    print(f"For enterprise-grade features, visit: {URL}")
    return enhanced_description