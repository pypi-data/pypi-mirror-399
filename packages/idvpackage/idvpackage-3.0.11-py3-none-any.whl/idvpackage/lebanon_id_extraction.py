from datetime import date
import base64
import time

from openai import OpenAI
from pydantic import BaseModel, Field
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    force=True,
)


def is_valid_past_date(date_str: str) -> bool:
    TODAY = date.today()

    # Must be a string in the format dd/mm/yyyy
    if not isinstance(date_str, str):
        return False

    try:
        parts = date_str.split("/")
        if len(parts) != 3:
            return False

        day, month, year = map(int, parts)
    except (ValueError, TypeError):
        return False

    # Rule 1: year > 1900
    if year <= 1900:
        return False

    # Rule 2: month 1..12
    if month < 1 or month > 12:
        return False

    # Basic month -> max day mapping; February handled with leap-year rule
    if month in (1, 3, 5, 7, 8, 10, 12):
        max_day = 31
    elif month in (4, 6, 9, 11):
        max_day = 30
    elif month == 2:
        # leap year?
        is_leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
        max_day = 29 if is_leap else 28
    else:
        return False  # unreachable but safe

    if day < 1 or day > max_day:
        return False

    # Now construct date and ensure it's strictly in the past (before TODAY)
    try:
        candidate = date(year, month, day)
    except ValueError:
        return False

    return candidate <= TODAY


PROMPT_PASSPORT = """
Extract ALL fields from this Lebanon Passport **front side** image with high accuracy.
Important: values ARE LOCATED UNDER THE LABEL in the passport layout. Always prefer the text that is directly below the label box. Do NOT pick nearby text, header text, or side text unless the value is physically beneath the label.
FIELD RULES (high precision)
1. Label -> value-under-label behavior:
   - For each field, find the label on the passport (e.g., "Date of Birth", "Surname", "Given Names", "Sex", "Nationality", "Passport No", "Place of Birth", "Authority", "Date of Issue").


Return a JSON object with the following fields (use the exact field names):
    - dob: Date of birth exactly as shown on the card, but always return in DD/MM/YYYY format (e.g., '15/06/1990'). If the card shows a different format, convert it to DD/MM/YYYY.
    - expiry_date: Date of expiry exactly as shown on the card, but always return in DD/MM/YYYY format (e.g., '15/06/1990'). If the card shows a different format, convert it to DD/MM/YYYY.
    - issue_date: Date of issue exactly as shown on the card, but always return in DD/MM/YYYY format (e.g., '15/06/1990'). If the card shows a different format, convert it to DD/MM/YYYY.
    - mrz1: First line of the MRZ
    - mrz2: Second line of the MRZ
    - last_name:  name as printed on the card (extract exactly as written) written as name
    - first_name: First name as printed on the card (extract exactly as written)
    - gender: Gender as either M or F (printed as Sex, extract exactly as written), if M output MALE if F output FEMALE
    - father_name: Father's name as printed on the card (extract exactly as written) value it right below First Name label
    - nationality: Nationality as printed on the card (extract exactly as written and return ISO 3166-1 alpha-3, e.g., LBN)
    - id_number: ID number as printed on the card (exactly 2 letters followed by 7 digits; pad with 0s if fewer digits)
    - place_of_birth: The place of birth in English (printed as Birth Place, extract exactly as written)
    - registry_place_and_number: Extract the registry place (in Arabic, as printed) and the registry number (as printed), and combine them in the format "<Arabic place> <number>"
    - authority: Authority as printed on the card (extract exactly as written below the label Authority)
    - mother_name: Mother's name as printed on the card (extract exactly as written), value is below the label Mother Full Name, which is on top of the passport
    - header_verified: Return True if one of the texts present in the image is "Republic of Lebanon" or "Républeue Libanaise", otherwise False.
    - dob_mrz: Date of birth as extracted from MRZ (in DD/MM/YYYY format)
    - id_number_mrz: ID number as extracted from MRZ
    - expiry_date_mrz: Expiry date as extracted from MRZ (in DD/MM/YYYY format)
    - gender_mrz: Gender as extracted from MRZ (M or F) if M return MALE else if F return FEMALE
Instructions:
    - Do NOT guess or hallucinate any values. If unclear, return empty string.
    - Only use information visible on the card.
    - Return the result as a single JSON object matching the schema above.
"""

