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

with open("face-to-sticker-api.json", "r") as file:
    workflow_json = file.read()


class Predictor(BasePredictor):
    def setup(self):
        self.comfyUI = ComfyUI("127.0.0.1:8188")
        self.comfyUI.start_server(OUTPUT_DIR, INPUT_DIR)
        self.comfyUI.load_workflow(
            workflow_json, check_inputs=False
        )

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
        loader = workflow["2"]["inputs"]
        sampler = workflow["4"]["inputs"]
        load_image = workflow["22"]["inputs"]
        upscaler = workflow["11"]["inputs"]
        instant_id = workflow["41"]["inputs"]
        ip_adapter = workflow["43"]["inputs"]

        load_image["image"] = kwargs["filename"]

        loader["cfg"] = kwargs["prompt_strength"]
        loader[
            "positive"
        ] = f"Sticker, {kwargs['prompt']}, cel shaded, svg, vector art, sharp"
        loader[
            "negative"
        ] = f"photo, photography, nsfw, nude, ugly, broken, watermark, oversaturated, soft {kwargs['negative_prompt']}"
        loader["empty_latent_width"] = kwargs["width"]
        loader["empty_latent_height"] = kwargs["height"]

        instant_id["weight"] = kwargs["instant_id_strength"]

        ip_adapter["weight"] = kwargs["ip_adapter_weight"]
        ip_adapter["noise"] = kwargs["ip_adapter_noise"]

        sampler["steps"] = kwargs["steps"]
        sampler["seed"] = kwargs["seed"]

        if kwargs["upscale"]:
            del workflow["5"]
            del workflow["9"]
            del workflow["10"]
            upscaler["steps"] = kwargs["upscale_steps"]
            upscaler["seed"] = kwargs["seed"]
        else:
            for node_id in range(11, 19):
                workflow.pop(str(node_id), None)

    def predict(
        self,
        image: Path = Input(
            description="An image of a person to be converted to a sticker",
            default=None,
        ),
        prompt: str = Input(default="a person"),
        negative_prompt: str = Input(
            default="",
            description="Things you do not want in the image",
        ),
        width: int = Input(default=1024),
        height: int = Input(default=1024),
        steps: int = Input(default=20),
        seed: int = Input(
            default=None, description="Fix the random seed for reproducibility"
        ),
        prompt_strength: float = Input(
            default=7,
            description="Strength of the prompt. This is the CFG scale, higher numbers lead to stronger prompt, lower numbers will keep more of a likeness to the original.",
        ),
        instant_id_strength: float = Input(
            default=1, description="How strong the InstantID will be.", ge=0, le=1
        ),
        ip_adapter_weight: float = Input(
            default=0.2,
            description="How much the IP adapter will influence the image",
            ge=0,
            le=1,
        ),
        ip_adapter_noise: float = Input(
            default=0.5,
            description="How much noise is added to the IP adapter input",
            ge=0,
            le=1,
        ),
        upscale: bool = Input(default=False, description="2x upscale the sticker"),
        upscale_steps: int = Input(
            default=10, description="Number of steps to upscale"
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
            seed=seed,
            prompt=prompt,
            negative_prompt=negative_prompt,
            width=width,
            height=height,
            steps=steps,
            upscale=upscale,
            upscale_steps=upscale_steps,
            prompt_strength=prompt_strength,
            instant_id_strength=instant_id_strength,
            ip_adapter_weight=ip_adapter_weight,
            ip_adapter_noise=ip_adapter_noise,
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
