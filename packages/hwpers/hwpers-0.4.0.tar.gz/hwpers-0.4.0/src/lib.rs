use pyo3::exceptions::PyIOError;
use pyo3::prelude::*;
use pyo3::types::PyBytes;
use std::path::PathBuf;

// ============================================================================
// Enums
// ============================================================================

/// Text alignment options
#[pyclass(name = "TextAlign", eq)]
#[derive(Clone, PartialEq)]
pub enum PyTextAlign {
    Left,
    Center,
    Right,
    Justify,
    Distribute,
}

/// Paragraph alignment options
#[pyclass(name = "ParagraphAlignment", eq)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyParagraphAlignment {
    Left,
    Right,
    Center,
    Justify,
    Distribute,
}

impl From<PyParagraphAlignment> for hwpers::style::ParagraphAlignment {
    fn from(val: PyParagraphAlignment) -> Self {
        match val {
            PyParagraphAlignment::Left => hwpers::style::ParagraphAlignment::Left,
            PyParagraphAlignment::Right => hwpers::style::ParagraphAlignment::Right,
            PyParagraphAlignment::Center => hwpers::style::ParagraphAlignment::Center,
            PyParagraphAlignment::Justify => hwpers::style::ParagraphAlignment::Justify,
            PyParagraphAlignment::Distribute => hwpers::style::ParagraphAlignment::Distribute,
        }
    }
}

/// List type options
#[pyclass(name = "ListType", eq)]
#[derive(Clone, PartialEq)]
pub enum PyListType {
    Bullet,
    Numbered,
    Alphabetic,
    Roman,
    Korean,
}

impl From<PyListType> for hwpers::style::ListType {
    fn from(val: PyListType) -> Self {
        match val {
            PyListType::Bullet => hwpers::style::ListType::Bullet,
            PyListType::Numbered => hwpers::style::ListType::Numbered,
            PyListType::Alphabetic => hwpers::style::ListType::Alphabetic,
            PyListType::Roman => hwpers::style::ListType::Roman,
            PyListType::Korean => hwpers::style::ListType::Korean,
        }
    }
}

/// Border line type options
#[pyclass(name = "BorderLineType", eq)]
#[derive(Clone, PartialEq)]
pub enum PyBorderLineType {
    None,
    Solid,
    Dashed,
    Dotted,
    Double,
    Thick,
}

impl From<PyBorderLineType> for hwpers::style::BorderLineType {
    fn from(val: PyBorderLineType) -> Self {
        match val {
            PyBorderLineType::None => hwpers::style::BorderLineType::None,
            PyBorderLineType::Solid => hwpers::style::BorderLineType::Solid,
            PyBorderLineType::Dashed => hwpers::style::BorderLineType::Dashed,
            PyBorderLineType::Dotted => hwpers::style::BorderLineType::Dotted,
            PyBorderLineType::Double => hwpers::style::BorderLineType::Double,
            PyBorderLineType::Thick => hwpers::style::BorderLineType::Thick,
        }
    }
}

/// Image format types
#[pyclass(name = "ImageFormat", eq)]
#[derive(Clone, PartialEq)]
pub enum PyImageFormat {
    Jpeg,
    Png,
    Bmp,
    Gif,
}

impl From<PyImageFormat> for hwpers::style::ImageFormat {
    fn from(val: PyImageFormat) -> Self {
        match val {
            PyImageFormat::Jpeg => hwpers::style::ImageFormat::Jpeg,
            PyImageFormat::Png => hwpers::style::ImageFormat::Png,
            PyImageFormat::Bmp => hwpers::style::ImageFormat::Bmp,
            PyImageFormat::Gif => hwpers::style::ImageFormat::Gif,
        }
    }
}

/// Image alignment options
#[pyclass(name = "ImageAlign", eq)]
#[derive(Clone, PartialEq)]
pub enum PyImageAlign {
    Left,
    Center,
    Right,
    InlineWithText,
}

impl From<PyImageAlign> for hwpers::style::ImageAlign {
    fn from(val: PyImageAlign) -> Self {
        match val {
            PyImageAlign::Left => hwpers::style::ImageAlign::Left,
            PyImageAlign::Center => hwpers::style::ImageAlign::Center,
            PyImageAlign::Right => hwpers::style::ImageAlign::Right,
            PyImageAlign::InlineWithText => hwpers::style::ImageAlign::InlineWithText,
        }
    }
}

/// Page orientation
#[pyclass(name = "PageOrientation", eq)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyPageOrientation {
    Portrait,
    Landscape,
}

impl From<PyPageOrientation> for hwpers::model::page_layout::PageOrientation {
    fn from(val: PyPageOrientation) -> Self {
        match val {
            PyPageOrientation::Portrait => hwpers::model::page_layout::PageOrientation::Portrait,
            PyPageOrientation::Landscape => hwpers::model::page_layout::PageOrientation::Landscape,
        }
    }
}

impl From<hwpers::model::page_layout::PageOrientation> for PyPageOrientation {
    fn from(val: hwpers::model::page_layout::PageOrientation) -> Self {
        match val {
            hwpers::model::page_layout::PageOrientation::Portrait => PyPageOrientation::Portrait,
            hwpers::model::page_layout::PageOrientation::Landscape => PyPageOrientation::Landscape,
        }
    }
}

/// Paper size options
#[pyclass(name = "PaperSize", eq)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyPaperSize {
    A4,
    A3,
    A5,
    Letter,
    Legal,
    Tabloid,
    B4,
    B5,
    Custom,
}

impl From<PyPaperSize> for hwpers::model::page_layout::PaperSize {
    fn from(val: PyPaperSize) -> Self {
        match val {
            PyPaperSize::A4 => hwpers::model::page_layout::PaperSize::A4,
            PyPaperSize::A3 => hwpers::model::page_layout::PaperSize::A3,
            PyPaperSize::A5 => hwpers::model::page_layout::PaperSize::A5,
            PyPaperSize::Letter => hwpers::model::page_layout::PaperSize::Letter,
            PyPaperSize::Legal => hwpers::model::page_layout::PaperSize::Legal,
            PyPaperSize::Tabloid => hwpers::model::page_layout::PaperSize::Tabloid,
            PyPaperSize::B4 => hwpers::model::page_layout::PaperSize::B4,
            PyPaperSize::B5 => hwpers::model::page_layout::PaperSize::B5,
            PyPaperSize::Custom => hwpers::model::page_layout::PaperSize::Custom,
        }
    }
}

impl From<hwpers::model::page_layout::PaperSize> for PyPaperSize {
    fn from(val: hwpers::model::page_layout::PaperSize) -> Self {
        match val {
            hwpers::model::page_layout::PaperSize::A4 => PyPaperSize::A4,
            hwpers::model::page_layout::PaperSize::A3 => PyPaperSize::A3,
            hwpers::model::page_layout::PaperSize::A5 => PyPaperSize::A5,
            hwpers::model::page_layout::PaperSize::Letter => PyPaperSize::Letter,
            hwpers::model::page_layout::PaperSize::Legal => PyPaperSize::Legal,
            hwpers::model::page_layout::PaperSize::Tabloid => PyPaperSize::Tabloid,
            hwpers::model::page_layout::PaperSize::B4 => PyPaperSize::B4,
            hwpers::model::page_layout::PaperSize::B5 => PyPaperSize::B5,
            hwpers::model::page_layout::PaperSize::Custom => PyPaperSize::Custom,
        }
    }
}

/// Page number format
#[pyclass(name = "PageNumberFormat", eq)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyPageNumberFormat {
    Numeric,
    RomanLower,
    RomanUpper,
    AlphaLower,
    AlphaUpper,
}

