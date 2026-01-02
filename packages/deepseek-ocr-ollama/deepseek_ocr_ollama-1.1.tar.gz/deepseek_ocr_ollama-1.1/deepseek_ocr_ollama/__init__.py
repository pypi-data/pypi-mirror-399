#!/usr/bin/env python
import base64
from io import BytesIO
from pathlib import Path
import mimetypes
from enum import Enum
import sys
import ollama
import json
from PIL import Image
import fitz
from collections import namedtuple
from .ref import RefDet, RefImage
from tqdm import tqdm

def convert_to_object(data):
    if isinstance(data, dict):
        converted_data = {
            key: convert_to_object(value) 
            for key, value in data.items()
        }
        return namedtuple('GenericObject', converted_data.keys())(**converted_data)
    elif isinstance(data, list):
        return [convert_to_object(item) for item in data]
    else:
        return data

def object_to_dict(obj):
    if hasattr(obj, '_asdict'):
        return dict((key, object_to_dict(value)) for key, value in obj._asdict().items())
    elif isinstance(obj, list):
        return [object_to_dict(element) for element in obj]
    else:
        return obj

class Modes(Enum):
    FULL = 0
    FULL_ALT = 1
    FULL_NO_DIR = 2
    FULL_NO_PAGES = 3
    TEXT = 4
    TEXT_NO_PAGES = 5

class OllamaOCRClient:
    def __init__(self, 
                 model_name="deepseek-ocr", 
                 dpi: int = 600,
                 include_image_base64: bool = True,
                 raw_prompt: str = None,
                 hint: str = None,
                 verbosity_level: int = 1
                 ):
        self.model_name = model_name
        self.dpi = dpi
        self.include_image_base64 = include_image_base64
        self.raw_prompt = raw_prompt
        self.hint = hint
        self.image_counter = 0
        self.verbosity_level = verbosity_level

    def process_image(self, image, index_page=0):
        response = self.process_deepseek(image)
        elements_boxes = RefDet.elements_boxes(response.message.content)
        base_image = RefImage(image)
        content = []
        images = []
        for rd in elements_boxes:
            if not isinstance(rd, RefDet):
                content.append(rd)
            elif rd.ref.lower() == "image":
                r = base_image.get_cropped_elements([rd])
                for ref, img, box in r:
                    if self.verbosity_level > 1:
                        print(f"Processing image box: {box}, ref: {ref}")
                    image_name = f"img_{self.image_counter}.png"
                    self.image_counter += 1
                    img_base64 = self.pil_image_to_base64(img) if self.include_image_base64 else None
                    content.append(f"![{image_name}]({image_name})")
                    images.append({
                        "id": image_name,
                        "image_base64": f"data:image/jpeg;base64,{img_base64}" if img_base64 else None,
                        "top_left_x": box[0],
                        "top_left_y": box[1],
                        "bottom_right_x": box[2],
                        "bottom_right_y": box[3],
                    })
        dimensions = {
            "width": image.width,
            "height": image.height
        }
        if self.dpi:
            dimensions["dpi"] = self.dpi
        return {
            "index": index_page,
            "markdown": "\n".join(content),
            "images": images,
            "dimensions": dimensions
        }

    def ocr_process(self, 
                    document_path: Path
                    ):
        images = self.process_images(document_path)

        pages = []
        _images = enumerate(images)
        if self.verbosity_level > 0:
            _images = tqdm(_images, total=len(images), desc="Processing pages")

        for i, image in _images:
            page_data = self.process_image(image, index_page=i)
            pages.append(convert_to_object(page_data))

        return convert_to_object({
            "pages": pages,
            "model": self.model_name
        })
    
    def pil_image_to_base64(self, image: Image.Image):
        buffered = BytesIO()
        image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
        return img_str

    def process_deepseek(self, image):
        if self.raw_prompt:
            prompt = self.raw_prompt
        else:
            prompt = "<image>\n<|grounding|>Convert the document to markdown."
            if self.hint:
                prompt += f" {self.hint}"
        try:
            response = ollama.chat(
                model='deepseek-ocr',
                messages=[
                    {"role": "user",
                        "content": "<image>\n<|grounding|>Convert the document to markdown.",
                        "images": [self.pil_image_to_base64(image)]
                    }
                ],
            )
        except Exception as e:
            print(f"Connection error while communicating with Ollama: {e}", file=sys.stderr)
            sys.exit(1)
        return response
    
    def process_images(self, document_path: Path):
        mimetype, _ = mimetypes.guess_type(document_path)
        if mimetype.startswith("image/"):
            self.dpi = None
            images = [Image.open(document_path)]
        elif mimetype == "application/pdf":
            pdf_doc = fitz.open(document_path)
            images = []
            for page_num in range(len(pdf_doc)):
                page = pdf_doc.load_page(page_num)
                pix = page.get_pixmap(dpi=self.dpi)
                img_data = pix.tobytes("png")
                image = Image.open(BytesIO(img_data))
                images.append(image)
            pdf_doc.close()
        else:
            images = []
        return images

