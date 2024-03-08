import subprocess
import time
import os

from weights_manifest import WeightsManifest

BASE_URL = "https://weights.replicate.delivery/default/comfy-ui"
BASE_PATH = "ComfyUI/models"


class WeightsDownloader:
    def __init__(self):
        self.weights_manifest = WeightsManifest()
        self.weights_map = self.weights_manifest.weights_map

    def download_weights(self, weight_str):
        if weight_str in self.weights_map:
            if self.weights_manifest.is_non_commercial_only(weight_str):
                print(
                    f"⚠️  {weight_str} is for non-commercial use only. Unless you have obtained a commercial license.\nDetails: https://github.com/fofr/cog-comfyui/blob/main/weights_licenses.md"
                )
            self.download_if_not_exists(
                weight_str,
                self.weights_map[weight_str]["url"],
                self.weights_map[weight_str]["dest"],
            )
        else:
            raise ValueError(
                f"{weight_str} unavailable. View the list of available weights: https://github.com/fofr/cog-comfyui/blob/main/supported_weights.md"
            )

    def download_lora_from_replicate_url(self, uuid, url):
        dest = f"{BASE_PATH}/loras"
        self.download_custom_lora(uuid, url, dest)

    def download_torch_checkpoints(self):
        self.download_if_not_exists(
            "mobilenet_v2-b0353104.pth",
            f"{BASE_URL}/custom_nodes/comfyui_controlnet_aux/mobilenet_v2-b0353104.pth.tar",
            "/root/.cache/torch/hub/checkpoints/",
        )

    def download_if_not_exists(self, weight_str, url, dest):
        if not os.path.exists(f"{dest}/{weight_str}"):
            self.download(weight_str, url, dest)

    def download(self, weight_str, url, dest):
        if "/" in weight_str:
            subfolder = weight_str.rsplit("/", 1)[0]
            dest = os.path.join(dest, subfolder)
            os.makedirs(dest, exist_ok=True)

        print(f"⏳ Downloading {weight_str} to {dest}")
        start = time.time()
        subprocess.check_call(
            ["pget", "--log-level", "warn", "-xf", url, dest], close_fds=False
        )
        elapsed_time = time.time() - start
        downloaded_file_path = os.path.join(dest, os.path.basename(weight_str))

        try:
            file_size_bytes = os.path.getsize(downloaded_file_path)
            file_size_megabytes = file_size_bytes / (1024 * 1024)
            print(
                f"⌛️ Completed in {elapsed_time:.2f}s, size: {file_size_megabytes:.2f}MB"
            )
        except FileNotFoundError:
            print(f"⌛️ Completed in {elapsed_time:.2f}s but file not found.")

    def download_custom_lora(self, uuid, url, dest):
        if not os.path.exists(f"{dest}/{uuid}"):
            dest_with_uuid = os.path.join(dest, uuid)
            os.makedirs(dest_with_uuid, exist_ok=True)

            print(f"⏳ Downloading {uuid} to {dest_with_uuid}")
            start = time.time()
            subprocess.check_call(
                ["pget", "--log-level", "warn", "-xf", url, dest_with_uuid],
                close_fds=False,
            )
            elapsed_time = time.time() - start

            self.handle_replicate_tar(uuid, dest_with_uuid)

            preserved_file_path = os.path.join(dest_with_uuid, f"{uuid}.safetensors")
            try:
                file_size_bytes = os.path.getsize(preserved_file_path)
                file_size_megabytes = file_size_bytes / (1024 * 1024)
                print(
                    f"⌛️ Completed in {elapsed_time:.2f}s, size: {file_size_megabytes:.2f}MB"
                )
            except FileNotFoundError:
                print(f"⌛️ Completed in {elapsed_time:.2f}s but file not found.")
        else:
            print(f"✅ {uuid} lora folder already exists.")

    def handle_replicate_tar(self, uuid, dest_with_uuid):
        extracted_lora_path = os.path.join(dest_with_uuid, "lora.safetensors")
        new_file_path = os.path.join(dest_with_uuid, f"{uuid}.safetensors")

        if os.path.exists(extracted_lora_path):
            os.rename(extracted_lora_path, new_file_path)
            print(
                f"✅ {uuid}.safetensors has been extracted and saved to {new_file_path}"
            )
        else:
            raise FileNotFoundError(f"lora.safetensors not found in {dest_with_uuid}.")

        # Delete other files (embeddings.pti and special_params.json) if they exist
        for file_name in ["embeddings.pti", "special_params.json"]:
            file_path = os.path.join(dest_with_uuid, file_name)
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"🗑️ Removed {file_path}")
