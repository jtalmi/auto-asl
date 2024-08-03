import os
import torch
import subprocess
import json
import numpy as np
from PIL import Image

from sam2.build_sam import build_sam2_video_predictor

#
# Input Params
#

VIDEO_ID = "57707"
WORD = "theater"

input_video_path = f"./wlasl_videos/{VIDEO_ID}.mp4"

# Check if input video exists
if not os.path.exists(input_video_path):
    print(f"Error: Input video not found at {input_video_path}")
    exit(1)

input_frames_dir = f"./input_video_frames/{WORD}"
os.makedirs(input_frames_dir, exist_ok=True)

output_frames_dir = f"./output_video_frames/{WORD}"
os.makedirs(output_frames_dir, exist_ok=True)

final_output_dir = "./output_videos"
os.makedirs(final_output_dir, exist_ok=True)

sam2_checkpoint = "../checkpoints/sam2_hiera_large.pt"
model_cfg = "sam2_hiera_l.yaml"


def get_video_info(video_path):
    command = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        video_path,
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    return json.loads(result.stdout)


def extract_all_frames(video_path, output_dir, fps):
    os.makedirs(output_dir, exist_ok=True)
    command = [
        "ffmpeg",
        "-i",
        video_path,
        "-vf",
        f"fps={fps}",
        f"{output_dir}/%04d.jpg",
    ]
    subprocess.run(command, check=True)


def compile_output_video(input_dir, output_path, fps):
    command = [
        "ffmpeg",
        "-framerate",
        str(fps),
        "-i",
        f"{input_dir}/masked_content_%04d.png",
        "-c:v",
        "libx264",
        "-pix_fmt",
        "yuv420p",
        output_path,
    ]
    subprocess.run(command, check=True)


#
# Step 1: Split keyframes
#
# import pdb; pdb.set_trace()

video_info = get_video_info(input_video_path)
fps = eval(video_info["streams"][0]["r_frame_rate"])

extract_all_frames(input_video_path, input_frames_dir, fps)
frame_count = len([f for f in os.listdir(input_frames_dir) if f.endswith(".jpg")])
print(f"Extracted {frame_count} frames at {fps} fps from the video.")


# use bfloat16 for the entire notebook
torch.autocast(device_type="cuda", dtype=torch.bfloat16).__enter__()

if torch.cuda.get_device_properties(0).major >= 8:
    # turn on tfloat32 for Ampere GPUs (https://pytorch.org/docs/stable/notes/cuda.html#tensorfloat-32-tf32-on-ampere-devices)
    torch.backends.cuda.matmul.allow_tf32 = True
    torch.backends.cudnn.allow_tf32 = True
    print("Using allow_tf32")


predictor = build_sam2_video_predictor(model_cfg, sam2_checkpoint)


# scan all the JPEG frame names in this directory
frame_names = [
    p
    for p in os.listdir(input_frames_dir)
    if os.path.splitext(p)[-1] in [".jpg", ".jpeg", ".JPG", ".JPEG"]
]
frame_names.sort(key=lambda p: int(os.path.splitext(p)[0]))

# initialize the image state
inference_state = predictor.init_state(video_path=input_frames_dir)
predictor.reset_state(inference_state)

ann_frame_idx = 0  # the frame index we interact with
ann_obj_id = (
    1  # give a unique id to each object we interact with (it can be any integers)
)

# Get the image dimensions
image = Image.open(os.path.join(input_frames_dir, frame_names[ann_frame_idx]))
width, height = image.size

# Calculate click positions
center_x = width // 2
center_y = height // 2
lower_y = center_y + (height // 4)
upper_y = center_y - (height // 4)

# Set three positive clicks vertically aligned in the middle
points = np.array(
    [[center_x, upper_y], [center_x, center_y], [center_x, lower_y]], dtype=np.float32
)
# All clicks are positive
labels = np.array([1, 1, 1], dtype=np.int32)

_, out_obj_ids, out_mask_logits = predictor.add_new_points(
    inference_state=inference_state,
    frame_idx=ann_frame_idx,
    obj_id=ann_obj_id,
    points=points,
    labels=labels,
)

# run propagation throughout the video and collect the results in a dict
video_segments = {}  # video_segments contains the per-frame segmentation results
for out_frame_idx, out_obj_ids, out_mask_logits in predictor.propagate_in_video(
    inference_state
):
    video_segments[out_frame_idx] = {
        out_obj_id: (out_mask_logits[i] > 0.0).cpu().numpy()
        for i, out_obj_id in enumerate(out_obj_ids)
    }


# After running propagation and collecting results in video_segments
for out_frame_idx in range(len(frame_names)):
    # Load the original frame
    original_image = Image.open(
        os.path.join(input_frames_dir, frame_names[out_frame_idx])
    ).convert("RGBA")

    # Create a transparent image
    output_image = Image.new("RGBA", original_image.size, (0, 0, 0, 0))

    if out_frame_idx in video_segments:
        for out_obj_id, out_mask in video_segments[out_frame_idx].items():
            # Reshape the mask if necessary
            if out_mask.ndim == 3:
                out_mask = out_mask.squeeze()
            if out_mask.shape != original_image.size[::-1]:
                out_mask = out_mask.reshape(original_image.size[::-1])

            # Convert boolean mask to alpha channel
            alpha = Image.fromarray((out_mask * 255).astype(np.uint8))

            # Apply the mask to the original image
            original_array = np.array(original_image)
            alpha_array = np.array(alpha)
            original_array[:, :, 3] = alpha_array

            # Overlay this on the output image
            masked_image = Image.fromarray(original_array)
            output_image = Image.alpha_composite(output_image, masked_image)

    # Save the output image
    output_image.save(
        os.path.join(output_frames_dir, f"masked_content_{out_frame_idx:04d}.png")
    )


print(f"Masks saved to {output_frames_dir}")


# Step 4: Compile output video
final_output_path = f"{final_output_dir}/{WORD}_{VIDEO_ID}.mp4"
compile_output_video(output_frames_dir, final_output_path, fps)
print(f"Final video compiled and saved to {final_output_path}")