impl From<PyPageNumberFormat> for hwpers::model::header_footer::PageNumberFormat {
    fn from(val: PyPageNumberFormat) -> Self {
        match val {
            PyPageNumberFormat::Numeric => hwpers::model::header_footer::PageNumberFormat::Numeric,
            PyPageNumberFormat::RomanLower => {
                hwpers::model::header_footer::PageNumberFormat::RomanLower
            }
            PyPageNumberFormat::RomanUpper => {
                hwpers::model::header_footer::PageNumberFormat::RomanUpper
            }
            PyPageNumberFormat::AlphaLower => {
                hwpers::model::header_footer::PageNumberFormat::AlphaLower
            }
            PyPageNumberFormat::AlphaUpper => {
                hwpers::model::header_footer::PageNumberFormat::AlphaUpper
            }
        }
    }
}

/// Hyperlink type
#[pyclass(name = "HyperlinkType", eq)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyHyperlinkType {
    Url,
    Email,
    File,
    Bookmark,
    ExternalBookmark,
}

impl From<PyHyperlinkType> for hwpers::model::HyperlinkType {
    fn from(val: PyHyperlinkType) -> Self {
        match val {
            PyHyperlinkType::Url => hwpers::model::HyperlinkType::Url,
            PyHyperlinkType::Email => hwpers::model::HyperlinkType::Email,
            PyHyperlinkType::File => hwpers::model::HyperlinkType::File,
            PyHyperlinkType::Bookmark => hwpers::model::HyperlinkType::Bookmark,
            PyHyperlinkType::ExternalBookmark => hwpers::model::HyperlinkType::ExternalBookmark,
        }
    }
}

/// Hyperlink display mode
#[pyclass(name = "HyperlinkDisplay", eq)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyHyperlinkDisplay {
    TextOnly,
    UrlOnly,
    Both,
}

impl From<PyHyperlinkDisplay> for hwpers::model::HyperlinkDisplay {
    fn from(val: PyHyperlinkDisplay) -> Self {
        match val {
            PyHyperlinkDisplay::TextOnly => hwpers::model::HyperlinkDisplay::TextOnly,
            PyHyperlinkDisplay::UrlOnly => hwpers::model::HyperlinkDisplay::UrlOnly,
            PyHyperlinkDisplay::Both => hwpers::model::HyperlinkDisplay::Both,
        }
    }
}

/// Page apply type for headers/footers
#[pyclass(name = "PageApplyType", eq)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyPageApplyType {
    All,
    FirstPage,
    EvenPages,
    OddPages,
}

impl From<PyPageApplyType> for hwpers::model::header_footer::PageApplyType {
    fn from(val: PyPageApplyType) -> Self {
        match val {
            PyPageApplyType::All => hwpers::model::header_footer::PageApplyType::All,
            PyPageApplyType::FirstPage => hwpers::model::header_footer::PageApplyType::FirstPage,
            PyPageApplyType::EvenPages => hwpers::model::header_footer::PageApplyType::EvenPages,
            PyPageApplyType::OddPages => hwpers::model::header_footer::PageApplyType::OddPages,
        }
    }
}

/// Header/Footer alignment
#[pyclass(name = "HeaderFooterAlignment", eq)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyHeaderFooterAlignment {
    Left,
    Center,
    Right,
}

impl From<PyHeaderFooterAlignment> for hwpers::model::header_footer::HeaderFooterAlignment {
    fn from(val: PyHeaderFooterAlignment) -> Self {
        match val {
            PyHeaderFooterAlignment::Left => {
                hwpers::model::header_footer::HeaderFooterAlignment::Left
            }
            PyHeaderFooterAlignment::Center => {
                hwpers::model::header_footer::HeaderFooterAlignment::Center
            }
            PyHeaderFooterAlignment::Right => {
                hwpers::model::header_footer::HeaderFooterAlignment::Right
            }
        }
    }
}

/// Text box alignment
#[pyclass(name = "TextBoxAlignment", eq)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyTextBoxAlignment {
    Inline,
    Left,
    Center,
    Right,
    Absolute,
}

impl From<PyTextBoxAlignment> for hwpers::model::TextBoxAlignment {
    fn from(val: PyTextBoxAlignment) -> Self {
        match val {
            PyTextBoxAlignment::Inline => hwpers::model::TextBoxAlignment::Inline,
            PyTextBoxAlignment::Left => hwpers::model::TextBoxAlignment::Left,
            PyTextBoxAlignment::Center => hwpers::model::TextBoxAlignment::Center,
            PyTextBoxAlignment::Right => hwpers::model::TextBoxAlignment::Right,
            PyTextBoxAlignment::Absolute => hwpers::model::TextBoxAlignment::Absolute,
        }
    }
}

/// Text box border style
#[pyclass(name = "TextBoxBorderStyle", eq)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyTextBoxBorderStyle {
    None,
    Solid,
    Dotted,
    Dashed,
    Double,
}

impl From<PyTextBoxBorderStyle> for hwpers::model::TextBoxBorderStyle {
    fn from(val: PyTextBoxBorderStyle) -> Self {
        match val {
            PyTextBoxBorderStyle::None => hwpers::model::TextBoxBorderStyle::None,
            PyTextBoxBorderStyle::Solid => hwpers::model::TextBoxBorderStyle::Solid,
            PyTextBoxBorderStyle::Dotted => hwpers::model::TextBoxBorderStyle::Dotted,
            PyTextBoxBorderStyle::Dashed => hwpers::model::TextBoxBorderStyle::Dashed,
            PyTextBoxBorderStyle::Double => hwpers::model::TextBoxBorderStyle::Double,
        }
    }
}

/// Cell alignment options
#[pyclass(name = "CellAlign", eq)]
#[derive(Clone, Copy, PartialEq)]
pub enum PyCellAlign {
    Left,
    Center,
    Right,
}

impl From<PyCellAlign> for hwpers::style::CellAlign {
    fn from(val: PyCellAlign) -> Self {
        match val {
            PyCellAlign::Left => hwpers::style::CellAlign::Left,
            PyCellAlign::Center => hwpers::style::CellAlign::Center,
            PyCellAlign::Right => hwpers::style::CellAlign::Right,
        }
    }
}

// ============================================================================
// Style Classes
// ============================================================================

/// Text style configuration
#[pyclass(name = "TextStyle")]
#[derive(Clone)]
pub struct PyTextStyle {
    inner: hwpers::style::TextStyle,
}

#[pymethods]
impl PyTextStyle {
    #[new]
    fn new() -> Self {
        PyTextStyle {
            inner: hwpers::style::TextStyle::new(),
        }
    }

    fn font(&self, font_name: &str) -> Self {
        PyTextStyle {
            inner: self.inner.clone().font(font_name),
        }
    }

    fn size(&self, size_pt: u32) -> Self {
        PyTextStyle {
            inner: self.inner.clone().size(size_pt),
        }
    }

    fn bold(&self) -> Self {
        PyTextStyle {
            inner: self.inner.clone().bold(),
        }
    }

    fn italic(&self) -> Self {
        PyTextStyle {
            inner: self.inner.clone().italic(),
        }
    }

    fn underline(&self) -> Self {
        PyTextStyle {
            inner: self.inner.clone().underline(),
        }
    }

    fn strikethrough(&self) -> Self {
        PyTextStyle {
            inner: self.inner.clone().strikethrough(),
        }
    }

    fn color(&self, color: u32) -> Self {
        PyTextStyle {
            inner: self.inner.clone().color(color),
        }
    }

    fn background(&self, color: u32) -> Self {
        PyTextStyle {
            inner: self.inner.clone().background(color),
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "TextStyle(bold={}, italic={}, underline={})",
            self.inner.bold, self.inner.italic, self.inner.underline
        )
    }
}

