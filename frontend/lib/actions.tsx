"use server"

// Authentication Actions
export async function signIn(formData: FormData) {
  const email = formData.get("email") as string
  const password = formData.get("password") as string

  // Simulate authentication
  await new Promise((resolve) => setTimeout(resolve, 1000))

  if (email && password) {
    // In a real app, you'd validate credentials and create a session
    return { success: true, message: "Signed in successfully" }
  }

  return { success: false, message: "Invalid credentials" }
}

// Document Actions
export async function saveDocument(documentData: {
  id?: string
  title: string
  content: string
  type: string
}) {
  await new Promise((resolve) => setTimeout(resolve, 500))

  // In a real app, you'd save to database
  const documentId = documentData.id || `doc_${Date.now()}`

  return {
    success: true,
    documentId,
    message: "Document saved successfully",
    timestamp: new Date().toISOString(),
  }
}

export async function generateAIContent(prompt: string, documentType: string) {
  await new Promise((resolve) => setTimeout(resolve, 2000))

  // Simulate AI content generation based on prompt and document type
  const aiResponses: Record<string, string> = {
    "defamation notice": `
    <h3>DEFAMATION NOTICE</h3>
    <p>TO: [Recipient Name and Address]</p>
    <p>NOTICE OF DEFAMATORY STATEMENTS</p>
    <p>You are hereby notified that you have made false and defamatory statements about [Client Name] that have caused damage to their reputation and standing in the community.</p>
    <p>DEMAND FOR RETRACTION:</p>
    <ol>
      <li>Immediately cease and desist from making any further defamatory statements;</li>
      <li>Publish a full retraction of the false statements within [X] days;</li>
      <li>Provide written assurance that no further defamatory statements will be made.</li>
    </ol>
    <p>Failure to comply may result in legal action for damages.</p>
  `,
    "breach of contract": `
    <h3>BREACH OF CONTRACT NOTICE</h3>
    <p>TO: [Breaching Party Name and Address]</p>
    <p>NOTICE OF MATERIAL BREACH</p>
    <p>You are in material breach of the contract dated [Date] for failure to [specific breach details].</p>
    <p>CURE PERIOD:</p>
    <p>You have [X] days from receipt of this notice to cure the breach by [specific cure requirements].</p>
    <p>If the breach is not cured within the specified time period, we reserve the right to:</p>
    <ol>
      <li>Terminate the contract;</li>
      <li>Seek monetary damages;</li>
      <li>Pursue all available legal remedies.</li>
    </ol>
  `,
    "eviction notice": `
    <h3>NOTICE TO QUIT AND DELIVER UP POSSESSION</h3>
    <p>TO: [Tenant Name(s)] and all other occupants of the premises located at:</p>
    <p>[Property Address]</p>
    <p>YOU ARE HEREBY NOTIFIED that your tenancy is terminated effective [Date].</p>
    <p>REASON FOR TERMINATION:</p>
    <p>[Specific reason - non-payment of rent, lease violation, etc.]</p>
    <p>YOU ARE REQUIRED to quit and deliver up possession of the premises to the landlord within [X] days after service of this notice.</p>
    <p>If you fail to do so, legal proceedings will be instituted against you to recover possession, damages, and costs.</p>
  `,
    "cease and desist": `
    <h3>CEASE AND DESIST NOTICE</h3>
    <p>TO: [Recipient Name and Address]</p>
    <p>DEMAND TO CEASE AND DESIST</p>
    <p>You are hereby directed to immediately CEASE AND DESIST from [specific activity/behavior].</p>
    <p>Your actions constitute [legal violation - harassment, copyright infringement, etc.] and must stop immediately.</p>
    <p>DEMANDS:</p>
    <ol>
      <li>Immediately cease the prohibited activity;</li>
      <li>Provide written confirmation of compliance within [X] days;</li>
      <li>Refrain from any similar conduct in the future.</li>
    </ol>
    <p>Failure to comply will result in legal action seeking injunctive relief and damages.</p>
  `,
    "will clause": `
    <h3>TESTAMENTARY DISPOSITION</h3>
    <p>I, [Testator Name], being of sound mind and disposing memory, do hereby make, publish, and declare this to be my Last Will and Testament.</p>
    <p>ARTICLE I - REVOCATION</p>
    <p>I hereby revoke all former wills and codicils made by me.</p>
    <p>ARTICLE II - PERSONAL REPRESENTATIVE</p>
    <p>I nominate and appoint [Executor Name] as the Personal Representative of this Will.</p>
    <p>ARTICLE III - DISPOSITION OF PROPERTY</p>
    <p>I give, devise, and bequeath all of my property, both real and personal, to [Beneficiary Details].</p>
  `,
    "plaintiff complaint": `
    <h3>COMPLAINT FOR [CAUSE OF ACTION]</h3>
    <p>TO THE HONORABLE COURT:</p>
    <p>Plaintiff [Name] complains against Defendant [Name] and alleges:</p>
    <p>PARTIES</p>
    <p>1. Plaintiff is [description of plaintiff].</p>
    <p>2. Defendant is [description of defendant].</p>
    <p>JURISDICTION AND VENUE</p>
    <p>3. This Court has jurisdiction over this matter pursuant to [legal basis].</p>
    <p>CAUSE OF ACTION</p>
    <p>4. [Statement of facts giving rise to the claim].</p>
    <p>WHEREFORE, Plaintiff demands judgment against Defendant for [relief sought].</p>
  `,
    "confidentiality clause": `
    <h3>CONFIDENTIALITY</h3>
    <p>The parties acknowledge that they may have access to certain confidential information of the other party. Each party agrees to:</p>
    <ol>
      <li>Hold and maintain all confidential information in strict confidence;</li>
      <li>Not disclose confidential information to third parties without prior written consent;</li>
      <li>Use confidential information solely for the purposes of this agreement;</li>
      <li>Return or destroy all confidential information upon termination of this agreement.</li>
    </ol>
  `,
    "termination clause": `
    <h3>TERMINATION</h3>
    <p>This agreement may be terminated:</p>
    <ol>
      <li>By mutual written consent of both parties;</li>
      <li>By either party with thirty (30) days written notice;</li>
      <li>Immediately by either party in case of material breach that remains uncured after fifteen (15) days written notice;</li>
      <li>Immediately in case of bankruptcy, insolvency, or assignment for benefit of creditors.</li>
    </ol>
  `,
    "payment terms": `
    <h3>PAYMENT TERMS</h3>
    <p>Payment shall be made according to the following terms:</p>
    <ol>
      <li>All payments are due within thirty (30) days of invoice date;</li>
      <li>Late payments shall incur a service charge of 1.5% per month;</li>
      <li>All payments shall be made in U.S. dollars;</li>
      <li>Client is responsible for all bank fees and transaction costs.</li>
    </ol>
  `,
    "liability limitations": `
    <h3>LIMITATION OF LIABILITY</h3>
    <p>TO THE MAXIMUM EXTENT PERMITTED BY LAW:</p>
    <ol>
      <li>NEITHER PARTY SHALL BE LIABLE FOR INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES;</li>
      <li>EACH PARTY'S TOTAL LIABILITY SHALL NOT EXCEED THE TOTAL AMOUNT PAID UNDER THIS AGREEMENT;</li>
      <li>THESE LIMITATIONS APPLY REGARDLESS OF THE THEORY OF LIABILITY;</li>
      <li>THESE LIMITATIONS SHALL SURVIVE TERMINATION OF THIS AGREEMENT.</li>
    </ol>
  `,
  }

  // Find matching response or generate generic content
  const matchingKey = Object.keys(aiResponses).find((key) => prompt.toLowerCase().includes(key))

  const content = matchingKey
    ? aiResponses[matchingKey]
    : `
    <h3>AI GENERATED CONTENT</h3>
    <p>Based on your request: "${prompt}"</p>
    <p>This section would contain AI-generated legal content specific to ${documentType} documents. The AI would analyze your requirements and generate appropriate legal language, clauses, and formatting.</p>
    <p>Key considerations for this type of content would include:</p>
    <ul>
      <li>Legal compliance and current regulations</li>
      <li>Industry-specific requirements</li>
      <li>Jurisdictional considerations</li>
      <li>Best practices and standard clauses</li>
    </ul>
  `

  return {
    success: true,
    content,
    prompt,
  }
}

export async function shareDocument(documentId: string, email: string) {
  await new Promise((resolve) => setTimeout(resolve, 1000))

  return {
    success: true,
    message: `Document shared with ${email}`,
    shareLink: `https://droitdraft.com/shared/${documentId}`,
  }
}
