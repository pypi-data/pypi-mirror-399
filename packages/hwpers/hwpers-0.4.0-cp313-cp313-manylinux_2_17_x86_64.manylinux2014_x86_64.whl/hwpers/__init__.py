"""
# hwpers

Python bindings for [hwpers](https://github.com/Indosaram/hwpers) - A Rust library for reading and writing Korean Hangul Word Processor (HWP) files.

## Installation

Install from PyPI:

```bash
pip install hwpers
```

### From source

For development or to get the latest version:

```bash
git clone https://github.com/Indosaram/hwpers-py
cd hwpers-py
pip install maturin
maturin develop
```

## Quick Start

### Reading HWP files

Load an HWP document and extract its contents. The `HwpDocument` class provides methods to access text, metadata, and document properties.

```python
import hwpers

# Read from file path
doc = hwpers.read_file("document.hwp")

# Extract all text content
text = doc.extract_text()
print(text)

# Access document metadata
print(f"Title: {doc.get_title()}")
print(f"Author: {doc.get_author()}")
print(f"Pages: {doc.get_page_count()}")
print(f"Characters: {doc.get_character_count()}")
print(f"Sections: {doc.section_count()}")
print(f"Compressed: {doc.is_compressed()}")

# You can also read from bytes (useful for web applications or streams)
with open("document.hwp", "rb") as f:
    doc = hwpers.read_bytes(f.read())
```

### Writing HWP files

Create new HWP documents using `HwpWriter`. Add content like paragraphs, headings, and lists, then save to a file.

```python
import hwpers

writer = hwpers.HwpWriter()

# Set document metadata (appears in file properties)
writer.set_title("My Document")
writer.set_author("Author Name")
writer.set_subject("Subject")
writer.set_keywords("keyword1, keyword2")

# Add content to the document
writer.add_heading("Chapter 1", 1)  # Level 1 heading
writer.add_paragraph("This is a paragraph.")
writer.add_bullet_list(["Item 1", "Item 2", "Item 3"])
writer.add_numbered_list(["First", "Second", "Third"])

# Save to file
writer.save("output.hwp")

# Or get document as bytes (useful for web responses)
data = writer.to_bytes()
```

## Text Styling

### Basic Styles

Use `TextStyle` to apply formatting like bold, italic, colors, and fonts. Methods can be chained for convenience.

```python
import hwpers

writer = hwpers.HwpWriter()

# Create a style with multiple formatting options
# Method chaining makes it easy to combine styles
style = (hwpers.TextStyle()
    .bold()                       # Bold text
    .italic()                     # Italic text
    .underline()                  # Underlined text
    .strikethrough()              # Strikethrough text
    .size(14)                     # Font size in points
    .color(0xFF0000)              # Text color (RGB hex: red)
    .background_color(0xFFFF00)   # Highlight color (RGB hex: yellow)
    .font_name("맑은 고딕"))       # Font family name

writer.add_paragraph_with_style("Styled text", style)
writer.save("styled.hwp")
```

### Mixed Styles in One Paragraph

Combine multiple styles within a single paragraph using `StyledText`. Each segment can have its own formatting.

```python
import hwpers

writer = hwpers.HwpWriter()

# Create text segments with different styles
texts = [
    hwpers.StyledText("Normal ", hwpers.TextStyle()),
    hwpers.StyledText("Bold ", hwpers.TextStyle().bold()),
    hwpers.StyledText("Red", hwpers.TextStyle().color(0xFF0000)),
]

# Add all segments as one paragraph
writer.add_styled_paragraph(texts)
writer.save("mixed_styles.hwp")
```

### Paragraph Alignment

Control text alignment within paragraphs. Options include left, center, right, justify, and distribute.

```python
import hwpers

writer = hwpers.HwpWriter()

# Different alignment options
writer.add_aligned_paragraph("Left aligned", hwpers.ParagraphAlignment.Left)
writer.add_aligned_paragraph("Center aligned", hwpers.ParagraphAlignment.Center)
writer.add_aligned_paragraph("Right aligned", hwpers.ParagraphAlignment.Right)
writer.add_aligned_paragraph("Justified text spreads across the line", hwpers.ParagraphAlignment.Justify)

writer.save("aligned.hwp")
```

## Tables

### Simple Table

Create tables from 2D lists. The first row is typically used as headers.

```python
import hwpers

writer = hwpers.HwpWriter()

# Create a table from a 2D list
# First row becomes the header
writer.add_table([
    ["Name", "Age", "City"],      # Header row
    ["Alice", "30", "Seoul"],     # Data rows
    ["Bob", "25", "Busan"],
])

writer.save("table.hwp")
```

### TableBuilder (Advanced)

For complex tables with cell merging and custom borders, use `TableBuilder`. It provides a fluent API for precise control.

```python
import hwpers

writer = hwpers.HwpWriter()

# Create a 4-row, 3-column table
tb = hwpers.TableBuilder(4, 3)

# Set the header row (row 0)
tb.set_header_row(["Column A", "Column B", "Column C"])

# Set individual cells (row, col, text)
# Method chaining allows setting multiple cells in one line
tb.set_cell(1, 0, "Row 1").set_cell(1, 1, "Data").set_cell(1, 2, "More")
tb.set_cell(2, 0, "Row 2").set_cell(2, 1, "Data").set_cell(2, 2, "More")
tb.set_cell(3, 0, "Row 3").set_cell(3, 1, "Data").set_cell(3, 2, "More")

# Merge cells horizontally: merge row 3, columns 0 through 1
tb.merge_cells(3, 0, 1)

# Apply border styles
tb.set_all_borders(hwpers.CellBorderStyle())  # Add borders to all cells
# Or remove all borders: tb.no_borders()

writer.add_table_with_builder(tb)
writer.save("advanced_table.hwp")
```

## Page Layout

### Paper Size and Orientation

Configure page dimensions and orientation. Use presets or custom sizes.

```python
import hwpers

writer = hwpers.HwpWriter()

# Quick presets for common layouts
writer.set_a4_portrait()       # A4 size, vertical
writer.set_a4_landscape()      # A4 size, horizontal
writer.set_letter_portrait()   # US Letter, vertical
writer.set_letter_landscape()  # US Letter, horizontal

# Using PageLayout for more control
layout = hwpers.PageLayout.a4_portrait()
writer.set_page_layout(layout)

# Set paper size and orientation separately
writer.set_paper_size(hwpers.PaperSize.A3)
writer.set_page_orientation(hwpers.PageOrientation.Landscape)

# Custom page size in millimeters (width, height)
writer.set_custom_page_size_mm(200.0, 300.0)

writer.save("layout.hwp")
```

### Margins

Set page margins using presets or custom values in millimeters/inches.

```python
import hwpers

writer = hwpers.HwpWriter()

# Margin presets
writer.set_normal_margins()  # Standard margins
writer.set_narrow_margins()  # Reduced margins for more content
writer.set_wide_margins()    # Larger margins for binding

# Custom margins in millimeters (top, bottom, left, right)
writer.set_page_margins_mm(25.0, 25.0, 30.0, 30.0)

# Custom margins in inches
writer.set_page_margins_inches(1.0, 1.0, 1.25, 1.25)

# Combine layout and margins
layout = hwpers.PageLayout.a4_portrait().with_margins(hwpers.PageMargins.narrow())
writer.set_page_layout(layout)

writer.save("margins.hwp")
```

## Hyperlinks

Add clickable links to URLs, email addresses, files, or bookmarks within the document.

```python
import hwpers

writer = hwpers.HwpWriter()

# Basic URL hyperlink (text, URL)
writer.add_hyperlink("Visit Google", "https://google.com")

# Email link - opens default email client
writer.add_email_link("Contact Us", "info@example.com")

# File link - opens local file
writer.add_file_link("Open Document", "/path/to/file.hwp")

# Bookmark link - jumps to a location within the document
writer.add_bookmark_link("Go to Section", "section1")

# Using Hyperlink class for more options
link = hwpers.Hyperlink.url("Visit Site", "https://example.com")
writer.add_hyperlink_with_options(link)

# Embed hyperlinks within paragraph text
# Useful when only part of the text should be clickable
text = "Visit our website for more information."
ranges = [
    # Link "website" (characters 10-17) to URL
    hwpers.TextRange(10, 17, "https://example.com"),
]
writer.add_paragraph_with_hyperlinks(text, ranges)

writer.save("links.hwp")
```

## Images

Insert images from files or bytes. Control size and alignment.

```python
import hwpers

writer = hwpers.HwpWriter()

# Simple image insertion (uses original size)
writer.add_image("photo.jpg")

# Image with custom size and alignment
options = hwpers.ImageOptions()
options.width = 200   # Width in pixels
options.height = 150  # Height in pixels
options.alignment = hwpers.ImageAlign.Center  # Left, Center, Right, InlineWithText
writer.add_image_with_options("photo.jpg", options)

# Insert image from bytes (useful for generated images or downloads)
with open("photo.png", "rb") as f:
    image_data = f.read()
    writer.add_image_from_bytes(image_data, hwpers.ImageFormat.Png)

writer.save("images.hwp")
```

## Text Boxes

Create positioned text boxes with optional borders and backgrounds.

```python
import hwpers

writer = hwpers.HwpWriter()

# Simple inline text box
writer.add_text_box("Text in a box")

# Positioned text box at specific coordinates
# Parameters: text, x, y, width, height (in HWP units)
# Use hwpers.mm_to_hwp_units() to convert from millimeters
writer.add_text_box_at_position("Positioned box", 1000, 2000, 5000, 3000)

# Text box with styled text inside
style = hwpers.TextStyle().bold().color(0x0000FF)
writer.add_styled_text_box("Blue bold text", style)

# Fully customized text box with border and background
box_style = hwpers.CustomTextBoxStyle(
    alignment=hwpers.TextBoxAlignment.Center,     # Text alignment inside box
    border_style=hwpers.TextBoxBorderStyle.Solid, # Border: None_, Solid, Dashed, Dotted, Double
    border_color=0x000000,                        # Border color (black)
    background_color=0xEEEEEE                     # Background color (light gray)
)
writer.add_custom_text_box("Custom box", 1000, 1000, 5000, 2000, box_style)

writer.save("textboxes.hwp")
```

## Headers, Footers, and Page Numbers

Add headers and footers that appear on every page (or specific pages).

```python
import hwpers

writer = hwpers.HwpWriter()

# Simple header and footer (appears on all pages, left-aligned)
writer.add_header("Document Title")
writer.add_footer("Page Footer")

# Header/footer with options
writer.add_header_with_options(
    "Header Text",
    hwpers.PageApplyType.All,            # All, FirstPage, OddPages, EvenPages
    hwpers.HeaderFooterAlignment.Center  # Left, Center, Right
)

writer.add_footer_with_options(
    "Footer Text",
    hwpers.PageApplyType.All,
    hwpers.HeaderFooterAlignment.Right
)

# Automatic page numbers in header or footer
writer.add_header_with_page_number()
writer.add_footer_with_page_number()

# Configure page numbering format
# Parameters: start_page, format
writer.set_page_numbering(1, hwpers.PageNumberFormat.Numeric)      # 1, 2, 3...
writer.set_page_numbering(1, hwpers.PageNumberFormat.RomanUpper)   # I, II, III...
writer.set_page_numbering(1, hwpers.PageNumberFormat.RomanLower)   # i, ii, iii...
writer.set_page_numbering(1, hwpers.PageNumberFormat.AlphaUpper)   # A, B, C...
writer.set_page_numbering(1, hwpers.PageNumberFormat.AlphaLower)   # a, b, c...

writer.save("headers_footers.hwp")
```

## Lists

Create bulleted, numbered, and nested lists.

```python
import hwpers

writer = hwpers.HwpWriter()

# Simple bullet list
writer.add_bullet_list(["Apple", "Banana", "Cherry"])

# Simple numbered list
writer.add_numbered_list(["First", "Second", "Third"])

# Lists with different styles
writer.add_list(["A", "B", "C"], hwpers.ListType.Alphabetic)  # A. B. C.
writer.add_list(["I", "II", "III"], hwpers.ListType.Roman)    # I. II. III.
writer.add_list(["가", "나", "다"], hwpers.ListType.Korean)   # Korean numbering

# Nested lists (lists within lists)
writer.start_list(hwpers.ListType.Numbered)
writer.add_list_item("Item 1")

# Start a nested bullet list inside the numbered list
writer.start_nested_list(hwpers.ListType.Bullet)
writer.add_list_item("Sub-item A")
writer.add_list_item("Sub-item B")
writer.end_list()  # End nested list

writer.add_list_item("Item 2")
writer.end_list()  # End outer list

writer.save("lists.hwp")
```

## Other Features

### Multi-column Layout

Create newspaper-style multi-column layouts.

```python
import hwpers

writer = hwpers.HwpWriter()

# Set 2-column layout
writer.set_columns(2)

# Add content - it will flow across columns
writer.add_paragraph("This text will appear in a two-column layout...")

writer.save("columns.hwp")
```

### Page Background Color

Set a background color for all pages.

```python
import hwpers

writer = hwpers.HwpWriter()

# Set page background color (RGB hex)
writer.set_page_background_color(0xFFFAF0)  # Light beige/cream color

writer.add_paragraph("Content on colored background")
writer.save("background.hwp")
```

### Update Statistics

Recalculate document statistics like page count and character count.

```python
import hwpers

writer = hwpers.HwpWriter()

# Add content...
writer.add_paragraph("Some content here")

# Update statistics before saving
# This ensures accurate page/character counts in document properties
writer.update_statistics()

writer.save("document.hwp")
```

## Unit Conversions

HWP files use internal units for measurements. Use these functions to convert between common units and HWP units.

- 1 inch = 7200 HWP units
- 1 mm = 283.465 HWP units

```python
import hwpers

# Convert millimeters to HWP units
hwp_units = hwpers.mm_to_hwp_units(10.0)  # Returns ~2835

# Convert HWP units back to millimeters
mm = hwpers.hwp_units_to_mm(2835)  # Returns ~10.0

# Convert inches to HWP units
hwp_units = hwpers.inches_to_hwp_units(1.0)  # Returns 7200

# Convert HWP units back to inches
inches = hwpers.hwp_units_to_inches(7200)  # Returns 1.0

# Example: Create a text box with size in millimeters
x = hwpers.mm_to_hwp_units(20)       # 20mm from left
y = hwpers.mm_to_hwp_units(30)       # 30mm from top
width = hwpers.mm_to_hwp_units(50)   # 50mm wide
height = hwpers.mm_to_hwp_units(25)  # 25mm tall

writer = hwpers.HwpWriter()
writer.add_text_box_at_position("Positioned in mm", x, y, width, height)
writer.save("units_example.hwp")
```
"""

