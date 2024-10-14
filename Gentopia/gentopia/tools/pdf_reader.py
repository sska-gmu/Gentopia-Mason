import PyPDF2
import requests
from io import BytesIO
from typing import Optional, AnyStr, Type, Any, Dict, List
from collections import Counter
from gentopia.tools.basetool import BaseTool, BaseModel, Field


class PdfSummarizerArgs(BaseModel):
    pdf_url: str = Field(..., description="The URL of the PDF file to read.")

class PdfSummarizer(BaseTool):
    # Tool to summarize a pdf 

    name = "pdf_reader"
    description = ("Pdf summarizer reads the pdf from a given URL and summarizes it")

    args_schema: Optional[Type[BaseModel]] = PdfSummarizerArgs

    def _run(self, pdf_url: AnyStr) -> str:
        try:
            # Find the pdf
            pdf_data = requests.get(pdf_url)
            # check for errors
            pdf_data.raise_for_status()  
            return self.summarize_data(self.read_pdf(pdf_data))

        except Exception as ex:
            return str(ex)
        
    # read the pdf  
    def read_pdf(self, pdf_data: BytesIO) -> str:
        with BytesIO(pdf_data.content) as pdf_file:
            data_reader = PyPDF2.PdfReader(pdf_file)
            # Extract text from every page   
            extr_text = ""
            for page in data_reader.pages:
                extr_text += page.extract_text() + "\n"
        return extr_text

    def summarize_data(self, text: str) -> str:
        # Tokenize 
        sentences = text.split('. ')
        
        # Create a word frequency distribution
        word_freq = self.get_word_freq(text)
        
        # Calculate scores for the sentences
        sentence_value = {}
        # Consider top 4 sentences
        top_n = 4 
        sentence_sort =  sorted(sentence_value, key=self.calc_sent_score(sentence_value, sentences, word_freq).get, reverse=True)
        summary_sent = sentence_sort[:top_n]
        final_sent = '. '.join(summary_sent)+'.'
        return  final_sent
    
    # Get word frequency
    def get_word_freq(self, text: str):
        # convert to lower case and split
        words = text.lower().split()
        word_frequencies = Counter(words)
        return word_frequencies
    
    #calculate score
    def calc_sent_score(self, sentence_value: Dict[str, float], sentences: List[str], word_freq: Dict[str,int]):
        for line in sentences:
            for word in line.lower().split():
                if word in word_freq:
                    if line not in sentence_value:
                        sentence_value[line] = 0
                    sentence_value[line] += word_freq[word]
        return sentence_value
    
    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError

if __name__ == "__main__":
    pdf_url = "https://sample.com/example.pdf" 
    ans = PDFReader()._run(pdf_url)
    print(ans)
