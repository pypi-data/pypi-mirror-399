
import base64
import time
from io import BytesIO
from typing import Optional
import cv2

from openai import OpenAI
from pydantic import BaseModel, Field
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)


PROMPT_PASSPORT = """
Extract ALL fields from this Jordan Passport **front side** image with high accuracy.

Return a JSON object with the following fields (use the exact field names):

- dob: Date of birth exactly as shown on the card, but always return in DD/MM/YYYY format (e.g., '15/06/1990'). If the card shows a different format, convert it to DD/MM/YYYY.
- date_of_expiry: Date of expiry exactly as shown on the card, but always return in DD/MM/YYYY format (e.g., '15/06/1990'). If the card shows a different format, convert it to DD/MM/YYYY.
- mrz1: First line of the MRZ (extract exactly as written).
- mrz2: Second line of the MRZ (extract exactly as written).
- name: Full name as printed on the card (extract exactly as written).
- first_name: First name as printed on the card (extract exactly as written).
- gender: Gender as either M or F (printed as Sex; output MALE if M, FEMALE if F).
- place_of_issue: Issuing place as printed on the card (extract exactly as written).
- full_name: Full name as printed on the card (extract exactly as written).
- last_name: Last name from the full name (extract exactly as written; if not present, return null).
- mother_name: Mother's full name as printed on the card (look for the label "Mother Full Name" and extract the name exactly as written in English, even if Arabic is present).
- nationality: Nationality as printed on the card and return ISO 3166-1 alpha-3 code (e.g., JOR).
- passport_national_number: National number as printed on the card (extract exactly as written) return empty string if not present.
- passport_number: Passport number as printed on the card (exactly 8 characters)
- issuing_date: Date of issue exactly as shown on the card, always in DD/MM/YYYY format.
- place_of_birth: Place of birth as printed on the card, tagged under Address (extract exactly as written).
- header_verified: Return True if any of these texts are present in the image: "Hashemite Kingdom of Jordan", "Hashemite Kingdom", or "Jordan"; otherwise False.
- dob_mrz: Date of birth as extracted from MRZ (in DD/MM/YYYY format)
- id_number_mrz: ID number as extracted from MRZ
- expiry_date_mrz: Expiry date as extracted from MRZ (in DD/MM/YYYY format)
- gender_mrz: Gender as extracted from MRZ (M or F) if M return MALE else if F return FEMALE

Instructions:
Instructions:
- Do NOT guess or hallucinate any values. If unclear,return empty string.
- Only use information visible on the card.
- Return the result as a single JSON object matching the schema above.
"""


class JordanPassportFront(BaseModel):
    dob: str = Field(
        ...,
        description="The date of birth (preserve (dd/mm/yyyy) format)",
    )
    expiry_date: str = Field(
        ...,
        description="The date of expiry  (preserve (dd/mm/yyyy) format) tagged as Date if Expiry",
    )

    mrz1: str = Field(..., description="First line of the MRZ")

    mrz2: str = Field(..., description="Second line of the MRZ")

    name: str = Field(
        ...,
        description="Full name as printed on the card (extract exactly as written on the card)",
    )

    first_name: str = Field(
        ...,
        description="First name as printed on the card (extract exactly as written on the card)",
    )

    gender: str = Field(
        ...,
        description="Gender as either M or F , (printed as Sex,  Male if M or Female if F)",
    )

    place_of_issue: str = Field(
        ...,
        description="Issuing place as printed on the card (extract exactly as written on the card)",
    )

    full_name: str = Field(
        ...,
        description="Full name as printed on the card (extract exactly as written on the card)",
    )

    last_name: Optional[str] = Field(
        None,
        description="Last name from the full name",
    )

    mother_name: str = Field(
        ...,
        description=" Mother's full name as printed on the card (look for the label Mother Full Name and extract the name exactly as written in English, Even Arabic is present)",
    )

    nationality: str = Field(
        ...,
        description="Nationality as printed on the card and return ISO 3166-1 alpha-3, e.g., JOR",
    )

    passport_number: str = Field(
        ...,
        min_length=8,
        max_length=8,
        description="ID number as printed on the card, extract exactly as written on the card ",
    )

    passport_national_number: str = Field(
        ...,
        description="National number as printed on the card, extract exactly as written on the card  return empty string if not present",
    )

    issuing_date: str = Field(
        ...,
        description="The date of issue  (preserve (dd/mm/yyyy) format)",
    )

    place_of_birth: str = Field(
        ...,
        description="Place of birth as printed on the card tagged under Address tag, extract exactly as written on the card",
    )

    header_verified: bool = Field(
        ...,
        description=" Return True if one of the texts present in the image Hashemite Kingdom of Jordan or Hashemite Kingdom or Jordan ",
    )
    
    dob_mrz: str = Field(
        ..., description="Date of birth as extracted from MRZ (in DD/MM/YYYY format)"
    )
    passport_number_mrz: str = Field(
        ..., description="Passport number as extracted from MRZ"
    )
    expiry_date_mrz: str = Field(
        ..., description="Expiry date as extracted from MRZ (in DD/MM/YYYY format)"
    )
    gender_mrz: str = Field(
        ..., description="Gender as extracted from MRZ (M or F) if M return MALE else if F return FEMALE"
    )


