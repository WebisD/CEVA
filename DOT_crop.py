# Class for CROP and ROTATE the DOT

class DOTCrop:
    def __init__(self, image, bouding_boxes: list) -> None:
        self.image = image
        self.bouding_boxes = bouding_boxes
    
    #
    # APENAS UM EXEMPLO. PODEM MUDAR COMO DESEJAREM
    #
    def reorient_dot(self, image, bouding_boxes):
        self.crop_dot(image, bouding_boxes)
        self.rotate_dot()
        return
    
    def crop_dot(self, image, bouding_boxes):
        pass

    def rotate_dot(self, image):
        pass
    