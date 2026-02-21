# MouseCam

MouseCam is a simple Python program that allows users to control their mouse using gestures from their webcam. This program uses the MediaPipe Hand Landmarker task, OpenCV, and PyAutoGUI to function.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the necessary packages from requirements.txt.

```bash
pip install -r /path/to/requirements.txt
```

## Usage

In the terminal, run the following command to launch the program:
```bash
python /path/to/camera.py
```

The program will automatically choose an operational camera to use as the input. Should you wish to run the program using a specific camera, please add the following argument, where the camera index is a numerical value indicating the camera's position in the Device Manager list.
```bash
python /path/to/camera.py <camera-index>
```

Additionally, should you wish to see your camera feed while using the program, please use the following argument:
```bash
python /path/to/camera.py -show
```

Both arguments can be used simultaneously if needed:
```bash
python /path/to/camera.py -show 1
```

## Author and Contributing
This program was first created by Peter Buddendeck on 2/20/2026. Modifications are welcomed.

## License

[MIT](https://choosealicense.com/licenses/mit/)