/// Border line style
#[pyclass(name = "BorderLineStyle")]
#[derive(Clone)]
pub struct PyBorderLineStyle {
    inner: hwpers::style::BorderLineStyle,
}

#[pymethods]
impl PyBorderLineStyle {
    #[new]
    #[pyo3(signature = (line_type=None, thickness=None, color=None))]
    fn new(line_type: Option<PyBorderLineType>, thickness: Option<u8>, color: Option<u32>) -> Self {
        let lt = line_type
            .map(|t| t.into())
            .unwrap_or(hwpers::style::BorderLineType::Solid);
        PyBorderLineStyle {
            inner: hwpers::style::BorderLineStyle::new(
                lt,
                thickness.unwrap_or(1),
                color.unwrap_or(0x000000),
            ),
        }
    }

    #[staticmethod]
    fn none() -> Self {
        PyBorderLineStyle {
            inner: hwpers::style::BorderLineStyle::none(),
        }
    }

    #[staticmethod]
    fn solid(thickness: u8) -> Self {
        PyBorderLineStyle {
            inner: hwpers::style::BorderLineStyle::solid(thickness),
        }
    }

    #[staticmethod]
    fn dashed(thickness: u8) -> Self {
        PyBorderLineStyle {
            inner: hwpers::style::BorderLineStyle::dashed(thickness),
        }
    }

    fn with_color(&self, color: u32) -> Self {
        PyBorderLineStyle {
            inner: self.inner.clone().with_color(color),
        }
    }
}

/// Cell border style
#[pyclass(name = "CellBorderStyle")]
#[derive(Clone)]
pub struct PyCellBorderStyle {
    inner: hwpers::style::CellBorderStyle,
}

#[pymethods]
impl PyCellBorderStyle {
    #[new]
    fn new() -> Self {
        PyCellBorderStyle {
            inner: hwpers::style::CellBorderStyle::new(),
        }
    }

    #[staticmethod]
    fn all_borders(style: PyBorderLineStyle) -> Self {
        PyCellBorderStyle {
            inner: hwpers::style::CellBorderStyle::all_borders(style.inner),
        }
    }

    #[staticmethod]
    fn no_borders() -> Self {
        PyCellBorderStyle {
            inner: hwpers::style::CellBorderStyle::no_borders(),
        }
    }

    #[staticmethod]
    fn outer_borders() -> Self {
        PyCellBorderStyle {
            inner: hwpers::style::CellBorderStyle::outer_borders(),
        }
    }

    fn set_left(&self, style: PyBorderLineStyle) -> Self {
        PyCellBorderStyle {
            inner: self.inner.clone().set_left(style.inner),
        }
    }

    fn set_right(&self, style: PyBorderLineStyle) -> Self {
        PyCellBorderStyle {
            inner: self.inner.clone().set_right(style.inner),
        }
    }

    fn set_top(&self, style: PyBorderLineStyle) -> Self {
        PyCellBorderStyle {
            inner: self.inner.clone().set_top(style.inner),
        }
    }

    fn set_bottom(&self, style: PyBorderLineStyle) -> Self {
        PyCellBorderStyle {
            inner: self.inner.clone().set_bottom(style.inner),
        }
    }
}

/// Image options
#[pyclass(name = "ImageOptions")]
#[derive(Clone)]
pub struct PyImageOptions {
    inner: hwpers::style::ImageOptions,
}

#[pymethods]
impl PyImageOptions {
    #[new]
    fn new() -> Self {
        PyImageOptions {
            inner: hwpers::style::ImageOptions::new(),
        }
    }

    fn width(&self, width_mm: u32) -> Self {
        PyImageOptions {
            inner: self.inner.clone().width(width_mm),
        }
    }

    fn height(&self, height_mm: u32) -> Self {
        PyImageOptions {
            inner: self.inner.clone().height(height_mm),
        }
    }

    fn align(&self, alignment: PyImageAlign) -> Self {
        PyImageOptions {
            inner: self.inner.clone().align(alignment.into()),
        }
    }

    fn wrap_text(&self, wrap: bool) -> Self {
        PyImageOptions {
            inner: self.inner.clone().wrap_text(wrap),
        }
    }

    fn caption(&self, text: &str) -> Self {
        PyImageOptions {
            inner: self.inner.clone().caption(text),
        }
    }
}

/// Styled text helper
#[pyclass(name = "StyledText")]
#[derive(Clone)]
pub struct PyStyledText {
    inner: hwpers::style::StyledText,
}

#[pymethods]
impl PyStyledText {
    #[new]
    fn new(text: String) -> Self {
        PyStyledText {
            inner: hwpers::style::StyledText::new(text),
        }
    }

    fn add_range(&self, start: usize, end: usize, style: PyTextStyle) -> Self {
        PyStyledText {
            inner: self.inner.clone().add_range(start, end, style.inner),
        }
    }

    fn style_substring(&self, substring: &str, style: PyTextStyle) -> Self {
        PyStyledText {
            inner: self.inner.clone().style_substring(substring, style.inner),
        }
    }

    fn style_all_occurrences(&self, substring: &str, style: PyTextStyle) -> Self {
        PyStyledText {
            inner: self
                .inner
                .clone()
                .style_all_occurrences(substring, style.inner),
        }
    }

    #[getter]
    fn text(&self) -> String {
        self.inner.text.clone()
    }
}

/// Hyperlink style options
#[pyclass(name = "HyperlinkStyle")]
#[derive(Clone)]
pub struct PyHyperlinkStyle {
    pub text_color: u32,
    pub underline: bool,
    pub new_window: bool,
}

#[pymethods]
impl PyHyperlinkStyle {
    #[new]
    #[pyo3(signature = (text_color=0x0000FF, underline=true, new_window=false))]
    fn new(text_color: u32, underline: bool, new_window: bool) -> Self {
        PyHyperlinkStyle {
            text_color,
            underline,
            new_window,
        }
    }

    #[getter]
    fn text_color(&self) -> u32 {
        self.text_color
    }

    #[getter]
    fn underline(&self) -> bool {
        self.underline
    }

    #[getter]
    fn new_window(&self) -> bool {
        self.new_window
    }
}

impl From<&PyHyperlinkStyle> for hwpers::writer::HyperlinkStyleOptions {
    fn from(val: &PyHyperlinkStyle) -> Self {
        hwpers::writer::HyperlinkStyleOptions {
            text_color: val.text_color,
            underline: val.underline,
            new_window: val.new_window,
        }
    }
}

/// Hyperlink object
#[pyclass(name = "Hyperlink")]
#[derive(Clone)]
pub struct PyHyperlink {
    inner: hwpers::model::Hyperlink,
}

#[pymethods]
impl PyHyperlink {
    #[new]
    #[allow(clippy::too_many_arguments)]
    #[pyo3(signature = (display_text, target_url, hyperlink_type=None, tooltip=None, display_mode=None, text_color=None, underline=None, new_window=None))]
    fn new(
        display_text: String,
        target_url: String,
        hyperlink_type: Option<PyHyperlinkType>,
        tooltip: Option<String>,
        display_mode: Option<PyHyperlinkDisplay>,
        text_color: Option<u32>,
        underline: Option<bool>,
        new_window: Option<bool>,
    ) -> Self {
        let default = hwpers::model::Hyperlink::default();
        let hl = hwpers::model::Hyperlink {
            display_text,
            target_url,
            hyperlink_type: hyperlink_type
                .map(|ht| ht.into())
                .unwrap_or(default.hyperlink_type),
            tooltip,
            display_mode: display_mode
                .map(|dm| dm.into())
                .unwrap_or(default.display_mode),
            text_color: text_color.unwrap_or(default.text_color),
            underline: underline.unwrap_or(default.underline),
            open_in_new_window: new_window.unwrap_or(default.open_in_new_window),
            ..default
        };
        PyHyperlink { inner: hl }
    }

