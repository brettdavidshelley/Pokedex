import cv2  # OpenCV for image/video processing
import time  # Timing functions (not currently used but might come in handy)
import random  # Random colors for drawing boxes
import argparse  # Command-line argument parsing
import numpy as np  # Numerical operations, especially arrays
import pandas as pd  # Data handling (used to read the Pokédex CSV)

# Load the Pokédex data from a CSV file
df = pd.read_csv("audio/pokemon.csv")

import pyttsx3  # Text-to-speech engine

# Initialize the text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 160)  # Speed it up for a more robotic "Dexter" vibe
engine.setProperty('voice', 'english')  # Use the default English voice

# Generate a spoken Pokédex entry from the CSV data
def get_pokedex_entry(name):
    row = df[df['english_name'] == name]
    if row.empty:
        return f"{name} not found in Pokedex."  # Mystery Pokémon?

    row = row.iloc[0]  # Get the first matching row

    # Extract relevant info
    primary_type = row['primary_type']
    secondary_type = row['secondary_type'] if pd.notna(row['secondary_type']) else None
    classification = row['classification']
    height_m = row.get('height_m', None)
    weight_kg = row.get('weight_kg', None)

    # Convert height and weight if they're available
    # height_str = f"{height_m} meters ({round(height_m * 3.28084, 2)} feet)" if pd.notna(height_m) else "an unknown height"
    # weight_str = f"{weight_kg} kilograms ({round(weight_kg * 2.20462, 2)} pounds)" if pd.notna(weight_kg) else "an unknown weight"
    height_str = f"{round(height_m * 3.28084, 2)} feet" if pd.notna(height_m) else "an unknown height"
    weight_str = f"{round(weight_kg * 2.20462, 2)} pounds" if pd.notna(weight_kg) else "an unknown weight"

    ability = row['abilities_0']
    other_ability = row['abilities_1'] if pd.notna(row['abilities_1']) else None
    hidden_ability = row['abilities_hidden'] if pd.notna(row['abilities_hidden']) else None
    description = row['description']

    # Construct the type and ability info text
    type_info = f"It is {primary_type}-type" + (f" and {secondary_type}-type" if secondary_type else "")
    ability_info = f"It's ability is {ability}."
    if other_ability:
        ability_info += f" It can also have the ability {other_ability}."
    if hidden_ability:
        ability_info += f" It's hidden ability is {hidden_ability}."

    # Construct the final Pokédex entry
    entry = (
        f"{classification}. {name}. {type_info}. "
        f"It is {height_str} tall and weighs {weight_str}. "
        f"{ability_info} {description}"
    )

    return entry

# Speak the Pokédex entry for a Pokémon
def speak_pokemon(name):
    engine.say(". . . " + get_pokedex_entry(name))
    engine.runAndWait()

# Load an image, video, or webcam stream
def loadSource(source_file):
    img_formats = ['jpg', 'jpeg', 'png', 'tif', 'tiff', 'dng', 'webp', 'mpo']
    key = 1  # Key for video display speed; 0 for images
    frame = None
    cap = None

    if source_file == "0":
        image_type = False  # Webcam is considered video
        source_file = 0
    else:
        # Check if the file is an image based on extension
        image_type = source_file.split('.')[-1].lower() in img_formats

    # Load image or video
    if image_type:
        frame = cv2.imread(source_file)
        key = 0  # Show image until a key is pressed
    else:
        cap = cv2.VideoCapture(source_file)

    return image_type, key, frame, cap

# Introduce Dexter with a classic Pokédex-style monologue
def introduction():
    intro_str = """Hi, I'm Dexter, a Pokedex programmed by Brett Shelley for Pokemon trainer Brett Shelley of the town of Milton Georgia.
    My function is to provide Brett with information and advice regarding Pokemon and their training.
    If lost or stolen, I cannot be replaced."""
    intro_str = "Hi, I'm Dexter, a Pokedex programmed by Brett Shelley."  # Simplified for now
    engine.say(". . . " + intro_str)
    engine.runAndWait()

