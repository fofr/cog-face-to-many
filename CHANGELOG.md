## 2024-02-26

- Fix: Always cancel and clear the ComfyUI server queue after a prediction
- Add support for ComfyUI_Comfyroll_CustomNodes
- Correctly download embeddings nested within prompt strings

## 2024-02-22

- Add safetensor SDXL lightning checkpoints, UNETs and Loras

## 2024-02-21

- Add SDXL lightning UNETs and Lora weights

Models added:

- sdxl_lightning_2step_lora.pth
- sdxl_lightning_4step_lora.pth
- sdxl_lightning_8step_lora.pth
- sdxl_lightning_1step_unet_x0.pth
- sdxl_lightning_2step_unet.pth
- sdxl_lightning_4step_unet.pth
- sdxl_lightning_8step_unet.pth
- epicrealismXL_v10.safetensors
- RealVisXL_V4.0.safetensors

## 2024-02-20

- Add support for [WAS nodes](https://github.com/fofr/cog-comfyui/pull/25)
- Add support for [comfyui-segment-anything](https://github.com/storyicon/comfyui_segment_anything)

Models added:

- mobile_sam.pt
- sam_hq_vit_b.pth
- sam_hq_vit_h.pth
- sam_hq_vit_l.pth
- groundingdino_swinb_cogcoor.pth
- groundingdino_swint_ogc.pth
- absolutereality_v181.safetensors
- [PerfectEyesXL Lora](https://civitai.com/models/118427/perfect-eyes-xl)
- [More details Lora](https://civitai.com/models/82098/add-more-details-detail-enhancer-tweaker-lora)
- [FastNegative embedding](https://civitai.com/models/71961/fast-negative-embedding-fastnegativev2)

## 2024-02-17

- Add support for [ComfyUI-Impact-Pack](https://github.com/fofr/cog-comfyui/pull/22)
- Add ViT-H, ViT-L and ViT-B [segment anything models](https://github.com/facebookresearch/segment-anything)
- Update [ComfyUI-AnimateDiff-Evolved](https://github.com/kosinkadink/ComfyUI-AnimateDiff-Evolved) to support Gen2 nodes (Fixes #19)

## 2024-02-14

- Add support for [InstantID](https://github.com/cubiq/ComfyUI_InstantID)
- Add support for [comfyui-reactor-nodes](https://github.com/Gourieff/comfyui-reactor-node)
- Improve support for Insightface in ComfyUI_IPAdapter_plus
- [Fix FaceID lora location](https://github.com/fofr/cog-comfyui/issues/15)

Models added:

- instantid-ipadapter.bin
- instantid-controlnet.safetensors
- antelopev2

## 2024-02-13

- Disable metadata on saved outputs (#14 by @digitaljohn)
- Add support for AIO_Preprocessor on ComfyUI_Controlnet_Aux
- Allow passing of an already parsed JSON workflow (helpful when forking the repo to push new Replicate models)

Models added:

- [copaxTimelessxlSDXL1_v8.safetensors](https://civitai.com/models/118111?modelVersionId=198246)

Loras added:

- [MODILL_XL_0.27_RC.safetensors](https://civitai.com/models/192139/modillxl-modern-colorful-illustration-style-lora)

## 2024-02-09

Models added:

- [artificialguybr](https://huggingface.co/artificialguybr) LoRAs
- [epicrealism_naturalSinRC1VAE.safetensors](https://civitai.com/models/25694/epicrealism)
- [motionctrl_svd.ckpt](https://huggingface.co/TencentARC/MotionCtrl)
- [sdxl_vae.safetensors](https://huggingface.co/stabilityai/sdxl-vae)

Face restoration and detection models:

- codeformer.pth
- GFPGANv1.3.pth
- GFPGANv1.4.pth
- RestoreFormer.pth
- detection_mobilenet0.25_Final.pth
- detection_Resnet50_Final.pth
- parsing_parsenet.pth
- yolov5l-face.pth
- yolov5n-face.pth

## 2024-01-23

Models added:

- [COOLKIDS_MERGE_V2.5.safetensors](https://civitai.com/models/60724/kids-illustration)
- [dreamlabsoil_V2_v2.safetensors](https://civitai.com/models/50718/dreamlabsoilv2)

Custom nodes added:

- https://github.com/BadCafeCode/masquerade-nodes-comfyui 240209b

## 2024-01-22

Models added:

- photomaker-v1.bin
- albedobaseXL_v13.safetensors
- RealESRGAN_x4plus_anime_6B.pth
- 4x_NMKD-Siax_200k.pth
- 4x-UltraSharp.pth
- [Harrlogos_v2.0.safetensors](https://civitai.com/models/176555/harrlogos-xl-finally-custom-text-generation-in-sd)
- starlightXLAnimated_v3.safetensors

Custom nodes added:

- https://github.com/TinyTerra/ComfyUI_tinyterraNodes eda8a09
- https://github.com/ssitu/ComfyUI_UltimateSDUpscale bcefc5b
- https://github.com/cubiq/ComfyUI_essentials c9236fe
- https://github.com/shiimizu/ComfyUI-PhotoMaker 75542a4
- https://github.com/pythongosssss/ComfyUI-Custom-Scripts 9916c13
