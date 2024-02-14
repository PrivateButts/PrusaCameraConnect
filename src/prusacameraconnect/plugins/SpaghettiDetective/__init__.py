from plugins import BasePluginHandler


class DetectivePlugin(BasePluginHandler):
    def __init__(self, config):
        self.snapshot_url = config.get("snapshot_url")
        self.detective_url = config.get("detective_url")

    def image_processing_hook(self, image):
        return image