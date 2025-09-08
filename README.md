# Web Media Converter

A beautiful, local web-based media converter with stunning UI themes. Convert videos to WebM and images to WebP format with style!

![Python](https://img.shields.io/badge/Python-3.7+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## Features

- **Video Conversion**: Convert any video format to WebM
- **Image Conversion**: Convert any image format to WebP
- **5 Beautiful Themes**:
  - **Default**: Modern gradient design
  - **Glass**: Advanced glass morphism with animated backgrounds
  - **Liquid**: Dynamic liquid glass with color-shifting gradients
  - **Dark**: Sleek dark mode for night owls
  - **Soft**: Neumorphic design with soft shadows
- **Local Processing**: All conversions happen on your machine - no uploads to external servers
- **Quality Control**: Adjustable quality settings for optimal file size
- **Size Comparison**: Real-time display of file size reduction
- **Drag & Drop**: Simple drag-and-drop interface
- **Smooth Animations**: Beautiful transitions and effects
- **Auto-Download**: Files automatically download after conversion
- **Persistent Settings**: Theme preference saved locally

## Screenshots

### Available Themes

1. **Default Theme** - Clean, modern gradient design
2. **Glass Theme** - Beautiful glass morphism with blur effects
3. **Liquid Theme** - Dynamic liquid glass with animated gradients
4. **Dark Theme** - Easy on the eyes for nighttime use
5. **Soft Theme** - Trendy neumorphic design

## Quick Start

### Prerequisites

- Python 3.7 or higher
- FFmpeg installed on your system

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/web-media-converter.git
cd web-media-converter
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install FFmpeg**

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
Download from [FFmpeg official website](https://ffmpeg.org/download.html)

### Running the Application

```bash
python converter.py
```

The application will start and be available at:
```
http://127.0.0.1:8080
```

## Usage

1. **Open your browser** and navigate to `http://127.0.0.1:8080`
2. **Choose a theme** using the buttons in the top-right corner
3. **Drag and drop** your media file or click to browse
4. **Adjust quality** settings if needed (optional)
5. **Wait for conversion** - progress bar shows the status
6. **File downloads automatically** when conversion is complete

## Theme Details

### Glass Theme
- Advanced glass morphism effects
- Animated background with parallax scrolling
- Translucent elements with backdrop blur
- Perfect for modern, elegant interfaces

### Liquid Theme
- Dynamic color-shifting gradients
- Liquid glass effects with distortion
- Animated background patterns
- Vibrant and energetic design

### Neumorphism (Soft) Theme
- Soft, extruded elements
- Subtle shadows and highlights
- Minimalist and trendy design
- Easy on the eyes

## Supported Formats

### Video Input
- MP4, AVI, MOV, MKV, FLV, WMV, M4V, MPG, MPEG, 3GP, and more

### Image Input
- JPG, JPEG, PNG, GIF, BMP, TIFF, TIF, SVG, and more

### Output Formats
- **Videos**: WebM (VP9 codec with Opus audio)
- **Images**: WebP (lossy compression)

## Configuration

### Quality Settings
- **10-30%**: Higher quality, larger file size
- **40-60%**: Balanced quality and size
- **70-90%**: Lower quality, smaller file size

### Maximum File Size
- Default: 500MB
- Can be modified in `converter.py` (line 14)

## Technical Details

### Technologies Used
- **Backend**: Python Flask
- **Frontend**: Pure HTML/CSS/JavaScript (no frameworks)
- **Conversion**: FFmpeg
- **Styling**: CSS3 with advanced effects (glass morphism, neumorphism)
- **Storage**: Browser localStorage for theme preferences

### File Processing
- Files are temporarily stored during conversion
- Automatic cleanup after conversion
- No permanent storage of user files
- All processing happens locally

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- FFmpeg for media conversion capabilities
- Flask for the web framework
- The open-source community for inspiration

## Troubleshooting

### Port Already in Use
If you see "Port 8080 is in use", either:
- Stop the other application using port 8080
- Or modify the port in `converter.py` (last line)

### FFmpeg Not Found
Make sure FFmpeg is installed and in your system PATH:
```bash
ffmpeg -version
```

### Conversion Fails
- Check that your input file is not corrupted
- Ensure you have enough disk space for temporary files
- Try adjusting the quality settings

## Contact

For questions or support, please open an issue on GitHub.

---

Made with care for the community | Convert locally, stay private!