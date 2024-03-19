import os
import glob
from PIL import Image

class AssetsManager:
    def __init__(self, assets_path, source_resolution='HD', target_resolution='1280x720'):
        self.assets_path = assets_path
        self.source_resolution = source_resolution
        self.cache_dir = '.cache'
        self.assets = {}
        if source_resolution == 'HD':
            self.sw, self.sh = 1920, 1080
        
        assets = glob.glob(os.path.join(assets_path, f'*{source_resolution}.png'))
        if source_resolution == target_resolution:
            self.assets = {os.path.basename(a).split('.')[0].replace(source_resolution,''): a for a in assets}
        else:
            for asset in assets:
                path = self.resize_image(asset, target_resolution)
                self.assets[os.path.basename(asset).split('.')[0].replace(source_resolution,'')] = path

    def resize_image(self, image_path, resolution):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        target_image_path = os.path.join(self.cache_dir, os.path.basename(image_path).replace(self.source_resolution, resolution))
        with Image.open(image_path) as img:
            patch_w, patch_h = img.size
            w, h = [int(x) for x in resolution.split('x')]
            tw, th = patch_w * w // self.sw, patch_h * h // self.sh
            img = img.resize((tw, th))
            img.save(target_image_path)
        return target_image_path

    def get_asset_path(self, asset_name):
        return self.assets[asset_name]
