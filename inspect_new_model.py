import torch
import sys

try:
    state_dict = torch.load("Solution/backend/model/dziribert_absa-2.pt", map_location="cpu")
    print("Keys in state_dict:")
    for key in list(state_dict.keys())[:5]: # just some keys
        print(f"  {key}")
    
    if "classifier.weight" in state_dict:
        print(f"classifier.weight shape: {state_dict['classifier.weight'].shape}")
    elif "model.classifier.weight" in state_dict:
         print(f"model.classifier.weight shape: {state_dict['model.classifier.weight'].shape}")
    else:
        # look for any classifier or fc
        for k in state_dict.keys():
            if "classifier" in k or "fc" in k:
                print(f"Found potential output layer: {k} -> {state_dict[k].shape}")
except Exception as e:
    print(f"Error: {e}")
