from __future__ import annotations
import logging
import cv2
import numpy as np
import numpy.typing as npt
from typing import Sequence

from .errors import InvalidImageError


LOGGER = logging.getLogger(__name__)

MIN_IMAGE_WIDTH = 10
MIN_IMAGE_HEIGHT = 10
# We're in control of the image sizing via the originals that are stored under
# assets/.  However, it costs very little to check this and avoid an OOM condition
MAX_IMAGE_WIDTH = 10000
MAX_IMAGE_HEIGHT = 10000


def image_as_grayscale(image: np.ndarray | None) -> np.ndarray | None:
    """Return a single-channel grayscale image when appropriate.

    This helper converts a BGR (3-channel) image to a 2D grayscale image
    using OpenCV's `cv2.cvtColor` with `cv2.COLOR_BGR2GRAY`. If the input is
    already a 2D array (assumed to be grayscale) it is returned unchanged.

    Parameters
    - image: np.ndarray | None
        The input image. May be a 2D grayscale array, a 3D BGR color array,
        or ``None``.

    Returns
    - np.ndarray | None
        A 2D ndarray representing the grayscale image, or ``None`` when the
        input is ``None``.

    Notes
    - The function preserves the input dtype (commonly ``uint8``).
    - Conversion assumes OpenCV's BGR channel ordering for color images.
    - This function performs only a lightweight conversion and does not
      validate image size or dtype; call ``image_validator`` before using in
      contexts that require strict validation.
    """
    if image is None:
        return None
    if image.ndim > 2:
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return image

def scale_consistency(source_points: npt.NDArray[np.float32], destination_points: npt.NDArray[np.float32]) -> float:
    """Estimate the average scale ratio between two point sets.

    The function computes the per-axis standard deviation of `source_points`
    and `destination_points` (axis=0), forms the element-wise ratio
    ``dst_std / (src_std + eps)``, and returns the mean of those ratios. A
    returned value near ``1.0`` indicates that the two point sets have
    similar spatial spread; values > 1 indicate that `destination_points` are
    on average more spread out (scaled up), and values < 1 indicate a
    relative shrink.

    Parameters
    - source_points: npt.NDArray[np.float32]
        Array of shape (N, 2) containing x/y coordinates from the source
        image (e.g., scan keypoints).
    - destination_points: npt.NDArray[np.float32]
        Array of shape (N, 2) containing corresponding x/y coordinates from
        the destination image (e.g., original keypoints).

    Returns
    - float
        The mean scale ratio computed from the X and Y axis spreads.

    Notes
    - A small epsilon (1e-6) is added to the denominator to avoid division
      by zero when the source spread is extremely small.
    - The function does not validate input shapes or correspondence; callers
      should ensure the arrays are aligned and of appropriate shape.
    """
    src_std = np.std(source_points, axis=0)
    dst_std = np.std(destination_points, axis=0)

    scale_ratio = np.mean(dst_std / (src_std + 1e-6))
    LOGGER.debug(f"Spread check scale ratio: {scale_ratio:.2f}")
    return scale_ratio

def y_coordinate_correlation(source_points: npt.NDArray[np.float32], destination_points: npt.NDArray[np.float32]) -> float:
    """Compute an absolute correlation of Y coordinates between two point sets.

    The function computes the Pearson correlation coefficient between the Y
    (vertical) coordinates of `source_points` and `destination_points` using
    NumPy's `np.corrcoef`, extracts the off-diagonal value and returns its
    absolute value. A result close to 1.0 indicates strong linear correlation
    in the same or opposite direction (useful for detecting upright vs
    flipped-by-180-degree orientation), while values near 0 indicate little
    linear correspondence.

    Parameters
    - source_points: npt.NDArray[np.float32]
        Array of shape (N, 2) with (x, y) coordinates from the source image.
    - destination_points: npt.NDArray[np.float32]
        Array of shape (N, 2) with (x, y) coordinates from the destination
        image.

    Returns
    - float
        Absolute Pearson correlation coefficient between the Y coordinates of
        the two arrays (in range [0.0, 1.0]). Higher values indicate stronger
        linear relationship.

    Notes
    - The function does not validate input shape or correspondence of points;
      callers must ensure the inputs are properly paired and have sufficient
      variance.
    - By returning the absolute value, the caller can detect strong
      correlation regardless of whether the relationship is positive or
      negative (e.g., upright vs 180-degree rotated).
    """
    corr_matrix = np.corrcoef(source_points[:, 1], destination_points[:, 1])
    y_corr = corr_matrix[0, 1]
    LOGGER.debug(f"Y-coordinate correlation: {y_corr:.2f}")

    return abs(y_corr)

