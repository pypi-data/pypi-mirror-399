# spellfixer/core.py

import os
import subprocess
import torch
from huggingface_hub import snapshot_download

# --- Torchtune Imports ---
from torchtune.models.llama3 import llama3_tokenizer
from torchtune.models.llama3_2 import llama3_2_1b
from torchtune.generation import generate
from torchtune.training.checkpointing import FullModelHFCheckpointer
from torchtune.data import Message

# Set the device automatically (MPS for Mac, CUDA for Nvidia, else CPU)
if torch.backends.mps.is_available():
    device = "mps"
elif torch.cuda.is_available():
    device = "cuda"
else:
    device = "cpu"

# Global variables (Warm Start)
model = None
tokenizer = None

def download_model(model_name):
    local_dir = f"/tmp/torchtune/llama3_2_1B/{model_name}/epoch_0"
    repo_id = f"Xamxl/{model_name}"
    os.makedirs(local_dir, exist_ok=True)
    print(f"Downloading {repo_id} to {local_dir}...")
    snapshot_download(
        repo_id=repo_id,
        local_dir=local_dir,
        repo_type="model",
        token=True
    )
    print("Download complete.")

def is_downloaded(model_path):
    files = "model.safetensors"
    if model_path != "/tmp/Llama-3.2-1B-Instruct":
        model_path = "/tmp/torchtune/llama3_2_1B/" + model_path + "/epoch_0"
        files = "model-00001-of-00001.safetensors"
    return os.path.exists(os.path.join(model_path, files))

def prep_model(model_path):
    if not is_downloaded(model_path):
        if model_path != "/tmp/Llama-3.2-1B-Instruct":
            download_model(model_path)
        else:
            # Note: This requires the 'tune' CLI to be available in the environment
            subprocess.run('tune download meta-llama/Llama-3.2-1B-Instruct --ignore-patterns "original/consolidated.00.pth"', shell=True, check=True)

def load_model(model_path="/tmp/Llama-3.2-1B-Instruct"):
    prep_model(model_path)

    global model, tokenizer
    files = "model.safetensors"
    
    # Determine exact path based on input
    if model_path != "/tmp/Llama-3.2-1B-Instruct":
        model_path = "/tmp/torchtune/llama3_2_1B/" + model_path + "/epoch_0"
        files = "model-00001-of-00001.safetensors"

    print(f"Loading model from {model_path} to {device}...")
    
    # FIX: Initialize model on the correct device
    model = llama3_2_1b().to(device)
    
    # Load tokenizer
    try:
        tokenizer = llama3_tokenizer(path=model_path + "/original/tokenizer.model")
    except:
        try:
            tokenizer = llama3_tokenizer(path=model_path + "/tokenizer.model")
        except Exception as e:
            print(f"Error loading tokenizer: {e}")
            raise

    # Load checkpoint
    checkpointer = FullModelHFCheckpointer(
        checkpoint_dir=model_path,
        checkpoint_files=[files],
        model_type="LLAMA3_2",
        output_dir="/tmp/output",
    )
    checkpoint = checkpointer.load_checkpoint()
    model.load_state_dict(checkpoint["model"])
    print("Model loaded successfully.")

def generate_text(prompt: str) -> str:
    if model is None or tokenizer is None:
        return "Error: Model not loaded. Run load_model() first."
        
    messages = [
        Message(role="user", content=prompt),
        Message(role="assistant", content=""),
    ]
    
    # Tokenize
    encoded_data = tokenizer({"messages": messages}, inference=True)
    prompt_tokens = encoded_data["tokens"]
    
    # FIX: Move tensor to the correct device
    prompt_tensor = torch.tensor(prompt_tokens, device=device).unsqueeze(0)

    # Generate
    output, logits = generate(
        model,
        prompt_tensor,
        max_generated_tokens=100,
        pad_id=0,
        temperature=0,
        stop_tokens=tokenizer.stop_tokens
    )

    generated_tokens = output[0].tolist()
    decoded_text = tokenizer.decode(generated_tokens)
    
    # Return text (attempting to strip the input prompt if possible)
    # Note: Depending on tokenizer/formatting, simple slicing might need adjustment.
    return decoded_text[len(prompt):]

# Allow running this file directly for testing
if __name__ == "__main__":
    print(f"Running in test mode on {device}...")
    load_model("spellfixer_v1")
    print("Result:", generate_text("helo"))