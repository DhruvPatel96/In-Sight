import cv2
import json
import torch
from ultralytics import YOLO

def process_video(queue, video_path):
    # Ensure CUDA is available and set the device to GPU
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")

    # Load YOLOv8 model
    model = YOLO('yolov8n.pt')

    # Move the model to the GPU if available
    if device.type == 'cuda':
        model.to(device)

    # Open the video file
    cap = cv2.VideoCapture(video_path)

    # Check if video opened successfully
    if not cap.isOpened():
        print("Error opening video file")
        return

    boundary_box = {}
    frame_index = 0
    chunk_size = 100 # Process 100 frames at a time

    while True:
        frames = []
        for _ in range(chunk_size):
            ret, frame = cap.read()
            if not ret:
                break # Break the loop if no more frames
            frames.append(frame)
        if not frames:
            break # No more frames to process

        for frame in frames:
            # Resize the frame to a size divisible by 32 (e.g., 640x640)
            frame_resized = cv2.resize(frame, (640, 640))

            # Convert the resized frame to a tensor, normalize it, and move it to the device
            frame_tensor = torch.from_numpy(frame_resized).permute(2, 0, 1).float().div(255).unsqueeze(0).to(device)

            # Perform object detection on the frame
            results_gen = model(frame_tensor, tracker="bytetracker.yaml", stream=True, show=True)

            # Iterate over the generator to process each result
            for result in results_gen:
                # Extract bounding boxes and convert to list
                boundary_box[frame_index] = result.boxes.xyxy.cpu().numpy().tolist()
                frame_index += 1

        # Optionally, free up GPU memory
        torch.cuda.empty_cache()

    # Release the video capture object
    cap.release()

    # Convert results to JSON
    results_json = json.dumps(boundary_box)

    # Put JSON results in the queue
    queue.put(results_json)
