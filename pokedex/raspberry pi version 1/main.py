import cv2
import time
import random
import argparse
import numpy as np
import pandas as pd
df = pd.read_csv("audio/pokemon.csv")

import subprocess
import time
image_path = "photos/photo.jpg" #no photos exist here until the special case is loaded
import os


img_formats = ['jpg', 'jpeg', 'png', 'tif', 'tiff', 'dng', 'webp', 'mpo']  # List of image formats

# This method extracts information from the pokemon.csv file. This code iterates throught he 
# rows until it sees the pokemon name, and then it goes through the columns to find information
# about the pokemon
def get_pokedex_entry(name):
    row = df[df['english_name'] == name]
    if row.empty:
        return f"{name} not found in Pokedex."

    row = row.iloc[0]

    primary_type = row['primary_type']
    secondary_type = row['secondary_type'] if pd.notna(row['secondary_type']) else None
    classification = row['classification']
    # height = row['height_m']
    # weight = row['weight_kg']
    height_m = row.get('height_m', None)
    weight_kg = row.get('weight_kg', None)

    # Convert height and weight if they exist
    if pd.notna(height_m):
        height_ft = round(height_m * 3.28084, 2)
        height_str = f"{height_m} meters ({height_ft} feet)"
    else:
        height_str = "an unknown height"

    if pd.notna(weight_kg):
        weight_lb = round(weight_kg * 2.20462, 2)
        weight_str = f"{weight_kg} kilograms ({weight_lb} pounds)"
    else:
        weight_str = "an unknown weight"
    
    ability = row['abilities_0']
    other_ability = row['abilities_1'] if pd.notna(row['abilities_1']) else None
    hidden_ability = row['abilities_hidden'] if pd.notna(row['abilities_hidden']) else None
    description = row['description']

    type_info = f"It is {primary_type}-type" + (f" and {secondary_type}-type" if secondary_type else "")
    ability_info = f"It's ability is {ability}."
    if other_ability:
        ability_info += f" It can also have the ability {other_ability}."
    if hidden_ability:
        ability_info += f" It's hidden ability is {hidden_ability}."

    entry = (
        f"{classification}. {name}. {type_info}. "
        f"It is {height_ft} feet tall and weighs {weight_lb} pounds. "
        f"{ability_info} {description}"
    )

    return entry