    #[staticmethod]
    fn url(display_text: &str, url: &str) -> Self {
        let default = hwpers::model::Hyperlink::default();
        let hl = hwpers::model::Hyperlink {
            display_text: display_text.to_string(),
            target_url: url.to_string(),
            hyperlink_type: hwpers::model::HyperlinkType::Url,
            ..default
        };
        PyHyperlink { inner: hl }
    }

    #[staticmethod]
    fn email(display_text: &str, email: &str) -> Self {
        let default = hwpers::model::Hyperlink::default();
        let hl = hwpers::model::Hyperlink {
            display_text: display_text.to_string(),
            target_url: format!("mailto:{}", email),
            hyperlink_type: hwpers::model::HyperlinkType::Email,
            ..default
        };
        PyHyperlink { inner: hl }
    }

    fn with_position(&self, start: u32, length: u32) -> Self {
        let mut hl = self.inner.clone();
        hl.start_position = start;
        hl.length = length;
        PyHyperlink { inner: hl }
    }
}

/// Floating text box style
#[pyclass(name = "FloatingTextBoxStyle")]
#[derive(Clone)]
pub struct PyFloatingTextBoxStyle {
    pub opacity: u8,
    pub rotation: i16,
}

#[pymethods]
impl PyFloatingTextBoxStyle {
    #[new]
    #[pyo3(signature = (opacity=255, rotation=0))]
    fn new(opacity: u8, rotation: i16) -> Self {
        PyFloatingTextBoxStyle { opacity, rotation }
    }

    #[getter]
    fn opacity(&self) -> u8 {
        self.opacity
    }

    #[getter]
    fn rotation(&self) -> i16 {
        self.rotation
    }
}

impl From<&PyFloatingTextBoxStyle> for hwpers::writer::FloatingTextBoxStyle {
    fn from(val: &PyFloatingTextBoxStyle) -> Self {
        hwpers::writer::FloatingTextBoxStyle {
            opacity: val.opacity,
            rotation: val.rotation,
        }
    }
}

/// Custom text box style
#[pyclass(name = "CustomTextBoxStyle")]
#[derive(Clone)]
pub struct PyCustomTextBoxStyle {
    pub alignment: PyTextBoxAlignment,
    pub border_style: PyTextBoxBorderStyle,
    pub border_color: u32,
    pub background_color: u32,
}

#[pymethods]
impl PyCustomTextBoxStyle {
    #[new]
    #[pyo3(signature = (alignment=PyTextBoxAlignment::Inline, border_style=PyTextBoxBorderStyle::Solid, border_color=0x000000, background_color=0xFFFFFF))]
    fn new(
        alignment: PyTextBoxAlignment,
        border_style: PyTextBoxBorderStyle,
        border_color: u32,
        background_color: u32,
    ) -> Self {
        PyCustomTextBoxStyle {
            alignment,
            border_style,
            border_color,
            background_color,
        }
    }

    #[getter]
    fn alignment(&self) -> PyTextBoxAlignment {
        self.alignment
    }

    #[getter]
    fn border_style(&self) -> PyTextBoxBorderStyle {
        self.border_style
    }

    #[getter]
    fn border_color(&self) -> u32 {
        self.border_color
    }

    #[getter]
    fn background_color(&self) -> u32 {
        self.background_color
    }
}

impl From<&PyCustomTextBoxStyle> for hwpers::writer::CustomTextBoxStyle {
    fn from(val: &PyCustomTextBoxStyle) -> Self {
        hwpers::writer::CustomTextBoxStyle {
            alignment: val.alignment.into(),
            border_style: val.border_style.into(),
            border_color: val.border_color,
            background_color: val.background_color,
        }
    }
}

/// Heading style
#[pyclass(name = "HeadingStyle")]
#[derive(Clone)]
pub struct PyHeadingStyle {
    inner: hwpers::style::HeadingStyle,
}

#[pymethods]
impl PyHeadingStyle {
    #[staticmethod]
    fn for_level(level: u8) -> Self {
        PyHeadingStyle {
            inner: hwpers::style::HeadingStyle::for_level(level),
        }
    }

    #[getter]
    fn numbering(&self) -> bool {
        self.inner.numbering
    }

    #[getter]
    fn spacing_before(&self) -> i32 {
        self.inner.spacing_before
    }

    #[getter]
    fn spacing_after(&self) -> i32 {
        self.inner.spacing_after
    }

    #[getter]
    fn font_size(&self) -> Option<u32> {
        self.inner.text_style.font_size
    }

    #[getter]
    fn bold(&self) -> bool {
        self.inner.text_style.bold
    }
}

/// List style
#[pyclass(name = "ListStyle")]
#[derive(Clone)]
pub struct PyListStyle {
    inner: hwpers::style::ListStyle,
}

#[pymethods]
impl PyListStyle {
    #[new]
    #[pyo3(signature = (list_type=PyListType::Bullet, indent=None, spacing=None))]
    fn new(list_type: PyListType, indent: Option<i32>, spacing: Option<i32>) -> Self {
        let default = hwpers::style::ListStyle::default();
        let style = hwpers::style::ListStyle {
            list_type: list_type.into(),
            indent: indent.unwrap_or(default.indent),
            spacing: spacing.unwrap_or(default.spacing),
            ..default
        };
        PyListStyle { inner: style }
    }

    #[getter]
    fn indent(&self) -> i32 {
        self.inner.indent
    }

    #[getter]
    fn spacing(&self) -> i32 {
        self.inner.spacing
    }
}

/// Table style
#[pyclass(name = "TableStyle")]
#[derive(Clone)]
pub struct PyTableStyle {
    inner: hwpers::style::TableStyle,
}

#[pymethods]
impl PyTableStyle {
    #[new]
    fn new() -> Self {
        PyTableStyle {
            inner: hwpers::style::TableStyle::default(),
        }
    }

    #[getter]
    fn border_width(&self) -> u8 {
        self.inner.border_width
    }

    #[getter]
    fn border_color(&self) -> u32 {
        self.inner.border_color
    }

    #[getter]
    fn background_color(&self) -> Option<u32> {
        self.inner.background_color
    }

    #[getter]
    fn padding(&self) -> i32 {
        self.inner.padding
    }
}

/// Text range for styled text
#[pyclass(name = "TextRange")]
#[derive(Clone)]
pub struct PyTextRange {
    inner: hwpers::style::TextRange,
}

#[pymethods]
impl PyTextRange {
    #[new]
    fn new(start: usize, end: usize, style: PyTextStyle) -> Self {
        PyTextRange {
            inner: hwpers::style::TextRange::new(start, end, style.inner),
        }
    }

    #[staticmethod]
    fn entire_text(text_len: usize, style: PyTextStyle) -> Self {
        PyTextRange {
            inner: hwpers::style::TextRange::entire_text(text_len, style.inner),
        }
    }

    #[getter]
    fn start(&self) -> usize {
        self.inner.start
    }

    #[getter]
    fn end(&self) -> usize {
        self.inner.end
    }
}

/// Page margins
#[pyclass(name = "PageMargins")]
#[derive(Clone)]
pub struct PyPageMargins {
    inner: hwpers::model::page_layout::PageMargins,
}

#[pymethods]
impl PyPageMargins {
    #[new]
    fn new() -> Self {
        PyPageMargins {
            inner: hwpers::model::page_layout::PageMargins::default(),
        }
    }

    #[staticmethod]
    fn new_mm(left: f32, right: f32, top: f32, bottom: f32) -> Self {
        PyPageMargins {
            inner: hwpers::model::page_layout::PageMargins::new_mm(left, right, top, bottom),
        }
    }

