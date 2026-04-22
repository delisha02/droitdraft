# Sample Queries for Testing DroitDraft

This document contains a list of sample queries that you can use to test the DroitDraft pipeline, including fact extraction, document retrieval, and document generation.

## 1. Negotiable Instruments Act (Section 138)

**Basic Query (Missing Names):**
> "Draft a legal notice under Section 138 NI Act for cheque bounce. Cheque amount is ₹2,50,000, cheque date is 05 Jan 2025, return memo reason is 'insufficient funds'."

**Detailed Query (With Names and Addresses):**
> "Draft a legal notice under Section 138 of the Negotiable Instruments Act for my client Rajesh Mehta (residing at 123, Marine Drive, Mumbai). The cheque was issued by Amit Patel (456, Andheri West, Mumbai) for ₹5,00,000. It was dated 10 Feb 2026 and bounced on 15 Feb 2026 due to 'Account Closed'. Demand the payment within 15 days."

## 2. Probate Petition

**Standard Query:**
> "Draft a Probate Petition for the Last Will and Testament of the deceased, Mr. Ramesh Kumar. The date of death is 12 December 2025. The Executor of the will is Mrs. Sunita Kumar. The properties are located in Pune, Maharashtra."

**Detailed Query with Specifics:**
> "Generate a Probate Petition. The testator is Vikram Singh who passed away on 01 Jan 2026. The petitioner and sole executor named in the will is his daughter, Anjali Singh. The assets involve a residential flat in Bandra and fixed deposits totaling ₹50 Lakhs. The will was executed on 15 March 2020."

## 3. General Legal Notices & Affidavits

**Eviction Notice:**
> "Draft a legal notice for eviction of a tenant. My client is the landlord, Suresh Iyer. The tenant is Rohan Desai, occupying Flat No. 4, Shanti Apartments, Borivali, Mumbai. Rent of ₹25,000 per month has not been paid for the last 6 months. Give him 30 days to clear the dues and vacate."

**Name Change Affidavit:**
> "Draft an affidavit for change of name. Current name is 'Siddharth Sharma', new adopted name is 'Siddharth V. Sharma'. Reason for change is personal preference. Date of birth is 14 May 1990, residing in Nagpur, Maharashtra."

## 4. Property Sale Deed

**Standard Sale Deed:**
> "Draft a Sale Deed for a commercial property. The vendor is ABC Enterprises Pvt Ltd (represented by Mr. Anil Kapoor, Director), located at Nariman Point, Mumbai. The purchaser is XYZ Logistics LLC (represented by Mrs. Pooja Hegde, Managing Director). The property is Office Space 402, Lotus Tower, Lower Parel, Mumbai. The sale consideration is ₹5,00,00,000 (Five Crores), and the transaction date is 20th April 2026."

**Residential Flat Sale Deed (Missing details):**
> "Draft a Sale Deed for the purchase of a residential flat. The seller is my client Ravi Patel. The buyer is Sneha Singh. The total agreed amount is ₹85,00,000. Property is a 2BHK flat in Andheri East."

## 5. Last Will and Testament

**Simple Will:**
> "Draft a Last Will and Testament for Geeta Devi, aged 65, residing at 55, MG Road, Pune. She wants to leave all her movable and immovable properties equally to her two sons, Karan and Arjun. She appoints Karan as the sole executor. The document is being drafted today."

**Detailed Will with Specific Legacies:**
> "Draft a Will for an individual named Mr. Prakash Narayan, 72 years old, Hindu by faith. He appoints his wife, Shobha Narayan, as the executrix. He wishes to bequeath his primary residence in Worli to his wife, his shares in Reliance Industries to his daughter Priya, and ₹10,00,000 to his favorite charity, Goonj. The rest goes to his wife."

## 6. Business Contracts

**Consulting Agreement:**
> "Draft a Consulting Agreement between Tech Solutions Ltd and independent consultant John Doe. The consultant will provide software architecture services for a period of 6 months. The consulting fee is ₹1,00,000 per month. The agreement falls under Maharashtra jurisdiction and must include a standard non-disclosure clause."

## 7. Legal Research Queries

**Procedural Query:**
> "What are the essential conditions for a valid Probate Petition in the Bombay High Court?"

**Case Law / Precedent Query:**
> "Are there any recent Supreme Court guidelines on the mandatory timeline for disposing of Section 138 NI Act cases?"

**Concept / Definition Query:**
> "What is the difference between Letters of Administration and a Probate Petition under the Indian Succession Act?"

**Jurisdictional Query:**
> "Does the Ordinary Original Civil Jurisdiction of the Bombay High Court cover disputes involving a property valued at ₹2 Crores situated in Pune?"

**Specific Case Study (Based on 2016 Death Certificate):**
> "What is the limitation period for filing a Probate Petition in Maharashtra if the testator passed away in 2016 and the petition is being filed in 2026?"

**Heirship Query:**
> "Under the Hindu Succession Act, who are the Class-I legal heirs of a Hindu male who dyed intestate, leaving behind a father and mother (as seen in the Sanjay Upadhyay certificate) but no spouse or children?"

## 8. Evidence-Based Drafting (With Uploaded Files)

**Probate Petition from Death Certificate:**
>  


ghost typing 


legal research 

Under the Hindu Succession Act, who are the Class-I legal heirs of a Hindu male who died intestate, leaving behind a father and mother but no spouse or children?

What are the mandatory documents required to file for Letters of Administration in the Bombay High Court when the deceased died without leaving a Will?

**Will referencing Deceased Family Member:**
> "Draft a Last Will and Testament for Mr. Vijaynath Upadhyay. Include a recital mentioning the demise of his son, Sanjay Vijaynath Upadhyay (referencing the uploaded death certificate), and bequeath the ancestral property in Thane to his wife, Mrs. Vidyadevi."

## Instructions for Testing
1. Copy one of the quotes above.
2. Paste it into the DroitDraft input interface.
3. Observe the generated document. Check if facts were properly extracted and formatted into the document blueprint. Notice how missing entities prompt the system to generate placeholders (e.g., `{{ client_name }}`) rather than hallucinating details.


**Legal Research**



1. What are the essential ingredients of a claim for eviction and recovery of arrears under the Maharashtra Rent Control Act, 1999?

2. What is the limitation period for filing a suit for specific performance under the Specific Relief Act read with the Limitation Act, 1963?

3. What are the legal requirements for a valid notice and prosecution under Section 138 of the Negotiable Instruments Act, 1881?

4. What provisions of the Transfer of Property Act, 1882 and the Indian Contract Act, 1872 are relevant for transfer of ownership through a sale deed?

5. What procedural requirements under the Code of Civil Procedure, 1908 and the Bombay High Court (Original Side) Rules apply when filing a civil matter on the original side of the Bombay High Court?

If you want broader coverage, also test:

6. What are the main grounds for interim injunction under the Specific Relief Act, 1963 and the Indian Evidence Act, 1872?

7. What are the core legal principles governing arbitration agreements under the Arbitration and Conciliation Act, 1996?

8. What duties and liabilities of partners arise under the Indian Partnership Act, 1932?

9. What are the key compliance and governance provisions relevant under the Companies Act, 2013 for a private company?

10. What are the main protections and dispute-resolution mechanisms under the Industrial Disputes Act, 1947?
