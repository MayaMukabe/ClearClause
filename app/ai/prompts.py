"""Prompts for health-insurance analysis, claims, and appeals."""

ANALYSIS_SYSTEM = """You are ClearClause AI, an informational helper for health insurance documents
such as explanations of benefits (EOBs), denial letters, bills, coverage summaries, and claim notices.

You do not provide legal, medical, or insurance advice.

Rules:
- Use only the document text provided. Never invent providers, member names, dates, claim numbers, amounts, or coverage terms.
- If a field is not in the document, set it to "Not specified in the document".
- Distinguish facts stated in the document from your interpretation.
- Write in everyday language for someone without insurance training.
- HIGH RISK: denials, large patient-responsibility amounts, missing authorizations, appeal deadlines, coverage exclusions, or underpayments that need immediate attention.
- MEDIUM RISK: items to review or clarify (coding issues, network status, deductibles, unclear patient costs).
- LOW RISK: routine or standard information with minimal concern.
- Never tell the user a claim will succeed or that a denial is unlawful.

Return JSON that matches the required schema exactly.
"""

ANALYSIS_USER = """Health insurance document text (page markers included when available):
{document_text}

{chunk_note}

Extract:
- overview: insurance_provider, member_name, service_dates, claim_number, document_type
- plain_language: a short, clear explanation of what this document says and what it means for the member
- findings: important items (denials, costs, coverage, deadlines, codes). For each: name, original_text, location, risk_level (high|medium|low), simple_explanation, why_it_matters, stated_in_document
- processing_notes for missing pages, unreadable scans, or unspecified items

Never invent document language.
"""

LETTER_SYSTEM = """You draft clear, professional health-insurance letters for a consumer.
Use only facts from the provided document and analysis. Never invent claim numbers, dates, amounts, or diagnoses.
If a needed fact is missing, use a bracketed placeholder like [claim number if known].
Do not promise that the insurer will approve the request.
Write in first person as the member (or as their authorized representative if that is all the document supports).
Keep a respectful, factual tone.
This is not legal advice.
"""

CLAIM_USER = """Write a professional claim letter the member can send to the insurer, based on this document.

Document name: {document_name}

Extracted text:
{document_text}

Analysis JSON:
{analysis_json}

Include: member identification as available, claim or service details, what is being requested (payment/processing of the claim), and a short list of enclosed documents the member should attach.
"""

APPEAL_USER = """Write a professional appeal letter requesting review of a denied or underpaid claim, based on this document.

Document name: {document_name}

Extracted text:
{document_text}

Analysis JSON:
{analysis_json}

Include: member and claim identifiers as available, what was denied or underpaid, why the member is requesting reconsideration in plain language, any deadlines mentioned, and a respectful request for a written decision.
"""


def analysis_json_schema() -> dict:
    return {
        "type": "object",
        "additionalProperties": False,
        "properties": {
            "overview": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "insurance_provider": {"type": "string"},
                    "member_name": {"type": "string"},
                    "service_dates": {"type": "string"},
                    "claim_number": {"type": "string"},
                    "document_type": {"type": "string"},
                },
                "required": [
                    "insurance_provider",
                    "member_name",
                    "service_dates",
                    "claim_number",
                    "document_type",
                ],
            },
            "plain_language": {"type": "string"},
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "name": {"type": "string"},
                        "original_text": {"type": "string"},
                        "location": {"type": "string"},
                        "risk_level": {"type": "string", "enum": ["high", "medium", "low"]},
                        "simple_explanation": {"type": "string"},
                        "why_it_matters": {"type": "string"},
                        "stated_in_document": {"type": "boolean"},
                    },
                    "required": [
                        "name",
                        "original_text",
                        "location",
                        "risk_level",
                        "simple_explanation",
                        "why_it_matters",
                        "stated_in_document",
                    ],
                },
            },
            "processing_notes": {"type": "array", "items": {"type": "string"}},
        },
        "required": ["overview", "plain_language", "findings", "processing_notes"],
    }
