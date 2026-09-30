from hck2609.contracts import CleanData, RawData

import json
from pptx import Presentation

def pptx_to_json(file_path):
    """
    Reads a PowerPoint file, extracts metadata, joins slide body elements 
    with a newline, and formats the output into the desired JSON structure.
    """
    prs = Presentation(file_path)
    presentation_data = []
    
    # Extract presentation-level core properties for metadata
    core_props = prs.core_properties
    doc_title = core_props.title if core_props.title else file_path
    doc_author = core_props.author if core_props.author else "Unknown"
    
    # Iterate through each slide in the presentation
    for slide_index, slide in enumerate(prs.slides):
        body_elements = []
        
        # Extract text from shapes on the slide
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    text = paragraph.text.strip()
                    if text:
                        body_elements.append(text)
        
        # Join the text elements with a newline character
        combined_body = "\n".join(body_elements)
        
        # Construct the structured dictionary for the slide
        slide_entry = {
            "DocType": "ppt",
            "metadata": {
                "presentation_title": doc_title,
                "author": doc_author,
                "slide_number": slide_index + 1
            },
            "body": combined_body
        }
        
        presentation_data.append(slide_entry)
        
    # Convert the Python structure to a formatted JSON string
    return json.dumps(presentation_data, indent=4)

def docx_to_json(file_path):
    """
    Reads a Word document (.docx), extracts its paragraphs and table content for the body,
    pulls metadata from core properties, and formats it into the JSON structure.
    """
    doc = Document(file_path)
    
    # Extract metadata from core properties
    core_props = doc.core_properties
    metadata = {
        "title": core_props.title if core_props.title else "",
        "author": core_props.author if core_props.author else "",
        "last_modified_by": core_props.last_modified_by if core_props.last_modified_by else "",
        "revision": core_props.revision if core_props.revision else 1
    }
    
    body_elements = []
    
    # Extract text from paragraphs
    for paragraph in doc.paragraphs:
        text = paragraph.text.strip()
        if text:
            body_elements.append(text)
            
    # Extract text from tables if the document contains any
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                text = cell.text.strip()
                if text:
                    body_elements.append(text)
                    
    # Join all body elements with a newline character
    combined_body = "\n".join(body_elements)
    
    # Construct the final JSON dictionary structure
    document_data = {
        "DocType": "word",
        "metadata": metadata,
        "body": combined_body
    }
    
    # Convert to a formatted JSON string
    return json.dumps(document_data, indent=4)


def clean(raw: RawData) -> CleanData:
    """Clean and normalise raw data. Stub: strips names, drops missing rows."""
    df = raw.dropna().copy()
    df["name"] = df["name"].str.strip().str.lower()
    return df


