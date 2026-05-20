#!/usr/bin/env python
"""
Download from W&B the raw dataset and apply some basic data cleaning, exporting the result to a new artifact
"""
import argparse
import logging
import os
import tempfile
import glob
import wandb
import pandas as pd


logging.basicConfig(level=logging.INFO, format="%(asctime)-15s %(message)s")
logger = logging.getLogger()

# DO NOT MODIFY
def go(args):

    run = wandb.init(job_type="basic_cleaning")
    run.config.update(args)

    # Download input artifact. This will also log that this script is using this
    # Use explicit safe temp dir to avoid Windows path error caused by ':' in artifact name
    _artifact_obj = run.use_artifact(args.input_artifact)
    _safe_root = tempfile.mkdtemp(prefix="wb_")
    _art_dir = _artifact_obj.download(root=_safe_root)
    _csv_files = glob.glob(os.path.join(_art_dir, "*.csv"))
    artifact_local_path = _csv_files[0]
    df = pd.read_csv(artifact_local_path)

    # Drop outliers
    min_price = args.min_price
    max_price = args.max_price
    idx = df['price'].between(min_price, max_price)
    df = df[idx].copy()

    # Convert last_review to datetime
    df['last_review'] = pd.to_datetime(df['last_review'])

    # Save the cleaned data
    df.to_csv('clean_sample.csv', index=False)

    logger.info(f"Saving cleaned data with {len(df)} rows")

    # Log the new data
    artifact = wandb.Artifact(
        args.output_artifact,
        type=args.output_type,
        description=args.output_description,
    )
    artifact.add_file("clean_sample.csv")
    run.log_artifact(artifact)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="A very basic data cleaning")

    parser.add_argument(
        "--input_artifact",
        type=str,
        help="Name of the input artifact to be cleaned (e.g. sample.csv:latest)",
        required=True
    )

    parser.add_argument(
        "--output_artifact",
        type=str,
        help="Name for the output cleaned artifact (e.g. clean_sample.csv)",
        required=True
    )

    parser.add_argument(
        "--output_type",
        type=str,
        help="Type of the output artifact (e.g. clean_sample)",
        required=True
    )

    parser.add_argument(
        "--output_description",
        type=str,
        help="Description of the output artifact",
        required=True
    )

    parser.add_argument(
        "--min_price",
        type=float,
        help="Minimum price to consider when filtering outliers (dollars)",
        required=True
    )

    parser.add_argument(
        "--max_price",
        type=float,
        help="Maximum price to consider when filtering outliers (dollars)",
        required=True
    )

    args = parser.parse_args()

    go(args)
