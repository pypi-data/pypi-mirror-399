import aspose.pdf
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class ComparisonOptions:
    '''Represents a PDF document comparison options class.'''
    
    def __init__(self):
        ...
    
    @property
    def extraction_area(self) -> aspose.pdf.Rectangle:
        '''Get and set the rectangular area in which the text of pages will be compared.'''
        ...
    
    @extraction_area.setter
    def extraction_area(self, value: aspose.pdf.Rectangle):
        ...
    
    @property
    def exclude_tables(self) -> bool:
        '''Get and set the option that determines whether tables are excluded from comparison.
        This option cannot be set together with :attr:`ComparisonOptions.extraction_area` option.
        The default value is false.'''
        ...
    
    @exclude_tables.setter
    def exclude_tables(self, value: bool):
        ...
    
    @property
    def exclude_areas1(self) -> list[aspose.pdf.Rectangle]:
        '''Get and set the exclude areas. Used for the first page or document in the comparison method.
        This option can be setted along with :attr:`ComparisonOptions.exclude_tables`.
        This option can't be setted along with :attr:`ComparisonOptions.extraction_area` option.'''
        ...
    
    @exclude_areas1.setter
    def exclude_areas1(self, value: list[aspose.pdf.Rectangle]):
        ...
    
    @property
    def exclude_areas2(self) -> list[aspose.pdf.Rectangle]:
        '''Get and set the exclude areas. Used for the second page or document in the comparison method.
        This option can be setted along with :attr:`ComparisonOptions.exclude_tables`.
        This option can't be setted along with :attr:`ComparisonOptions.extraction_area` option.'''
        ...
    
    @exclude_areas2.setter
    def exclude_areas2(self, value: list[aspose.pdf.Rectangle]):
        ...
    
    @property
    def edit_operations_order(self) -> aspose.pdf.comparison.EditOperationsOrder:
        '''Gets and sets the edit operations order.'''
        ...
    
    @edit_operations_order.setter
    def edit_operations_order(self, value: aspose.pdf.comparison.EditOperationsOrder):
        ...
    
    ...

class DiffOperation:
    
    def equals(self, op: aspose.pdf.comparison.DiffOperation) -> bool:
        ...
    
    @property
    def operation(self) -> aspose.pdf.comparison.Operation:
        ...
    
    @property
    def text(self) -> str:
        ...
    
    ...

class DocumentComparisonStatistics(aspose.pdf.comparison.TextItemComparisonStatistics):
    '''Represents a document comparison statistics class.'''
    
    def __init__(self):
        ...
    
    @property
    def pages_statistics(self) -> None:
        '''Gets and sets the list of pages statistics.'''
        ...
    
    ...

class GraphicalPdfComparer:
    
    def __init__(self):
        ...
    
    @overload
    def compare_pages_to_pdf(self, page1: aspose.pdf.Page, page2: aspose.pdf.Page, result_pdf_path: str) -> None:
        ...
    
    @overload
    def compare_pages_to_pdf(self, page1: aspose.pdf.Page, page2: aspose.pdf.Page, pdf_document: aspose.pdf.Document) -> None:
        ...
    
    def get_difference(self, page1: aspose.pdf.Page, page2: aspose.pdf.Page) -> aspose.pdf.comparison.ImagesDifference:
        ...
    
    def compare_documents_to_pdf(self, document1: aspose.pdf.Document, document2: aspose.pdf.Document, result_pdf_path: str) -> None:
        ...
    
    def compare_pages_to_image(self, page1: aspose.pdf.Page, page2: aspose.pdf.Page, result_image_path: str) -> None:
        ...
    
    def compare_documents_to_images(self, document1: aspose.pdf.Document, document2: aspose.pdf.Document, target_directory: str, file_name_prefix: str, image_format: aspose.pydrawing.Imaging.ImageFormat) -> None:
        ...
    
    @property
    def resolution(self) -> aspose.pdf.devices.Resolution:
        ...
    
    @resolution.setter
    def resolution(self, value: aspose.pdf.devices.Resolution):
        ...
    
    @property
    def color(self) -> aspose.pdf.Color:
        ...
    
    @color.setter
    def color(self, value: aspose.pdf.Color):
        ...
    
    @property
    def threshold(self) -> float:
        ...
    
    @threshold.setter
    def threshold(self, value: float):
        ...
    
    ...