PROMPT_FRONT_TEXT = """
You are a data parser for Lebanese National ID Cards. You will be provided with **RAW TEXT** extracted via OCR from the given image which is the front side of National ID card.

The OCR text may contain noise, or have lines out of order. Your task is to reconstruct the structured data by finding specific Arabic labels and values.

### 1. Extraction Rules (Pattern Matching)

* **Names:**
    * Look for the token **"الاسم"** (Name) -> The text following it is `first_name`.
    * Look for **"الشهرة"** (Surname/Fame) -> The text following it is `last_name`.
    * Look for **"اسم الاب"** (Father's Name) -> The text following it is `father_name`.
    * Look for **"اسم الام"** or **"اسم الام وشهرتها"** -> The text following it is `mother_name`.
    * *Action:* Extract the Arabic text exactly. Then, transliterate these names into English (`_en` fields).
    * Combine name, father_name and last_name to form `full_name`.

* **Place of Birth:**
    * Look for the keyword **"محل الولادة"** or **"محل الولاده"**.
    * Extract the text immediately following this label.

* **Date of Birth:**
    * Look for the keyword **"تاريخ الولادة"**.
    * Extract the date pattern (usually YYYY/MM/DD) following it.
    * *Format:* Convert the Arabic numerals (١٩٧٤/٠٥/٢٠) to Western digits (1974/05/20).

* **ID Number (The 12-Digit Code):**
    * **Crucial:** This number often appears **without a label** in the raw text.
    * *Pattern:* Search the entire text for a sequence of **exactly 12 digits** in arabic.
    * It is typically the longest numeric sequence in the text.

### 2. Instructions:
    - Do NOT guess or hallucinate any values. If unclear, return empty string.
    - Use only the information from the provided text.
    - Return the result as a single JSON object matching the schema above.
"""

PROMPT_BACK_TEXT = """
You are a data parser for Lebanese National ID Cards. You will be provided with **RAW TEXT** extracted via OCR from the given image which is the back side of National ID card.

### 1. Extraction Rules (Keyword Association)

Scan the text for the following Arabic labels. Extract the value associated with them.

* **Gender:**
    * Keyword: **"الجنس"**
    * Value: usually "ذكر" (Male) or "أنثى" / "انتى" (Female).
    * *Action:* Extract Arabic, then set `gender` to "MALE" or "FEMALE".

* **Marital Status:**
    * Keyword: **"الوضع العائلي"**
    * Value: "عزباء" (Single), "متأهل" (Married), "أرمل" (Widowed), "مطلق" (Divorced).
    * *Action:* Extract Arabic, then translate to English for `marital_status_en`.

* **Record Number (Sijil):**
    * Keyword: **"رقم السجل"** or just **"السجل"**.
    * *Pattern:* This is usually a short number (1 to 4 digits). Do NOT confuse this with dates or long ID numbers.

* **Location:**
    * **Village/Locality:** Look for **"المحلة"** or **"القرية"**.
    * **Governate:** Look for **"المحافظة"**.
    * **District:** Look for **"القضاء"**.

* **Issue Date:**
    * Keyword: **"تاريخ الإصدار"** or **"تاريخ الاصدار"**.
    * *Pattern:* Look for a date format (YYYY/MM/DD) specifically near this keyword.

### 2. Instructions:
    - Do NOT guess or hallucinate any values. If unclear, return empty string.
    - Use only the information from the provided text.
    - Return the result as a single JSON object matching the schema above.

"""


class LebaneseIDCardFront(BaseModel):
    first_name: str = Field(..., description="First in Arabic, exactly as printed.")
    name: str = Field(
        ...,
        description="Full name in Arabic, which is the combination of first name, father name and last name.",
    )
    name_en: str = Field(..., description="Transliterate full name into English.")
    father_name: str = Field(
        ..., description="Father name in Arabic, exactly as printed."
    )
    mother_name: str = Field(
        ..., description="Mother name in Arabic, exactly as printed."
    )
    last_name: str = Field(..., description="Last name in Arabic, exactly as printed.")
    first_name_en: str = Field(..., description="Transliterate first name into English.")
    father_name_en: str = Field(
        ..., description="Transliterate father's name into English."
    )
    mother_name_en: str = Field(
        ..., description="Transliterate mother's name into English."
    )
    last_name_en: str = Field(..., description="Transliterate last name into English.")
    id_number_ar: str = Field(
        ..., description="12-digit ID number in Arabic numerals, exactly as printed."
    )
    id_number: str = Field(
        ...,
        description="Convert 12-digit Arabic numercal ID number into Western/English digits (0-9).",
    )
    dob_ar: str = Field(
        ..., description="Date of Birth in Arabic numerals, exactly as printed."
    )
    dob: str = Field(
        ...,
        description="Convert Date of Birth from Arabic numerals to Western/English digits in YYYY/MM/DD format.",
    )
    place_of_birth: str = Field(
        ..., description="Place of Birth in Arabic, exactly as printed."
    )
    place_of_birth_en: str = Field(
        ..., description="Transliterate Place of Birth into English."
    )
    header_verified: bool = Field(
        ...,
        description="Whether the following texts are present in the image: وزارة الداخلية ,الجمهورية اللبنانية",
    )
    civil_status_verified: bool = Field(
        ...,
        description="Return True if any of the texts present in the image are General Directorate, Convergence, Municipalities, Personal Status, statement of individuals.",
    )