def process_image(side):
    if side == "first" or side == "page1":
        prompt = PROMPT_PASSPORT
        model = JordanPassportFront

    else:
        raise ValueError(
            "Invalid document side specified. please upload front side of passport'."
        )

    return model, prompt


def get_openai_response(prompt: str, model_type, image: BytesIO, genai_key):
    b64_image = base64.b64encode(image.getvalue()).decode("utf-8")
    for attempt in range(3):
        try:
            client = OpenAI(api_key=genai_key)
            response = client.responses.parse(
                model="gpt-4.1-mini",
                input=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting information from identity documents.",
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt},
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{b64_image}",
                                "detail": "low",
                            },
                        ],
                    },
                ],
                text_format=model_type,
            )
            return response.output_parsed
        except Exception as e:
            logging.info(f"[ERROR] Attempt {attempt + 1} failed: {str(e)}")
            time.sleep(2)
    return None


def _image_to_jpeg_bytesio(image) -> BytesIO:
    """
    Accepts: numpy.ndarray (OpenCV BGR), PIL.Image.Image, bytes/bytearray, or io.BytesIO
    Returns: io.BytesIO containing JPEG bytes (ready for get_openai_response)
    """
    import numpy as np

    if isinstance(image, BytesIO):
        image.seek(0)
        return image

    if isinstance(image, (bytes, bytearray)):
        return BytesIO(image)

    try:
        from PIL.Image import Image as _PILImage

        if isinstance(image, _PILImage):
            buf = BytesIO()
            image.convert("RGB").save(buf, format="JPEG", quality=95)
            buf.seek(0)
            return buf
    except Exception:
        pass

    if isinstance(image, np.ndarray):
        success, enc = cv2.imencode(".jpg", image)
        if not success:
            raise ValueError("cv2.imencode failed")
        return BytesIO(enc.tobytes())

    raise TypeError(
        "Unsupported image type. Provide numpy.ndarray, PIL.Image.Image, bytes, or io.BytesIO."
    )


def get_response_from_openai_jor(image, side, country, openai_key):
    logging.info("Processing image for Jordan passport extraction OPENAI......")
    logging.info(f" and type: {type(image)}")
    try:
        image = _image_to_jpeg_bytesio(image)
    except Exception as e:
        logging.error(f"Error encoding image: {e}")
        return {"error": "Image encoding failed"}
    try:
        model, prompt = process_image(side)
        logging.info(f"Using model: {model.__name__} and prompt {prompt[:100]}")
    except ValueError as ve:
        logging.error(f"Error: {ve}")
        return {"error": str(ve)}

    try:
        response = get_openai_response(prompt, model, image, openai_key)
    except Exception as e:
        logging.error(f"Error during OpenAI request: {e}")
        return {"error": "OpenAI request failed"}

    response_data = vars(response)
    logging.info(f"Openai response: {response}")
    return response_data
