# HabitAware

HabitAware is a computer vision-based application designed to help users monitor and reduce nail-biting and hair-pulling behaviors. Using real-time camera input, the application detects these behaviors and provides visual feedback and warnings to help users become more aware of their habits.

## Features

- Real-time behavior detection for nail-biting and hair-pulling
- Visual feedback with on-screen indicators
- Timer tracking for behavior duration
- Stress attempt counter
- Web interface for easy access and monitoring
- Sound notifications for behavior detection

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/HabitAware.git
cd HabitAware
```

2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Desktop Application
Run the desktop version:
```bash
python app.py
```

### Web Application
Run the web version:
```bash
streamlit run app_web.py
```

## How It Works

HabitAware uses computer vision techniques to:
1. Detect hand positions and movements
2. Identify face zones
3. Monitor interactions between hands and face
4. Track specific behaviors like nail-biting and hair-pulling
5. Provide real-time feedback and warnings

## Project Structure

- `app.py` - Main desktop application
- `app_web.py` - Web interface using Streamlit
- `detection.py` - Core detection logic
- `camera_manager.py` - Camera handling
- `sound_manager.py` - Sound notifications
- `StressPopup.py` - Stress warning popups
- `ui.py` - User interface components
- `assets/` - Resource files

## Dependencies

- OpenCV (cv2)
- MediaPipe
- Streamlit
- Python 3.x


## Acknowledgments

- OpenCV for computer vision capabilities
- MediaPipe for hand and face detection
- Streamlit for web interface 

## License

This project is licensed under the **Creative Commons Attribution-NonCommercial 4.0 International (CC BY-NC 4.0)** License.

You are free to use, remix, and learn from this code for personal or educational purposes.  
🚫 Please do not reuse this project for competitions or commercial use without significant original contributions and proper attribution.

Original creators: [Jackie Lin, Rayat Chowdhury, Fuad Farhan]