    #[staticmethod]
    fn new_inches(left: f32, right: f32, top: f32, bottom: f32) -> Self {
        PyPageMargins {
            inner: hwpers::model::page_layout::PageMargins::new_inches(left, right, top, bottom),
        }
    }

    #[staticmethod]
    fn narrow() -> Self {
        PyPageMargins {
            inner: hwpers::model::page_layout::PageMargins::narrow(),
        }
    }

    #[staticmethod]
    fn normal() -> Self {
        PyPageMargins {
            inner: hwpers::model::page_layout::PageMargins::normal(),
        }
    }

    #[staticmethod]
    fn wide() -> Self {
        PyPageMargins {
            inner: hwpers::model::page_layout::PageMargins::wide(),
        }
    }

    fn with_header_footer_mm(&self, header: f32, footer: f32) -> Self {
        PyPageMargins {
            inner: self.inner.clone().with_header_footer_mm(header, footer),
        }
    }

    fn with_gutter_mm(&self, gutter: f32) -> Self {
        PyPageMargins {
            inner: self.inner.clone().with_gutter_mm(gutter),
        }
    }

    fn with_mirror_margins(&self, mirror: bool) -> Self {
        PyPageMargins {
            inner: self.inner.clone().with_mirror_margins(mirror),
        }
    }
}

/// Page layout configuration
#[pyclass(name = "PageLayout")]
#[derive(Clone)]
pub struct PyPageLayout {
    inner: hwpers::model::page_layout::PageLayout,
}

#[pymethods]
impl PyPageLayout {
    #[new]
    fn new(paper_size: PyPaperSize, orientation: PyPageOrientation) -> Self {
        PyPageLayout {
            inner: hwpers::model::page_layout::PageLayout::new(
                paper_size.into(),
                orientation.into(),
            ),
        }
    }

    #[staticmethod]
    fn a4_portrait() -> Self {
        PyPageLayout {
            inner: hwpers::model::page_layout::PageLayout::a4_portrait(),
        }
    }

    #[staticmethod]
    fn a4_landscape() -> Self {
        PyPageLayout {
            inner: hwpers::model::page_layout::PageLayout::a4_landscape(),
        }
    }

    #[staticmethod]
    fn letter_portrait() -> Self {
        PyPageLayout {
            inner: hwpers::model::page_layout::PageLayout::letter_portrait(),
        }
    }

    #[staticmethod]
    fn letter_landscape() -> Self {
        PyPageLayout {
            inner: hwpers::model::page_layout::PageLayout::letter_landscape(),
        }
    }

    #[staticmethod]
    fn custom_mm(width_mm: f32, height_mm: f32, orientation: PyPageOrientation) -> Self {
        PyPageLayout {
            inner: hwpers::model::page_layout::PageLayout::custom_mm(
                width_mm,
                height_mm,
                orientation.into(),
            ),
        }
    }

    fn with_margins(&self, margins: PyPageMargins) -> Self {
        PyPageLayout {
            inner: self.inner.clone().with_margins(margins.inner),
        }
    }

    fn with_columns(&self, columns: u16, spacing_mm: f32) -> Self {
        PyPageLayout {
            inner: self.inner.clone().with_columns(columns, spacing_mm),
        }
    }

    fn with_column_line(&self, show_line: bool) -> Self {
        PyPageLayout {
            inner: self.inner.clone().with_column_line(show_line),
        }
    }

    fn with_background_color(&self, color: u32) -> Self {
        PyPageLayout {
            inner: self.inner.clone().with_background_color(color),
        }
    }

    fn with_page_numbering(&self, start: u16, format: PyPageNumberFormat) -> Self {
        PyPageLayout {
            inner: self.inner.clone().with_page_numbering(start, format.into()),
        }
    }

    #[getter]
    fn paper_size(&self) -> PyPaperSize {
        self.inner.paper_size.into()
    }

    #[getter]
    fn orientation(&self) -> PyPageOrientation {
        self.inner.orientation.into()
    }

    #[getter]
    fn width(&self) -> u32 {
        self.inner.width
    }

    #[getter]
    fn height(&self) -> u32 {
        self.inner.height
    }

    fn effective_width(&self) -> u32 {
        self.inner.effective_width()
    }

    fn effective_height(&self) -> u32 {
        self.inner.effective_height()
    }

    fn column_width(&self) -> u32 {
        self.inner.column_width()
    }
}

// ============================================================================
// TableBuilder (Python-friendly wrapper)
// ============================================================================

/// Table cell data for builder
#[derive(Clone)]
struct TableCell {
    row: u32,
    col: u32,
    text: String,
}

/// Table builder for creating tables with advanced formatting
#[pyclass(name = "TableBuilder")]
pub struct PyTableBuilder {
    rows: u32,
    cols: u32,
    cells: Vec<TableCell>,
    has_header: bool,
    outer_border: Option<PyBorderLineStyle>,
    inner_border: Option<PyBorderLineStyle>,
    no_borders: bool,
    merges: Vec<(u32, u32, u32, u32)>, // (start_row, start_col, end_row, end_col)
}

#[pymethods]
impl PyTableBuilder {
    #[new]
    fn new(rows: u32, cols: u32) -> Self {
        PyTableBuilder {
            rows,
            cols,
            cells: Vec::new(),
            has_header: false,
            outer_border: None,
            inner_border: None,
            no_borders: false,
            merges: Vec::new(),
        }
    }

    fn set_header_row(&mut self, has_header: bool) -> PyTableBuilder {
        PyTableBuilder {
            has_header,
            ..self.clone()
        }
    }

    fn set_cell(&mut self, row: u32, col: u32, text: String) -> PyTableBuilder {
        let mut cells = self.cells.clone();
        cells.push(TableCell { row, col, text });
        PyTableBuilder {
            cells,
            ..self.clone()
        }
    }

    fn merge_cells(
        &mut self,
        start_row: u32,
        start_col: u32,
        end_row: u32,
        end_col: u32,
    ) -> PyTableBuilder {
        let mut merges = self.merges.clone();
        merges.push((start_row, start_col, end_row, end_col));
        PyTableBuilder {
            merges,
            ..self.clone()
        }
    }

    fn set_outer_borders(&mut self, style: PyBorderLineStyle) -> PyTableBuilder {
        PyTableBuilder {
            outer_border: Some(style),
            ..self.clone()
        }
    }

    fn set_inner_borders(&mut self, style: PyBorderLineStyle) -> PyTableBuilder {
        PyTableBuilder {
            inner_border: Some(style),
            ..self.clone()
        }
    }

    fn set_all_borders(&mut self, style: PyBorderLineStyle) -> PyTableBuilder {
        PyTableBuilder {
            outer_border: Some(style.clone()),
            inner_border: Some(style),
            ..self.clone()
        }
    }

    fn no_borders(&mut self) -> PyTableBuilder {
        PyTableBuilder {
            no_borders: true,
            ..self.clone()
        }
    }

    #[getter]
    fn row_count(&self) -> u32 {
        self.rows
    }

    #[getter]
    fn col_count(&self) -> u32 {
        self.cols
    }
}

impl Clone for PyTableBuilder {
    fn clone(&self) -> Self {
        PyTableBuilder {
            rows: self.rows,
            cols: self.cols,
            cells: self.cells.clone(),
            has_header: self.has_header,
            outer_border: self.outer_border.clone(),
            inner_border: self.inner_border.clone(),
            no_borders: self.no_borders,
            merges: self.merges.clone(),
        }
    }
}

// ============================================================================
// Render Module
// ============================================================================

/// Render options for HWP rendering
#[pyclass(name = "RenderOptions")]
#[derive(Clone)]
pub struct PyRenderOptions {
    inner: hwpers::render::RenderOptions,
}