def compute_inlier_ratio(mask: npt.NDArray[np.uint8], source_points: npt.NDArray[np.float32]) -> float:
    """Compute the fraction of inlier matches from a RANSAC mask.

    This helper interprets ``mask`` as a boolean-like array (commonly the
    mask returned by OpenCV's `findHomography` when using RANSAC), flattens
    it with ``mask.ravel()``, and counts the number of truthy elements as
    inliers. The inlier ratio is calculated as ``inliers / total_matches``
    where ``total_matches`` is the length of ``source_points``.

    Parameters
    - mask: npt.NDArray[np.uint8]
        A 1-D or 2-D array-like mask where non-zero values indicate inliers
        and zero values indicate outliers. Typical shape is (N, 1) or (N,).
    - source_points: npt.NDArray[np.float32]
        Array of matched source coordinates (shape (N, 2)). The function uses
        ``len(source_points)`` as the denominator when computing the ratio.

    Returns
    - float
        Fraction of matches that are inliers (range 0.0 to 1.0).

    Notes
    - If ``source_points`` is empty, a ``ZeroDivisionError`` will be raised.
      Callers should ensure there is at least one match before invoking this
      helper.
    - The function converts the mask to a 1-D view with ``ravel()`` and sums
      truthy values; ensure the mask uses an integer/binary representation
      (e.g., dtype ``uint8`` with values 0 or 1).
    """
    matches_mask = mask.ravel()
    total_matches = len(source_points)
    inliers = int(np.sum(matches_mask))
    outliers = total_matches - inliers
    inlier_ratio = inliers / total_matches
    LOGGER.debug(f"Inliers: {inliers}, Outliers: {outliers}, Inlier Ratio: {inlier_ratio:.2%}")
    return inlier_ratio

def is_homography_plausible(H, scan_shape, dst_size) -> bool:
    """Validate basic geometric plausibility of a homography warp.

    The function applies the homography ``H`` to the four corners of the
    source image (determined from ``scan_shape``) to produce projected
    corner coordinates. It then performs two lightweight geometric checks:

    - Convexity: ensures the projected quadrilateral is convex (rejects
      bow-tie / self-intersecting results).
    - Area: compares the contour area of the projected polygon to the area
      of the destination size (``dst_size``). If the projected area is
      smaller than 1% of the destination area, the transform is considered
      an implosion; if it is larger than 10× the destination area, it is
      considered an explosion.

    Parameters
    - H: array-like
        A 3x3 homography matrix (as produced by `cv2.findHomography`) that
        maps source coordinates into destination coordinates. The function
        expects a valid, non-``None`` matrix.
    - scan_shape: sequence
        Shape of the source image (height, width, ...) — only the first two
        elements are used to form the source corner coordinates.
    - dst_size: tuple[int, int]
        Destination image size as ``(width, height)`` — this follows the
        argument order used by ``cv2.warpPerspective``.

    Returns
    - bool
        ``True`` when the homography produces a convex projected polygon
        whose area is within reasonable bounds of the destination area;
        ``False`` otherwise. Warnings are logged for failed checks to aid
        debugging.

    Notes
    - This is a fast heuristic intended to filter obviously incorrect
      homographies; it is not a rigorous geometric validity proof.
    """
    h, w = scan_shape[:2]
    # dst_size is the final tuple argument to cv2.warpPerspective, unpack into discrete vars
    dst_w, dst_h = dst_size
    corners = np.array([[0, 0], [w, 0], [w, h], [0, h]], dtype=np.float32).reshape(-1, 1, 2)
    pred_corners = cv2.perspectiveTransform(corners, H) # type: ignore[reportArgumentType]

    # Check for convexity
    if not cv2.isContourConvex(pred_corners):
        LOGGER.warning("Warp results in a non-convex shape (bowtie effect)")
        return False

    # Check area
    area = cv2.contourArea(pred_corners)
    dst_area = dst_w * dst_h
    if area < (0.01 * dst_area):
        LOGGER.warning("Resulting image is too small (implosion)")
        return False

    if area > (10 * dst_area):
        LOGGER.warning("Resulting image too large (explosion)")
        return False
    return True


