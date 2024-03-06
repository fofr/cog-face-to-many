import os
import shutil
import random
import json
from typing import List
from cog import BasePredictor, Input, Path
from helpers.comfyui import ComfyUI

OUTPUT_DIR = "/tmp/outputs"
INPUT_DIR = "/tmp/inputs"
COMFYUI_TEMP_OUTPUT_DIR = "ComfyUI/temp"

with open("face-to-many-api.json", "r") as file:
    workflow_json = file.read()


LORA_WEIGHTS_MAPPING = {
    "3D": "artificialguybr/3DRedmond-3DRenderStyle-3DRenderAF.safetensors",
    "Emoji": "fofr/emoji.safetensors",
    "Video game": "artificialguybr/PS1Redmond-PS1Game-Playstation1Graphics.safetensors",
    "Pixels": "artificialguybr/PixelArtRedmond-Lite64.safetensors",
    "Clay": "artificialguybr/ClayAnimationRedm.safetensors",
    "Toy": "artificialguybr/ToyRedmond-FnkRedmAF.safetensors",
}

LORA_TYPES = list(LORA_WEIGHTS_MAPPING.keys())

class Predictor(BasePredictor):
    def setup(self):
        self.comfyUI = ComfyUI("127.0.0.1:8188")
        self.comfyUI.start_server(OUTPUT_DIR, INPUT_DIR)
        self.comfyUI.load_workflow(workflow_json, check_inputs=False)
        self.download_loras()

    def download_loras(self):
        for weight in LORA_WEIGHTS_MAPPING.values():
            self.comfyUI.weights_downloader.download_weights(weight)

    def cleanup(self):
        self.comfyUI.clear_queue()
        for directory in [OUTPUT_DIR, INPUT_DIR, COMFYUI_TEMP_OUTPUT_DIR]:
            if os.path.exists(directory):
                shutil.rmtree(directory)
            os.makedirs(directory)

    def handle_input_file(self, input_file: Path):
        file_extension = os.path.splitext(input_file)[1].lower()
        if file_extension in [".jpg", ".jpeg", ".png", ".webp"]:
            filename = f"input{file_extension}"
            shutil.copy(input_file, os.path.join(INPUT_DIR, filename))
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")

        return filename

    def log_and_collect_files(self, directory, prefix=""):
        files = []
        for f in os.listdir(directory):
            if f == "__MACOSX":
                continue
            path = os.path.join(directory, f)
            if os.path.isfile(path):
                print(f"{prefix}{f}")
                files.append(Path(path))
            elif os.path.isdir(path):
                print(f"{prefix}{f}/")
                files.extend(self.log_and_collect_files(path, prefix=f"{prefix}{f}/"))
        return files

    def update_workflow(self, workflow, **kwargs):
        style = kwargs["style"]
        prompt = kwargs["prompt"]
        negative_prompt = kwargs["negative_prompt"]

        load_image = workflow["22"]["inputs"]
        load_image["image"] = kwargs["filename"]

        loader = workflow["2"]["inputs"]
        loader["cfg"] = kwargs["prompt_strength"]
        loader["positive"] = self.style_to_prompt(style, prompt)
        loader["negative"] = self.style_to_negative_prompt(style, negative_prompt)

        lora_loader = workflow["3"]["inputs"]
        lora_loader["lora_name_1"] = LORA_WEIGHTS_MAPPING[style]

        instant_id = workflow["41"]["inputs"]
        instant_id["weight"] = kwargs["instant_id_strength"]

        sampler = workflow["4"]["inputs"]
        sampler["denoise"] = kwargs["denoising_strength"]
        sampler["seed"] = kwargs["seed"]

    def style_to_prompt(self, style, prompt):
        style_prompts = {
            "3D": f"3D Render Style, 3DRenderAF, {prompt}",
            "Emoji": f"memoji, emoji, {prompt}, 3d render, sharp",
            "Video game": f"Playstation 1 Graphics, PS1 Game, {prompt}, Video game screenshot",
            "Pixels": f"Pixel Art, PixArFK, {prompt}",
            "Clay": f"Clay Animation, Clay, {prompt}",
            "Toy": f"FnkRedmAF, {prompt}, toy, miniature",
        }
        return style_prompts[style]

    def style_to_negative_prompt(self, style, negative_prompt=""):
        if negative_prompt:
            negative_prompt = f"{negative_prompt}, "

        start_base_negative = "nsfw, nude, oversaturated, "
        end_base_negative = "ugly, broken, watermark"
        specifics = {
            "3D": "photo, photography, ",
            "Emoji": "photo, photography, blurry, soft, ",
            "Video game": "text, photo, ",
            "Pixels": "photo, photography, ",
            "Clay": "",
            "Toy": "",
        }

        return f"{specifics[style]}{start_base_negative}{negative_prompt}{end_base_negative}"

    def predict(
        self,
        image: Path = Input(
            description="An image of a person to be converted",
            default=None,
        ),
        style: str = Input(
            default="3D",
            choices=LORA_TYPES,
            description="Style to convert to",
        ),
        prompt: str = Input(default="a person"),
        negative_prompt: str = Input(
            default="",
            description="Things you do not want in the image",
        ),
        denoising_strength: float = Input(
            default=0.65,
            ge=0,
            le=1,
            description="How much of the original image to keep. 1 is the complete destruction of the original image, 0 is the original image",
        ),
        prompt_strength: float = Input(
            default=7,
            ge=0,
            le=20,
            description="Strength of the prompt. This is the CFG scale, higher numbers lead to stronger prompt, lower numbers will keep more of a likeness to the original.",
        ),
        instant_id_strength: float = Input(
            default=1, description="How strong the InstantID will be.", ge=0, le=1
        ),
        seed: int = Input(
            default=None, description="Fix the random seed for reproducibility"
        ),
    ) -> List[Path]:
        """Run a single prediction on the model"""
        self.cleanup()

        if image is None:
            raise ValueError("No image provided")

        filename = self.handle_input_file(image)

        if seed is None:
            seed = random.randint(0, 2**32 - 1)
            print(f"Random seed set to: {seed}")

        workflow = json.loads(workflow_json)
        self.update_workflow(
            workflow,
            filename=filename,
            style=style,
            denoising_strength=denoising_strength,
            seed=seed,
            prompt=prompt,
            negative_prompt=negative_prompt,
            prompt_strength=prompt_strength,
            instant_id_strength=instant_id_strength,
        )

        wf = self.comfyUI.load_workflow(workflow, check_weights=False)
        self.comfyUI.connect()
        self.comfyUI.run_workflow(wf)

        files = []
        output_directories = [OUTPUT_DIR]

        for directory in output_directories:
            print(f"Contents of {directory}:")
            files.extend(self.log_and_collect_files(directory))

        return files