#[pymethods]
impl PyRenderOptions {
    #[new]
    #[pyo3(signature = (dpi=96, scale=1.0, show_margins=false, show_baselines=false))]
    fn new(dpi: u32, scale: f32, show_margins: bool, show_baselines: bool) -> Self {
        PyRenderOptions {
            inner: hwpers::render::RenderOptions {
                dpi,
                scale,
                show_margins,
                show_baselines,
            },
        }
    }

    #[getter]
    fn dpi(&self) -> u32 {
        self.inner.dpi
    }

    #[getter]
    fn scale(&self) -> f32 {
        self.inner.scale
    }

    #[getter]
    fn show_margins(&self) -> bool {
        self.inner.show_margins
    }

    #[getter]
    fn show_baselines(&self) -> bool {
        self.inner.show_baselines
    }
}

/// Rendered page output
#[pyclass(name = "RenderedPage")]
pub struct PyRenderedPage {
    width: i32,
    height: i32,
    page_number: u32,
}

#[pymethods]
impl PyRenderedPage {
    #[getter]
    fn width(&self) -> i32 {
        self.width
    }

    #[getter]
    fn height(&self) -> i32 {
        self.height
    }

    #[getter]
    fn page_number(&self) -> u32 {
        self.page_number
    }
}

/// Render result containing all pages
#[pyclass(name = "RenderResult")]
pub struct PyRenderResult {
    pages: Vec<PyRenderedPage>,
    svg_pages: Vec<String>,
}

#[pymethods]
impl PyRenderResult {
    #[getter]
    fn page_count(&self) -> usize {
        self.pages.len()
    }

    fn get_page(&self, index: usize) -> Option<PyRenderedPage> {
        self.pages.get(index).map(|p| PyRenderedPage {
            width: p.width,
            height: p.height,
            page_number: p.page_number,
        })
    }

    fn to_svg(&self, page_index: usize) -> Option<String> {
        self.svg_pages.get(page_index).cloned()
    }

    fn all_svg(&self) -> Vec<String> {
        self.svg_pages.clone()
    }
}

// ============================================================================
// HwpDocument
// ============================================================================

#[pyclass(name = "HwpDocument")]
pub struct PyHwpDocument {
    inner: hwpers::HwpDocument,
}

#[pymethods]
impl PyHwpDocument {
    fn extract_text(&self) -> String {
        self.inner.extract_text()
    }

    fn section_count(&self) -> usize {
        self.inner.body_texts.len()
    }

    fn get_title(&self) -> Option<String> {
        self.inner
            .get_properties()
            .and_then(|p| p.document_title.clone())
    }

    fn get_author(&self) -> Option<String> {
        self.inner
            .get_properties()
            .and_then(|p| p.document_author.clone())
    }

    fn get_character_count(&self) -> u32 {
        self.inner
            .get_properties()
            .map(|p| p.total_character_count)
            .unwrap_or(0)
    }

    fn get_page_count(&self) -> u32 {
        self.inner
            .get_properties()
            .map(|p| p.total_page_count)
            .unwrap_or(0)
    }

    fn is_compressed(&self) -> bool {
        self.inner.header.is_compressed()
    }

    /// Render the document with optional render options
    /// Note: Rendering may fail on documents created with HwpWriter as they may lack
    /// proper page definitions. This works best with documents read from actual HWP files.
    #[pyo3(signature = (options=None))]
    fn render(&self, options: Option<PyRenderOptions>) -> PyResult<PyRenderResult> {
        let opts = options.map(|o| o.inner).unwrap_or_default();

        // Use catch_unwind to handle panics from the render engine
        let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            let renderer = hwpers::render::HwpRenderer::new(&self.inner, opts);
            renderer.render()
        }));

        match result {
            Ok(render_result) => {
                let pages: Vec<PyRenderedPage> = render_result.pages.iter().map(|p| PyRenderedPage {
                    width: p.width,
                    height: p.height,
                    page_number: p.page_number,
                }).collect();

                let svg_pages: Vec<String> = (0..render_result.pages.len())
                    .filter_map(|i| render_result.to_svg(i))
                    .collect();

                Ok(PyRenderResult { pages, svg_pages })
            }
            Err(_) => {
                Err(PyIOError::new_err("Render failed: document may lack required page definitions. Rendering works best with documents read from HWP files."))
            }
        }
    }

    /// Convert a page to SVG directly
    /// Note: This may fail on documents created with HwpWriter.
    #[pyo3(signature = (page_index=0, options=None))]
    fn to_svg(
        &self,
        page_index: usize,
        options: Option<PyRenderOptions>,
    ) -> PyResult<Option<String>> {
        let opts = options.map(|o| o.inner).unwrap_or_default();

        let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            let renderer = hwpers::render::HwpRenderer::new(&self.inner, opts);
            let render_result = renderer.render();
            render_result.to_svg(page_index)
        }));

        match result {
            Ok(svg) => Ok(svg),
            Err(_) => Err(PyIOError::new_err(
                "Render failed: document may lack required page definitions.",
            )),
        }
    }

    fn __repr__(&self) -> String {
        format!(
            "HwpDocument(sections={}, chars={})",
            self.section_count(),
            self.get_character_count()
        )
    }
}

// ============================================================================
// HwpWriter
// ============================================================================

#[pyclass(name = "HwpWriter")]
pub struct PyHwpWriter {
    inner: hwpers::HwpWriter,
}

#[pymethods]
impl PyHwpWriter {
    #[new]
    fn new() -> Self {
        PyHwpWriter {
            inner: hwpers::HwpWriter::new(),
        }
    }

    // Note: from_document() is not exposed because HwpDocument doesn't implement Clone
    // and the Rust API takes ownership. Use HwpWriter() to create new documents instead.

    // === Paragraph Methods ===