from .hwpers_py import (
    # Document classes
    HwpDocument,
    HwpWriter,

    # Style enums
    TextAlign,
    ParagraphAlignment,
    ListType,
    BorderLineType,
    ImageFormat,
    ImageAlign,
    PageOrientation,
    PaperSize,
    PageNumberFormat,
    HyperlinkType,
    HyperlinkDisplay,
    PageApplyType,
    HeaderFooterAlignment,
    TextBoxAlignment,
    TextBoxBorderStyle,
    CellAlign,

    # Style classes
    TextStyle,
    BorderLineStyle,
    CellBorderStyle,
    ImageOptions,
    StyledText,
    HyperlinkStyle,
    Hyperlink,
    FloatingTextBoxStyle,
    CustomTextBoxStyle,
    PageMargins,
    PageLayout,
    HeadingStyle,
    ListStyle,
    TableStyle,
    TextRange,

    # TableBuilder
    TableBuilder,

    # Render classes
    RenderOptions,
    RenderedPage,
    RenderResult,

    # Functions
    read_file,
    read_bytes,

    # Unit conversion functions
    mm_to_hwp_units,
    inches_to_hwp_units,
    hwp_units_to_mm,
    hwp_units_to_inches,
)

__version__ = "0.4.0"
__all__ = [
    # Document classes
    "HwpDocument",
    "HwpWriter",

    # Style enums
    "TextAlign",
    "ParagraphAlignment",
    "ListType",
    "BorderLineType",
    "ImageFormat",
    "ImageAlign",
    "PageOrientation",
    "PaperSize",
    "PageNumberFormat",
    "HyperlinkType",
    "HyperlinkDisplay",
    "PageApplyType",
    "HeaderFooterAlignment",
    "TextBoxAlignment",
    "TextBoxBorderStyle",
    "CellAlign",

    # Style classes
    "TextStyle",
    "BorderLineStyle",
    "CellBorderStyle",
    "ImageOptions",
    "StyledText",
    "HyperlinkStyle",
    "Hyperlink",
    "FloatingTextBoxStyle",
    "CustomTextBoxStyle",
    "PageMargins",
    "PageLayout",
    "HeadingStyle",
    "ListStyle",
    "TableStyle",
    "TextRange",

    # TableBuilder
    "TableBuilder",

    # Render classes
    "RenderOptions",
    "RenderedPage",
    "RenderResult",

    # Functions
    "read_file",
    "read_bytes",

    # Unit conversion functions
    "mm_to_hwp_units",
    "inches_to_hwp_units",
    "hwp_units_to_mm",
    "hwp_units_to_inches",
]
