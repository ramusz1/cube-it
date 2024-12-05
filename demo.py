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
    from cubeit.raw import read_raw, raw2cube_chw
    from cubeit.util import cube2RGB_chw


    device = 'cuda'
    W,H = 2048, 1088
    model = load_model(os.path.join("pretrained","trc_bi_synth_coco_100k.pth.tar"), device)
    raw = read_raw(os.path.join("data","image_000000.raw"), 16, W, H)
    cube0 = raw2cube_chw(raw, 4)
    cube1 = im2cube(raw, model, guided_adjust=False, device=device)
    cube2 = im2cube(raw, model, guided_adjust=True, device=device)
    rgb0 = cube2RGB_chw(cube0)
    rgb1 = cube2RGB_chw(cube1)
    rgb2 = cube2RGB_chw(cube2)
    
    fig, axs = plt.subplots(2,4)

    axs[0,0].imshow(raw)
    axs[0,1].imshow(rgb0)
    axs[0,2].imshow(rgb1)
    axs[0,3].imshow(rgb2)

    axs[0,0].set_title("raw")
    axs[0,1].set_title("lr")
    axs[0,2].set_title("demosaicked")
    axs[0,3].set_title("w guided adjust")

    x1,y1,x2,y2 = 300,300,400,400
    axs[1,0].imshow(raw[y1:y2, x1:x2])
    axs[1,1].imshow(rgb0[y1//4:y2//4, x1//4:x2//4])
    axs[1,2].imshow(rgb1[y1:y2, x1:x2])
    axs[1,3].imshow(rgb2[y1:y2, x1:x2])

    fig.tight_layout()
    plt.show()
