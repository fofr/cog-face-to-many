class ComfyUI_InstantID:
    @staticmethod
    def add_weights(weights_to_download, node):
        if "class_type" in node:
            if node["class_type"] == "InstantIDFaceAnalysis":
                weights_to_download.append("antelopev2")
            elif node["class_type"] == "InstantIDModelLoader":
                if "inputs" in node and "instantid_file" in node["inputs"]:
                    if node["inputs"]["instantid_file"] == "ipadapter.bin":
                        node["inputs"]["instantid_file"] = "instantid-ip-adapter.bin"
                        weights_to_download.append("instantid-ip-adapter.bin")
            elif node["class_type"] == "ControlNetLoader":
                if "inputs" in node and "control_net_name" in node["inputs"]:
                    if (
                        node["inputs"]["control_net_name"]
                        == "instantid/diffusion_pytorch_model.safetensors"
                    ):
                        node["inputs"][
                            "control_net_name"
                        ] = "instantid-controlnet.safetensors"
                        weights_to_download.append("instantid-controlnet.safetensors")
