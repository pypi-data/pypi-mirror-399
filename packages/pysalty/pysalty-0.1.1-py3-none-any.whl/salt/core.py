import io
import re
from dataclasses import dataclass, field
from typing import List, Tuple

import torch.nn as nn
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, PathPatch
from matplotlib.path import Path
from PIL import Image
from .theme import Theme, DarkTheme


def _Prettify(name: str) -> str:
    name = name.replace("_", " ")
    name = re.sub(r"([a-z])([A-Z])", r"\1 \2", name)
    return name.title()


def _TextBlock(label, per_char=0.14, line_h=0.45, pad=0.6):
    lines = label.split("\n")
    w = max(len(l) * per_char for l in lines) + pad
    h = len(lines) * line_h + pad
    return w, h

def _BBoxIntersects(b1, b2):
    x1, y1, x2, y2 = b1
    x3, y3, x4, y4 = b2
    return not (x2 < x3 or x4 < x1 or y2 < y3 or y4 < y1)


def _EdgeBBox(x1, y1, x2, y2, pad=0.4):
    return (
        min(x1, x2) - pad,
        min(y1, y2) - pad,
        max(x1, x2) + pad,
        max(y1, y2) + pad,
    )


def _NodeBBox(n):
    return (n.X, n.Y - n.H, n.X + n.W, n.Y)


@dataclass
class Node:
    Label: str
    Children: List["Node"] = field(default_factory=list)
    X: float = 0
    Y: float = 0
    W: float = 0
    H: float = 0
    IsContainer: bool = False

    OutEdges: dict = field(default_factory=lambda: {
        "Left": [],
        "Right": [],
        "Bottom": []
    })
    InEdges: dict = field(default_factory=lambda: {
        "Left": [],
        "Right": [],
        "Top": []
    })



def _ParseModel(model: nn.Module) -> List[Node]:
    nodes = []
    for name, module in model.named_children():
        n = Node(_Prettify(name))
        if isinstance(module, nn.Sequential):
            for layer in module:
                n.Children.append(Node(_Prettify(layer.__class__.__name__)))
        else:
            n.Children.append(Node(_Prettify(module.__class__.__name__)))
        n.IsContainer = len(n.Children) > 1
        nodes.append(n)
    return nodes



def _Layout(nodes: List[Node], theme: Theme):
    GAP_X, GAP_Y = 3.2, 2.2
    MAX_H = 14

    for n in nodes:
        title_w, _ = _TextBlock(n.Label)
        if n.IsContainer:
            child_ws, child_hs = zip(*(_TextBlock(c.Label) for c in n.Children))
            n.W = max(title_w, max(child_ws)) + 1.4
            n.H = theme.TitleHeight + sum(child_hs) + len(child_hs) * 0.8
        else:
            n.W = title_w + 1.4
            n.H = 2.4

    x, col_h, col_w = 0, 0, 0
    prev = None

    for n in nodes:
        if prev:
            cand_y = prev.Y - prev.H - GAP_Y
            if abs(cand_y) < MAX_H:
                n.X = prev.X
                n.Y = cand_y
            else:
                x += col_w + GAP_X
                col_h = 0
                col_w = 0
                n.X = x
                n.Y = 0
        else:
            n.X = x
            n.Y = 0

        col_h += n.H + GAP_Y
        col_w = max(col_w, n.W)
        prev = n

        if n.IsContainer:
            cy = n.Y - theme.TitleHeight - 0.4
            for c in n.Children:
                c.W, c.H = _TextBlock(c.Label)
                c.X = n.X + (n.W - c.W) / 2
                c.Y = cy
                cy -= c.H + 0.8


def _ChooseSides(a: Node, b: Node):
    dx = b.X - a.X
    dy = b.Y - a.Y

    if dy < 0:
        return "Bottom", "Top"

    
    if dy > 0:
        return ("Right" if dx >= 0 else "Left", "Top")

    
    return ("Right" if dx >= 0 else "Left",
            "Left" if dx >= 0 else "Right")



def _PortPosition(n: Node, side: str, theme: Theme, count: int, index: int):
    offset = (index - (count - 1) / 2) * theme.PortSeparation

    if side == "Left":
        return (n.X - theme.PortOffset, n.Y - n.H / 2 + offset)
    if side == "Right":
        return (n.X + n.W + theme.PortOffset, n.Y - n.H / 2 + offset)
    if side == "Top":
        return (n.X + n.W / 2 + offset, n.Y + theme.PortOffset)
    if side == "Bottom":
        return (n.X + n.W / 2 + offset, n.Y - n.H - theme.PortOffset)

    raise ValueError("Invalid port side")

