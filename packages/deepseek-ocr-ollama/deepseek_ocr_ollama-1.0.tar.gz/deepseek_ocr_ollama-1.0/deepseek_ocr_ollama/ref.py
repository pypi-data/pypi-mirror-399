from PIL import ImageDraw, ImageFont
import re

class RefDet:
    def __init__(self, ref, det):
        self.ref = ref
        self.det = det
    
    def __repr__(self):
        return f"RefDet(ref={self.ref}, det={self.det})"
    
    def det_proportional_boxes(self, img_width = 1000, img_height = 1000, as_int=True, margin_width=0, margin_height=0):
        proportional_boxes = []
        for box in self.det:
            x1, y1, x2, y2 = box
            x1 = max(0, x1 - margin_width)
            y1 = max(0, y1 - margin_height)
            x2 = min(1000, x2 + margin_width)
            y2 = min(1000, y2 + margin_height)
            pw1 = x1 / 1000.0 * img_width
            ph1 = y1 / 1000.0 * img_height
            pw2 = x2 / 1000.0 * img_width
            ph2 = y2 / 1000.0 * img_height
            proportional_boxes.append([pw1, ph1, pw2, ph2])
        if as_int:
            proportional_boxes = [[int(coord + 0.5) for coord in box] for box in proportional_boxes]
        return proportional_boxes

    @staticmethod
    def ref_det(content):
        ref = re.search(r'<\|ref\|>(.*?)<\|/ref\|>', content, re.DOTALL)
        det = re.search(r'<\|det\|>(.*?)<\|/det\|>', content, re.DOTALL)
        if ref and det:
            return ref.group(1).strip(), det.group(1).strip()
        return None, None

    @staticmethod
    def dets_boxes(dets):
        boxes = re.findall(r'\[([^\[]*?)\]', dets)
        def dets_coords(box):
            coords = re.findall(r'(\d+)', box)
            return [int(coord) for coord in coords]
        return [dets_coords(box.strip()) for box in boxes]

    @staticmethod
    def elements_boxes(content, filter_ref=None, filter_ref_case_sensitive=False):
        elements = content.split('\n')
        ref_dets = []
        for el in elements:
            ref, dets = RefDet.ref_det(el)
            if not ref or not dets:
                ref_dets.append(el)
                continue
            rd = RefDet(ref, [det for det in RefDet.dets_boxes(dets)])
            if filter_ref:
                if filter_ref_case_sensitive:
                    if rd.ref == filter_ref:
                        ref_dets.append(rd)
                else:
                    if rd.ref.lower() == filter_ref.lower():
                        ref_dets.append(rd)
            else:
                ref_dets.append(rd)
        return ref_dets

class RefImage:
    def __init__(self, image):
        self.image = image
    
    def draw_boxes(self, elements_boxes, box_color=(255, 0, 0), border_width=2, verbose=False, font_size=16):
        image_copy = self.image.copy()
        draw = ImageDraw.Draw(image_copy)
        try:
            custom_font = ImageFont.truetype("arial.ttf", font_size) 
        except IOError:
            if verbose:
                print("Could not load custom font, using default font.")
            custom_font = ImageFont.load_default(font_size)
        for rd in elements_boxes:
            if not isinstance(rd, RefDet):
                continue
            for box in rd.det_proportional_boxes(image_copy.width, image_copy.height):
                x1, y1, x2, y2 = box
                draw.rectangle([x1, y1, x2, y2], outline=box_color, width=border_width)
                draw.text((x1 + font_size * 0.3, y1 + font_size * 0.2), rd.ref, fill=box_color, font=custom_font)
        return image_copy
    
    def get_cropped_elements(self, elements_boxes, margin_width=0, margin_height=0):
        cropped_images = []
        for rd in elements_boxes:
            if not isinstance(rd, RefDet):
                continue
            for box in rd.det_proportional_boxes(self.image.width, self.image.height, margin_width=margin_width, margin_height=margin_height):
                x1, y1, x2, y2 = box
                cropped_image = self.image.crop((x1, y1, x2, y2))
                cropped_images.append((rd.ref, cropped_image, box))
        return cropped_images

