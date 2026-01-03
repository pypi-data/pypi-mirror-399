from collections import OrderedDict
import cv2
from PIL import Image
from torch.utils.data.dataloader import Dataset
import numpy as np
import warnings
from torch import Tensor, cat
from torchcodec.decoders import VideoDecoder
from torchvision.transforms import Resize

class VideoDataset(Dataset):
    """
    Dataset class for fetching specific information about a video.
    The class requires a list of videos that it has to process.
    """

    def __init__(self, videos, v2=False, device='cuda', batch_size=100) -> None:
        super().__init__()
        self.videos = videos
        self.v2 = v2
        self.device = device
        self.batch_size = batch_size
    def __getitem__(self, index: int):
        """
        This function, picks a video and returns 4 values.
            str: Contains the name of the video
            list: List containing only the frame indices that are readable
            number: fps of the video
            list: a list containing all the frames as image arrays
        """
        video = self.videos[index]
        decoder = VideoDecoder(video, device=self.device)
        frames_num = decoder.metadata.num_frames
        fps = decoder.metadata.average_fps_from_header
        height, width = decoder.metadata.height, decoder.metadata.width
        frames = []
        batch_size = self.batch_size
        if not self.v2:
            rem_frames = frames_num%batch_size
            tot_batches = frames_num//batch_size
            end = 0
            for start in range(0, frames_num, batch_size):
                end = start+batch_size
                frame_set = decoder[start:end]
                resize = Resize((height//2, width//2))
                frames.append(resize(frame_set).cpu())
            if rem_frames!=0:
                frame_set = decoder[end:]
                if isinstance(frame_set, Tensor) and frame_set.shape[0] != 0:
                    resize = Resize((height//2, width//2))
                    frames.append(resize(frame_set).cpu())

        frames = cat(frames).permute(0, 2, 3, 1).cpu().numpy()
        if self.v2 and len(frames) > 0 and ((not isinstance(frames[0], np.ndarray) and (not isinstance(frames[0], Image.Image)))):
            warnings.warn("No Frames read in the video")
        return video, range(frames_num), fps, frames

    def __len__(self) -> int:
        return len(self.videos)
