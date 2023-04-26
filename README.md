# Multimedia-Scene-Detection_Project3
A Python-based multimedia project that processes video files to automatically detect scene changes, extract shot information, generate thumbnails, and save the shot data to an XLS file. The project utilizes the PySceneDetect library and OpenPyXL for handling video and spreadsheet files, respectively.


# Multimedia-Scene-Detection_Project3: The Crucible

A Python-based multimedia project that processes video files to automatically detect scene changes, extract shot information, generate thumbnails, and save the shot data to an XLS file. The project utilizes the PySceneDetect library and OpenPyXL for handling video and spreadsheet files, respectively. The Crucible project aims to assist editorial teams in visually reviewing marked shots and adding comments on them, integrating with CMS systems like Frame.io and Shotgrid.

## Features

1. Process video files to detect scene changes
2. Extract shot information from a populated database
3. Convert marks to timecodes using ffmpeg or other 3rd party tools
4. Export shot information to an XLS file with timecode ranges
5. Generate thumbnails for each shot and embed them in the XLS file

## Dependencies

- Python 3
- pandas
- openpyxl
- scenedetect
- ffmpeg
- pymongo

## Installation

1. Install Python 3 if you haven't already.
2. Install the required libraries using pip:

pip install pandas openpyxl scenedetect ffmpeg-python pymongo


## Usage

Run the script with the following command:

python crucible_project.py --process <input_video_file> --output <output_xlsx_file>


Replace `<input_video_file>` with the path to the video file you want to process and `<output_xlsx_file>` with the desired output Excel file name.

## Example


python crucible_project.py --process twitch_nft_demo.mp4 --output output.xlsx


This command will process the `twitch_nft_demo.mp4` video file and create an Excel file named `output.xlsx` with the detected scene information and thumbnails.

## License

This project is distributed under the [MIT License](https://opensource.org/licenses/MIT).

## Acknowledgements

- [PySceneDetect](https://pyscenedetect.readthedocs.io/en/latest/)
- [ffmpeg-python](https://github.com/kkroening/ffmpeg-python)
- [pymongo](https://github.com/mongodb/mongo-python-driver)


