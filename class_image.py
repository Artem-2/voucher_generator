class image_data:
    def __init__(self) -> None:
         self.size_factor = {"Width":float,"Height":float}
         self.type = str() #TEXT, QRCODE, BRCODE
         self.coordinates = {"X":int,"Y":int}