'''
def _DrawPort(ax, x, y, theme: Theme):
    ax.add_patch(Rectangle(
        (x - theme.PortSize / 2, y - theme.PortSize / 2),
        theme.PortSize,
        theme.PortSize,
        facecolor=theme.Accent,
        edgecolor="none",
        zorder=6
    ))'''


def _DrawEdges(ax, edges, nodes, theme: Theme):
    
    for a, b in edges:
        out_side, in_side = _ChooseSides(a, b)
        a.OutEdges[out_side].append(b)
        b.InEdges[in_side].append(a)

    
    ROUTE_MARGIN = 2.5
    route_y = max(n.Y for n in nodes) + ROUTE_MARGIN

    
    for a, b in edges:
        out_side, in_side = _ChooseSides(a, b)

        i_out = a.OutEdges[out_side].index(b)
        i_in = b.InEdges[in_side].index(a)

        x1, y1 = _PortPosition(
            a, out_side, theme,
            len(a.OutEdges[out_side]), i_out
        )
        x2, y2 = _PortPosition(
            b, in_side, theme,
            len(b.InEdges[in_side]), i_in
        )

        '''_DrawPort(ax, x1, y1, theme)
        _DrawPort(ax, x2, y2, theme)'''

        
        edge_box = _EdgeBBox(x1, y1, x2, y2)

        interferes = False
        for n in nodes:
            if n is a or n is b:
                continue
            if _BBoxIntersects(edge_box, _NodeBBox(n)):
                interferes = True
                break

        
        if interferes:
            
            mid_y = max(route_y, y1 + 1.5)

            path = Path(
                [
                    (x1, y1),
                    (x1, mid_y),
                    (x2, mid_y),
                    (x2, y2),
                ],
                [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
            )
        else:
            
            dx = (x2 - x1) * theme.BezierStrength
            path = Path(
                [
                    (x1, y1),
                    (x1 + dx, y1),
                    (x2 - dx, y2),
                    (x2, y2),
                ],
                [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4]
            )

        ax.add_patch(PathPatch(
            path,
            edgecolor=theme.Line,
            lw=theme.EdgeWidth,
            facecolor="none",
            zorder=2
        ))

        '''ax.add_patch(FancyArrowPatch(
            (x2, y2 + 0.01),
            (x2, y2),
            arrowstyle="-|>",
            lw=theme.EdgeWidth,
            color=theme.Accent,
            zorder=3
        ))'''



def _DrawBox(ax, x, y, w, h, label, fill, theme: Theme, lw):
    ax.add_patch(FancyBboxPatch(
        (x, y - h),
        w, h,
        boxstyle=f"round,pad={theme.BoxPadding},rounding_size={theme.CornerRadius}",
        linewidth=lw,
        edgecolor=theme.Primary,
        facecolor=fill
    ))

    ax.text(
        x + w / 2,
        y - h / 2,
        label,
        ha="center",
        va="center",
        color=theme.Text,
        fontsize=theme.FontSize,
        family=theme.FontFamily
    )


def _DrawContainer(ax, n: Node, theme: Theme):
    _DrawBox(ax, n.X, n.Y, n.W, n.H, "", theme.BoxFill, theme, 2.0)

    ax.text(
        n.X + n.W / 2,
        n.Y - 0.6,
        n.Label,
        ha="center",
        va="center",
        color=theme.Text,
        fontsize=theme.TitleFontSize
    )

    prev = None
    for c in n.Children:
        _DrawBox(ax, c.X, c.Y, c.W, c.H, c.Label, theme.ChildFill, theme, 1.2)
        if prev:
            ax.add_patch(FancyArrowPatch(
                (prev.X + prev.W / 2, prev.Y - prev.H - 0.15),
                (c.X + c.W / 2, c.Y + 0.15),
                arrowstyle="-|>",
                lw=1.4,
                color=theme.Accent
            ))
        prev = c



def Visualize(model: nn.Module, theme: Theme = DarkTheme, save_path: str | None = None):
    nodes = _ParseModel(model)
    _Layout(nodes, theme)

    edges = list(zip(nodes, nodes[1:]))

    fig, ax = plt.subplots(figsize=(22, 10))
    fig.patch.set_facecolor(theme.Background)
    ax.set_facecolor(theme.Background)

    
    for n in nodes:
        if n.IsContainer:
            _DrawContainer(ax, n, theme)
        else:
            _DrawBox(ax, n.X, n.Y, n.W, n.H, n.Label, theme.BoxFill, theme, 2.0)

    
    _DrawEdges(ax, edges, nodes, theme)

    ax.axis("off")
    ax.autoscale()
    ax.margins(0.15)

    if save_path:
        buf = io.BytesIO()
        fig.savefig(buf, dpi=300, bbox_inches="tight", facecolor=theme.Background)
        Image.open(buf).save(save_path)

    return fig

