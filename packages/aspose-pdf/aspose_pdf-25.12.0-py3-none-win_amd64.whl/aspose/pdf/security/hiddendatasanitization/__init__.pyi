import aspose.pdf
import aspose.pydrawing
import datetime
import decimal
import io
import uuid
from typing import Iterable

class HiddenDataSanitizationOptions:
    '''Represents the configuration options for sanitizing hidden data within a document.'''
    
    def __init__(self):
        ...
    
    @staticmethod
    def all(self) -> aspose.pdf.security.hiddendatasanitization.HiddenDataSanitizationOptions:
        '''Creates a new instance of the :class:`HiddenDataSanitizationOptions` class with all options set for sanitization.
        This includes enabling the removal of annotations, JavaScript, metadata, attachments, search index, private information,
        flattening of forms and layers, while disabling the option to convert pages to images.
        Optional configurations like :attr:`HiddenDataSanitizationOptions.image_compression_options` or :attr:`HiddenDataSanitizationOptions.convert_pages_to_images` can be manually modified
        after obtaining the instance, as they are not active by default.
        
        :returns: A :class:`HiddenDataSanitizationOptions` instance with all sanitization options preconfigured.'''
        ...
    
    @property
    def image_compression_options(self) -> aspose.pdf.optimization.ImageCompressionOptions:
        '''Gets or sets the document image conversion option.
        The option must be enabled manually when using the :meth:`HiddenDataSanitizationOptions.all` method if it is required.'''
        ...
    
    @image_compression_options.setter
    def image_compression_options(self, value: aspose.pdf.optimization.ImageCompressionOptions):
        ...
    
    @property
    def convert_pages_to_images(self) -> bool:
        '''Gets or sets the option to convert pages to images.
        If this option is enabled, the ImageCompressionOptions option will be ignored.
        The option must be enabled manually when using the :meth:`HiddenDataSanitizationOptions.all` method if it is required.
        The conversion of pages to images will occur after clearing the main hidden data, which is controlled by other options.'''
        ...
    
    @convert_pages_to_images.setter
    def convert_pages_to_images(self, value: bool):
        ...
    
    @property
    def image_dpi(self) -> int:
        '''Gets or sets the option to resolve page images during conversion.'''
        ...
    
    @image_dpi.setter
    def image_dpi(self, value: int):
        ...
    
    @property
    def remove_annotations(self) -> bool:
        '''Gets or sets a value indicating whether to remove annotations from the document.
        When enabled, all annotations present in the document will be removed during the sanitization process.
        Redact annotations will be applied.'''
        ...
    
    @remove_annotations.setter
    def remove_annotations(self, value: bool):
        ...
    
    @property
    def remove_search_index_and_private_info(self) -> bool:
        '''Gets or sets a value indicating whether the search index and private information should be removed from the document.
        Enables the removal of embedded search indices and private data to enhance document security and privacy.'''
        ...
    
    @remove_search_index_and_private_info.setter
    def remove_search_index_and_private_info(self, value: bool):
        ...
    
    @property
    def flatten_forms(self) -> bool:
        '''Gets or sets a value indicating whether forms in the document
        should be flattened during the sanitization process.
        Flattening forms converts interactive form fields into static content,
        making them non-editable or fillable.'''
        ...
    
    @flatten_forms.setter
    def flatten_forms(self, value: bool):
        ...
    
    @property
    def flatten_layers(self) -> bool:
        '''Gets or sets the option to flatten the layers in the PDF document.
        When enabled, all layers in the document are merged into a single layer, removing their separate structure.
        This option is useful for sanitizing documents by simplifying their content and ensuring no hidden data resides within layers.'''
        ...
    
    @flatten_layers.setter
    def flatten_layers(self, value: bool):
        ...
    
    @property
    def remove_java_scripts_and_actions(self) -> bool:
        '''Gets or sets a value indicating whether JavaScript and associated actions should be removed from the document.
        This option is useful to eliminate potential security vulnerabilities introduced by embedded scripts.'''
        ...
    
    @remove_java_scripts_and_actions.setter
    def remove_java_scripts_and_actions(self, value: bool):
        ...
    
    @property
    def remove_metadata(self) -> bool:
        '''Gets or sets an option to remove metadata from the document.
        If set to true, metadata such as document properties and additional embedded
        metadata information will be removed during sanitization.'''
        ...
    
    @remove_metadata.setter
    def remove_metadata(self, value: bool):
        ...
    
    @property
    def remove_attachments(self) -> bool:
        '''Gets or sets the option to remove all attached files from the document.
        When enabled, it ensures that any attachments within the PDF are eliminated during the sanitation process.'''
        ...
    
    @remove_attachments.setter
    def remove_attachments(self, value: bool):
        ...
    
    ...

class HiddenDataSanitizer:
    '''Represents a class for sanitizing hidden data.'''
    
    def __init__(self, options: aspose.pdf.security.hiddendatasanitization.HiddenDataSanitizationOptions):
        '''Provides functionality to sanitize hidden data from a PDF document, ensuring that sensitive or unnecessary
        information such as metadata, annotations, JavaScripts, or private content is removed or transformed.
        
        :param options: The options to use for sanitization.'''
        ...
    
    @staticmethod
    def sanitize_all_to_images(self, document: aspose.pdf.Document, dpi: int) -> None:
        '''Replaces page content with images and removes other hidden data.
        Allows you to remove hidden text with a background color, as well as text hidden under images.
        Also completely removes all interactive elements.
        The document is converted to images as is, and then cleared of any remaining hidden data.
        If you need to clear first and then convert, use the main class method.
        
        :param document: The docunent object.
        :param dpi: The dpi of pages' images.'''
        ...
    
    def sanitize(self, document: aspose.pdf.Document) -> None:
        '''Sanitizes a given PDF document by removing or transforming hidden data.
        
        :param document: The PDF document to be sanitized.'''
        ...
    
    ...

