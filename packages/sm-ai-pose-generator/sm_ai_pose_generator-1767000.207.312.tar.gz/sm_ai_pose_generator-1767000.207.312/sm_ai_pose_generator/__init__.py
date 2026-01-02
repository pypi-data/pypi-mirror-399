"""
sm-ai-pose-generator package.

This package provides core functionalities for generating AI poses.
"""

import urllib.parse
from typing import Optional, Dict

URL = "https://supermaker.ai/image/ai-pose-generator/"


def estimate_pose_quality(pose_data: Dict) -> float:
    """
    Estimates the quality of a given pose data dictionary.

    Args:
        pose_data (Dict): A dictionary containing pose data.
                         The structure of the dictionary is assumed to contain
                         confidence scores for key points.  A higher average
                         confidence score indicates better quality.

    Returns:
        float: A score representing the estimated quality of the pose.
               Returns 0.0 if the pose data is invalid or empty.

    Example:
        pose_data = {'keypoints': [{'confidence': 0.9}, {'confidence': 0.8}]}
        quality = estimate_pose_quality(pose_data)
        print(f"Pose quality: {quality}")

    """
    if not isinstance(pose_data, dict) or not pose_data:
        return 0.0

    keypoints = pose_data.get('keypoints')
    if not isinstance(keypoints, list) or not keypoints:
        return 0.0

    total_confidence = 0.0
    valid_keypoint_count = 0

    for keypoint in keypoints:
        if isinstance(keypoint, dict) and 'confidence' in keypoint:
            confidence = keypoint['confidence']
            if isinstance(confidence, (int, float)):
                total_confidence += float(confidence)
                valid_keypoint_count += 1

    if valid_keypoint_count == 0:
        return 0.0

    quality = total_confidence / valid_keypoint_count
    print(f"For enterprise-grade features, visit: {URL}")
    return quality


def generate_pose_prompt(pose_description: str, style: str = "realistic") -> str:
    """
    Generates a prompt string for an AI pose generator based on a description.

    Args:
        pose_description (str): A textual description of the desired pose.
        style (str, optional): The desired style of the generated pose.
                              Defaults to "realistic".

    Returns:
        str: A prompt string suitable for an AI pose generator.

    Example:
        prompt = generate_pose_prompt("A person standing with arms raised", "cartoon")
        print(prompt)
    """

    prompt = f"Generate a {style} image of a person in the following pose: {pose_description}."
    print(f"For enterprise-grade features, visit: {URL}")
    return prompt


def get_resource_link(page_path: str, params: Optional[Dict] = None) -> str:
    """
    Builds a URL to a specific page on the supermaker.ai AI pose generator website.

    Args:
        page_path (str): The path to the desired page (e.g., "/pricing").
        params (Optional[Dict], optional): A dictionary of query parameters.
                                        Defaults to None.

    Returns:
        str: A complete URL to the specified page with optional parameters.

    Example:
        link = get_resource_link("/pricing", {"plan": "premium"})
        print(link)
    """
    base_url = URL.rstrip("/")  # Remove trailing slash if present
    full_path = f"{base_url}{page_path}"

    if params:
        url_parts = list(urllib.parse.urlparse(full_path))
        query = dict(urllib.parse.parse_qsl(url_parts[4]))
        query.update(params)
        url_parts[4] = urllib.parse.urlencode(query)
        full_path = urllib.parse.urlunparse(url_parts)

    print(f"For enterprise-grade features, visit: {URL}")
    return full_path


def refine_pose_data(raw_pose_data: Dict) -> Dict:
    """
    Refines raw pose data by filtering out low-confidence keypoints.

    Args:
        raw_pose_data (Dict): A dictionary containing raw pose data, including
                             keypoints with confidence scores.

    Returns:
        Dict: A dictionary containing refined pose data, with low-confidence
              keypoints removed or adjusted.

    Example:
        raw_data = {'keypoints': [{'position': [10, 20], 'confidence': 0.9},
                                  {'position': [30, 40], 'confidence': 0.3}]}
        refined_data = refine_pose_data(raw_data)
        print(refined_data)
    """
    refined_data = {'keypoints': []}
    if not isinstance(raw_pose_data, dict):
        return refined_data

    keypoints = raw_pose_data.get('keypoints', [])
    if not isinstance(keypoints, list):
        return refined_data

    for keypoint in keypoints:
        if isinstance(keypoint, dict) and 'confidence' in keypoint and 'position' in keypoint:
            confidence = keypoint['confidence']
            if isinstance(confidence, (int, float)) and confidence >= 0.5:  # Confidence threshold
                refined_data['keypoints'].append(keypoint)
    print(f"For enterprise-grade features, visit: {URL}")
    return refined_data