def make_orb_for_image(
    image: npt.NDArray[np.uint8],
    base_nfeatures: int = 500,
    max_features: int = 5000,
):
    h, w = image.shape[:2]
    area = w * h
    # base_area is defined from what we think the minimum scan size will be
    # 150dpi for an 8.5x11 sheet of paper is 1275x1650
    base_area = 1600 * 1200
    nfeatures = int(base_nfeatures * max(1.0, area / base_area))
    nfeatures = min(max(nfeatures, base_nfeatures), max_features)
    LOGGER.info(f"ORB feature count after calculation: {nfeatures}")
    return cv2.ORB_create(
        nfeatures=nfeatures,
        edgeThreshold=31,  # default but figure out how we want to scale this between 31 and 51
        scoreType=cv2.ORB_HARRIS_SCORE,  # Also default, but being explicit
    )


# TODO: Evaluate SIFT and AKAZE
# For SIFT and AKAZE use the cv2.NORM_L2 matcher rather than cv2.NORM_HAMMING (or brute force)
# Additional recommendation for SIFT is to gaussian blur the image to avoid having the handwriting
# be considered as input to the matcher.



def image_validator(image: np.ndarray, param_name: str) -> None:
    """Validate an image array and raise with the parameter name in the exception message."""
    if not isinstance(image, np.ndarray):
        raise InvalidImageError(f"{param_name} is not a NumPy NDArray object")

    if image.ndim not in (2, 3):
        raise InvalidImageError(f"{param_name} must be a 2D or 3D array")

    if image.shape[0] < MIN_IMAGE_HEIGHT or image.shape[1] < MIN_IMAGE_WIDTH:
        raise InvalidImageError(f"{param_name} image is too small to process")
    
    if image.shape[0] >= MAX_IMAGE_HEIGHT or image.shape[1] >= MAX_IMAGE_WIDTH:
        raise InvalidImageError(f"{param_name} image is too large to process")

    if not np.issubdtype(image.dtype, np.uint8):
        raise InvalidImageError(f"{param_name} array type must be uint8 (or subtype)")

