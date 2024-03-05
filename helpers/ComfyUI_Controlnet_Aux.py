MODELS = {
    "UNet.pth": "bdsqlsz/qinglong_controlnet-lllite/Annotators",
    "mobile_sam.pt": "dhkim2810/MobileSAM",
    "hrnetv2_w64_imagenet_pretrained.pth": "hr16/ControlNet-HandRefiner-pruned",
    "graphormer_hand_state_dict.bin": "hr16/ControlNet-HandRefiner-pruned",
    "rtmpose-m_ap10k_256_bs5.torchscript.pt": "hr16/DWPose-TorchScript-BatchSize5",
    "dw-ll_ucoco_384_bs5.torchscript.pt": "hr16/DWPose-TorchScript-BatchSize5",
    "rtmpose-m_ap10k_256.onnx": "hr16/UnJIT-DWPose",
    "yolo_nas_s_fp16.onnx": "hr16/yolo-nas-fp16",
    "yolo_nas_m_fp16.onnx": "hr16/yolo-nas-fp16",
    "yolox_l.torchscript.pt": "hr16/yolox-onnx",
    "densepose_r101_fpn_dl.torchscript": "LayerNorm/DensePose-TorchScript-with-hint-image",
    "densepose_r50_fpn_dl.torchscript": "LayerNorm/DensePose-TorchScript-with-hint-image",
    "mlsd_large_512_fp32.pth": "lllyasviel/Annotators",
    "150_16_swin_l_oneformer_coco_100ep.pth": "lllyasviel/Annotators",
    "ControlNetHED.pth": "lllyasviel/Annotators",
    "ZoeD_M12_N.pt": "lllyasviel/Annotators",
    "scannet.pt": "lllyasviel/Annotators",
    "hand_pose_model.pth": "lllyasviel/Annotators",
    "upernet_global_small.pth": "lllyasviel/Annotators",
    "latest_net_G.pth": "lllyasviel/Annotators",
    "netG.pth": "lllyasviel/Annotators",
    "sk_model2.pth": "lllyasviel/Annotators",
    "dpt_hybrid-midas-501f0c75.pt": "lllyasviel/Annotators",
    "table5_pidinet.pth": "lllyasviel/Annotators",
    "erika.pth": "lllyasviel/Annotators",
    "250_16_swin_l_oneformer_ade20k_160k.pth": "lllyasviel/Annotators",
    "sk_model.pth": "lllyasviel/Annotators",
    "body_pose_model.pth": "lllyasviel/Annotators",
    "res101.pth": "lllyasviel/Annotators",
    "facenet.pth": "lllyasviel/Annotators",
    "isnetis.ckpt": "skytnt/anime-seg",
    "yolox_l.onnx": "yzd-v/DWPose",
    "dw-ll_ucoco_384.onnx": "yzd-v/DWPose",
}


class ComfyUI_Controlnet_Aux:
    @staticmethod
    def models():
        return MODELS

    @staticmethod
    def weights_map(base_url):
        return {
            key: {
                "url": f"{base_url}/custom_nodes/comfyui_controlnet_aux/{key}.tar",
                "dest": f"ComfyUI/custom_nodes/comfyui_controlnet_aux/ckpts/{MODELS[key]}",
            }
            for key in MODELS
        }

    # Controlnet preprocessor models are not included in the API JSON
    # We need to add them manually based on the nodes being used to
    # avoid them being downloaded automatically from elsewhere
    @staticmethod
    def node_class_mapping():
        return {
            # Depth
            "MiDaS-NormalMapPreprocessor": "dpt_hybrid-midas-501f0c75.pt",
            "MiDaS-DepthMapPreprocessor": "dpt_hybrid-midas-501f0c75.pt",
            "Zoe-DepthMapPreprocessor": "ZoeD_M12_N.pt",
            "LeReS-DepthMapPreprocessor": ["res101.pth", "latest_net_G.pth"],
            "MeshGraphormer-DepthMapPreprocessor": [
                "hrnetv2_w64_imagenet_pretrained.pth",
                "graphormer_hand_state_dict.bin",
            ],
            # Segmentation
            "BAE-NormalMapPreprocessor": "scannet.pt",
            "OneFormer-COCO-SemSegPreprocessor": "150_16_swin_l_oneformer_coco_100ep.pth",
            "OneFormer-ADE20K-SemSegPreprocessor": "250_16_swin_l_oneformer_ade20k_160k.pth",
            "UniFormer-SemSegPreprocessor": "upernet_global_small.pth",
            "SemSegPreprocessor": "upernet_global_small.pth",
            "AnimeFace_SemSegPreprocessor": ["UNet.pth", "isnetis.ckpt"],
            "SAMPreprocessor": "mobile_sam.pt",
            # Line extractors
            "AnimeLineArtPreprocessor": "netG.pth",
            "HEDPreprocessor": "ControlNetHED.pth",
            "FakeScribblePreprocessor": "ControlNetHED.pth",
            "M-LSDPreprocessor": "mlsd_large_512_fp32.pth",
            "PiDiNetPreprocessor": "table5_pidinet.pth",
            "LineArtPreprocessor": ["sk_model.pth", "sk_model2.pth"],
            "Manga2Anime_LineArt_Preprocessor": "erika.pth",
            # Pose
            "OpenposePreprocessor": [
                "body_pose_model.pth",
                "hand_pose_model.pth",
                "facenet.pth",
            ],
        }

    @staticmethod
    def add_weights(weights_to_download, node):
        node_class = node.get("class_type")
        node_mapping = ComfyUI_Controlnet_Aux.node_class_mapping()

        if node_class and node_class in node_mapping:
            class_weights = node_mapping[node_class]
            if isinstance(class_weights, list):
                weights_to_download.extend(class_weights)
            else:
                weights_to_download.append(class_weights)

        # Additional check for AIO_Preprocessor and its preprocessor input value
        if node_class == "AIO_Preprocessor" and "preprocessor" in node.get("inputs", {}):
            preprocessor = node["inputs"]["preprocessor"]
            if preprocessor in node_mapping:
                preprocessor_weights = node_mapping[preprocessor]
                if isinstance(preprocessor_weights, list):
                    weights_to_download.extend(preprocessor_weights)
                else:
                    weights_to_download.append(preprocessor_weights)
