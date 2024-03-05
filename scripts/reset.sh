#!/bin/bash
sudo rm -rf ComfyUI
git submodule update --init --recursive
./scripts/clone_plugins.sh
