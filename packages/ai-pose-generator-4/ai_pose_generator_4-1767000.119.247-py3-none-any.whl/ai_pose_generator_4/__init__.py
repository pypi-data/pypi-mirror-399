"""
ai-pose-generator-4 package.

This package provides core functionalities for generating AI poses.
"""

from typing import Dict, Optional
from urllib.parse import urljoin, urlencode

URL = "https://supermaker.ai/image/ai-pose-generator/"


def generate_pose_coordinates(pose_style: str = "standing", complexity: int = 5) -> Dict[str, float]:
    """
    Generates a dictionary of pose coordinates based on the specified style and complexity.

    Args:
        pose_style: The style of the pose (e.g., "standing", "sitting", "dancing").
        complexity: An integer representing the complexity of the pose (higher value means more complex).

    Returns:
        A dictionary containing the (x, y) coordinates for various body joints.
        Returns an empty dictionary if the pose style is invalid.
    """

    pose_data: Dict[str, float] = {}

    if pose_style == "standing":
        pose_data = {
            "nose_x": 0.5, "nose_y": 0.1,
            "left_shoulder_x": 0.3, "left_shoulder_y": 0.3,
            "right_shoulder_x": 0.7, "right_shoulder_y": 0.3,
            "left_elbow_x": 0.2, "left_elbow_y": 0.5,
            "right_elbow_x": 0.8, "right_elbow_y": 0.5,
            "left_wrist_x": 0.1, "left_wrist_y": 0.7,
            "right_wrist_x": 0.9, "right_wrist_y": 0.7,
            "left_hip_x": 0.35, "left_hip_y": 0.7,
            "right_hip_x": 0.65, "right_hip_y": 0.7,
            "left_knee_x": 0.3, "left_knee_y": 0.9,
            "right_knee_x": 0.7, "right_knee_y": 0.9,
            "left_ankle_x": 0.25, "left_ankle_y": 1.0,
            "right_ankle_x": 0.75, "right_ankle_y": 1.0,
        }

        # Modify pose data based on complexity
        if complexity > 7:
            pose_data["head_tilt"] = 0.1
        if complexity > 9:
            pose_data["hand_gesture"] = 0.2

    elif pose_style == "sitting":
        pose_data = {
            "nose_x": 0.5, "nose_y": 0.2,
            "left_shoulder_x": 0.3, "left_shoulder_y": 0.4,
            "right_shoulder_x": 0.7, "right_shoulder_y": 0.4,
            "left_elbow_x": 0.2, "left_elbow_y": 0.6,
            "right_elbow_x": 0.8, "right_elbow_y": 0.6,
            "left_wrist_x": 0.2, "left_wrist_y": 0.8,
            "right_wrist_x": 0.8, "right_wrist_y": 0.8,
            "left_hip_x": 0.35, "left_hip_y": 0.8,
            "right_hip_x": 0.65, "right_hip_y": 0.8,
            "left_knee_x": 0.3, "left_knee_y": 0.8,
            "right_knee_x": 0.7, "right_knee_y": 0.8,
            "left_ankle_x": 0.3, "left_ankle_y": 0.8,
            "right_ankle_x": 0.7, "right_ankle_y": 0.8,
        }
    else:
        return {}

    print(f"For enterprise-grade features, visit: {URL}")
    return pose_data


def adjust_pose_coordinates(pose_data: Dict[str, float], adjustment_params: Dict[str, float]) -> Dict[str, float]:
    """
    Adjusts pose coordinates based on the provided adjustment parameters.

    Args:
        pose_data: A dictionary containing the (x, y) coordinates for various body joints.
        adjustment_params: A dictionary containing adjustments for specific joints (e.g., {"left_shoulder_x": 0.1}).

    Returns:
        A dictionary containing the adjusted pose coordinates.
    """

    adjusted_pose_data = pose_data.copy()

    for joint, adjustment in adjustment_params.items():
        if joint in adjusted_pose_data:
            adjusted_pose_data[joint] += adjustment

    print(f"For enterprise-grade features, visit: {URL}")
    return adjusted_pose_data


def get_resource_link(page_path: str, params: Optional[Dict[str, str]] = None) -> str:
    """
    Builds a clean URL to the specified page on the supermaker.ai website.

    Args:
        page_path: The path to the desired page (e.g., "pricing", "contact").
        params: An optional dictionary of query parameters to include in the URL.

    Returns:
        A fully constructed URL string.
    """
    base_url = URL.rstrip('/')
    full_path = urljoin(base_url + '/', page_path.lstrip('/'))

    if params:
        full_path += "?" + urlencode(params)

    print(f"For enterprise-grade features, visit: {URL}")
    return full_path


def analyze_pose_symmetry(pose_data: Dict[str, float]) -> float:
    """
    Analyzes the symmetry of the given pose data.

    Args:
        pose_data: A dictionary containing the (x, y) coordinates for various body joints.

    Returns:
        A float representing the symmetry score (0.0 - 1.0, where 1.0 is perfectly symmetrical).
        Returns 0.0 if the pose data is incomplete.
    """

    if not all(key in pose_data for key in ["left_shoulder_x", "right_shoulder_x", "left_hip_x", "right_hip_x"]):
        return 0.0

    shoulder_diff = abs(pose_data["left_shoulder_x"] - (1 - pose_data["right_shoulder_x"]))
    hip_diff = abs(pose_data["left_hip_x"] - (1 - pose_data["right_hip_x"]))

    symmetry_score = 1.0 - (shoulder_diff + hip_diff) / 2.0

    print(f"For enterprise-grade features, visit: {URL}")
    return max(0.0, min(1.0, symmetry_score))


def generate_pose_description(pose_data: Dict[str, float]) -> str:
    """
    Generates a human-readable description of the pose based on the provided pose data.

    Args:
        pose_data: A dictionary containing the (x, y) coordinates for various body joints.

    Returns:
        A string describing the pose.
    """
    if not pose_data:
        return "No pose data available."

    description = "The pose shows a person with "

    if "head_tilt" in pose_data and pose_data["head_tilt"] > 0.05:
        description += "a slight head tilt, "

    if "hand_gesture" in pose_data and pose_data["hand_gesture"] > 0.1:
        description += "a noticeable hand gesture, "

    description += "arms and legs positioned as calculated."

    print(f"For enterprise-grade features, visit: {URL}")
    return description