class HtmlDiffOutputGenerator:
    
    @overload
    def __init__(self):
        ...
    
    @overload
    def __init__(self, text_style: aspose.pdf.comparison.OutputTextStyle):
        ...
    
    @property
    def equal_style(self) -> str:
        ...
    
    @equal_style.setter
    def equal_style(self, value: str):
        ...
    
    @property
    def insert_style(self) -> str:
        ...
    
    @insert_style.setter
    def insert_style(self, value: str):
        ...
    
    @property
    def delete_style(self) -> str:
        ...
    
    @delete_style.setter
    def delete_style(self, value: str):
        ...
    
    @property
    def strikethrough_deleted(self) -> bool:
        ...
    
    @strikethrough_deleted.setter
    def strikethrough_deleted(self, value: bool):
        ...
    
    ...

class IFileOutputGenerator:
    
    @overload
    def generate_output(self, diffrences, target_file_path: str) -> None:
        ...
    
    @overload
    def generate_output(self, diffrences, target_file_path: str) -> None:
        ...
    
    ...

class IStringOutputGenerator:
    
    @overload
    def generate_output(self, diffrences) -> str:
        ...
    
    @overload
    def generate_output(self, diffrences) -> str:
        ...
    
    ...

class ImagesDifference:
    
    def get_destination_image(self) -> aspose.pydrawing.Bitmap:
        ...
    
    def difference_to_image(self, color: aspose.pdf.Color, background_color: aspose.pdf.Color) -> aspose.pydrawing.Bitmap:
        ...
    
    @property
    def source_image(self) -> aspose.pydrawing.Bitmap:
        ...
    
    @property
    def difference(self) -> list[int]:
        ...
    
    @property
    def stride(self) -> int:
        ...
    
    @property
    def height(self) -> int:
        ...
    
    ...

class JsonDiffOutputGenerator:
    
    def __init__(self):
        ...
    
    ...

class MarkdownDiffOutputGenerator:
    
    def __init__(self):
        ...
    
    ...

class OutputTextStyle:
    
    def __init__(self):
        ...
    
    @property
    def inserted_style(self) -> None:
        ...
    
    @inserted_style.setter
    def inserted_style(self, value: None):
        ...
    
    @property
    def deleted_style(self) -> None:
        ...
    
    @deleted_style.setter
    def deleted_style(self, value: None):
        ...
    
    @property
    def equal_style(self) -> None:
        ...
    
    @equal_style.setter
    def equal_style(self, value: None):
        ...
    
    @property
    def strikethrough_deleted(self) -> bool:
        ...
    
    @strikethrough_deleted.setter
    def strikethrough_deleted(self, value: bool):
        ...
    
    ...

class PdfOutputGenerator:
    
    @overload
    def __init__(self):
        ...
    
    @overload
    def __init__(self, page_info: aspose.pdf.PageInfo):
        ...
    
    @overload
    def __init__(self, text_style: aspose.pdf.comparison.OutputTextStyle):
        ...
    
    @overload
    def __init__(self, text_style: aspose.pdf.comparison.OutputTextStyle, page_info: aspose.pdf.PageInfo):
        ...
    
    ...

