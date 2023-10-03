
from io import StringIO
from PyPDF2 import PdfReader


def process(uploaded_files, from_local=False):
    text = ""
    if(from_local):
        for data_file in uploaded_files:
            name = data_file.filename
            extension = name.split(".")[1]
            print(extension)
            if data_file is not None and extension == "txt":
                stringio = StringIO(data_file.getvalue().decode("utf-8"))
                txt = stringio.read()
                text += txt
            if data_file is not None and extension == "pdf":
                pdf_reader = PdfReader(data_file)
                for page in pdf_reader.pages:
                    text += page.extract_text()
    else:
         for file in uploaded_files:
             text += file.read().decode("utf-8")
    return text
