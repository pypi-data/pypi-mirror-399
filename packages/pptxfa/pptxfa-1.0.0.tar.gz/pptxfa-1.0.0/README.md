# pptxfa

pptxfa is a Python library for creating .pptx files with Persian/Arabic RTL (Right-to-Left) support. This library allows you to create PowerPoint presentations from scratch with full support for RTL (Persian/Arabic) and LTR (English) text, including mixed content.

## Features

- Create PowerPoint presentations from scratch
- Full RTL (Right-to-Left) support for Persian/Arabic text
- Support for mixed RTL/LTR content
- Customizable text properties (font, size, color, alignment)
- Support for different slide layouts

## Installation

```bash
pip install pptxfa
```

## Usage

```python
from pptxfa import PptxEditor

# Create a new presentation
editor = PptxEditor()
editor.create_presentation()

# Add a title slide
title_props = {
    'font_name': 'Vazirmatn',
    'font_size': 24,
    'bold': True,
    'rtl': True
}
subtitle_props = {
    'font_name': 'Vazirmatn',
    'font_size': 18,
    'rtl': True
}
editor.add_title_slide(
    title="عنوان ارائه",
    subtitle="زیرعنوان ارائه",
    title_properties=title_props,
    subtitle_properties=subtitle_props
)

# Add a content slide
content_props = {
    'font_name': 'Vazirmatn',
    'font_size': 16,
    'rtl': True
}
editor.add_content_slide(
    title="اسلاید محتوا",
    content="متن محتوای اسلاید",
    title_properties=title_props,
    content_properties=content_props
)

# Save the presentation
editor.save("presentation.pptx")
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.