def get_mode_from_string(mode_str: str):
    for mode in Modes:
        if mode.name == mode_str.upper() or mode.value == mode_str:
            return mode
    raise ValueError(f"Unknown mode: {mode_str}")

def b64encode_document(document_path: Path):
    try:
        with open(document_path, "rb") as doc_file:
            return base64.b64encode(doc_file.read()).decode('utf-8')
    except FileNotFoundError:
        return None
    except Exception as e:
        return None
    
def b64decode_document(base64_data: str, output_path: Path):
    if ',' in base64_data:
        _, base64_str = base64_data.split(',', 1)
    else:
        base64_str = base64_data
    try:
        image_data = base64.b64decode(base64_str)
    except (base64.binascii.Error, ValueError) as e:
        print(f"Error decoding base64 data: {e}", file=sys.stderr)
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'wb') as f:
        f.write(image_data)

class Page:
    def __init__(self, index, markdown=None, images=None):
        self.index = index
        self.markdown = markdown
        self.images = images if images is not None else []

    def write_markdown(self, output_path: Path, append: bool = False, insert = None):
        if self.markdown:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            mode = 'a' if append else 'w'
            with open(output_path, mode) as md_file:
                if insert:
                    md_file.write(insert)
                md_file.write(self.markdown)
    
    def write_images(self, output_directory: Path):
        if not self.images:
            return
        
        for image in self.images:
            if image and image.image_base64:
                image_name = image.id
                image_path = output_directory / image_name
                b64decode_document(image.image_base64, image_path)

class DeepseekOCRDocument:
    def __init__(self, 
                 document_path: Path, 
                 include_images=True,
                 output_directory: Path = None,
                 generate_pages=True,
                 full_directory_name="full",
                 page_separator="\n",
                 page_directory_name="page_<index>",
                 page_text_name="<stem>.md",
                 json_ocr_response_path=None,
                 save_json=True,
                 dpi: int = 600,
                 model_name: str = "deepseek-ocr",
                 raw_prompt: str = None,
                 hint: str = None,
                 verbosity_level: int = 1
                ):
        self.document_path = document_path
        self.include_images = include_images
        self.generate_pages = generate_pages
        self.save_json = save_json
        self.full_directory_name = full_directory_name
        self.page_separator = page_separator
        self.page_directory_name = page_directory_name
        self.page_text_name = page_text_name
        self.json_ocr_response_path = json_ocr_response_path
        self.dpi = dpi
        self.model_name = model_name
        self.raw_prompt = raw_prompt
        self.hint = hint
        self.verbosity_level = verbosity_level
        if output_directory is None:
            self.output_directory = self.get_input_path().parent / self.get_input_path().stem
        else:
            self.output_directory = output_directory

    def get_ocr_response(self, document_path):
        client = OllamaOCRClient(
            model_name=self.model_name,
            dpi=self.dpi,
            include_image_base64=self.include_images,
            raw_prompt=self.raw_prompt,
            hint=self.hint
            )
        self.ocr_response = client.ocr_process(
            document_path=document_path
        )

    def process_document(self):
        if not self.document_path.exists():
            raise FileNotFoundError(f"The document {self.document_path} does not exist.")
        if not self.document_path.is_file():
            raise ValueError(f"The path {self.document_path} is not a valid file.")
        
        mimetype, _ = mimetypes.guess_type(self.document_path)
        if mimetype is None:
            raise ValueError(f"Could not determine the MIME type for {self.document_path}.")
        if not mimetype.startswith("image/") and not mimetype.startswith("application/pdf"):
            raise ValueError(f"Unsupported MIME type: {mimetype}. Only image and PDF files are supported.")

        self.get_ocr_response(self.document_path)
        self.write_json()
        self.process_ocr_response()

    def process_json_response(self):
        if self.json_ocr_response_path is None or not self.json_ocr_response_path.exists():
            raise FileNotFoundError(f"The JSON OCR response {self.json_ocr_response_path} does not exist.")
        
        with open(self.json_ocr_response_path, "r") as json_file:
            self.ocr_response = convert_to_object(json.load(json_file))
        self.write_json()
        self.process_ocr_response()

    def process(self):
        if self.json_ocr_response_path is not None:
            self.process_json_response()
        else:
            self.process_document()

    def get_input_path(self):
        if self.json_ocr_response_path is not None:
            return self.json_ocr_response_path
        return self.document_path
    
    def write_json(self):
        if self.save_json:
            output_path = (self.output_directory / self.get_input_path().stem).with_suffix(".json")
            self.output_directory.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w") as text_file:
                json.dump(object_to_dict(self.ocr_response), text_file, indent=2)

    def process_ocr_response(self):
        response_pages = self.ocr_response.pages
        if not response_pages:
            print("No pages found in the OCR response.")
            return
        
        pages = []

        full_dir = self.output_directory / self.full_directory_name

        for r_page in response_pages:
            page = Page(
                index=r_page.index,
                markdown=r_page.markdown,
                images=r_page.images
            )
            if self.generate_pages:
                page_dir = self.output_directory / self.page_directory_name.replace("<index>", str(page.index))
                page.write_markdown((
                    page_dir / self.page_text_name.
                    replace("<stem>", self.get_input_path().stem).
                    replace("<index>", str(page.index))
                    ).with_suffix(".md"))
                if self.include_images:
                    page.write_images(page_dir)
            if self.include_images:
                page.write_images(full_dir)
            pages.append(page)
        for i, page in enumerate(sorted(pages, key=lambda p: p.index)):
            first = i == 0
            md_file = (full_dir / self.get_input_path().stem).with_suffix(".md")
            insert = self.page_separator if not first else None
            page.write_markdown(md_file, append=not first, insert=insert)

