import torch
import numpy as np
from cubeit import ResD, gf_reproj_err_minimizer_chw


def load_model(model_checkpoint, device='cuda'):
    model = ResD(pattern=4).to(device)
    model.load_state_dict(
        torch.load(model_checkpoint)["state_dict"]
    )
    return model.eval().to(device)


"""
@param im: input raw image, with values in range [0,1023]
@param model: Instance of demosaicing model
@param guided adjust: flag. If enabled, additional postprocessing step is performed which reduces reprojection error
@param device: inference device. Must match models device
@returns: cube of shape 16xHxW. Band order is determined by the mosaic pattern in the RAW image.
"""
def im2cube(im, model, guided_adjust=False, device='cuda'):
    cube = np.clip(model.pred_raw_chw(raw, device), 0, 1023)
    if guided_adjust:
        cube = gf_reproj_err_minimizer_chw(cube, raw, pattern=4)     
    return cube


if __name__ == "__main__":
    import os
    import matplotlib.pyplot as plt
    from cubeit.raw import read_raw

    device = 'cuda'
    W,H = 2048, 1088
    model = load_model(os.path.join("pretrained","best.pth.tar"), device)
    raw = read_raw(os.path.join("data","image_000000.raw"), 16, W, H)
    cube1 = im2cube(raw, model, guided_adjust=False, device=device)
    cube2 = im2cube(raw, model, guided_adjust=True, device=device)
    
    fig, axs = plt.subplots(2,8)
    for i in range(8):
        axs[0,i].imshow(cube1[i * 2], vmin=0, vmax=1023)
        axs[1,i].imshow(cube2[i * 2], vmin=0, vmax=1023)
        axs[0,i].axis("off")
        axs[1,i].axis("off")
        axs[0,i].set_title(f"band {i * 2}")
        axs[1,i].set_title(f"band {i * 2}\nadjusted")
    fig.tight_layout()
    plt.show()
    
