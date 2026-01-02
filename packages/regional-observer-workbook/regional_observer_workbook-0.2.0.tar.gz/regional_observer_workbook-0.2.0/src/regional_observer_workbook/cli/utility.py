import argparse
import logging
import os
from regional_observer_workbook.consts import (
    FormName,
    Revision,
)
from regional_observer_workbook.form_original import load, load_bounding_boxes
from regional_observer_workbook.operations import (
    align_to_original,
    get_cell,
    image_as_grayscale,
)
import cv2
import numpy as np
from PIL import ImageDraw, Image


LOGGER = logging.getLogger(__name__)


# TODO: Can probably make this more generic
def form_option_type(arg: str) -> FormName:
    try:
        return FormName(arg)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid option: '{arg}'. Valid options are: "
            f"{', '.join(FormName.__members__.values())}"
        )


def revision_option_type(arg: str) -> Revision:
    try:
        return Revision(arg)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"Invalid option: '{arg}'. Valid options are: "
            f"{', '.join(Revision.__members__.values())}"
        )


def show_bounding_boxes(
    aligned_image: np.ndarray,
    bbox_grid: np.ndarray,
    output_file: str,
) -> None:
    im = Image.fromarray(aligned_image)
    # Need to convert to RGB
    im = im.convert("RGB")
    draw = ImageDraw.Draw(im)
    for r, c in np.ndindex(bbox_grid.shape[:2]):
        box_data = bbox_grid[r, c]
        x, y, w, h = box_data.astype(int)
        coords = [x, y, x + w, y + h]
        draw.rectangle(coords, outline="red", width=2)
    im.save(output_file)


def extract(
    aligned_image: np.ndarray,
    bbox_grid: np.ndarray,
    output_directory: str,
    base_name: str,
) -> None:
    for r, c in np.ndindex(bbox_grid.shape[:2]):
        cell = get_cell(r, c, aligned_image, bbox_grid)
        # Allows 99 rows and 99 columns
        filename = f"{base_name}_r{r:02d}_c{c:02d}.png"
        fq_path = os.path.join(output_directory, filename)
        cv2.imwrite(fq_path, cell)


def main() -> None:
    logging.basicConfig(level=logging.INFO)
    # Need an action parameter that's either 'extract' or 'show-bounding-boxes'
    # Need revision, form_name, and bbox_name
    parser = argparse.ArgumentParser(
        prog="form-extract-cli",
        description="Utility script for Regional Observer Workbook",
    )
    parser.add_argument(
        "activity",
        choices=["extract", "show-bounding-boxes"],
        help="Activity performed by the CLI:  extract will output cells as discrete images, show-bounding-boxes will overlay bounding boxes on scan",
    )
    parser.add_argument(
        "--scan",
        help="Scanned image to operate on",
    )
    parser.add_argument(
        "--revision",
        type=revision_option_type,
        choices=[e.value for e in Revision],
        default=Revision.v2018,
    )
    parser.add_argument(
        "--form-name",
        type=form_option_type,
        choices=[e.value for e in FormName],
        default=FormName.PS4,
    )
    parser.add_argument(
        "--bounding-box-name",
        default="sample-data",
    )
    parser.add_argument(
        "--output-dir",
        default=".",
    )
    parser.add_argument(
        "--base-name",
    )
    parser.add_argument(
        "--max-features",
        type=int,
        default=1500,
        help="The maximum number of features used for matching scan to original",
    )
    parser.add_argument(
        "--keep-percent",
        type=float,
        default=0.2,
        help="The percentage of features to keep during alignment",
    )
    # TODO: After we get CI/CD working, get this dynamically
    parser.add_argument(
        "--version",
        action="version",
        version="Regional Observer Workbook Utility 1.0.0",
    )
    args = parser.parse_args()
    bbox_grid = load_bounding_boxes(
        revision=args.revision,
        form_name=args.form_name,
        bbox_name=args.bounding_box_name,
    )
    LOGGER.info(f"Loaded bounding box with shape {bbox_grid.shape}")
    original = load(revision=args.revision, form_name=args.form_name)
    scan_image = cv2.imread(args.scan)
    scan_image = image_as_grayscale(scan_image)
    if scan_image is None:
        raise ValueError(f"Unable to load image from file {args.scan}")
    # TODO: Create args for max_features and keep_percent
    LOGGER.info("Aligning image to original")
    scan_image = align_to_original(
        scan_image,
        original,
        max_features=args.max_features,
        keep_percent=args.keep_percent,
    )
    if args.activity == "show-bounding-boxes":
        base_name = args.base_name or "aligned-with-bboxes"
        # There are smarter ways of doing this, but this is okay for a trivial utility
        output_file = f"{args.output_dir}/{base_name}.png"
        LOGGER.info("Drawing bounding boxes on scanned image")
        show_bounding_boxes(scan_image, bbox_grid, output_file)
        LOGGER.info("Updated image available at %s", output_file)
    elif args.activity == "extract":
        # If no base name is given, use the scan file name without extension
        base_name = args.base_name or os.path.splitext(os.path.basename(args.scan))[0]
        LOGGER.info("Using base name of %s", base_name)
        extract(scan_image, bbox_grid, args.output_dir, base_name)
        LOGGER.info("Extraction complete")
    else:
        # Shouldn't happen given that it was constrained to choices
        print("Unsupported activity")


if __name__ == "__main__":
    main()