def construct_from_mode(
    document_path: Path,
    dpi: int = 600,
    output_directory: Path = None,
    json_ocr_response_path: Path = None,
    page_separator: str = "\n",
    write_json: bool = True,
    mode: Modes = Modes.FULL,
    model_name: str = "deepseek-ocr",
    raw_prompt: str = None,
    hint: str = None,
    verbosity_level: int = 1
):
    try:
        found = False
        for model in ollama.list().get("models", []):
            if model.model == model_name or model.model.split(":")[0] == model_name:
                found = True
                break
        if not found:
            if verbosity_level > 0:
                print(f"Warning: Model '{model_name}' not found in Ollama models.", file=sys.stderr)
    except Exception as e:
        print(f"Connection error while communicating with Ollama: {e}", file=sys.stderr)
        sys.exit(1)
    kwargs = dict(
        document_path=document_path,
        dpi=dpi,
        output_directory=output_directory,
        json_ocr_response_path=json_ocr_response_path,
        page_separator=page_separator,
        save_json=write_json,
        model_name=model_name,
        raw_prompt=raw_prompt,
        hint=hint,
        verbosity_level=verbosity_level
    )
    match mode:
        case Modes.FULL:
            kwargs.update(
                include_images=True,
                generate_pages=True
            )
        case Modes.FULL_ALT:
            kwargs.update(
                include_images=True,
                generate_pages=True,
                full_directory_name="."
            )
        case Modes.FULL_NO_DIR:
            kwargs.update(
                include_images=True,
                generate_pages=True,
                full_directory_name=".",
                page_directory_name=".",
                page_text_name="<stem><index>.md"
            )
        case Modes.FULL_NO_PAGES:
            kwargs.update(
                include_images=True,
                generate_pages=False,
                full_directory_name="."
            )
        case Modes.TEXT:
            kwargs.update(
                include_images=False,
                generate_pages=True,
                full_directory_name=".",
                page_directory_name=".",
                page_text_name="<stem><index>.md"
            )
        case Modes.TEXT_NO_PAGES:
            kwargs.update(
                include_images=False,
                generate_pages=False,
                full_directory_name="."
            )
        case _:
            raise ValueError(f"Unknown mode: {mode}")
    return DeepseekOCRDocument(**kwargs)
