from scenedetect import VideoManager
from scenedetect import SceneManager
from scenedetect.detectors import ContentDetector

import argparse
import os
import ffmpeg
import pandas as pd
from pymongo import MongoClient
from PIL import Image
import base64
import subprocess

from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.drawing.image import Image as OpenPyXLImage
import io

import tempfile







def process_video(video_file):
    video_manager = VideoManager([video_file])
    scene_manager = SceneManager()
    scene_manager.add_detector(ContentDetector(threshold=30))
    base_timecode = video_manager.get_base_timecode()
    video_manager.set_downscale_factor()

    video_manager.start()
    scene_manager.detect_scenes(frame_source=video_manager, show_progress=True)

    scene_list = scene_manager.get_scene_list(base_timecode)
    with open('shot_timestamps.csv', 'w') as f:
        f.write("pkt_pts_time,lavfi.scene_score\n")
        for start_time, end_time in scene_list:
            f.write(f"{start_time.get_seconds()},0\n")


def get_video_length(video_file):
    result = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", video_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(result.stdout)

def extract_shot_information(shot_timestamps_csv, video_length):
    # Read the shot timestamps CSV file and convert it to a list of dictionaries
    shots_df = pd.read_csv(shot_timestamps_csv, names=["frame", "pkt_pts_time"], header=None)
    if "pkt_pts_time" in shots_df.columns:
        # Convert the "pkt_pts_time" column to a numeric data type
        shots_df["pkt_pts_time"] = pd.to_numeric(shots_df["pkt_pts_time"], errors="coerce")
        shots = shots_df[shots_df["pkt_pts_time"] <= video_length].to_dict(orient="records")
    else:
        print("Warning: 'pkt_pts_time' column not found in the CSV file.")
        shots = shots_df.to_dict(orient="records")
    return shots





def save_shots_to_database(shots, database_name="multimedia", collection_name="shots"):
    if not shots:
        print("Warning: No shots to save to the database.")
        return

    client = MongoClient("mongodb://localhost:27017/")
    db = client[database_name]
    collection = db[collection_name]
    collection.insert_many(shots)


def generate_thumbnail(video_file, time, output_file, size=(96, 74)):
    (
        ffmpeg.input(video_file, ss=time)
        .filter("scale", size[0], size[1])
        .output(output_file, vframes=1)
        .overwrite_output()
        .run()
    )




def save_shots_to_xls(shots, output_file):
    from openpyxl import Workbook
    from openpyxl.utils.dataframe import dataframe_to_rows
    from openpyxl.drawing.image import Image
    from PIL import Image as PILImage

    for shot in shots:
        shot['_id'] = str(shot['_id'])

    df = pd.DataFrame(shots)

    wb = Workbook()
    ws = wb.active

    # Write header row
    header = list(df.columns)
    header.remove('thumbnail_base64')  # Remove thumbnail_base64 from the header
    header.append('thumbnail')          # Add the 'thumbnail' header
    ws.append(header)

    for i, row in df.iterrows():
        base64_image = row.get('thumbnail_base64', None)
        data_row = [format(round(float(row['frame']), 4), '.4f')] + list(row.drop(['frame', 'thumbnail_base64']))
        ws.append(data_row)

        if base64_image:
            print(f"Adding image to row {i + 2}")  # Debugging information
            imgdata = base64.b64decode(base64_image)
            img = PILImage.open(io.BytesIO(imgdata))
            img_io = io.BytesIO()
            img.save(img_io, format="PNG")
            img_io.seek(0)
            img = Image(img_io)
            img.width = 96
            img.height = 74
            ws.column_dimensions['D'].width = img.width // 6 + 2  # Increase column width
            ws.row_dimensions[i + 2].height = img.height * 1.5   # Increase row height
            ws.add_image(img, f"D{i + 2}")
        else:
            print(f"No image found for row {i + 2}")  # Debugging information

    wb.save(output_file)




def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--process", type=str, help="Path to the input video file")
    parser.add_argument("--output", type=str, default="crucible_project_output.xlsx", help="Path to the output XLS file")
    args = parser.parse_args()

    if args.process:
        process_video(args.process)
        video_length = get_video_length(args.process)
        shots = extract_shot_information("shot_timestamps.csv", video_length)
        save_shots_to_database(shots)

        with tempfile.TemporaryDirectory() as tempdir:

             for i, shot in enumerate(shots):
                  thumbnail_path = f"thumbnail_{i}.jpg"
                  generate_thumbnail(args.process, shot["pkt_pts_time"], thumbnail_path)

                  with open(thumbnail_path, "rb") as image_file:
                        base64_thumbnail = base64.b64encode(image_file.read()).decode("utf-8")
                  shot["thumbnail_base64"] = base64_thumbnail

             if args.output:
                  save_shots_to_xls(shots, args.output)


if __name__ == "__main__":
    main()
