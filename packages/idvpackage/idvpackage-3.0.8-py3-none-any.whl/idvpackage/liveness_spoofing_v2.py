import cv2
import os
import numpy as np
from deepface import DeepFace
from idvpackage.spoof_resources.generate_patches import CropImage
import torch
import torch.nn.functional as F
from idvpackage.spoof_resources.MiniFASNet import MiniFASNetV1SE, MiniFASNetV2
from idvpackage.spoof_resources import transform as trans
import pkg_resources
from concurrent.futures import ThreadPoolExecutor
import logging 
MODEL_MAPPING = {"MiniFASNetV1SE": MiniFASNetV1SE, "MiniFASNetV2": MiniFASNetV2}


def get_bbox(frame):
    try:
        face_objs = DeepFace.extract_faces(frame, detector_backend="fastmtcnn")
        if face_objs:
            biggest_face = max(
                face_objs,
                key=lambda face: face["facial_area"]["w"] * face["facial_area"]["h"],
            )
            facial_area = biggest_face["facial_area"]
            x, y, w, h = (
                facial_area["x"],
                facial_area["y"],
                facial_area["w"],
                facial_area["h"],
            )
            bbox = [x, y, w, h]
            return bbox
        else:
            return None
    except Exception as e:
        print(f"Error in face detection: {e}")
        return None


def parse_model_name(model_name):
    info = model_name.split("_")[0:-1]
    h_input, w_input = info[-1].split("x")
    model_type = model_name.split(".pth")[0].split("_")[-1]
    scale = None if info[0] == "org" else float(info[0])
    return int(h_input), int(w_input), model_type, scale


