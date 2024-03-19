import os
import urllib.request
import subprocess
import threading
import time
import json
import urllib
import uuid
import json
import os
import websocket
import random
from weights_downloader import WeightsDownloader
from urllib.error import URLError


# custom_nodes helpers
from helpers.ComfyUI_IPAdapter_plus import ComfyUI_IPAdapter_plus
from helpers.ComfyUI_Controlnet_Aux import ComfyUI_Controlnet_Aux
from helpers.ComfyUI_InstantID import ComfyUI_InstantID
from helpers.ComfyUI_BRIA_AI_RMBG import ComfyUI_BRIA_AI_RMBG


class ComfyUI:
    def __init__(self, server_address):
        self.weights_downloader = WeightsDownloader()
        self.server_address = server_address
        ComfyUI_IPAdapter_plus.prepare()

    def start_server(self, output_directory, input_directory):
        self.input_directory = input_directory
        self.output_directory = output_directory

        self.download_pre_start_models()

        server_thread = threading.Thread(
            target=self.run_server, args=(output_directory, input_directory)
        )
        server_thread.start()

        start_time = time.time()
        while not self.is_server_running():
            if time.time() - start_time > 60:  # If more than a minute has passed
                raise TimeoutError("Server did not start within 60 seconds")
            time.sleep(1)  # Wait for 1 second before checking again

        print("Server running")

    def run_server(self, output_directory, input_directory):
        command = f"python ./ComfyUI/main.py --output-directory {output_directory} --input-directory {input_directory} --disable-metadata --preview-method none --gpu-only"
        server_process = subprocess.Popen(command, shell=True)
        server_process.wait()

    def is_server_running(self):
        try:
            with urllib.request.urlopen(
                "http://{}/history/{}".format(self.server_address, "123")
            ) as response:
                return response.status == 200
        except URLError:
            return False

    def download_pre_start_models(self):
        # Some models need to be downloaded and loaded before starting ComfyUI
        self.weights_downloader.download_torch_checkpoints()

    def handle_weights(self, workflow):
        print("Checking weights")
        weights_to_download = []
        weights_filetypes = [
            ".ckpt",
            ".safetensors",
            ".pt",
            ".pth",
            ".bin",
            ".onnx",
            ".torchscript",
        ]

        for node in workflow.values():
            for handler in [
                ComfyUI_Controlnet_Aux,
                ComfyUI_IPAdapter_plus,
                ComfyUI_InstantID,
                ComfyUI_BRIA_AI_RMBG,
            ]:
                handler.add_weights(weights_to_download, node)

            if "inputs" in node:
                for input in node["inputs"].values():
                    if isinstance(input, str):
                        if any(input.endswith(ft) for ft in weights_filetypes):
                            weights_to_download.append(input)

        weights_to_download = list(set(weights_to_download))

        for weight in weights_to_download:
            self.weights_downloader.download_weights(weight)
            print(f"✅ {weight}")

        print("====================================")

    def is_image_or_video_value(self, value):
        filetypes = [".png", ".jpg", ".jpeg", ".webp", ".mp4", ".webm"]
        return isinstance(value, str) and any(
            value.lower().endswith(ft) for ft in filetypes
        )

    def handle_inputs(self, workflow):
        print("Checking inputs")
        seen_inputs = set()
        for node in workflow.values():
            if "inputs" in node:
                for input_key, input_value in node["inputs"].items():
                    if isinstance(input_value, str) and input_value not in seen_inputs:
                        seen_inputs.add(input_value)
                        if input_value.startswith(("http://", "https://")):
                            filename = os.path.join(
                                self.input_directory, os.path.basename(input_value)
                            )
                            if not os.path.exists(filename):
                                print(f"Downloading {input_value} to {filename}")
                                urllib.request.urlretrieve(input_value, filename)
                            node["inputs"][input_key] = filename
                            print(f"✅ {filename}")
                        elif self.is_image_or_video_value(input_value):
                            filename = os.path.join(
                                self.input_directory, os.path.basename(input_value)
                            )
                            if not os.path.exists(filename):
                                print(f"❌ {filename} not provided")
                            else:
                                print(f"✅ {filename}")

        print("====================================")

    def connect(self):
        self.client_id = str(uuid.uuid4())
        self.ws = websocket.WebSocket()
        self.ws.connect(f"ws://{self.server_address}/ws?clientId={self.client_id}")

    def post_request(self, endpoint, data=None):
        url = f"http://{self.server_address}{endpoint}"
        headers = {"Content-Type": "application/json"} if data else {}
        json_data = json.dumps(data).encode("utf-8") if data else None
        req = urllib.request.Request(
            url, data=json_data, headers=headers, method="POST"
        )
        with urllib.request.urlopen(req) as response:
            if response.status != 200:
                print(f"Failed: {endpoint}, status code: {response.status}")

    # https://github.com/comfyanonymous/ComfyUI/blob/master/server.py
    def clear_queue(self):
        self.post_request("/queue", {"clear": True})
        self.post_request("/interrupt")

    def queue_prompt(self, prompt):
        try:
            # Prompt is the loaded workflow (prompt is the label comfyUI uses)
            p = {"prompt": prompt, "client_id": self.client_id}
            data = json.dumps(p).encode("utf-8")
            req = urllib.request.Request(
                f"http://{self.server_address}/prompt?{self.client_id}", data=data
            )

            output = json.loads(urllib.request.urlopen(req).read())
            return output["prompt_id"]
        except urllib.error.HTTPError as e:
            print(f"ComfyUI error: {e.code} {e.reason}")
            http_error = True

        if http_error:
            raise Exception(
                "ComfyUI Error – Your workflow could not be run. This usually happens if you’re trying to use an unsupported node. Check the logs for 'KeyError: ' details, and go to https://github.com/fofr/cog-comfyui to see the list of supported custom nodes."
            )

    def wait_for_prompt_completion(self, workflow, prompt_id):
        while True:
            out = self.ws.recv()
            if isinstance(out, str):
                message = json.loads(out)
                if message["type"] == "executing":
                    data = message["data"]
                    if data["node"] is None and data["prompt_id"] == prompt_id:
                        break
                    elif data["prompt_id"] == prompt_id:
                        node = workflow.get(data["node"], {})
                        meta = node.get("_meta", {})
                        class_type = node.get("class_type", "Unknown")
                        print(
                            f"Executing node {data['node']}, title: {meta.get('title', 'Unknown')}, class type: {class_type}"
                        )
            else:
                continue

    def load_workflow(self, workflow, check_inputs=True, check_weights=True):
        if not isinstance(workflow, dict):
            wf = json.loads(workflow)
        else:
            wf = workflow

        # There are two types of ComfyUI JSON
        # We need the API version
        if any(key in wf.keys() for key in ["last_node_id", "last_link_id", "version"]):
            raise ValueError(
                "You need to use the API JSON version of a ComfyUI workflow. To do this go to your ComfyUI settings and turn on 'Enable Dev mode Options'. Then you can save your ComfyUI workflow via the 'Save (API Format)' button."
            )

        if check_inputs:
            self.handle_inputs(wf)

        if check_weights:
            self.handle_weights(wf)

        return wf

    def randomise_input_seed(self, input_key, inputs):
        if input_key in inputs and isinstance(inputs[input_key], (int, float)):
            new_seed = random.randint(0, 2**32 - 1)
            print(f"Randomising {input_key} to {new_seed}")
            inputs[input_key] = new_seed

    def randomise_seeds(self, workflow):
        for node_id, node in workflow.items():
            inputs = node.get("inputs", {})
            seed_keys = ["seed", "noise_seed", "rand_seed"]
            for seed_key in seed_keys:
                self.randomise_input_seed(seed_key, inputs)

    def run_workflow(self, workflow):
        print("Running workflow")
        prompt_id = self.queue_prompt(workflow)
        self.wait_for_prompt_completion(workflow, prompt_id)
        output_json = self.get_history(prompt_id)
        print("outputs: ", output_json)
        print("====================================")

    def get_history(self, prompt_id):
        with urllib.request.urlopen(
            f"http://{self.server_address}/history/{prompt_id}"
        ) as response:
            output = json.loads(response.read())
            return output[prompt_id]["outputs"]