class SideBySideComparisonOptions:
    '''Represents an options class for comparing documents with side-by-side output.'''
    
    def __init__(self):
        ...
    
    @property
    def comparison_mode(self) -> aspose.pdf.comparison.ComparisonMode:
        '''Gets and sets a comparison mode.
        The default value is Aspose.Pdf.Comparison.ComparisonMode.IgnoreSpaces.'''
        ...
    
    @comparison_mode.setter
    def comparison_mode(self, value: aspose.pdf.comparison.ComparisonMode):
        ...
    
    @property
    def additional_change_marks(self) -> bool:
        '''Get and set the property that determines whether additional change markers are displayed.
        If set, displays change marks that are not on the current page but are present on another page.
        If the change lacates between words, the mark may not be positioned exactly relative to the whitespace character.
        The default value is ``False``.'''
        ...
    
    @additional_change_marks.setter
    def additional_change_marks(self, value: bool):
        ...
    
    @property
    def exclude_tables(self) -> bool:
        '''Get and set the option that determines whether tables are excluded from comparison.
        This option cannot be set together with :attr:`SideBySideComparisonOptions.comparison_area1` and :attr:`SideBySideComparisonOptions.comparison_area2`.
        The default value is ``False``.'''
        ...
    
    @exclude_tables.setter
    def exclude_tables(self, value: bool):
        ...
    
    @property
    def comparison_area1(self) -> aspose.pdf.Rectangle:
        '''Get and set the comparison area. Used for the first page or document in the comparison method.
        This option can't be setted along with :attr:`SideBySideComparisonOptions.exclude_tables`, :attr:`SideBySideComparisonOptions.exclude_areas1` and :attr:`SideBySideComparisonOptions.exclude_areas2` options.'''
        ...
    
    @comparison_area1.setter
    def comparison_area1(self, value: aspose.pdf.Rectangle):
        ...
    
    @property
    def comparison_area2(self) -> aspose.pdf.Rectangle:
        '''Get and set the comparison area. Used for the second page or document in the comparison method.
        This option can't be setted along with :attr:`SideBySideComparisonOptions.exclude_tables`, :attr:`SideBySideComparisonOptions.exclude_areas1` and :attr:`SideBySideComparisonOptions.exclude_areas2` options.'''
        ...
    
    @comparison_area2.setter
    def comparison_area2(self, value: aspose.pdf.Rectangle):
        ...
    
    @property
    def exclude_areas1(self) -> list[aspose.pdf.Rectangle]:
        '''Get and set the exclude areas. Used for the first page or document in the comparison method.
        This option can be setted along with :attr:`SideBySideComparisonOptions.exclude_tables`. This option can't be setted along with :attr:`SideBySideComparisonOptions.comparison_area1` option.'''
        ...
    
    @exclude_areas1.setter
    def exclude_areas1(self, value: list[aspose.pdf.Rectangle]):
        ...
    
    @property
    def exclude_areas2(self) -> list[aspose.pdf.Rectangle]:
        '''Get and set the exclude areas. Used for the second page or document in the comparison method.
        This option can be setted along with :attr:`SideBySideComparisonOptions.exclude_tables`. This option can't be setted along with :attr:`SideBySideComparisonOptions.comparison_area2` option.'''
        ...
    
    @exclude_areas2.setter
    def exclude_areas2(self, value: list[aspose.pdf.Rectangle]):
        ...
    
    @property
    def delete_color(self) -> aspose.pdf.Color:
        '''Gets or sets the color used to mark deleted content during a side-by-side comparison.
        This property defines the visual representation for deletions in the comparison result.'''
        ...
    
    @delete_color.setter
    def delete_color(self, value: aspose.pdf.Color):
        ...
    
    @property
    def insert_color(self) -> aspose.pdf.Color:
        '''Gets or sets the color used to mark inserted content during a side-by-side comparison.
        This property defines the visual representation for insertion in the comparison result.'''
        ...
    
    @insert_color.setter
    def insert_color(self, value: aspose.pdf.Color):
        ...
    
    ...

class SideBySidePdfComparer:
    
    @overload
    @staticmethod
    def compare(self, page1: aspose.pdf.Page, page2: aspose.pdf.Page, target_pdf_path: str, options: aspose.pdf.comparison.SideBySideComparisonOptions) -> None:
        ...
    
    @overload
    @staticmethod
    def compare(self, document1: aspose.pdf.Document, document2: aspose.pdf.Document, target_pdf_path: str, options: aspose.pdf.comparison.SideBySideComparisonOptions) -> None:
        ...
    
    ...

class TextItemComparisonStatistics:
    '''Represents a text comparison ststistics class.'''
    
    def __init__(self):
        ...
    
    @property
    def total_characters(self) -> int:
        '''Gets and sets the total number of characters.'''
        ...
    
    @property
    def deleted_characters_count(self) -> int:
        '''Gets and sets the number of deleted characters.'''
        ...
    
    @property
    def inserted_characters_count(self) -> int:
        '''Gets and sets the number of inseted characters.'''
        ...
    
    @property
    def delete_operations_count(self) -> int:
        '''Gets and sets the number of delete operations.'''
        ...
    
    @property
    def insert_operations_count(self) -> int:
        '''Gets and sets the number of insert operations.'''
        ...
    
    ...

