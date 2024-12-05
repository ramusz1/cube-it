import torch
from torch import nn
import numpy as np


class BaseDemosaicNet(torch.nn.Module):

    def __init__(self):
        super().__init__()

    def pred_raw(self, x, device):
        if isinstance(x, np.ndarray):
            x = torch.from_numpy(x)
        x = x.to(device).unsqueeze(0).unsqueeze(0) # batch the input
        x = x.type(torch.float32) / 1024
        output = self.forward(x).squeeze(0).movedim(0,-1) * 1024
        return output.numpy(force=True)

    def pred_raw_chw(self, x, device):
        if isinstance(x, np.ndarray):
            x = torch.from_numpy(x)
        x = x.to(device).unsqueeze(0).unsqueeze(0) # batch the input
        x = x.type(torch.float32) / 1024
        output = self.forward(x).squeeze(0) * 1024
        return output.numpy(force=True)


class ResBlock(nn.Module):

    def __init__(self, in_channels, out_channels, ksize=3):
        super(ResBlock, self).__init__()
        assert ksize % 2 == 1
        p = ksize // 2
        self.block = nn.Sequential(
           nn.Conv2d(in_channels, out_channels, kernel_size=ksize, padding=p),
           nn.ReLU(inplace=True),
           nn.Conv2d(out_channels, out_channels, kernel_size=ksize, padding=p)
        )

    def forward(self, x):
        return x + self.block(x)


class ResD(BaseDemosaicNet): # nn.Module previously

    def __init__(self, pattern):
        super().__init__()
        self.pattern = pattern
        self.net = nn.Sequential(
            nn.Conv2d(1 + 3, 64, kernel_size=5, padding=2), # raw + positional encoding
            nn.ReLU(inplace=True),
            ResBlock(64,64, ksize=5),
            ResBlock(64,64, ksize=5),
            ResBlock(64,64, ksize=5),
            ResBlock(64,64),
            ResBlock(64,64),
        )
        self.final_layers = nn.Sequential(
            nn.Conv2d(64 + 1 + 3, 32, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, pattern * pattern, kernel_size=3, padding=1)
        )
    
    def forward(self, x):
        # x : batch, channels, height, width
        b, c, h, w = x.shape
        # c == 1 because we are working with raw inputs
        pos_x, pos_y = torch.meshgrid(torch.linspace(0, 1, self.pattern), torch.linspace(0, 1, self.pattern), indexing="ij")
        pos_band = pos_x * self.pattern + pos_y
        pos_band /= torch.max(pos_band)
        pos_encoding = torch.stack([pos_x, pos_y, pos_band], axis=0).type(x.dtype).to(x.device)
        # print(pos_encoding.shape)
        pos_encoding = pos_encoding.repeat((1, h // self.pattern, w // self.pattern))

        # print(pos_encoding)
        x = torch.cat((x, pos_encoding.unsqueeze(0).expand(b,-1,-1,-1)), dim=1)
        input_copy = x.clone()
        x = self.net(x)
        # concatenate the input to possibly reduce the ireprojection error
        x = torch.cat((input_copy, x), dim=1)
        return self.final_layers(x)