def get_kernel(height, width):
    return ((height + 15) // 16, (width + 15) // 16)


def load_model(model_path):
    model_name = os.path.basename(model_path)
    h_input, w_input, model_type, _ = parse_model_name(model_name)
    kernel_size = get_kernel(h_input, w_input)
    model = MODEL_MAPPING[model_type](conv6_kernel=kernel_size).to("cpu")
    state_dict = torch.load(model_path, map_location="cpu")
    new_state_dict = (
        {k[7:]: v for k, v in state_dict.items()}
        if next(iter(state_dict)).startswith("module.")
        else state_dict
    )
    model.load_state_dict(new_state_dict)
    model.eval()
    return model


def predict(img, model):
    test_transform = trans.Compose([trans.ToTensor()])
    img = test_transform(img).unsqueeze(0).to("cpu")
    with torch.no_grad():
        result = model.forward(img)
        result = F.softmax(result).cpu().numpy()
    return result


def check_image(image):
    height, width, _ = image.shape
    if width / height != 3 / 4:
        print("Image is not appropriate!!!\nHeight/Width should be 4/3.")
        return False
    return True


# def frame_count_and_save(cap):
#     frames = []
#     frame_skip = 8
#     frame_index = 1
#     status, frame = cap.read()
#     while status:
#         if frame_index % frame_skip == 0:
#             frames.append(frame)
#         frame_index += 1
#         status, frame = cap.read()
#     cap.release()
#     return frames


def process_frame(frame, models, image_cropper):
    frame = cv2.resize(frame, (int(frame.shape[0] * 3 / 4), frame.shape[0]))
    if not check_image(frame):
        return None
    bbox = get_bbox(frame)
    if not bbox:
        return None
    prediction = np.zeros((1, 3))
    for model_name, model in models.items():
        h_input, w_input, model_type, scale = parse_model_name(model_name)
        param = {
            "org_img": frame,
            "bbox": bbox,
            "scale": scale,
            "out_w": w_input,
            "out_h": h_input,
            "crop": True if scale is not None else False,
        }
        img = image_cropper.crop(**param)
        prediction += predict(img, model)
        print("Model: {}, Prediction: {}".format(model_name, prediction))

    label = np.argmax(prediction)
    value = prediction[0][label] / 2
    label_text = (
        "LIVE"
        if (label == 1 and value > 0.45) or (label == 2 and value < 0.55)
        else "SPOOF"
    )
    return label_text


def get_frames_from_video(video_path):

    frames_to_process = []
    cap = None

    try:
        if not video_path or not isinstance(video_path, str):
            logging.error("Invalid video path provided.")
            return []

        #open video capture
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            logging.error(f"Failed to open video file: {video_path}")
            return []
        
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

        logging.info(f"Total frame count in video: {frame_count}")

        if frame_count <= 0:
            logging.error(f"invalid frame count ({frame_count}) for video: {video_path}")
            return []

        if frame_count < 6:
            logging.info(f"Video has less than 6 frames ({frame_count}). Processing all frames.")
            for i in range(frame_count):
                cap.set(cv2.CAP_PROP_POS_FRAMES, i)
                status, frame = cap.read()
                if status:
                    frames_to_process.append(frame)
        else:
            logging.info(f"Video has {frame_count} frames. Extracting 6 representative frames.")
            frame_positions = [
                int(frame_count * 0.05),
                int(frame_count * 0.15),
                int(frame_count * 0.45),
                int(frame_count * 0.55),
                int(frame_count * 0.85),
                int(frame_count * 0.95),
            ]
            
            logging.info(f"Calculated frame positions for extraction: {frame_positions}")

            for pos in frame_positions:
                position = max(0, min(pos, frame_count - 1))
                logging.info(f"Extracting frame at position: {position}")
                cap.set(cv2.CAP_PROP_POS_FRAMES, position)
                status, frame = cap.read()
                if status and frame is not None:
                    if frame.size > 0:
                        frames_to_process.append(frame)
                    else:
                        logging.warning(f"Extracted frame at position {position} is empty.")
                else:
                    logging.warning(f"Failed to read frame at position {position}.")
            
            logging.info(f"Total frames extracted for processing: {len(frames_to_process)} from frame count {frame_count}")
            

            if not frames_to_process:
                logging.error("No valid frames extracted from video.")
                
            return frames_to_process
        
    except Exception as e:
        logging.error(f"Error during frame extraction: {e}")
        return []

    finally:
        if cap is not None:
            logging.info("Releasing video capture resources....")
            cap.release()

def test(video_path):
    image_cropper = CropImage()
    models = {
        "2.7_80x80_MiniFASNetV2.pth": load_model(
            pkg_resources.resource_filename(
                "idvpackage", "spoof_resources/2.7_80x80_MiniFASNetV2.pth"
            )
        ),
        "4_0_0_80x80_MiniFASNetV1SE.pth": load_model(
            pkg_resources.resource_filename(
                "idvpackage", "spoof_resources/4_0_0_80x80_MiniFASNetV1SE.pth"
            )
        ),
    }

    frames_to_process = get_frames_from_video(video_path)

    logging.info(f"Total frames extracted for processing: {len(frames_to_process)}")

    # frames = frame_count_and_save(cap)
    # frames_to_process = (
    #     [frames[0], frames[3], frames[6], frames[-7], frames[-4], frames[-1]]
    #     if len(frames) > 3
    #     else frames[:]
    # )

    #if no frames to process, return unknown
    if not frames_to_process:
        logging.error("No frames to process for liveness detection.")
        return ""
    
    else:
        all_predictions = []
        with ThreadPoolExecutor() as executor:
            futures = [
                executor.submit(process_frame, frame, models, image_cropper)
                for frame in frames_to_process
            ]
            for future in futures:
                result = future.result()
                if result:
                    all_predictions.append(result)

        if all_predictions.count("SPOOF") >= 3:
            # print('\n##################\nConsider\n##################\n')
            return "consider"

        # print('\n##################\nClear\n##################\n')
        return "clear"

        # for frame in frames_to_process:
        #     result = process_frame(frame, models, image_cropper)
        #     if result:
        #         all_predictions.append(result)

        # if all_predictions.count("SPOOF") >= 3:
        #     # print('\n##################\nConsider\n##################\n')
        #     return "consider"

        # # print('\n##################\nClear\n##################\n')
        # return "clear"
