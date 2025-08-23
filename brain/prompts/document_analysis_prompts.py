# brain/prompts/document_analysis_prompts.py
"""
Centralized prompts for document analysis and LLM fallback analysis.
"""

DOCUMENT_ANALYSIS_PROMPT = """
Analyze this {file_type} document content for product roadmap planning:

{content}

Please provide a JSON analysis with:
1. "content_summary": Brief summary of the document
2. "strategic_elements": List of strategic planning elements found
3. "key_entities": Important entities (features, stakeholders, timelines)
4. "document_structure": Assessment of how well-structured the content is
5. "quality_indicators": Factors affecting document quality
6. "recommendations": Suggestions for better roadmap planning

Respond with valid JSON only.
"""

FALLBACK_ANALYSIS_PROMPT = """
This {file_extension} file failed traditional parsing. Please extract any useful information for product roadmap planning:

{content}

Provide a JSON response with:
1. "extracted_content": Any readable content you can identify
2. "potential_structure": Guessed document structure
3. "confidence_level": Your confidence in the extraction (0.0-1.0)
4. "recommendations": What would help parse this better

Respond with valid JSON only.
"""