class LebaneseIDCardBack(BaseModel):
    gender_ar: str = Field(..., description="Gender in Arabic, exactly as printed.")
    gender: str = Field(
        ..., description="Transliterate gender into English as Male or Female"
    )
    marital_status: str = Field(
        ..., description="Marital Status in Arabic, exactly as printed."
    )
    marital_status_en: str = Field(
        ..., description="Transliterate marital status into English."
    )
    issue_date_ar: str = Field(
        ...,
        description="Issue Date in Arabic numerals, exactly as printed, in YYYY/MM/DD format.",
    )
    issue_date: str = Field(
        ...,
        description="Convert Issue Date from Arabic numerals to Western/English digits in DD/MM/YYYY format.",
    )
    card_number_ar: str = Field(
        ..., description="4-digit card number in Arabic numerals, exactly as printed."
    )
    card_number: str = Field(
        ...,
        description="Convert 4-digit Arabic numeral card number into Western/English digits (0-9).",
    )
    village_ar: str = Field(..., description="Village in Arabic, exactly as printed.")
    village_en: str = Field(..., description="Transliterate village into English.")
    governate_ar: str = Field(..., description="Governate in Arabic, exactly as printed.")
    governate_en: str = Field(..., description="Transliterate governate into English.")
    district_ar: str = Field(..., description="District in Arabic, exactly as printed.")
    district_en: str = Field(..., description="Transliterate district into English.")
    header_verified: bool = Field(
        ...,
        description="Whether any one of the words present in the translated text Marital status or Family or Release|Sex|Register number",
    )


class LebanonPassport(BaseModel):
    dob: str = Field(
        ...,
        description="The date of birth (preserve (dd/mm/yyyy) format)",
    )
    expiry_date: str = Field(
        ...,
        description="The date of expiry  (preserve (dd/mm/yyyy) format)",
    )

    mrz1: str = Field(..., description="First line of the MRZ")

    mrz2: str = Field(..., description="Second line of the MRZ")

    last_name: str = Field(
        ...,
        description=" name as printed on the card (extract exactly as written on the card  value is below the label First Name)",
    )

    first_name: str = Field(
        ...,
        description="First name as printed on the card (extract exactly as written on the card  value is below the label Name)",
    )

    gender: str = Field(
        ...,
        description="Gender as either M or F , (printed as Sex, extract exactly as written on the card  value is below the label Sex)",
    )

    father_name: str = Field(
        ...,
        description="father name name as printed on the card (extract exactly as written on the card, value is below the label Father Name) which is right below the First Name",
    )

    # mother_name: str = Field(...,
    #                   description= " Mother's full name as printed on the card (look for the label Mother Full Name and extract the name exactly as written in English, Even Arabic is present)"
    #                 )

    nationality: str = Field(
        ...,
        description="Nationality as printed on the card and return ISO 3166-1 alpha-3, e.g., LBN",
    )
    id_number: str = Field(
        ...,
        min_length=9,
        max_length=9,
        description="ID number as printed on the card, extract exactly as written on the card (exactly 2 letters followed by 7 digits; pad with 0s if fewer digits)",
    )

    place_of_birth: str = Field(
        ...,
        description="The place of birth in english(printed as Birth Place, extract exactly as written on the card)",
    )

    issue_date: str = Field(
        ...,
        description="The date of issue  (preserve (dd/mm/yyyy) format)",
    )

    place_of_birth: str = Field(
        ...,
        description="Place of birth as printed on the card.",
    )

    mother_name: str = Field(
        ...,
        description="Mother's name as printed on the card (extract exactly as written on the card, value is below the label Mother Full Name)",
    )
    registry_place_and_number: str = Field(
        ...,
        description="extract the registry place (in Arabic, as printed) and the registry number (as printed), and combine them in the format '<Arabic place> <number>'  value is below the  label registry Place and Number",
    )
    authority: str = Field(
        ...,
        description="Authority as printed on the card  value is below the label Authority",
    )

    header_verified: bool = Field(
        ...,
        description=" Return True if one of the texts present in the image Republic of Lebanon or Républeue Libanaise ",
    )

    dob_mrz: str = Field(
        ..., description="Date of birth as extracted from MRZ (in DD/MM/YYYY format)"
    )
    id_number_mrz: str = Field(..., description="ID number as extracted from MRZ")
    expiry_date_mrz: str = Field(
        ..., description="Expiry date as extracted from MRZ (in DD/MM/YYYY format)"
    )
    gender_mrz: str = Field(
        ...,
        description="Gender as extracted from MRZ (M or F) if M return MALE else if F return FEMALE",
    )