# Main function starts here
if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=str, default="0", help="Video source (0 for webcam)")
    parser.add_argument("--names", type=str, default="data/class.names", help="File with Pokémon class names")
    parser.add_argument("--model", type=str, default="pokedex.onnx", help="ONNX model file")
    parser.add_argument("--thresh", type=float, default=0.75, help="Detection confidence threshold")
    parser.add_argument("--thickness", type=int, default=2, help="Bounding box thickness")
    args = parser.parse_args()

    # Load the YOLO model
    model = cv2.dnn.readNet(args.model)

    IMAGE_SIZE = 640  # Image input size for the model
    NAMES = []

    # Load class names from file
    with open(args.names, "r") as f:
        NAMES = [cname.strip() for cname in f.readlines()]

    # Assign random colors for each class label (so Pikachu doesn’t blend into the bushes)
    COLORS = [[random.randint(0, 255) for _ in range(3)] for _ in NAMES]

    # Load image/video source
    source_file = args.source
    image_type, key, frame, cap = loadSource(source_file)
    grabbed = True  # Used to control frame reading
    last_detected = None  # Track last detected Pokémon to avoid repeats

    # Gotta start with an intro!
    introduction()

    while True:
        # Grab the next frame for video sources
        if not image_type:
            (grabbed, frame) = cap.read()

        if not grabbed:
            exit()  # If no frame is available, quit

        image = frame.copy()

        # Prepare image for YOLO model
        blob = cv2.dnn.blobFromImage(image, 1/255.0, (IMAGE_SIZE, IMAGE_SIZE), swapRB=True, crop=False)
        model.setInput(blob)
        preds = model.forward()
        preds = preds.transpose((0, 2, 1))  # Reshape output

        # Calculate scaling factors to match image dimensions
        image_height, image_width, _ = image.shape
        x_factor = image_width / IMAGE_SIZE
        y_factor = image_height / IMAGE_SIZE

        rows = preds[0].shape[0]

        class_ids, confs, boxes = [], [], []

        pokemonName = None

        for i in range(rows):
            row = preds[0][i]
            conf = row[4]

            # Get class scores and determine the best class
            classes_score = row[4:]
            _, _, _, max_idx = cv2.minMaxLoc(classes_score)
            class_id = max_idx[1]

            if classes_score[class_id] > args.thresh:
                confs.append(classes_score[class_id])
                label = NAMES[int(class_id)]
                class_ids.append(class_id)

                # Only speak if it's a new detection
                if label != last_detected:
                    #print(f"Detected: {label}")
                    pokemonName = label
                    last_detected = label
                    #speak_pokemon(label)

                # Extract bounding box details
                x, y, w, h = row[0].item(), row[1].item(), row[2].item(), row[3].item()
                left = int((x - 0.5 * w) * x_factor)
                top = int((y - 0.5 * h) * y_factor)
                width = int(w * x_factor)
                height = int(h * y_factor)
                box = np.array([left, top, width, height])
                boxes.append(box)

        # Apply Non-Maximum Suppression to reduce duplicate boxes
        indexes = cv2.dnn.NMSBoxes(boxes, confs, 0.2, 0.5)

        for i in indexes:
            box = boxes[i]
            class_id = class_ids[i]
            score = confs[i]

            left, top, width, height = box

            # Draw bounding box
            cv2.rectangle(image, (left, top), (left + width, top + height), COLORS[class_id], args.thickness)

            # Add label with confidence score
            name = NAMES[class_id]
            score = round(float(score), 3)
            label_text = f'{name} {score}'

            font_size = args.thickness / 2.5
            margin = args.thickness * 2
            cv2.putText(image, label_text, (left, top - margin), cv2.FONT_HERSHEY_SIMPLEX, font_size, COLORS[class_id], args.thickness)

        # Mark the frame as processed
        grabbed = False

        # Show the image with detections
        cv2.imshow("Detected", image)

        if pokemonName:
            print(f"Detected: {label}")
            speak_pokemon(label)

        # Exit on 'q'
        if cv2.waitKey(key) == ord('q'):
            break