class TextPdfComparer:
    '''Represents a class to comparison two PDF pages or PDF documents.'''
    
    def __init__(self):
        ...
    
    @overload
    @staticmethod
    def compare_documents_page_by_page(self, document1: aspose.pdf.Document, document2: aspose.pdf.Document, options: aspose.pdf.comparison.ComparisonOptions) -> None:
        '''Compares two documents page by page.
        
        :param document1: First document..
        :param document2: Second document.
        :param options: Comparison options.
        :returns: List of changes by page.'''
        ...
    
    @overload
    @staticmethod
    def compare_documents_page_by_page(self, document1: aspose.pdf.Document, document2: aspose.pdf.Document, options: aspose.pdf.comparison.ComparisonOptions, result_pdf_document_path: str) -> None:
        '''Compares two documents page by page. The result is saved in a PDF file.
        
        :param document1: First document..
        :param document2: Second document.
        :param options: Comparison options.
        :param result_pdf_document_path: Path to the pdf file to save the comparison results.
        :returns: List of changes by page.'''
        ...
    
    @overload
    @staticmethod
    def compare_flat_documents(self, document1: aspose.pdf.Document, document2: aspose.pdf.Document, options: aspose.pdf.comparison.ComparisonOptions) -> None:
        '''Compares two documents page by page.
        The documents are compared as a whole. Before comparing text, the texts of document pages are combined into one text.
        
        :param document1: First document.
        :param document2: Second document.
        :param options: Comparison options.
        :returns: List of changes.'''
        ...
    
    @overload
    @staticmethod
    def compare_flat_documents(self, document1: aspose.pdf.Document, document2: aspose.pdf.Document, options: aspose.pdf.comparison.ComparisonOptions, result_pdf_document_path: str) -> None:
        '''Compares two documents page by page. The result is saved in a PDF file.
        The documents are compared as a whole. Before comparing text, the texts of document pages are combined into one text.
        
        :param document1: First document.
        :param document2: Second document.
        :param options: Comparison options.
        :param result_pdf_document_path: Path to the pdf file to save the comparison results.
        :returns: List of changes.'''
        ...
    
    @overload
    @staticmethod
    def create_comparison_statistics(self, diffs) -> aspose.pdf.comparison.TextItemComparisonStatistics:
        ...
    
    @overload
    @staticmethod
    def create_comparison_statistics(self, diffs) -> aspose.pdf.comparison.DocumentComparisonStatistics:
        ...
    
    @staticmethod
    def compare_pages(self, page1: aspose.pdf.Page, page2: aspose.pdf.Page, options: aspose.pdf.comparison.ComparisonOptions) -> None:
        '''Compares document pages.
        
        :param page1: First page.
        :param page2: Second page.
        :param options: Comparison options.
        :returns: The list of changes.'''
        ...
    
    @staticmethod
    def assembly_source_page_text(self, diffs) -> str:
        ...
    
    @staticmethod
    def assembly_destination_page_text(self, diffs) -> str:
        ...
    
    ...

class TextStyle:
    
    def __init__(self):
        ...
    
    @property
    def color(self) -> aspose.pdf.Color:
        ...
    
    @color.setter
    def color(self, value: aspose.pdf.Color):
        ...
    
    @property
    def background_color(self) -> aspose.pdf.Color:
        ...
    
    @background_color.setter
    def background_color(self, value: aspose.pdf.Color):
        ...
    
    ...

class ComparisonMode:
    
    NORMAL: ComparisonMode
    IGNORE_SPACES: ComparisonMode
    PARSE_SPACES: ComparisonMode

class EditOperationsOrder:
    '''Specifies the order of edit operations.'''
    
    INSERT_FIRST: EditOperationsOrder
    DELETE_FIRST: EditOperationsOrder

class Operation:
    
    EQUAL: Operation
    DELETE: Operation
    INSERT: Operation

