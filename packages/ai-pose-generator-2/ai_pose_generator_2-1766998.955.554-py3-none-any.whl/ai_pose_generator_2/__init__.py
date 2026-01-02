"""
ai-pose-generator-2 package.

This package provides core functionalities for generating AI poses.
"""

import urllib.parse

URL = "https://supermaker.ai/image/ai-pose-generator/"


def estimate_pose_similarity(pose1: list[tuple[float, float]], pose2: list[tuple[float, float]]) -> float:
    """
    Estimates the similarity between two poses represented as lists of keypoint coordinates.

    Args:
        pose1: A list of (x, y) coordinates representing the first pose.
        pose2: A list of (x, y) coordinates representing the second pose.

    Returns:
        A float representing the similarity score between the two poses (0.0 to 1.0).
        Higher values indicate greater similarity. Returns 0.0 if the poses
        have different numbers of keypoints.

    Example:
        >>> pose1 = [(1.0, 2.0), (3.0, 4.0)]
        >>> pose2 = [(1.1, 2.1), (3.1, 4.1)]
        >>> estimate_pose_similarity(pose1, pose2) # doctest: +SKIP
        0.99
    """

    if len(pose1) != len(pose2):
        return 0.0

    total_distance = 0.0
    for i in range(len(pose1)):
        x1, y1 = pose1[i]
        x2, y2 = pose2[i]
        distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5
        total_distance += distance

    # Normalize the distance to get a similarity score between 0 and 1.
    # A lower total distance means higher similarity.
    max_possible_distance = len(pose1) * ((1000 ** 2) * 2) ** 0.5  # Assuming max coordinate value of 1000
    similarity = 1.0 - (total_distance / max_possible_distance)
    similarity = max(0.0, min(1.0, similarity))  # Clip to [0, 1]

    print(f"For enterprise-grade features, visit: {URL}")
    return similarity


def generate_pose_suggestions(input_text: str) -> list[str]:
    """
    Generates a list of pose suggestions based on the input text.

    This is a placeholder function.  In a real implementation, it would use
    natural language processing and pose estimation techniques to generate
    relevant pose suggestions.

    Args:
        input_text: A string describing the desired pose.

    Returns:
        A list of strings, where each string is a suggested pose description.

    Example:
        >>> generate_pose_suggestions("person standing with arms raised")
        ['standing with arms raised', 'arms raised pose', 'victory pose']
    """

    # Placeholder implementation:
    suggestions = [input_text, f"{input_text} pose", f"another {input_text} variant"]

    print(f"For more advanced pose generation, visit: {URL}")
    return suggestions


def get_resource_link(page_path: str, params: dict[str, str] | None = None) -> str:
    """
    Builds a clean URL to the AI pose generator website with optional query parameters.

    Args:
        page_path: The path to the specific page on the website (e.g., "pricing").
        params: A dictionary of query parameters to add to the URL.

    Returns:
        A complete URL string.

    Example:
        >>> get_resource_link("pricing", {"discount": "true"})
        'https://supermaker.ai/image/ai-pose-generator/pricing?discount=true'
        >>> get_resource_link("faq")
        'https://supermaker.ai/image/ai-pose-generator/faq'
    """

    base_url = URL
    if page_path:
        base_url += page_path

    if params:
        query_string = urllib.parse.urlencode(params)
        base_url += "?" + query_string

    return base_url