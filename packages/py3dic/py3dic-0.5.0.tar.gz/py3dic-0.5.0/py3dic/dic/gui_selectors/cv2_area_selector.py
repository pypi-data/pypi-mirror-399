import cv2
import numpy as np

class AreaSelectorCV2:
    '''This class uses opencv to select an area or interest.
    # TODO replace this with my ROI code. (this would require to make the window modal)
    '''
    def __init__(self, PreliminaryImage):
        self.area = []
        self.cropping = False
        self.image = cv2.putText(PreliminaryImage, "Pick the area of interest (left click + move mouse) and press 'c' button to continue", (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),4)

    def pick_area_of_interest(self):
        """
        Picks area of interest from an image if data are not selected.

        Returns:
            list: A list of tuples representing the coordinates of the area of interest.
        """
        clone = self.image.copy()
        cv2.namedWindow('image', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('image', self.image.shape[1], self.image.shape[0])
        cv2.setMouseCallback("image", self.click_and_crop)

        while True:
            cv2.imshow("image", self.image)
            key = cv2.waitKey(1) & 0xFF

            if key == ord("r"):
                self.image = clone.copy()
            elif key == ord("c"):
                print(f'The area of interest is {self.area}')
                break
        return self.area

    def click_and_crop(self, event, x, y, flags, param):
        """
        Handles mouse events for selecting the area of interest.

        Args:
            event (int): OpenCV event type.
            x (int): X-coordinate of the mouse event.
            y (int): Y-coordinate of the mouse event.
            flags (int): Event flags.
            param (any): Extra parameters.
        """
        if event == cv2.EVENT_LBUTTONDOWN:
            self.area = [(x, y)]
            self.cropping = True

        elif event == cv2.EVENT_LBUTTONUP:
            self.area.append((x, y))
            self.cropping = False

            new_image = cv2.rectangle(self.image, self.area[0], self.area[1], (0, 255, 0), 2)
            cv2.imshow('image', new_image)