def process_image(side):
    if side == "first" or side == "page1":
        prompt = PROMPT_PASSPORT
        model = LebanonPassport

    else:
        logging.error(
            "Invalid document side specified. please upload front side of passport'."
        )
        return None, None

    return model, prompt


def process_text(side):
    if side == "front":
        prompt = PROMPT_FRONT_TEXT
        model = LebaneseIDCardFront

    elif side == "back":
        prompt = PROMPT_BACK_TEXT
        model = LebaneseIDCardBack

    else:
        raise ValueError("Invalid document side specified.")

    return model, prompt


def get_openai_response(prompt: str, model_type, image: str, genai_key):
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
                                "image_url": f"data:image/jpeg;base64,{image}",
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


def get_openai_response_from_text(
    prompt: str, model_type, image, extracted_text: str, genai_key
):
    for attempt in range(3):
        try:
            client = OpenAI(api_key=genai_key)
            response = client.responses.parse(
                model="gpt-4.1-mini",
                input=[
                    {
                        "role": "system",
                        "content": "You are an expert at extracting information from identity documents and extracted raw text.",
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "input_text", "text": prompt},
                            {"type": "input_text", "text": extracted_text},
                            {
                                "type": "input_image",
                                "image_url": f"data:image/jpeg;base64,{image}",
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


def get_response_from_openai_lbn(image, side, openai_key):
    logging.info("Processing image for Lebanon passport extraction OPENAI......")
    logging.info(f" and type: {type(image)}")
    try:
        image = base64.encodebytes(image).decode("utf-8")
    except Exception as e:
        logging.error(f"Error encoding image: {e}")
        return {"error": "Image encoding failed"}
    try:
        model, prompt = process_image(side)
        if model is None or prompt is None:
            return {
                "error": "Invalid document side specified. please upload front side of passport'."
            }
        logging.info(f"Using model: {model.__name__} and prompt {prompt[:100]}")
    except ValueError as ve:
        logging.error(f"Error: {ve}")
        return {"error": str(ve)}

    try:
        start_time = time.time()
        response = get_openai_response(prompt, model, image, openai_key)
        logging.info(f"OpenAI response time: {time.time() - start_time} seconds")
    except Exception as e:
        logging.error(f"Error during OpenAI request: {e}")
        return {"error": "OpenAI request failed"}

    response_data = vars(response)
    logging.info(f"Openai response: {response}")
    return response_data


def lebanon_id_extraction_from_text(extracted_text, image, side, openai_key):
    logging.info("Processing Lebanon ID front side extraction......")
    try:
        image = base64.encodebytes(image).decode("utf-8")
    except Exception as e:
        logging.error(f"Error encoding image: {e}")
        return {"error": "Image encoding failed"}
    try:
        model, prompt = process_text(side)
        logging.info(f"Using model: {model.__name__} and prompt {prompt[:100]}")
    except ValueError as ve:
        logging.error(f"Error: {ve}")
        return {"error": str(ve)}

    try:
        start_time = time.time()
        response = get_openai_response_from_text(
            prompt, model, image, extracted_text, openai_key
        )
        logging.info(f"OpenAI response time: {time.time() - start_time} seconds")
    except Exception as e:
        logging.error(f"Error during OpenAI request: {e}")
        return {"error": "OpenAI request failed"}

    response_data = vars(response)
    logging.info(f"Openai response: {response}")
    return response_data
