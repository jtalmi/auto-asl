# # Procedure to extract speaker videos

We're given an input which is 

VIDEO_ID = "57707"
WORD = "theater"

This script will extract the person in the center of the video signing and recast it against a transparent background

You have to put the script in the segment-anything-2 repo inside an auto_asl folder. It also relies on a folder full of wlasl_videos named <id>.mp4. They don't necessarily have to be wlasl videos, but they should be videos of people signing.

The final video will be in the output_videos folder as `{WORD}_{VIDEO_ID}.mp4`.