# For testing, we can align the original to itself and should get an image
# Would also try aligning with rotated/scaled versions of the original and see if it still works
# Last positive test would be to take original, fuzz it slightly, and then align and see if it still works
# For negative testing, align PNG of same size but random content and confirm that it fails.
def align_to_original(
    scan: npt.NDArray[np.uint8],
    original: npt.NDArray[np.uint8],
    max_features: int = 500,
    keep_percent: float = 0.2,
) -> npt.NDArray[np.uint8]:
    # This code uses "scan" and "original" to identify image sources
    # These correlate to the OpenCV documentation's use of "query" and "train", respectively
    image_validator(scan, "scan")
    image_validator(original, "original")

    if max_features < 4:
        raise ValueError("max_features must be a positive number GTE 4")

    if not (0 < keep_percent <= 1):
        raise ValueError("keep_percent must be a float between 0 and 1")

    if int(max_features * keep_percent) < 4:
        raise ValueError(
            "max_features and keep_percent combination must allow at least 4 points to be kept"
        )

    # NOTE: We can avoid this by ensuring that the original is stored as grayscale
    # Presumably could also store it in npy native format to avoid the load,
    # but that's probably not worth the disk space.
    original_grayscale = image_as_grayscale(original)
    if original_grayscale is None:
        raise ValueError("Original image could not be converted to grayscale")

    original_height, original_width = original_grayscale.shape
    # This assumes that the scan is in the correct orientation.
    # TODO: Either rotate the image (so that it's either 0 or 180 degrees from correct) or
    # make this code more resilient to a 90/-90 degree rotation
    _, scan_width = scan.shape

    scale_factor = original_width / scan_width

    # If the scanned image is significantly larger than the original, resize
    # to match scan.
    if scale_factor <= 0.5:
        LOGGER.info(f"Resizing scan by {scale_factor:.2f}")
        scan = cv2.resize(scan, (original_width, original_height))

    scan_grayscale = image_as_grayscale(scan)
    
    if scan_grayscale is None :
        raise ValueError("Scanned image could not be converted to grayscale")

    # NOTE: SIFT patent expired in 2020, so could consider using it instead of ORB if needed.
    # SURF is probably under patent until at least 2031 (Original date of filing looks like 2009, but grant is 2012 with the 12th year
    # payment assessed in 2023)

    # Use ORB to detect keypoints and extract features
    orb = cv2.ORB_create(max_features)
    # TODO: Test the new "make_orb_for_image" function   
    #orb = make_orb_for_image(original, max_features=max_features)
 
    scan_keypoints: Sequence[cv2.KeyPoint]
    scan_descriptors: np.ndarray # TODO: What is the type of a given element?
    (scan_keypoints, scan_descriptors) = orb.detectAndCompute(scan_grayscale, None)

    if scan_descriptors is None:
        raise ValueError("No features detected in scan image")

    LOGGER.debug(f"Number of scan keypoints detected: {len(scan_keypoints)}")
    LOGGER.debug(f"Number of scan descriptors detected: {scan_descriptors.shape[0]}")

    # This could be computed once and stored
    # Descriptors, as an ndarray, can be stored directly, but the keypoints needs to be pickled
    original_keypoints: Sequence[cv2.KeyPoint]
    original_descriptors: np.ndarray
    (original_keypoints, original_descriptors) = orb.detectAndCompute(original_grayscale, None)
    LOGGER.debug(f"Number of original keypoints detected: {len(original_keypoints)}")
    # NOTE: Not performing a None check on the original image as it should have features.  If it doesn't
    # the package is hosed, so we'll let the .shape call raise for us
    LOGGER.debug(f"Number of original descriptors detected: {original_descriptors.shape[0]}")

    # match features
    matcher = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = matcher.match(scan_descriptors, original_descriptors, None)

    LOGGER.debug(f"Number of identified matches: {len(matches)}")
    if len(matches) == 0:
        raise ValueError("No matches found between scan and original")

    # Sort by distance (similarity)
    matches = sorted(matches, key=lambda x: x.distance)

    keep = int(len(matches) * keep_percent)
    matches = matches[:keep]
    LOGGER.debug(f"Number of matches after limiting to top {keep_percent}%: {keep}")
    if matches is None or len(matches) < 4:
        raise ValueError("Not enough matches to compute homography")

    # keypoints bounds check
    LOGGER.debug("Performing keypoints bounds checking")
    max_query_idx = len(scan_keypoints)
    max_train_idx = len(original_keypoints)

    q_indices = np.array([m.queryIdx for m in matches])
    t_indices = np.array([m.trainIdx for m in matches])

    valid_mask = (q_indices < max_query_idx) & (t_indices < max_train_idx)

    if not np.all(valid_mask):
        LOGGER.warning(f"Found {np.sum(~valid_mask)} invalid match indices!")
        # Filter to only valid matches
        matches = [m for i, m in enumerate(matches) if valid_mask[i]]
        LOGGER.debug(f"Number of matches after filtering out invalid matches: {len(matches)}")

    LOGGER.debug("Keypoints bounds check complete")

    source_points: npt.NDArray[np.float32] = np.zeros((len(matches), 2), dtype="float")
    destination_points: npt.NDArray[np.float32] = np.zeros((len(matches), 2), dtype="float")

    for i, m in enumerate(matches):
        source_points[i] = scan_keypoints[m.queryIdx].pt
        destination_points[i] = original_keypoints[m.trainIdx].pt
    
    # For a scanner, the spatial distribution of keypoints should be constant
    scale_ratio = scale_consistency(source_points, destination_points)
    if scale_ratio < 0.8 or scale_ratio > 1.2:
        LOGGER.warning(f"Significant scale discrepance ({scale_ratio:.2f}), matches are likely noise")
    
    # Similarly, the angles of a scanned image should be correlated
    y_corr = y_coordinate_correlation(source_points, destination_points)
    if y_corr < 0.5:
        LOGGER.warning(f"Low Y-coordinate correlation ({y_corr:.2f}), matches are likely noise")

    # H could be None, raise if true
    (H, mask) = cv2.findHomography(source_points, destination_points, method=cv2.RANSAC)
    if H is None:
        LOGGER.warning("Alignment homography is `None`")
        raise ValueError("No homography found between scan and original")
    
    inlier_ratio = compute_inlier_ratio(mask, source_points)
    LOGGER.info(f"Inlier ratio: {inlier_ratio:.2%}")
    if inlier_ratio < 0.2:
        LOGGER.warning(f"Low inlier ratio ({inlier_ratio:.2%}), probable poor alignment")
    
    # TODO: Can we make original width/height constants?
    dst_size = (original_width, original_height)
    if is_homography_plausible(H, scan.shape, dst_size):
        return cv2.warpPerspective(scan, H, dst_size)
    else:
        raise ValueError("Homography is geometrically nonsensical")

