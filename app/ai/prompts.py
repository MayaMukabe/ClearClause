"""Prompt templates for contract analysis and the AI assistant."""

ANALYSIS_SYSTEM = """You are ClearClause AI, an informational contract explainer for people without legal training.
You do not provide legal advice and you never tell a user whether they should sign.

Rules:
- Use only the contract text provided. Never fabricate clauses, dates, fees, parties, or page numbers.
- If something is not stated, say it is not specified in the document.
- Distinguish facts that appear in the contract from your interpretation.
- Write simple explanations in everyday language. Avoid unnecessary jargon.
- Risk labels are informational, not legal conclusions. Do not treat a standard-looking clause as automatically safe.
- HIGH RISK: potentially significant concerns (large penalties, broad liability, hard-to-cancel terms, one-sided waivers).
- MEDIUM RISK: terms that may create unexpected duties, costs, or restrictions.
- LOW RISK: routine terms the user should still understand.
- For each clause include original wording copied from the document when possible.

Return JSON that matches the required schema exactly.
"""

ANALYSIS_USER = """Document category: {category}

Extracted contract text (page markers included):
{document_text}

{chunk_note}

Analyze this document and identify important financial obligations, contract terms, legal responsibilities, and potentially unfavorable terms.

For every identified clause return:
name, original_text, location (page or section), risk_level (high|medium|low),
simple_explanation, why_it_matters, consequences, what_to_watch_for,
questions (array of questions the user may want to ask),
category (financial|terms|legal|unfavorable),
stated_in_contract (boolean),
interpretation_note (short note if you are interpreting rather than quoting).

Also produce:
- overview: document_type, parties, effective_date, expiration_date, key_financial_terms
- summary covering payment, cancellation, renewal, rights, restrictions, risks
- before_you_sign: highlights (most important issues) and suggested_questions
- processing_notes for missing pages, unclear scans, or unspecified items

Never invent contract language.
"""

ASSISTANT_SYSTEM = """You are the ClearClause AI assistant. Answer questions about the user's current document.
Rules:
- The uploaded contract is the primary source. Quote or paraphrase only what appears there.
- Cite page numbers or section headings from the extracted text when possible.
- Use everyday language.
- If the contract does not say, say so clearly. Do not invent terms.
- Distinguish contract terms from general informational context.
- You do not give legal advice and you never tell the user to sign or not sign.
- If the user switches topics, stay grounded in this document unless they ask a general definition.
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
                    "document_type": {"type": "string"},
                    "parties": {"type": "string"},
                    "effective_date": {"type": "string"},
                    "expiration_date": {"type": "string"},
                    "key_financial_terms": {"type": "string"},
                },
                "required": [
                    "document_type",
                    "parties",
                    "effective_date",
                    "expiration_date",
                    "key_financial_terms",
                ],
            },
            "summary": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "contract_type": {"type": "string"},
                    "parties": {"type": "string"},
                    "important_dates": {"type": "string"},
                    "payment_obligations": {"type": "string"},
                    "financial_responsibilities": {"type": "string"},
                    "cancellation_policies": {"type": "string"},
                    "renewal_conditions": {"type": "string"},
                    "rights_and_responsibilities": {"type": "string"},
                    "important_restrictions": {"type": "string"},
                    "potential_risks": {"type": "string"},
                    "clauses_requiring_attention": {"type": "string"},
                },
                "required": [
                    "contract_type",
                    "parties",
                    "important_dates",
                    "payment_obligations",
                    "financial_responsibilities",
                    "cancellation_policies",
                    "renewal_conditions",
                    "rights_and_responsibilities",
                    "important_restrictions",
                    "potential_risks",
                    "clauses_requiring_attention",
                ],
            },
            "before_you_sign": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "highlights": {"type": "array", "items": {"type": "string"}},
                    "suggested_questions": {"type": "array", "items": {"type": "string"}},
                },
                "required": ["highlights", "suggested_questions"],
            },
            "clauses": {
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
                        "consequences": {"type": "string"},
                        "what_to_watch_for": {"type": "string"},
                        "questions": {"type": "array", "items": {"type": "string"}},
                        "category": {
                            "type": "string",
                            "enum": ["financial", "terms", "legal", "unfavorable"],
                        },
                        "stated_in_contract": {"type": "boolean"},
                        "interpretation_note": {"type": "string"},
                    },
                    "required": [
                        "name",
                        "original_text",
                        "location",
                        "risk_level",
                        "simple_explanation",
                        "why_it_matters",
                        "consequences",
                        "what_to_watch_for",
                        "questions",
                        "category",
                        "stated_in_contract",
                        "interpretation_note",
                    ],
                },
            },
            "processing_notes": {"type": "array", "items": {"type": "string"}},
        },
        "required": [
            "overview",
            "summary",
            "before_you_sign",
            "clauses",
            "processing_notes",
        ],
    }
