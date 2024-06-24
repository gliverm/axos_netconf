"""
File: loadingAnimations.py
Author: Ben Wilson (DevAuto Intern 2023)

Description: Houses the LoadingAnimation class which can be used to create non-progression based
loading animations that can run in any program without interrupting ongoing code.

An example of how this class can be used is shown below the class itself
and this script can be ran to see it in action
"""

import threading
import time


class LoadingAnimation:
    def __init__(
        self,
        text="Loading",
        animationFrames: list = ["    ", ".   ", "..  ", "... ", "...."],
        showElapsedTime=True,
        fps=2,
        display=True,  # if True the instance will handle displaying the animation
        hideOnComplete=True,
    ):
        self.loading = True
        self.animation_task = None
        self.startTime = None
        self.curr_frame_num = 0
        self.text = text
        self.fps = fps
        self.showElapsedTime = showElapsedTime
        self.frames = animationFrames
        self.currentFrame = ""
        self.display = display
        self.hideOnComplete = hideOnComplete
        self.elapsedTime = 0

    def _animate(self):
        while self.loading:
            self.elapsedTime = time.monotonic() - self.startTime
            frameToDisplay = self.frames[self.curr_frame_num]
            if self.display is True:
                print(self.currentFrame, end=" ")
            if self.showElapsedTime:
                self.currentFrame = f"\r{self.text}{frameToDisplay} Elapsed Time: {self.elapsedTime:.2f} seconds"
                time.sleep(0.05)
            else:
                self.currentFrame = f"\r{self.text}{frameToDisplay}"
                time.sleep(1 / self.fps)
        if self.display and self.hideOnComplete:
            clearCurrentLine()

    def _progressFrames(self):
        while self.loading:
            for fNum in range(0, len(self.frames)):
                self.curr_frame_num = fNum
                time.sleep(1 / self.fps)

    def start(self):
        self.loading = True
        self.startTime = time.monotonic()
        self.animation_thread = threading.Thread(target=self._animate)
        self.frames_thread = threading.Thread(target=self._progressFrames)
        # Put threads in daemon mode (stop when the main thread stops)
        self.animation_thread.daemon = True
        self.frames_thread.daemon = True
        # Start the threads
        self.animation_thread.start()
        self.frames_thread.start()

    def stop(self):
        # set loading to False to stop the animation loops
        self.loading = False
        # wait for both threads to finish executing
        self.animation_thread.join()
        # self.frames_thread.join()

    def get_current_frame(self) -> str:
        return self.currentFrame


def clearCurrentLine():
    """
    Clears the current line in the terminal.
    Used to remove the animation after completed.
    """
    print("\r", end="")


def clearPreviousLine():
    """
    Clears the current and previous lines of the terminal
    """
    print("\033[A                             \033[A")


# EXAMPLE USAGE CODE
if __name__ == "__main__":
    # Example usage
    animation = LoadingAnimation(
        text="Custom Text ", animationFrames=["\\", "|", "/", "-"], fps=10
    )
    animation.start()

    # Simulating some other code running in the background
    time.sleep(10)

    animation.stop()