    fn add_paragraph(&mut self, text: &str) -> PyResult<()> {
        self.inner
            .add_paragraph(text)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_paragraph_with_style(&mut self, text: &str, style: &PyTextStyle) -> PyResult<()> {
        self.inner
            .add_paragraph_with_style(text, &style.inner)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_styled_paragraph(&mut self, styled_text: &PyStyledText) -> PyResult<()> {
        self.inner
            .add_styled_paragraph(&styled_text.inner)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_aligned_paragraph(
        &mut self,
        text: &str,
        alignment: PyParagraphAlignment,
    ) -> PyResult<()> {
        self.inner
            .add_aligned_paragraph(text, alignment.into())
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_paragraph_with_spacing(
        &mut self,
        text: &str,
        line_spacing_percent: u32,
        before_mm: f32,
        after_mm: f32,
    ) -> PyResult<()> {
        self.inner
            .add_paragraph_with_spacing(text, line_spacing_percent, before_mm, after_mm)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_paragraph_with_bold(
        &mut self,
        text: &str,
        bold_ranges: Vec<(usize, usize)>,
    ) -> PyResult<()> {
        self.inner
            .add_paragraph_with_bold(text, bold_ranges)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_paragraph_with_colors(
        &mut self,
        text: &str,
        color_ranges: Vec<(usize, usize, u32)>,
    ) -> PyResult<()> {
        self.inner
            .add_paragraph_with_colors(text, color_ranges)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_paragraph_with_highlight(
        &mut self,
        text: &str,
        highlight_ranges: Vec<(usize, usize, u32)>,
    ) -> PyResult<()> {
        self.inner
            .add_paragraph_with_highlight(text, highlight_ranges)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_mixed_text(
        &mut self,
        text: &str,
        style_ranges: Vec<(usize, usize, PyTextStyle)>,
    ) -> PyResult<()> {
        let rust_ranges: Vec<(usize, usize, hwpers::style::TextStyle)> = style_ranges
            .into_iter()
            .map(|(start, end, style)| (start, end, style.inner))
            .collect();
        self.inner
            .add_mixed_text(text, rust_ranges)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_paragraph_with_hyperlinks(
        &mut self,
        text: &str,
        links: Vec<PyHyperlink>,
    ) -> PyResult<()> {
        let rust_links: Vec<hwpers::model::Hyperlink> =
            links.into_iter().map(|l| l.inner).collect();
        self.inner
            .add_paragraph_with_hyperlinks(text, rust_links)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    // === Heading Methods ===

    fn add_heading(&mut self, text: &str, level: u8) -> PyResult<()> {
        self.inner
            .add_heading(text, level)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    // === Table Methods ===

    fn add_table(&mut self, data: Vec<Vec<String>>) -> PyResult<()> {
        let data_refs: Vec<Vec<&str>> = data
            .iter()
            .map(|row| row.iter().map(|s| s.as_str()).collect())
            .collect();
        self.inner
            .add_simple_table(&data_refs)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_simple_table(&mut self, data: Vec<Vec<String>>) -> PyResult<()> {
        let data_refs: Vec<Vec<&str>> = data
            .iter()
            .map(|row| row.iter().map(|s| s.as_str()).collect())
            .collect();
        self.inner
            .add_simple_table(&data_refs)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_table_with_builder(&mut self, builder: &PyTableBuilder) -> PyResult<()> {
        // Build a 2D vector of cell data from the builder
        let mut data: Vec<Vec<String>> =
            vec![vec![String::new(); builder.cols as usize]; builder.rows as usize];

        for cell in &builder.cells {
            if (cell.row as usize) < data.len() && (cell.col as usize) < data[0].len() {
                data[cell.row as usize][cell.col as usize] = cell.text.clone();
            }
        }

        let data_refs: Vec<Vec<&str>> = data
            .iter()
            .map(|row| row.iter().map(|s| s.as_str()).collect())
            .collect();
        self.inner
            .add_simple_table(&data_refs)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    // === List Methods ===

    fn add_bullet_list(&mut self, items: Vec<String>) -> PyResult<()> {
        let items_refs: Vec<&str> = items.iter().map(|s| s.as_str()).collect();
        self.inner
            .add_list(&items_refs, hwpers::style::ListType::Bullet)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_numbered_list(&mut self, items: Vec<String>) -> PyResult<()> {
        let items_refs: Vec<&str> = items.iter().map(|s| s.as_str()).collect();
        self.inner
            .add_list(&items_refs, hwpers::style::ListType::Numbered)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_list(&mut self, items: Vec<String>, list_type: PyListType) -> PyResult<()> {
        let items_refs: Vec<&str> = items.iter().map(|s| s.as_str()).collect();
        self.inner
            .add_list(&items_refs, list_type.into())
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn start_list(&mut self, list_type: PyListType) -> PyResult<()> {
        self.inner
            .start_list(list_type.into())
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_list_item(&mut self, text: &str) -> PyResult<()> {
        self.inner
            .add_list_item(text)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn start_nested_list(&mut self, list_type: PyListType) -> PyResult<()> {
        self.inner
            .start_nested_list(list_type.into())
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn end_list(&mut self) -> PyResult<()> {
        self.inner
            .end_list()
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    // === Hyperlink Methods ===

    fn add_hyperlink(&mut self, display_text: &str, url: &str) -> PyResult<()> {
        self.inner
            .add_hyperlink(display_text, url)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_email_link(&mut self, display_text: &str, email: &str) -> PyResult<()> {
        self.inner
            .add_email_link(display_text, email)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_file_link(&mut self, display_text: &str, file_path: &str) -> PyResult<()> {
        self.inner
            .add_file_link(display_text, file_path)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_bookmark_link(&mut self, display_text: &str, bookmark_name: &str) -> PyResult<()> {
        self.inner
            .add_bookmark_link(display_text, bookmark_name)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_hyperlink_with_options(&mut self, hyperlink: PyHyperlink) -> PyResult<()> {
        self.inner
            .add_hyperlink_with_options(hyperlink.inner)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_custom_hyperlink(
        &mut self,
        display_text: &str,
        hyperlink_type: PyHyperlinkType,
        target_url: &str,
        display_mode: PyHyperlinkDisplay,
        style: &PyHyperlinkStyle,
    ) -> PyResult<()> {
        self.inner
            .add_custom_hyperlink(
                display_text,
                hyperlink_type.into(),
                target_url,
                display_mode.into(),
                style.into(),
            )
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    // === Image Methods ===

    fn add_image(&mut self, path: &str) -> PyResult<()> {
        self.inner
            .add_image(path)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_image_from_bytes(&mut self, data: &[u8], format: PyImageFormat) -> PyResult<()> {
        self.inner
            .add_image_from_bytes(data, format.into())
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_image_with_options(
        &mut self,
        data: &[u8],
        format: PyImageFormat,
        options: &PyImageOptions,
    ) -> PyResult<()> {
        self.inner
            .add_image_with_options(data, format.into(), &options.inner)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    // === Text Box Methods ===

    fn add_text_box(&mut self, text: &str) -> PyResult<()> {
        self.inner
            .add_text_box(text)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_text_box_at_position(
        &mut self,
        text: &str,
        x: u32,
        y: u32,
        width: u32,
        height: u32,
    ) -> PyResult<()> {
        self.inner
            .add_text_box_at_position(text, x, y, width, height)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_styled_text_box(&mut self, text: &str, style: &str) -> PyResult<()> {
        self.inner
            .add_styled_text_box(text, style)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_floating_text_box(
        &mut self,
        text: &str,
        x: u32,
        y: u32,
        width: u32,
        height: u32,
        style: &PyFloatingTextBoxStyle,
    ) -> PyResult<()> {
        self.inner
            .add_floating_text_box(text, x, y, width, height, style.into())
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn add_custom_text_box(
        &mut self,
        text: &str,
        x: u32,
        y: u32,
        width: u32,
        height: u32,
        style: &PyCustomTextBoxStyle,
    ) -> PyResult<()> {
        self.inner
            .add_custom_text_box(text, x, y, width, height, style.into())
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    // === Header/Footer Methods ===

    fn add_header(&mut self, text: &str) {
        self.inner.add_header(text);
    }

    fn add_footer(&mut self, text: &str) {
        self.inner.add_footer(text);
    }

    fn add_header_with_page_number(&mut self, text: &str, format: PyPageNumberFormat) {
        self.inner.add_header_with_page_number(text, format.into());
    }

    fn add_footer_with_page_number(&mut self, text: &str, format: PyPageNumberFormat) {
        self.inner.add_footer_with_page_number(text, format.into());
    }

    fn add_header_with_options(
        &mut self,
        text: &str,
        page_type: PyPageApplyType,
        alignment: PyHeaderFooterAlignment,
    ) {
        self.inner
            .add_header_with_options(text, page_type.into(), alignment.into());
    }

    fn add_footer_with_options(
        &mut self,
        text: &str,
        page_type: PyPageApplyType,
        alignment: PyHeaderFooterAlignment,
    ) {
        self.inner
            .add_footer_with_options(text, page_type.into(), alignment.into());
    }

    // === Page Layout Methods ===

    fn set_page_layout(&mut self, layout: &PyPageLayout) -> PyResult<()> {
        self.inner
            .set_page_layout(layout.inner.clone())
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn get_page_layout(&self) -> PyPageLayout {
        PyPageLayout {
            inner: self.inner.get_page_layout(),
        }
    }

    fn set_a4_portrait(&mut self) -> PyResult<()> {
        self.inner
            .set_a4_portrait()
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn set_a4_landscape(&mut self) -> PyResult<()> {
        self.inner
            .set_a4_landscape()
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn set_letter_portrait(&mut self) -> PyResult<()> {
        self.inner
            .set_letter_portrait()
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn set_letter_landscape(&mut self) -> PyResult<()> {
        self.inner
            .set_letter_landscape()
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn set_paper_size(&mut self, paper_size: PyPaperSize) {
        self.inner.set_paper_size(paper_size.into());
    }

    fn set_page_orientation(&mut self, orientation: PyPageOrientation) {
        self.inner.set_page_orientation(orientation.into());
    }

    fn set_custom_page_size(
        &mut self,
        width_mm: f32,
        height_mm: f32,
        orientation: PyPageOrientation,
    ) -> PyResult<()> {
        self.inner
            .set_custom_page_size(width_mm, height_mm, orientation.into())
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn set_custom_page_size_mm(&mut self, width_mm: f32, height_mm: f32) {
        self.inner.set_custom_page_size_mm(width_mm, height_mm);
    }

    fn set_page_margins_mm(&mut self, left: f32, right: f32, top: f32, bottom: f32) {
        self.inner.set_page_margins_mm(left, right, top, bottom);
    }

    fn set_page_margins_inches(&mut self, left: f32, right: f32, top: f32, bottom: f32) {
        self.inner.set_page_margins_inches(left, right, top, bottom);
    }

    fn set_narrow_margins(&mut self) {
        self.inner.set_narrow_margins();
    }

    fn set_normal_margins(&mut self) {
        self.inner.set_normal_margins();
    }

    fn set_wide_margins(&mut self) {
        self.inner.set_wide_margins();
    }

    fn set_columns(&mut self, columns: u16, spacing_mm: f32) {
        self.inner.set_columns(columns, spacing_mm);
    }

    fn set_page_background_color(&mut self, color: u32) {
        self.inner.set_page_background_color(color);
    }

    fn set_page_numbering(&mut self, start: u16, format: PyPageNumberFormat) -> PyResult<()> {
        self.inner
            .set_page_numbering(start, format.into())
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    // === Document Properties ===

    fn set_title(&mut self, title: &str) {
        self.inner.set_document_title(title);
    }

    fn set_author(&mut self, author: &str) {
        self.inner.set_document_author(author);
    }

    fn set_subject(&mut self, subject: &str) {
        self.inner.set_document_subject(subject);
    }

    fn set_keywords(&mut self, keywords: &str) {
        self.inner.set_document_keywords(keywords);
    }

    fn set_company(&mut self, company: &str) {
        self.inner.set_document_company(company);
    }

    fn update_statistics(&mut self) {
        self.inner.update_document_statistics();
    }

    // === Output ===

    fn save(&self, path: &str) -> PyResult<()> {
        self.inner
            .save_to_file(path)
            .map_err(|e| PyIOError::new_err(e.to_string()))
    }

    fn to_bytes<'py>(&self, py: Python<'py>) -> PyResult<Bound<'py, PyBytes>> {
        let bytes = self
            .inner
            .to_bytes()
            .map_err(|e| PyIOError::new_err(e.to_string()))?;
        Ok(PyBytes::new(py, &bytes))
    }

    fn extract_text(&self) -> String {
        self.inner.document().extract_text()
    }

    fn __repr__(&self) -> String {
        "HwpWriter()".to_string()
    }
}

// ============================================================================
// Module Functions
// ============================================================================

#[pyfunction]
fn read_file(path: &str) -> PyResult<PyHwpDocument> {
    let path = PathBuf::from(path);
    hwpers::HwpReader::from_file(&path)
        .map(|doc| PyHwpDocument { inner: doc })
        .map_err(|e| PyIOError::new_err(format!("Failed to read HWP file: {}", e)))
}

#[pyfunction]
fn read_bytes(data: &[u8]) -> PyResult<PyHwpDocument> {
    hwpers::HwpReader::from_bytes(data)
        .map(|doc| PyHwpDocument { inner: doc })
        .map_err(|e| PyIOError::new_err(format!("Failed to parse HWP data: {}", e)))
}

// ============================================================================
// Python Module
// ============================================================================

// ============================================================================
// Unit conversion functions
// ============================================================================

/// Convert millimeters to HWP units
#[pyfunction]
fn mm_to_hwp_units(mm: f32) -> u32 {
    hwpers::model::mm_to_hwp_units(mm)
}

/// Convert inches to HWP units
#[pyfunction]
fn inches_to_hwp_units(inches: f32) -> u32 {
    hwpers::model::inches_to_hwp_units(inches)
}

/// Convert HWP units to millimeters
#[pyfunction]
fn hwp_units_to_mm(units: u32) -> f32 {
    hwpers::model::hwp_units_to_mm(units)
}

/// Convert HWP units to inches
#[pyfunction]
fn hwp_units_to_inches(units: u32) -> f32 {
    hwpers::model::hwp_units_to_inches(units)
}

#[pymodule]
fn hwpers_py(m: &Bound<'_, PyModule>) -> PyResult<()> {
    // Document classes
    m.add_class::<PyHwpDocument>()?;
    m.add_class::<PyHwpWriter>()?;

    // Enums
    m.add_class::<PyTextAlign>()?;
    m.add_class::<PyParagraphAlignment>()?;
    m.add_class::<PyListType>()?;
    m.add_class::<PyBorderLineType>()?;
    m.add_class::<PyImageFormat>()?;
    m.add_class::<PyImageAlign>()?;
    m.add_class::<PyPageOrientation>()?;
    m.add_class::<PyPaperSize>()?;
    m.add_class::<PyPageNumberFormat>()?;
    m.add_class::<PyHyperlinkType>()?;
    m.add_class::<PyHyperlinkDisplay>()?;
    m.add_class::<PyPageApplyType>()?;
    m.add_class::<PyHeaderFooterAlignment>()?;
    m.add_class::<PyTextBoxAlignment>()?;
    m.add_class::<PyTextBoxBorderStyle>()?;

    // Style classes
    m.add_class::<PyTextStyle>()?;
    m.add_class::<PyBorderLineStyle>()?;
    m.add_class::<PyCellBorderStyle>()?;
    m.add_class::<PyImageOptions>()?;
    m.add_class::<PyStyledText>()?;
    m.add_class::<PyHyperlinkStyle>()?;
    m.add_class::<PyHyperlink>()?;
    m.add_class::<PyFloatingTextBoxStyle>()?;
    m.add_class::<PyCustomTextBoxStyle>()?;
    m.add_class::<PyPageMargins>()?;
    m.add_class::<PyPageLayout>()?;

    // Additional style classes
    m.add_class::<PyCellAlign>()?;
    m.add_class::<PyHeadingStyle>()?;
    m.add_class::<PyListStyle>()?;
    m.add_class::<PyTableStyle>()?;
    m.add_class::<PyTextRange>()?;

    // TableBuilder
    m.add_class::<PyTableBuilder>()?;

    // Render classes
    m.add_class::<PyRenderOptions>()?;
    m.add_class::<PyRenderedPage>()?;
    m.add_class::<PyRenderResult>()?;

    // Functions
    m.add_function(wrap_pyfunction!(read_file, m)?)?;
    m.add_function(wrap_pyfunction!(read_bytes, m)?)?;

    // Unit conversion functions
    m.add_function(wrap_pyfunction!(mm_to_hwp_units, m)?)?;
    m.add_function(wrap_pyfunction!(inches_to_hwp_units, m)?)?;
    m.add_function(wrap_pyfunction!(hwp_units_to_mm, m)?)?;
    m.add_function(wrap_pyfunction!(hwp_units_to_inches, m)?)?;

    Ok(())
}
