from dataclasses import dataclass


@dataclass
class Theme:
    # Colors
    Background: str
    Primary: str
    Accent: str
    Text: str
    Line: str
    BoxFill: str
    ChildFill: str

    # Typography
    FontFamily: str = "DejaVu Sans"
    FontSize: int = 12
    TitleFontSize: int = 13
    FontWeight: str = "regular"

    # Boxes
    CornerRadius: float = 0.15
    BoxPadding: float = 0.1
    TitleHeight: float = 1.2

    # Edges
    EdgeWidth: float = 4.0
    BezierStrength: float = 0.45




DarkTheme = Theme(
    Background="#121212",
    Primary="#8E7CFF",
    Accent="#FF9F43",
    Text="#EDEDED",
    Line="#B0B0B0",
    BoxFill="#1E1E1E",
    ChildFill="#242424",
)

LightTheme = Theme(
    Background="#FFFFFF",
    Primary="#333333",
    Accent="#333333",
    Text="#000000",
    Line="#444444",
    BoxFill="#F4F4F4",
    ChildFill="#EAEAEA",
)

PaperTheme = Theme(
    Background="#FFFFFF",
    Primary="#000000",
    Accent="#000000",
    Text="#000000",
    Line="#000000",
    BoxFill="#FFFFFF",
    ChildFill="#FFFFFF",
    CornerRadius=0.0,
    EdgeWidth=2.0,
)

DraculaTheme = Theme(
    Background="#282A36",
    Primary="#BD93F9",
    Accent="#FF79C6",
    Text="#F8F8F2",
    Line="#6272A4",
    BoxFill="#1E1F29",
    ChildFill="#2A2C3B",
)
