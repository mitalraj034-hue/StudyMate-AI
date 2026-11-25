import re
from typing import List, Dict, Any, Optional
from pathlib import Path
from pypdf import PdfReader 


def clean_text(text: str) -> str:
    """Normalize whitespace and remove non-printable characters."""
    if not text:
        return ""
    # Replace non-breaking spaces and irregular characters
    text = text.replace('\xa0', ' ').replace('\r\n', '\n').replace('\r', '\n')
    # Collapse multiple consecutive newlines or spaces
    text = re.sub(r'[ \t]+', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)
    return text.strip()


def detect_chapters_and_sections(pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Intelligently identifies chapter headings, module titles, and major sections
    across all readable pages of the PDF.
    Returns an ordered list of detected chapters with page ranges and subheadings.
    """
    chapter_patterns = [
        re.compile(r'^(?:CHAPTER|Chapter)\s+([0-9IVXLCDM]+)[\s:\-\.]*(.*)$', re.MULTILINE),
        re.compile(r'^(?:UNIT|Unit)\s+([0-9IVXLCDM]+)[\s:\-\.]*(.*)$', re.MULTILINE),
        re.compile(r'^(?:MODULE|Module)\s+([0-9IVXLCDM]+)[\s:\-\.]*(.*)$', re.MULTILINE),
        re.compile(r'^(?:SECTION|Section)\s+([0-9IVXLCDM]+)[\s:\-\.]*(.*)$', re.MULTILINE),
        re.compile(r'^([0-9]{1,2})\.0?\s+([A-Z][A-Za-z0-9\s,\-]{3,60})$', re.MULTILINE)
    ]

    detected_chapters: List[Dict[str, Any]] = []
    
    for page in pages_data:
        page_num = page["page_number"]
        text = page.get("text", "")
        if not text:
            continue

        lines = [line.strip() for line in text.split("\n") if line.strip()]
        for line in lines[:8]: # check top header lines of page
            matched = False
            for pat in chapter_patterns:
                m = pat.match(line)
                if m:
                    chap_num_raw = m.group(1).strip()
                    chap_title_raw = m.group(2).strip() if len(m.groups()) > 1 else ""
                    title = f"Chapter {chap_num_raw}: {chap_title_raw}" if chap_title_raw else f"Chapter {chap_num_raw}"
                    title = re.sub(r'\s+', ' ', title).strip(" :-.")

                    # Avoid immediate duplicates on the same page
                    if not any(c["title"].lower() == title.lower() for c in detected_chapters):
                        detected_chapters.append({
                            "chapter_number": len(detected_chapters) + 1,
                            "identifier": f"Chapter {chap_num_raw}",
                            "title": title,
                            "start_page": page_num,
                            "end_page": page_num,
                            "key_terms": []
                        })
                    matched = True
                    break
            if matched:
                break

    # If no explicit "Chapter X" pattern was found, partition pages into logical modules
    total_pages = len(pages_data)
    if not detected_chapters and total_pages > 0:
        if total_pages <= 3:
            detected_chapters.append({
                "chapter_number": 1,
                "identifier": "Chapter 1",
                "title": "Complete Document Overview",
                "start_page": 1,
                "end_page": total_pages,
                "key_terms": []
            })
        else:
            # Group into 3-page to 5-page logical sections
            step = max(2, min(5, (total_pages + 2) // 3))
            c_num = 1
            for start_p in range(1, total_pages + 1, step):
                end_p = min(total_pages, start_p + step - 1)
                detected_chapters.append({
                    "chapter_number": c_num,
                    "identifier": f"Chapter {c_num}",
                    "title": f"Chapter {c_num}: Pages {start_p} - {end_p}",
                    "start_page": start_p,
                    "end_page": end_p,
                    "key_terms": []
                })
                c_num += 1

    # Fix end_page boundaries
    for i in range(len(detected_chapters) - 1):
        detected_chapters[i]["end_page"] = max(
            detected_chapters[i]["start_page"],
            detected_chapters[i+1]["start_page"] - 1
        )
    if detected_chapters:
        detected_chapters[-1]["end_page"] = total_pages

    return detected_chapters


def extract_text_from_pdf(file_path: Path) -> Dict[str, Any]:
    """
    Extracts text page by page from a PDF file.
    Returns page metadata, extracted text per page, detected chapters, and aggregated text.
    """
    reader = PdfReader(str(file_path))
    total_pages = len(reader.pages)
    
    pages_data: List[Dict[str, Any]] = []
    full_text_parts: List[str] = []

    for page_idx, page in enumerate(reader.pages):
        page_num = page_idx + 1
        raw_text = page.extract_text() or ""
        cleaned = clean_text(raw_text)
        
        pages_data.append({
            "page_number": page_num,
            "text": cleaned,
            "char_count": len(cleaned),
            "word_count": len(cleaned.split())
        })
        if cleaned:
            full_text_parts.append(f"--- Page {page_num} ---\n{cleaned}")

    full_text = "\n\n".join(full_text_parts)
    chapters = detect_chapters_and_sections(pages_data)

    return {
        "total_pages": total_pages,
        "pages": pages_data,
        "full_text": full_text,
        "chapters": chapters
    }


def chunk_document(
    pages_data: List[Dict[str, Any]], 
    chapters: Optional[List[Dict[str, Any]]] = None,
    chunk_size: int = 700, 
    chunk_overlap: int = 120
) -> List[Dict[str, Any]]:
    """
    Chunks document content while strictly maintaining page-wise and chapter provenance.
    If a page has content, it is split into overlapping chunks labeled with its exact page number
    and associated chapter title.
    """
    chunks: List[Dict[str, Any]] = []
    chunk_idx = 0
    chapters = chapters or []

    def find_chapter_for_page(page_num: int) -> str:
        for ch in chapters:
            if ch.get("start_page", 1) <= page_num <= ch.get("end_page", 9999):
                return ch.get("title", f"Chapter {ch.get('chapter_number', 1)}")
        return "General Section"

    for page_item in pages_data:
        page_num = page_item["page_number"]
        page_text = page_item["text"]
        chapter_title = find_chapter_for_page(page_num)

        if not page_text or len(page_text.strip()) < 10:
            continue

        # If page fits in one chunk, keep it intact
        if len(page_text) <= chunk_size:
            chunks.append({
                "chunk_index": chunk_idx,
                "page_number": page_num,
                "chapter": chapter_title,
                "content": page_text
            })
            chunk_idx += 1
            continue

        # Paragraph / sentence based sliding window chunking
        start = 0
        text_length = len(page_text)
        while start < text_length:
            end = min(start + chunk_size, text_length)
            
            # If not at the very end, try to break at a period, question mark, or newline
            if end < text_length:
                boundary = max(
                    page_text.rfind(". ", start, end),
                    page_text.rfind(".\n", start, end),
                    page_text.rfind("\n\n", start, end),
                    page_text.rfind("? ", start, end)
                )
                if boundary != -1 and boundary > start + (chunk_size // 2):
                    end = boundary + 1

            chunk_text = page_text[start:end].strip()
            if len(chunk_text) > 20: # ignore trivial noise
                chunks.append({
                    "chunk_index": chunk_idx,
                    "page_number": page_num,
                    "chapter": chapter_title,
                    "content": chunk_text
                })
                chunk_idx += 1

            if end >= text_length:
                break
            start = end - chunk_overlap

    return chunks