# NOTE: The function below is a work-in-progress in getting the alignment function to match a document image
# from a camera vs. a scanner.  It sort-of works, in that we get a homography output.  Unfortunately, the boxes
# are off.  The camera-sourced image probably requires additional processing 
def align_camera_image_to_original(
    scan: npt.NDArray[np.uint8],
    original: npt.NDArray[np.uint8],
    max_features: int = 500,
    keep_percent: float = 0.2,
) -> npt.NDArray[np.uint8]:
    if not (isinstance(scan, np.ndarray) and isinstance(original, np.ndarray)):
        raise ValueError("scan and/or original are not NumPy NDArray objects")

    # Create a function that validates an image and takes the image plus the parameter name
    # Have it raise and include the parameter name in the exception message.
    # Can then test the function separately and not have to worry about validation calls in testing this
    # longer function.
    if scan.ndim not in (2, 3):
        raise ValueError("scan must be a 2D or 3D array")

    if original.ndim not in (2, 3):
        raise ValueError("original must be a 2D or 3D array")

    # TODO: Set minimum size constants
    if scan.shape[0] < 10 or scan.shape[1] < 10:
        raise ValueError("scan image is too small to process")
    if original.shape[0] < 10 or original.shape[1] < 10:
        raise ValueError("original image is too small to process")

    if not np.issubdtype(scan.dtype, np.uint8):
        raise TypeError("scan array type must be uint8 (or subtype)")

    if not np.issubdtype(original.dtype, np.uint8):
        raise TypeError("original array type must be uint8 (or subtype)")

    if max_features < 4:
        raise ValueError("max_features must be a positive number GTE 4")

    if not (0 < keep_percent <= 1):
        raise ValueError("keep_percent must be a float between 0 and 1")

    if int(max_features * keep_percent) < 4:
        raise ValueError(
            "max_features and keep_percent combination must allow at least 4 points to be kept"
        )
    # NOTE: We can avoid this by ensuring that the original is stored as grayscale
    # Presumably could also store it in npy native format to avoid the load,
    # but that's probably not worth the disk space.
    original_grayscale = image_as_grayscale(original)
    if original_grayscale is None:
        raise ValueError("Original image could not be converted to grayscale")

    original_height, original_width = original_grayscale.shape
    scan_height, scan_width = scan.shape

    scale_factor = original_width / scan_width

    # If the scanned image is significantly larger than the original, resize
    # to match scan.
    if scale_factor <= 0.5:
        scan = cv2.resize(scan, (original_width, original_height))

    scan_grayscale = image_as_grayscale(scan)
    
    if scan_grayscale is None :
        raise ValueError("Scanned image could not be converted to grayscale")
    
    
    
    scale_factor = original_width / scan_width
    LOGGER.info(f"Scan could be scaled by {scale_factor} to match original dimensions")

    # TODO: Make this an optional flag, but hard-code for now
    scan_grayscale = cv2.GaussianBlur(scan_grayscale, (5,5), 0)
    # TODO: Put this behind a flag
    #clahe = cv2.createCLAHE(clipLimit=2, tileGridSize=(8,8))
    #scan_grayscale = clahe.apply(scan_grayscale)

    # NOTE: SIFT patent expired in 2020, so could consider using it instead of ORB if needed.
    # SURF is probably under patent until at least 2031 (Original date of filing looks like 2009, but grant is 2012 with the 12th year
    # payment assessed in 2023)

    # Use ORB to detect keypoints and extract features
    orb = cv2.ORB_create(max_features)
    # TODO: Test the new "make_orb_for_image" function   
    #orb = make_orb_for_image(original, max_features=max_features)
    # At present (2025-12-28), the new function doesn't perform any better on scans captured with a camera
    # Leaving it out while we debug other issues
    # TODO: Check for None in both these detectAndCompute calls, raising if true
    # TODO: Debug log kpsA/kpsB counts
    # cv2.KeyPoint is the type of the elements in kpsA/kpsB

    scan_keypoints: Sequence[cv2.KeyPoint]
    scan_descriptors: np.ndarray
    (scan_keypoints, scan_descriptors) = orb.detectAndCompute(scan_grayscale, None)
    LOGGER.info(f"Number of scan keypoints detected: {len(scan_keypoints)}")
    LOGGER.info(f"Number of scan descriptors detected: {scan_descriptors.shape[0]}")
    # This could be computed once and stored
    original_keypoints: Sequence[cv2.KeyPoint]
    original_descriptors: np.ndarray
    (original_keypoints, original_descriptors) = orb.detectAndCompute(original_grayscale, None)
    LOGGER.info(f"Number of original keypoints detected: {len(original_keypoints)}")
    LOGGER.info(f"Number of original descriptors detected: {original_descriptors.shape[0]}")

    # AI recommends using different matcher for camera images
    bf = cv2.DescriptorMatcher_create(cv2.DESCRIPTOR_MATCHER_BRUTEFORCE_HAMMING)
    matches = bf.knnMatch(original_descriptors, scan_descriptors, k=2)

    # TODO: Look for len(matches) == 0
    LOGGER.info(f"Number of identified matches: {len(matches)}")

    good = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good.append(m)
    
    LOGGER.info(f"Good matches found: {len(good)}")

    if len(good) <= 10:
        raise ValueError("Not enough good matches to compute homography")
    
    # Unexpectedly, the code below works:  The query index should go with the scan and the train index should go with the
    # original.  However, changing it results in a garbage homography.
    source_points = np.array([original_keypoints[m.queryIdx].pt for m in good], dtype=np.float32).reshape(-1, 1, 2)
    # NOTE: This was trainIdx before, but queryIdx makes more sense given how we called knnMatch
    destination_points = np.array([scan_keypoints[m.trainIdx].pt for m in good], dtype=np.float32).reshape(-1, 1, 2)

    M, mask = cv2.findHomography(source_points, destination_points, cv2.RANSAC, 10.0)
    aligned = cv2.warpPerspective(scan, M, (original_width, original_height))
    return aligned


