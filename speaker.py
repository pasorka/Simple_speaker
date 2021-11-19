from gtts import gTTS
import docx
import fitz
import os
from abc import ABC, abstractmethod


def processing_string(func):
    """
    Decorator that handles string processing
    * Removes empry line
    * Concatenates line break
        
    Args:
        func ([generator]): Generator returning a string
    """

    def processing(text_file):
        
        word_wrapped = ''
        
        for line in func(text_file):
            
            line = line.strip()
                       
            if not(len(line)):
                continue
            
            if word_wrapped:
                line = word_wrapped + line
                word_wrapped = ''
            
            if line[-1] == '-':
                word_wrapped = line.split()[-1]
                line = line[:-len(word_wrapped)-1]
                word_wrapped = word_wrapped[:-1]

            yield line
        
    return processing


class BaseSpeaker(ABC):
    """
    Abstract base class for Speaker that implements the main functionality.
    Children implement functions for reading files of a certain format.
    """

    
    def __init__(self, file_path: str, out_path: str):
        self.file_path = file_path

        
        name = os.path.basename(file_path).split('.')[0]
        extension = '.mp3'
        self.out_path = os.path.join(out_path, name+extension)

        self.num_lines = self._count_lines()
    
    
    @abstractmethod
    def _read_file(self):
        """ """
        
        
    def _count_lines(self):
        lines = 0
        
        for _ in self._read_file():
            lines += 1
        
        return lines
    
    
    def recording(self, slow: bool = False, callback=False, callback_information='percent') -> int:
        """Writes voice acting to a file 

        Args:
            slow (bool): Reads text more slowly. Defaults to False.
            callback (bool): Return information about progress. Defaults to False.
            callback_information (str, ['percent', 'lines']): . Defaults to 'percent'.

        Yields:
            Iterator[int]: [description]
        """
        with open(self.out_path, 'wb') as sound_file:
            line_performed = 0
            for line in self._read_file():
                tts = gTTS(line, lang='ru', slow=slow)
                tts.write_to_fp(sound_file)
                
                if callback:
                    line_performed += 1
                    
                    if callback_information == 'percent':
                        percent = int(line_performed / self.num_lines * 100)
                        yield percent
                    elif callback_information == 'lines':
                        yield line_performed
        
    
    def __len__(self):
        return self.num_lines
    


class SpeakerTXT(BaseSpeaker):
    
    def __init__(self, file_path, out_path):
        super().__init__(file_path, out_path)
    
    
    @processing_string
    def _read_file(self) -> str:
        for line in open(self.file_path):
            yield line
    


class SpeakerDocx(BaseSpeaker):
    
    def __init__(self, file_path, out_path):
        super().__init__(file_path, out_path)
    
    
    @processing_string
    def _read_file(self):
        doc_file = docx.Document(self.file_path)
        for line in doc_file.paragraphs:
            line = line.text
            yield line



class SpeakerPdf(BaseSpeaker):
    
    def __init__(self, file_path, out_path):
        super().__init__(file_path, out_path)
    
    
    @processing_string
    def _read_file(self):
        pdf_file = fitz.open(self.file_path)
        
        for number_page in range(pdf_file.pageCount):
            page = pdf_file.load_page(number_page)
            text = page.get_text("text")
            
            for line in text.split('\n'):
                yield line    
    

            

def Speaker(file_path: str, out_path: str):
    """
        Factory of speaker
    """
    
    extension = os.path.splitext(file_path)[1]
    file_formats = ['txt', 'doc', 'pdf']
    string_formats = ' or '.join(file_formats)
    
    if extension == '.txt':
        return SpeakerTXT(file_path, out_path)
    elif extension == '.docx':
        return SpeakerDocx(file_path, out_path)
    elif extension == '.pdf':
        return SpeakerPdf(file_path, out_path)
    else:
        raise TypeError(f'Wrong format! You must use {string_formats}')



