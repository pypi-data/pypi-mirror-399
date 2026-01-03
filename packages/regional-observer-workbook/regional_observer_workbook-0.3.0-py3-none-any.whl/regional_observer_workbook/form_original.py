from __future__ import annotations
import importlib.resources
import json
import cv2
import numpy as np

from types import SimpleNamespace
from typing import Any

from .consts import (
    FormName,
    Revision,
)


# TODO: Add another operation that outputs all the assets
def load(revision: Revision, form_name: FormName, page: str = "page1") -> np.ndarray:
    """Load the original form image for the given revision and form name.

    Args:
        revision: The revision of the form to load.
        form_name: The name of the form to load.
        page: The specific page of the form to load (default is "page1").
    Returns:
        The original form image as a numpy array.
    Raises:
        ValueError: If the image cannot be loaded.
        FileNotFoundError: If the specified resource does not exist.
    """
    with (
        importlib.resources.files("regional_observer_workbook.assets")
        .joinpath(
            revision.value,
            form_name.value,
            page + ".png",
        )
        .open("rb") as img_file
    ):
        img_array = np.frombuffer(img_file.read(), np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Failed to load image for {revision}, {form_name}, {page}")
    return img


def load_bounding_boxes(
    revision: Revision, form_name: FormName, bbox_name: str
) -> np.ndarray:
    if not bbox_name.endswith(".npy"):
        bbox_name = f"{bbox_name}.npy"
    with (
        importlib.resources.files("regional_observer_workbook.assets")
        .joinpath(
            revision.value,
            form_name.value,
            bbox_name,
        )
        .open("rb") as bbox_file
    ):
        return np.load(bbox_file)


# Using "Any" as the return type so that IDEs won't complain about using dot access notation
def load_named_fields(
    revision: Revision,
    form_name: FormName,
) -> Any:
    with (
        importlib.resources.files("regional_observer_workbook.assets")
        .joinpath(revision.value, form_name.value, "form-fields.json")
        .open("rb") as json_file
    ):
        return json.load(json_file, object_hook=lambda d: SimpleNamespace(**d))
