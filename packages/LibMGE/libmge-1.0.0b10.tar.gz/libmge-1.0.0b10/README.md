# LibMGE

[![PyPI version](https://badge.fury.io/py/LibMGE.svg)](https://pypi.org/project/LibMGE/)
[![License: Zlib](https://img.shields.io/badge/License-Zlib-blue.svg)](https://opensource.org/licenses/Zlib)
[![Python](https://img.shields.io/pypi/pyversions/LibMGE.svg)](https://pypi.org/project/LibMGE/)

**LibMGE** is a powerful and easy-to-use graphical user interface library for developing 2D programs and games in Python.

## ✨ Features

- 🎮 Simple and intuitive API for 2D game development
- 🖼️ Built-in support for images and animated GIFs
- ⚡ Frame rate control and performance monitoring
- 🎨 Material and texture system
- ⌨️ Keyboard and event handling
- 🪟 Flexible window management

## 📦 Installation

```bash
pip install LibMGE
```

## 🔧 Dependencies

- [numpy](https://pypi.org/project/numpy/) - For efficient numerical operations
- [SDL2](https://github.com/libsdl-org/SDL) (bundled) - For graphics rendering

## 🚀 Quick Start

Here's a simple example that displays an animated GIF:

```python
import LibMGE

# Initialize the library
LibMGE.init()

# Create a window
window = LibMGE.Window(
    resolution=(500, 500), 
    flags=LibMGE.WindowFlag.Shown
)
window.frameRateLimit = 60

# Create a 2D object and load a GIF
gif = LibMGE.Object2D((0, 0), 0, (500, 500))
gif.material = LibMGE.Material(
    LibMGE.Texture(LibMGE.LoadImage("./image.gif"))
)

# Main loop
while True:
    LibMGE.update()
    window.update()
    window.title = f"LibMGE OpenGif | FPS: {window.frameRate}"
    
    # Exit on quit event or F1 key
    if LibMGE.QuitEvent() or LibMGE.keyboard(LibMGE.KeyboardButton.KeyF1):
        exit()
    
    gif.drawObject(window)
```

## 📚 Documentation

For detailed documentation and tutorials, visit:
- **Official Documentation**: [docs.libmge.org](https://docs.libmge.org/)
- **Website**: [libmge.org](https://libmge.org/)

## 🔗 Links

- **PyPI Package**: [pypi.org/project/LibMGE](https://pypi.org/project/LibMGE/)
- **Source Code**: [github.com/MonumentalGames/LibMGE](https://github.com/MonumentalGames/LibMGE)
- **Author Website**: [lucasguimaraes.pro](https://lucasguimaraes.pro/)

## 📝 License

LibMGE is distributed under the [zlib License](https://opensource.org/licenses/Zlib). This license allows you to freely use it in any software, whether personal, commercial, or open-source projects.

## 💻 Compatibility

LibMGE officially supports **Windows**. With some modifications, it can also run on:
- 🐧 **Linux** (experimental)
- 🤖 **Android** (experimental)

> **Note**: For best stability and performance, we recommend using LibMGE on Windows. Community contributions for better cross-platform support are welcome!

## 👤 Author

**Lucas Guimarães**
- Website: [lucasguimaraes.pro](https://lucasguimaraes.pro/)
- Email: commercial@lucasguimaraes.pro

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/MonumentalGames/LibMGE/issues).

**Current Version**: 1.0.0b10 (Beta)