def get_cell(
    row: int, col: int, aligned_image: np.ndarray, bbox: np.ndarray
) -> np.ndarray:
    """Extract a rectangular cell image from an aligned image using a bbox grid.

    The function indexes into a grid of bounding boxes `bbox` at the
    specified `(row, col)` position, where each bounding box is expected
    to contain four values in the order ``(x, y, w, h)`` (x/y top-left
    pixel coordinates and width/height in pixels). It returns the cropped
    subarray from ``aligned_image`` corresponding to that rectangle.

    Parameters
    - row: int
        Row index into the bounding-box grid.
    - col: int
        Column index into the bounding-box grid.
    - aligned_image: np.ndarray
        The source image (grayscale or color) from which to extract the
        cell. Slicing is performed as ``aligned_image[y:y+h, x:x+w]``.
    - bbox: np.ndarray
        Array of shape ``(n_rows, n_cols, 4)`` where the last dimension
        holds ``(x, y, w, h)`` for each cell. Coordinates are in pixel
        units and must be within the bounds of ``aligned_image``.

    Returns
    - np.ndarray
        The cropped image array for the specified cell. The returned array
        preserves the dtype and number of channels of ``aligned_image``.

    Raises
    - IndexError: if ``row`` or ``col`` is outside the grid dimensions.
    - ValueError: if the third dimension of ``bbox`` is not length 4.

    Notes
    - The function does not check that the extracted rectangle lies fully
      within ``aligned_image``; callers should ensure bounding boxes are
      valid or handle potential indexing errors from NumPy.
    """
    if row >= bbox.shape[0]:
        raise IndexError(
            f"Row index {row} out of bounds for bounding box with shape {bbox.shape}"
        )
    if col >= bbox.shape[1]:
        raise IndexError(
            f"Column index {col} out of bounds for bounding box with shape {bbox.shape}"
        )
    if bbox.shape[2] != 4:
        raise ValueError(
            f"Bounding box third dimension must be of length 4, got {bbox.shape[2]}"
        )
    x, y, w, h = bbox[row, col]
    return aligned_image[y : y + h, x : x + w]