def speak_pokemon(name):
    text = get_pokedex_entry(name)
    subprocess.run(
        ['espeak', '-v', 'en-us+f3', '-s', '120', '-p', '40', text],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    #engine.say(get_pokedex_entry(name)) #f"{name}, a wild Pokemon!")
    #engine.runAndWait()
    #print("Done speaking")

def introduction():
    intro_str = """I'm Dexter, a Pokedex programmed by Brett Shelley."""
    subprocess.run(
        ['espeak', '-v', 'en-us+f3', '-s', '120', '-p', '40', intro_str],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    #engine.say(intro_str)
    #engine.runAndWait()

# Function to load the source (image, video, or webcam)
def loadSource(source_file):
    key = 1 # 1 = Video, 0 = Image
    frame = None
    cap = None

    # If source is a webcam
    if(source_file == "0"):
        image_type = False  # Not an image, it's video from the webcam
        source_file = 0    
    else:
        image_type = source_file.split('.')[-1].lower() in img_formats  # Check if source is an image

    if (source_file == "special"):
        return loadSpecialCase()

    # Open image or video source
    if(image_type):
        frame = cv2.imread(source_file)  # Read image
        key = 0  # Set key for image
    else:
        cap = cv2.VideoCapture(source_file)  # Open video capture for video or webcam

    return image_type, key, frame, cap

def loadSpecialCase():
    key = 0
    # take a picture with the bash command
    subprocess.run(
        ["libcamera-still", "-t", "1", "--nopreview", "-o", image_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    ) #blocking so it will finish and save
    # read picture and load into memory
    frame = cv2.imread(image_path)
    time.sleep(0.5)
    # delete the picture since it is already in memory
    subprocess.run(['rm', image_path], check=True)
    # see if the image is a valid type
    image_type = image_path.split('.')[-1].lower() in img_formats
    print("photo loaded")
    return image_type, key, frame, None

if __name__ == '__main__':
    # Add argument parser for command line input
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, default="special", help="Video")  # Video source
    parser.add_argument("--names", type=str, default="data/class.names", help="Object Names")  # File containing class names
    parser.add_argument("--model", type=str, default="pokedex.onnx", help="Pretrained Model")  # ONNX model file
    parser.add_argument("--thresh", type=float, default=0.4, help="Confidence Threshold")  # Confidence threshold for detection
    #parser.add_argument("--thickness", type=int, default=2, help="Line Thickness on Bounding Boxes")  # Thickness of bounding box lines, don't need it for pi
    args = parser.parse_args()    

    # Load the YOLO model
    model = cv2.dnn.readNet(args.model)

    IMAGE_SIZE = 640  # Set the image size for the model
    NAMES = []
    # Read the object names from the specified file
    with open(args.names, "r") as f:
        NAMES = [cname.strip() for cname in f.readlines()]
    COLORS = [[random.randint(0, 255) for _ in range(3)] for _ in NAMES]  # Generate random colors for each object class

    source_file = args.source    
    # Load the source (image, video, or webcam)
    image_type, key, frame, cap = loadSource(source_file)
    grabbed = True

    last_detected = None

    introduction()

    # print("CAP IS OPENED:", cap.isOpened())

    while True:
        # Made a special case for the camera workaround, where we
        # take a picture every 0.5 seconds
        if (source_file == "special"):
            image_type, key, frame, cap = loadSpecialCase()

        # For video input, read the next frame
        if not image_type:
            (grabbed, frame) = cap.read()
            print("Camera grabbed:", grabbed)

        # Make a copy of the frame
        image = frame.copy()
    
        # Prepare image as input for the YOLO model
        blob = cv2.dnn.blobFromImage(image, 1/255.0, (IMAGE_SIZE, IMAGE_SIZE), swapRB=True, crop=False)

        # Initialize lists for detection results
        class_ids, confs, boxes = list(), list(), list()

        # Set input to the model and perform forward pass
        model.setInput(blob)
        preds = model.forward()
        preds = preds.transpose((0, 2, 1))  # Adjust output shape

        # Calculate scaling factors based on image size
        image_height, image_width, _ = image.shape
        x_factor = image_width / IMAGE_SIZE
        y_factor = image_height / IMAGE_SIZE

        rows = preds[0].shape[0]

        # Iterate over each prediction row
        for i in range(rows):
            row = preds[0][i]
            conf = row[4]  # Confidence score
            
            # Extract class scores and find the class with the highest score
            classes_score = row[4:]
            _,_,_, max_idx = cv2.minMaxLoc(classes_score)
            class_id = max_idx[1]
            if (classes_score[class_id] > args.thresh):  # Filter out weak predictions
                confs.append(classes_score[class_id])  # Store confidence
                label = NAMES[int(class_id)]  # Get class label
                class_ids.append(class_id)  # Store class ID

                # Speak pokemon name if it isn't a repeat of the last
                if label != last_detected:
                    print(f"Detected: {label}")
                    speak_pokemon(label)
                    last_detected = label
                
                # Extract bounding box coordinates
                x, y, w, h = row[0].item(), row[1].item(), row[2].item(), row[3].item() 
                left = int((x - 0.5 * w) * x_factor)
                top = int((y - 0.5 * h) * y_factor)
                width = int(w * x_factor)
                height = int(h * y_factor)
                box = np.array([left, top, width, height])
                boxes.append(box)  # Store bounding box coordinates

        # Apply Non-Maximum Suppression (NMS) to eliminate overlapping boxes
        indexes = cv2.dnn.NMSBoxes(boxes, confs, 0.2, 0.5)         

        # Don't need bounding boxes and labels on the image for raspberry pi version

        # Indicate the image has been processed
        grabbed = False
