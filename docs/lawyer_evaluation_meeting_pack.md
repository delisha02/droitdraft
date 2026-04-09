# Lawyer Evaluation Meeting Pack

Use this pack when meeting a lawyer to define the human evaluation setup for the DroitDraft research paper.

## 1. One-Page Checklist

Bring these into the meeting:

- Project summary in 3-5 lines
- List of supported document types
- 5-10 sample system outputs
- 10 sample research queries
- 10 sample drafting prompts
- Notebook or spreadsheet to record answers

Leave the meeting with these confirmed:

- Priority document types for evaluation
- Priority research query types for evaluation
- Approved benchmark prompts and queries
- Mandatory clauses per document type
- Preferred drafting format and tone
- Preferred citation style
- Definition of minor vs major mistake
- Definition of no edit / minor edit / moderate edit / major rewrite
- Lawyer scoring rubric approval
- Agreement on when output is acceptable for professional use

## 2. Meeting Questionnaire

### A. Lawyer Profile

- Name:
- Designation:
- Years of practice:
- Area of practice:
- Jurisdiction focus:
- Contact:

### B. Scope of Evaluation

1. Which document types should be included in the paper evaluation first?
   - Legal notice
   - Probate petition
   - Will
   - Sale deed
   - Affidavit
   - Other:

2. Which tasks matter most for evaluation?
   - Legal research answers
   - Draft generation
   - Fact extraction from evidence
   - Citation grounding
   - Draft language quality

3. Which jurisdiction should be treated as the main benchmark setting?
   - Maharashtra
   - India general
   - Other:

### C. Benchmark Query Collection

Ask the lawyer to provide or approve:

- 20-30 realistic legal research queries
- 20-30 realistic drafting prompts
- 5-10 unsupported or trick queries where the system should refuse
- 5-10 incomplete prompts with missing facts
- 5-10 citation-heavy prompts

For each sample, record:

- Query or drafting prompt:
- Document type:
- Difficulty: easy / medium / hard
- Expected outcome:
- Must cite authority? yes / no
- Must refuse if unsupported? yes / no

### D. Drafting Format and Language

4. What should a professionally acceptable draft include?
- Required heading format:
- Required clause order:
- Required closing format:
- Required factual details:

5. What tone should the AI use?
- Formal traditional legal drafting
- Modern plain legal English
- Highly conservative court style
- Other:

6. What language issues are unacceptable?
- Too casual
- Ambiguous
- Unsupported legal conclusion
- Wrong citation style
- Missing mandatory clause
- Other:

7. What citation style do you expect?
- Full statutory reference
- Section and Act name
- Case name plus citation
- Hyperlink not necessary
- Other:

### E. Quality Rules for Evaluation

8. What counts as a correct output?
- Legally correct:
- Factually correct:
- Complete:
- Properly formatted:
- Properly cited:

9. What counts as a minor error?
- Typo or wording improvement
- Small formatting issue
- Small phrasing change
- Other:

10. What counts as a major error?
- Wrong law
- Wrong fact
- Missing mandatory clause
- Misleading statement
- Unsupported citation
- Other:

11. When should the AI output definitely be reviewed by a lawyer?
- Low confidence
- Missing citations
- Conflicting facts
- High-stakes filing
- Unusual legal issue
- Other:

### F. Human Evaluation Rubric Approval

Please confirm whether the following evaluation dimensions are acceptable for the research paper:

- Legal correctness: 1-5
- Completeness: 1-5
- Grounding in facts and sources: 1-5
- Drafting quality and professional language: 1-5
- Risk level: 1-4
- Edit effort: 0-3
- Approved for professional use: yes / no

### G. Edit Effort Definitions

Please approve or revise these labels:

- 0 = No edit needed
- 1 = Minor edit needed
- 2 = Moderate edit needed
- 3 = Major rewrite needed

### H. Approval Threshold

12. When would you approve an output as professionally usable?
- As-is
- After minor edits only
- Only after moderate review
- Never without full legal review

13. What is the minimum standard for publication-quality evaluation?
- Average correctness score needed:
- Average completeness score needed:
- Maximum acceptable major-error rate:
- Maximum acceptable major-rewrite rate:

## 3. Reviewer Scoring Form

Use this per output during the formal evaluation.

- Sample ID:
- Task type: research / drafting / extraction
- Prompt or query:
- Output reviewed:

Scores:

- Legal correctness (1-5):
- Completeness (1-5):
- Grounding in facts/sources (1-5):
- Drafting quality/language (1-5):
- Risk level (1-4):
- Edit effort (0-3):
- Approved for professional use? yes / no

Error tags:

- Wrong fact
- Wrong law
- Missing clause
- Missing citation
- Unsupported claim
- Poor language
- Wrong format
- Other:

Reviewer notes:

- Main issue:
- Suggested improvement:
- Whether this should count as human-corrected: yes / no

## 4. Recommended Questions to Ask Verbally

- Which outputs would you trust enough to use after only a quick review?
- Which mistakes are most dangerous in legal drafting?
- What makes a draft sound professionally acceptable to you?
- Which clauses are non-negotiable for each document type?
- What kinds of citations are mandatory versus optional?
- Which prompts should the AI refuse instead of answering?

## 5. After the Meeting

Convert the lawyer’s feedback into:

- approved benchmark dataset
- mandatory-clause checklist
- style guide for drafting prompts and outputs
- scoring rubric for human evaluation
- error taxonomy for analysis in the paper
- correction-rate definition for reporting

## 6. Suggested Research Paper Reporting

After evaluation, report:

- number of lawyers involved
- their practice area and experience band
- number of samples evaluated
- scoring rubric used
- human correction rate
- major correction rate
- approval-for-use rate
- inter-annotator agreement if more than one lawyer reviews outputs
