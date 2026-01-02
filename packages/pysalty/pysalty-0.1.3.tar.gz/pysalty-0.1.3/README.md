# PySalty (Python Structural Architecture Layout Tool)

PySalty is a lightweight Python library for visualizing PyTorch neural network architectures as clean, publication ready diagrams.

It is designed for:

* research papers
* presentations
* documentation
* understanding complex models

PySalty focuses on clarity and aesthetics rather than training, execution, or graph theory.

---

## Features

* Automatic PyTorch model parsing
* Hierarchical visualization of nn.Sequential blocks
* Intelligent edge routing that avoids overlapping modules
* Multiple built in visual themes
* Fully customizable colors, fonts, and layout
* High resolution PNG export
* Zero dependency on model execution
* No arrows or ports for clean publication ready figures

---

## Installation

Install from PyPI:

```bash
pip install pysalty
```

---

## Quick Start

```bash
import torch.nn as nn
from salt import Visualize, PaperTheme

class SimpleNet(nn.Module):
    def __init__(self):
        super().__init__()
        self.Stem = nn.Sequential(
            nn.Conv2d(3, 64, 3),
            nn.ReLU(),
        )
        self.Head = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(64, 10),
        )

model = SimpleNet()

Visualize(
    model,
    theme=PaperTheme,
    save_path="model.png"
)
```

This produces a clean architecture diagram suitable for papers or slides.

---

## How model parsing works

PySalty parses only the top level children of your PyTorch model.

Example structure:

```bash
class MyModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.Stem = ...
        self.Stage1 = ...
        self.Stage2 = ...
        self.Head = ...
```

Each top level attribute becomes a block in the diagram.

---

### Containers nn.Sequential

If a top level module is an nn.Sequential, PySalty will:

* Draw it as a container box
* Draw each sub layer inside it
* Automatically connect internal layers vertically

Example:

```bash
self.Stem = nn.Sequential(
    ConvBNAct(...),
    ConvBNAct(...),
)
```

This becomes a container labeled Stem with child blocks inside.

---

### Non sequential modules

If a module is not an nn.Sequential, it is drawn as a single block labeled by its class name.

---

## Connections

* Blocks are connected in the order they appear in the model definition
* Routing automatically avoids overlapping other blocks
* Long connections are lifted above the diagram when needed
* No manual configuration is required

---

## Built in Themes

PySalty includes several ready to use themes defined in salt.theme.

### DarkTheme

Dark background with soft purple highlights. Suitable for presentations and screen viewing.

```bash
from salt import DarkTheme
```

### LightTheme

Clean white background with subtle gray outlines. Suitable for documentation.

```bash
from salt import LightTheme
```

### PaperTheme

Pure black and white styling with sharp corners and thinner edges. Recommended for research papers and LaTeX figures.

```bash
from salt import PaperTheme
```

### DraculaTheme

Dark purple background with neon accents inspired by the Dracula color palette.

```bash
from salt import DraculaTheme
```

---

### LightTheme

Clean white background with subtle gray outlines. Suitable for documentation.

```bash
from salt import LightTheme
```

---

### PaperTheme

Pure black and white styling with sharp corners and thinner edges. Recommended for research papers and LaTeX figures.

```bash
from salt import PaperTheme
```

---

### DraculaTheme

Dark purple background with neon accents inspired by the Dracula color palette.

```bash
from salt import DraculaTheme
```

---

## Creating your own theme

You can fully customize the appearance by creating a Theme object. All styling options are defined in salt.theme.Theme.

```bash
from salt import Theme

MyTheme = Theme(
    Background="#0B1020",
    Primary="#00E5FF",
    Accent="#FFD54F",
    Text="#E0F7FA",
    Line="#90A4AE",
    BoxFill="#102027",
    ChildFill="#1C313A",

    FontFamily="Times New Roman",
    FontSize=12,
    TitleFontSize=13,
    FontWeight="regular",

    CornerRadius=0.3,
    EdgeWidth=2.5,
)
```

Then use it:

```bash
Visualize(model, theme=MyTheme)
```

---

## Fonts

PySalty uses Matplotlib fonts.

Any font installed on your system can be used by setting:

```bash
FontFamily="Times New Roman"
```

Common choices for papers include Times New Roman, Computer Modern, and DejaVu Serif.

---

## Output

* By default, the figure is returned and can be shown inline in Jupyter
* Use save_path to export a high resolution PNG

```bash
Visualize(model, save_path="architecture.png")
```

---

## License

MIT License

Free for academic and commercial use.

---

## Notes and Limitations

* PySalty is a visualization tool, not a graph execution engine
* Skip connections and general DAGs are not yet supported
* Only top level modules are visualized by design

These decisions are intentional to keep diagrams clean and readable.

---

## Contributing

Contributions are welcome, including new themes, layout improvements, export formats, and documentation improvements.
