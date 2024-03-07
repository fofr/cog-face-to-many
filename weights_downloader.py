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
            print(f"⌛️ Completed in {elapsed_time:.2f}s")


    def download_custom_lora(self, uuid, url, dest):
        if not os.path.exists(f"{dest}/{uuid}"):
            if "/" in uuid:
                subfolder = uuid.rsplit("/", 1)[0]
                dest = os.path.join(dest, subfolder)
                os.makedirs(dest, exist_ok=True)

            print(f"⏳ Downloading {uuid} to {dest}")
            start = time.time()
            subprocess.check_call(
                ["pget", "--log-level", "warn", "-f", url, dest], close_fds=False
            )
            elapsed_time = time.time() - start
            downloaded_file_path = os.path.join(dest, os.path.basename(uuid))

            if downloaded_file_path.endswith('.tar'):
                downloaded_file_path = self.handle_replicate_tar(uuid, downloaded_file_path, dest)

            try:
                file_size_bytes = os.path.getsize(downloaded_file_path)
                file_size_megabytes = file_size_bytes / (1024 * 1024)
                print(
                    f"⌛️ Completed in {elapsed_time:.2f}s, size: {file_size_megabytes:.2f}MB"
                )
            except FileNotFoundError:
                print(f"⌛️ Completed in {elapsed_time:.2f}s")

    def handle_replicate_tar(self, uuid, downloaded_file_path, dest):
        if downloaded_file_path.endswith('.tar'):
            print(f"🔍 Extracting lora.safetensors from {downloaded_file_path}")
            try:
                subprocess.check_call(
                    ["tar", "-xf", downloaded_file_path, "lora.safetensors", "-C", dest],
                    close_fds=False
                )
                extracted_lora_path = os.path.join(dest, 'lora.safetensors')
                new_file_path = os.path.join(dest, f'{uuid}.safetensors')
                os.rename(extracted_lora_path, new_file_path)
                print(f"✅ {uuid}.safetensors has been extracted and saved to {new_file_path}")

                os.remove(downloaded_file_path)
                print(f"🗑️ Removed {downloaded_file_path}")
                return new_file_path

            except subprocess.CalledProcessError:
                os.remove(downloaded_file_path)
                print(f"🗑️ Removed {downloaded_file_path}")
                raise RuntimeError("Failed to extract lora.safetensors from the tar archive.")