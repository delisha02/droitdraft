"use client"

import { useState, useRef, useEffect, Suspense } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Separator } from "@/components/ui/separator"
import { Badge } from "@/components/ui/badge"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import {
  Bold,
  Italic,
  Underline,
  AlignLeft,
  AlignCenter,
  AlignRight,
  AlignJustify,
  List,
  ListOrdered,
  Save,
  Download,
  Printer as Print,
  Undo,
  Redo,
  Scale,
  Bot,
  FileText,
  Share,
  Strikethrough,
  Subscript,
  Superscript,
  Indent,
  Outdent,
  Table,
  ImageIcon,
  Link,
  Type,
  Sparkles,
  FileUp,
  X,
  Loader2,
  Paperclip,
  Trash2,
  Scan,
  Info,
} from "lucide-react"
import LinkComponent from "next/link"
import { useSearchParams, useRouter } from "next/navigation"
import { useDocument } from "@/hooks/use-document"
import { ShareModal } from "@/components/share-modal"
import * as React from "react"
import { useGhostTyping } from "@/hooks/use-ghost-typing"
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip"

const CITATION_REGEX = /(?:Section|Section|s\.)\s+\d+\s+of\s+[^.,;|\n]+|(?:\*|")[^"*]+\*?"?\s*,\s*(?:\d{4}[:\s])?[A-Z]+\s*(?:[-:\s]\d+)?/gi;

interface CitationLinkProps {
  text: string;
  sources: any[];
}

const CitationLink = ({ text, sources }: CitationLinkProps) => {
  const source = sources.find(s =>
    text.toLowerCase().includes(s.title?.toLowerCase()) ||
    (s.source && text.toLowerCase().includes(s.source.toLowerCase()))
  );

  if (!source) return <span className="font-medium text-indigo-700">{text}</span>;

  return (
    <TooltipProvider>
      <Tooltip>
        <TooltipTrigger asChild>
          <span className="font-semibold text-blue-700 border-b border-blue-200 cursor-help hover:bg-blue-50 px-0.5 rounded transition-colors">
            {text}
          </span>
        </TooltipTrigger>
        <TooltipContent className="max-w-xs p-3">
          <div className="space-y-1.5">
            <p className="font-bold text-xs">{source.title}</p>
            <p className="text-[10px] text-gray-500">{source.source}</p>
            {source.url && (
              <a
                href={source.url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-[10px] text-blue-600 hover:underline block mt-1"
              >
                View full document
              </a>
            )}
          </div>
        </TooltipContent>
      </Tooltip>
    </TooltipProvider>
  );
};

const renderWithCitations = (answer: string, sources: any[]) => {
  if (!answer) return null;

  const parts = answer.split(CITATION_REGEX);
  const matches = answer.match(CITATION_REGEX);

  if (!matches) return <p className="whitespace-pre-wrap">{answer}</p>;

  return (
    <p className="whitespace-pre-wrap">
      {parts.map((part, i) => (
        <React.Fragment key={i}>
          {part}
          {matches[i] && <CitationLink text={matches[i]} sources={sources} />}
        </React.Fragment>
      ))}
    </p>
  );
};

const documentTemplates = {
  // These will serve as fallbacks if the fetch fails
  notices: "Legal Notice",
  will: "Last Will & Testament",
  probate: "Probate Petition",
  "letters-of-administration": "Letters of Administration",
  "sale-deed": "Sale Deed",
  "development-agreement": "Development Agreement",
  contracts: "General Agreement",
}

/**
 * Converts basic Markdown/Plaintext with \n to HTML for the editor
 */
const formatToHtml = (text: string): string => {
  if (!text) return "";

  // 1. Handle Markdown Headers (# Title)
  let html = text.replace(/^# (.*$)/gm, '<h1 class="text-2xl font-bold mb-4">$1</h1>');
  html = html.replace(/^## (.*$)/gm, '<h2 class="text-xl font-bold mb-3">$1</h2>');
  html = html.replace(/^### (.*$)/gm, '<h3 class="text-lg font-bold mb-2">$1</h3>');

  // 2. Handle Bold (**text**)
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');

  // 3. Handle Italics (*text*)
  html = html.replace(/\*(.*?)\*/g, '<em>$1</em>');

  // 4. Handle Line Breaks (\n)
  // Double newlines -> Paragraphs
  html = html.split('\n\n').map(p => {
    if (p.trim().startsWith('<h')) return p; // Skip already handled headers
    return `<p class="mb-4">${p.replace(/\n/g, '<br />')}</p>`;
  }).join('');

  return html;
};

const fontFamilies = [
  "Times New Roman",
  "Arial",
  "Calibri",
  "Georgia",
  "Verdana",
  "Helvetica",
  "Courier New",
  "Comic Sans MS",
]

const fontSizes = ["8", "9", "10", "11", "12", "14", "16", "18", "20", "24", "28", "32", "36", "48", "72"]

const lineHeights = ["1.0", "1.15", "1.5", "2.0", "2.5", "3.0"]

function EditorContent() {
  const searchParams = useSearchParams()
  const docType = searchParams.get("type") || "contracts"
  const [isShareModalOpen, setIsShareModalOpen] = useState(false)
  const [currentFont, setCurrentFont] = useState("Times New Roman")
  const [currentFontSize, setCurrentFontSize] = useState("12")
  const [currentLineHeight, setCurrentLineHeight] = useState("1.5")
  const [aiPrompt, setAiPrompt] = useState("")
  const [templateData, setTemplateData] = useState<any>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [isExtracting, setIsExtracting] = useState<string | null>(null)
  const [uploadedFiles, setUploadedFiles] = useState<{ id: string, name: string }[]>([])
  const [researchQuery, setResearchQuery] = useState("")
  const [researchResult, setResearchResult] = useState<{ answer: string, sources: any[] } | null>(null)
  const [isResearching, setIsResearching] = useState(false)
  const [activeTab, setActiveTab] = useState<"drafting" | "research">("drafting")
  const editorRef = useRef<HTMLDivElement>(null)
  const typingTimerRef = useRef<any>(null)
  const router = useRouter()

  const { suggestion, fetchSuggestion, clearSuggestion } = useGhostTyping({
    caseFacts: templateData || {},
    docType: docType
  })

  useEffect(() => {
    const isAuthenticated = localStorage.getItem("isAuthenticated");
    if (isAuthenticated !== "true") {
      router.push("/auth/signin");
    }
  }, [router]);

  const {
    document: doc,
    isSaving,
    lastSaved,
    isFetching,
    handleSave: handleSaveHook,
    fetchDocument,
    updateDocument,
    handleGenerateAI: handleAiGenerateFromHook,
    isGenerating,
  } = useDocument({
    title: `Untitled ${documentTemplates[docType as keyof typeof documentTemplates] || "Document"}`,
    content: "",
    type: docType,
  })

  useEffect(() => {
    const docId = searchParams.get("id");
    if (docId) {
      fetchDocument(docId);
    } else if (docType) {
      const fetchTemplate = async () => {
        const token = localStorage.getItem("accessToken");
        try {
          // Determine if docType is a numeric ID or a category name
          const isId = /^\d+$/.test(docType);
          const endpoint = isId
            ? `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/templates/${docType}`
            : `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/templates/type/${docType}`;

          const response = await fetch(endpoint, {
            headers: { Authorization: `Bearer ${token}` }
          });
          if (response.ok) {
            const data = await response.json();
            console.log("Template fetched successfully:", data.name);
            setTemplateData(data);
          } else {
            console.error("Failed to fetch template:", await response.text());
          }
        } catch (error) {
          console.error("Failed to fetch template", error);
        }
      };
      fetchTemplate();
    }
  }, [searchParams, fetchDocument, docType]);

  const handleSave = async () => {
    const savedDoc = await handleSaveHook();
    if (savedDoc && savedDoc.id && !searchParams.get("id")) {
      // Update URL with the new ID without reloading the page
      router.replace(`/editor?type=${docType}&id=${savedDoc.id}`);
    }
  }

  // Rich text formatting functions
  const execCommand = (command: string, value?: string) => {
    try {
      if (editorRef.current) {
        editorRef.current.focus()
        const success = window.document.execCommand(command, false, value)
        if (!success) {
          console.warn(`Command ${command} failed`)
        }
        updateContentFromEditor()
      }
    } catch (error) {
      console.error(`Error executing command ${command}:`, error)
    }
  }

  const formatText = (command: string, value?: string) => {
    if (!editorRef.current) return

    // Ensure the editor is focused
    editorRef.current.focus()

    try {
      switch (command) {
        case "bold":
          execCommand("bold")
          break
        case "italic":
          execCommand("italic")
          break
        case "underline":
          execCommand("underline")
          break
        case "strikethrough":
          execCommand("strikeThrough")
          break
        case "subscript":
          execCommand("subscript")
          break
        case "superscript":
          execCommand("superscript")
          break
        case "justifyLeft":
        case "justifyCenter":
        case "justifyRight":
        case "justifyFull":
          execCommand(command)
          break
        case "insertUnorderedList":
        case "insertOrderedList":
          execCommand(command)
          break
        case "indent":
          execCommand("indent")
          break
        case "outdent":
          execCommand("outdent")
          break
        case "fontName":
          if (value) {
            execCommand("fontName", value)
            setCurrentFont(value)
          }
          break
        case "fontSize":
          if (value) {
            // Convert point size to HTML font size (1-7 scale)
            const htmlSize = Math.min(7, Math.max(1, Math.floor(Number.parseInt(value) / 4)))
            execCommand("fontSize", htmlSize.toString())
            setCurrentFontSize(value)
          }
          break
        case "foreColor":
          if (value) execCommand("foreColor", value)
          break
        case "hiliteColor":
          if (value) execCommand("hiliteColor", value)
          break
        case "createLink":
          const url = prompt("Enter URL:")
          if (url) execCommand("createLink", url)
          break
        case "insertImage":
          const imageUrl = prompt("Enter image URL:")
          if (imageUrl) execCommand("insertImage", imageUrl)
          break
        case "insertTable":
          insertTable()
          break
        case "undo":
          execCommand("undo")
          break
        case "redo":
          execCommand("redo")
          break
        default:
          execCommand(command, value)
      }
    } catch (error) {
      console.error(`Error in formatText for command ${command}:`, error)
    }
  }

  const insertTable = () => {
    try {
      const rows = prompt("Number of rows:") || "3"
      const cols = prompt("Number of columns:") || "3"

      let tableHTML = '<table border="1" style="border-collapse: collapse; width: 100%; margin: 10px 0;">'
      for (let i = 0; i < Number.parseInt(rows); i++) {
        tableHTML += "<tr>"
        for (let j = 0; j < Number.parseInt(cols); j++) {
          tableHTML +=
            '<td style="padding: 8px; border: 1px solid #ccc; min-width: 100px; min-height: 20px;">&nbsp;</td>'
        }
        tableHTML += "</tr>"
      }
      tableHTML += "</table><p>&nbsp;</p>"

      // Insert table using insertHTML or manual insertion
      if (editorRef.current) {
        const selection = window.getSelection()
        if (selection && selection.rangeCount > 0) {
          const range = selection.getRangeAt(0)
          const tableElement = window.document.createElement("div")
          tableElement.innerHTML = tableHTML
          range.insertNode(tableElement)
          updateContentFromEditor()
        }
      }
    } catch (error) {
      console.error("Error inserting table:", error)
    }
  }

  const applyLineHeight = (height: string) => {
    if (!editorRef.current) return

    try {
      const selection = window.getSelection()
      if (selection && selection.rangeCount > 0) {
        const range = selection.getRangeAt(0)
        const selectedContent = range.extractContents()
        const div = window.document.createElement("div")
        div.style.lineHeight = height
        div.appendChild(selectedContent)
        range.insertNode(div)
        updateContentFromEditor()
      } else {
        // Apply to entire editor if no selection
        editorRef.current.style.lineHeight = height
      }
      setCurrentLineHeight(height)
    } catch (error) {
      console.error("Error applying line height:", error)
    }
  }

  const updateContentFromEditor = () => {
    if (editorRef.current) {
      // Clear any existing ghost spans before saving/updating state
      const ghostSpan = editorRef.current.querySelector('.ghost-suggestion');
      if (ghostSpan) ghostSpan.remove();

      const newContent = editorRef.current.innerHTML;
      updateDocument({ content: newContent })

      // Trigger ghost typing suggestion if tab is active
      clearSuggestion();
      if (typingTimerRef.current) clearTimeout(typingTimerRef.current);
      typingTimerRef.current = setTimeout(() => {
        const text = editorRef.current?.innerText || "";
        if (text.length > 20) {
          fetchSuggestion(text);
        }
      }, 1000); // 1s delay
    }
  }

  // Effect to render ghost suggestion
  useEffect(() => {
    if (suggestion && editorRef.current) {
      // Remove old suggestion if any
      const oldGhost = editorRef.current.querySelector('.ghost-suggestion');
      if (oldGhost) oldGhost.remove();

      // We only insert at the VERY END of the content for now to keep it simple and safe
      const ghostSpan = window.document.createElement('span');
      ghostSpan.className = 'ghost-suggestion text-gray-400 opacity-50 select-none';
      ghostSpan.setAttribute('contenteditable', 'false');
      ghostSpan.innerText = suggestion;

      // Appending to the current selection/focus if possible
      const selection = window.getSelection();
      if (selection && selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        // Only show if cursor is at the end of a node
        if (range.collapsed) {
          range.insertNode(ghostSpan);
        }
      }
    }
  }, [suggestion]);

  const acceptSuggestion = () => {
    if (!editorRef.current) return;
    const ghostSpan = editorRef.current.querySelector('.ghost-suggestion');
    if (ghostSpan) {
      const text = ghostSpan.textContent || "";
      ghostSpan.remove();

      // Insert as real text at the current cursor position
      const selection = window.getSelection();
      if (selection && selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        const textNode = window.document.createTextNode(text);
        range.insertNode(textNode);
        range.setStartAfter(textNode);
        range.collapse(true);
        selection.removeAllRanges();
        selection.addRange(range);
      }

      clearSuggestion();
      updateContentFromEditor();
    }
  };

  const handlePrint = () => {
    try {
      const printWindow = window.open("", "_blank")
      if (printWindow && editorRef.current) {
        printWindow.document.write(`
          <html>
            <head>
              <title>${doc.title}</title>
              <style>
                body { 
                  font-family: ${currentFont}; 
                  font-size: ${currentFontSize}pt; 
                  line-height: ${currentLineHeight}; 
                  margin: 1in;
                  color: #000;
                }
                table { border-collapse: collapse; width: 100%; }
                table, th, td { border: 1px solid #000; }
                th, td { padding: 8px; text-align: left; }
                @media print { 
                  body { margin: 1in; } 
                  @page { margin: 1in; }
                }
              </style>
            </head>
            <body>${editorRef.current.innerHTML}</body>
          </html>
        `)
        printWindow.document.close()
        printWindow.print()
      }
    } catch (error) {
      console.error("Error printing:", error)
      alert("Print failed. Please try again.")
    }
  }

  const handleExport = async (format: "pdf" | "docx" | "doc") => {
    try {
      const response = await fetch("/api/documents/export", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          content: editorRef.current?.innerHTML || "",
          title: doc.title,
          format,
          font: currentFont,
          fontSize: currentFontSize,
          lineHeight: currentLineHeight,
        }),
      })

      const result = await response.json()

      if (result.success) {
        // Create download link
        const link = window.document.createElement("a")
        link.href = result.downloadUrl
        link.download = `${doc.title}.${format}`
        window.document.body.appendChild(link)
        link.click()
        window.document.body.removeChild(link)
      } else {
        alert(`Export failed: ${result.message}`)
      }
    } catch (error) {
      console.error("Export error:", error)
      alert("Export failed. Please try again.")
    }
  }

  const handleAiGenerate = async () => {
    // We need at least a prompt OR a file to proceed
    if (!aiPrompt.trim() && uploadedFiles.length === 0) return;

    // 1. If only files are present (no prompt), it's a "Populate from Evidence" flow
    if (!aiPrompt.trim() && uploadedFiles.length > 0) {
      // For now, scan the first file to populate the template
      await handleScanFacts(uploadedFiles[0].id);
      return;
    }

    // 2. Otherwise, it's a Drafting flow (Prompt only OR Prompt + Evidence)
    const fileIds = uploadedFiles.map(f => f.id);
    console.log("Starting AI generation with template ID:", templateData?.id);

    try {
      const generatedContent = await handleAiGenerateFromHook(aiPrompt, fileIds, templateData?.id);

      if (generatedContent && editorRef.current) {
        // The backend returns the FULL formatted document now.
        // We should replace the content to ensure consistency.
        editorRef.current.innerHTML = formatToHtml(generatedContent);
        updateContentFromEditor();
        setAiPrompt("");
      } else if (!generatedContent) {
        alert("The AI assistant was unable to generate content for this request. Please try a different prompt or check your files.");
      }
    } catch (error) {
      console.error("AI Generation error:", error);
      alert("A system error occurred during generation. Please check the console for details.");
    }
  }

  const handleResearchQuery = async () => {
    if (!researchQuery.trim()) return;

    setIsResearching(true);
    const token = localStorage.getItem("accessToken");
    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/research/query`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify({
          query: researchQuery,
          limit: 5
        })
      });

      if (response.ok) {
        const data = await response.json();
        setResearchResult(data);
      } else {
        alert("Failed to perform research.");
      }
    } catch (error) {
      console.error("Research error:", error);
      alert("An error occurred during research.");
    } finally {
      setIsResearching(false);
    }
  }

  const hasSyncedRef = useRef(false);

  const insertToDraft = (content: string) => {
    if (!editorRef.current) return;

    const selection = window.getSelection();
    if (selection && selection.rangeCount > 0) {
      const range = selection.getRangeAt(0);
      range.deleteContents();
      const div = window.document.createElement("div");
      div.innerHTML = formatToHtml(content);
      const frag = window.document.createDocumentFragment();
      let node, lastNode;
      while ((node = div.firstChild)) {
        lastNode = frag.appendChild(node);
      }
      range.insertNode(frag);

      // Move cursor after the inserted content
      if (lastNode) {
        range.setStartAfter(lastNode);
        range.collapse(true);
        selection.removeAllRanges();
        selection.addRange(range);
      }

      updateContentFromEditor();
    } else {
      // Fallback: append to end
      editorRef.current.innerHTML += formatToHtml(content);
      updateContentFromEditor();
    }
  };

  // Sync document content to editor
  useEffect(() => {
    if (!editorRef.current || hasSyncedRef.current || isFetching) return;

    const docId = searchParams.get("id");

    if (docId && doc.content) {
      // Load existing document
      console.log("Syncing existing document to editor");
      editorRef.current.innerHTML = doc.content;
      hasSyncedRef.current = true;
    } else if (!docId && templateData) {
      // Load template for new document
      console.log("Syncing template to editor:", templateData.name);
      const currentDate = new Date().toLocaleDateString('en-GB'); // DD/MM/YYYY
      const processedContent = templateData.content.replace(/\{\{\s*drafting_date\s*\}\}/g, currentDate);
      const finalHtml = formatToHtml(processedContent);
      editorRef.current.innerHTML = finalHtml;
      updateDocument({
        title: templateData.name,
        content: finalHtml,
        type: docType
      });
      hasSyncedRef.current = true;
    }
  }, [isFetching, doc.content, templateData, editorRef.current, doc.id]);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const token = localStorage.getItem("accessToken");
    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/upload/`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
        body: formData,
      });

      console.log("Upload response status:", response.status);

      if (response.ok) {
        const data = await response.json();
        setUploadedFiles(prev => [...prev, { id: data.filename, name: data.original_name }]);
      } else {
        alert("Failed to upload file.");
      }
    } catch (error) {
      console.error("Upload error:", error);
      alert("An error occurred during upload.");
    } finally {
      setIsUploading(false);
    }
  };

  const removeFile = (id: string) => {
    setUploadedFiles(prev => prev.filter(f => f.id !== id));
  };

  const handleScanFacts = async (id: string) => {
    setIsExtracting(id);
    const token = localStorage.getItem("accessToken");
    try {
      const encodedId = encodeURIComponent(id);
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/upload/extract/${encodedId}`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        applyFactsToDraft(data.facts);
      } else {
        alert("Failed to extract facts.");
      }
    } catch (error) {
      console.error("Extraction error:", error);
      alert("An error occurred during scanning.");
    } finally {
      setIsExtracting(null);
    }
  };

  const applyFactsToDraft = (facts: any) => {
    if (!editorRef.current) return;
    let content = editorRef.current.innerHTML;

    // Map extracted facts to common placeholders
    const mappings: { [key: string]: string } = {};

    // Parties
    if (facts.parties) {
      facts.parties.forEach((p: any, i: number) => {
        const role = p.role?.toLowerCase() || '';
        const prefix = role || `party${i + 1}`;

        // General mappings
        mappings[`{{ ${prefix}_name }}`] = p.name;
        mappings[`{{ ${prefix}_full_name }}`] = p.name;
        mappings[`{{ ${prefix}_address }}`] = p.address;

        // Specific role-based mappings for Maharashtra templates
        if (role === 'testator') {
          mappings['{{ testator_full_name }}'] = p.name;
          mappings['{{ testator_address }}'] = p.address;
        } else if (role === 'executor') {
          mappings['{{ executor_name }}'] = p.name;
          mappings['{{ executor_address }}'] = p.address;
        } else if (role === 'deceased') {
          mappings['{{ deceased_name }}'] = p.name;
          mappings['{{ deceased_address }}'] = p.address;
        } else if (role === 'seller' || role === 'vendor') {
          mappings['{{ seller_name }}'] = p.name;
          mappings['{{ seller_address }}'] = p.address;
        } else if (role === 'buyer' || role === 'purchaser') {
          mappings['{{ buyer_name }}'] = p.name;
          mappings['{{ buyer_address }}'] = p.address;
        } else if (role === 'petitioner') {
          mappings['{{ petitioner_name }}'] = p.name;
        }
      });
    }

    // Dates
    if (facts.timeline) {
      facts.timeline.forEach((t: any) => {
        const desc = t.description?.toLowerCase() || '';
        if (desc.includes("death")) {
          mappings['{{ date_of_death }}'] = t.date;
        } else if (desc.includes("execution") || desc.includes("signed")) {
          mappings['{{ date_of_execution }}'] = t.date;
          mappings['{{ will_date }}'] = t.date;
        } else if (desc.includes("notice")) {
          mappings['{{ date_of_notice }}'] = t.date;
        }
      });
    }

    // Location
    if (facts.location) {
      mappings['{{ place_of_execution }}'] = facts.location;
      mappings['{{ place_of_death }}'] = facts.location;
      mappings['{{ location }}'] = facts.location;
    }

    // Apply mappings
    let matchCount = 0;

    Object.keys(mappings).forEach(key => {
      if (mappings[key]) {
        // Create a robust regex: 
        // 1. Escape special characters
        // 2. Allow any amount of whitespace (\s*) where a space exists in the key
        // 3. Case-insensitive matching
        const escapedKey = key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
          .replace(/\\ /g, '\\s*');
        const regex = new RegExp(escapedKey, 'gi');

        if (content.match(regex)) {
          content = content.replace(regex, `<span class="bg-yellow-100 border-b border-yellow-400 font-medium">${mappings[key]}</span>`);
          matchCount++;
        }
      }
    });

    if (matchCount > 0) {
      editorRef.current.innerHTML = content;
      updateDocument({ content });
      alert(`Facts extracted! ${matchCount} types of facts were populated and highlighted.`);
    } else {
      alert("No matching {{ placeholders }} were found in this document to populate with extracted facts.");
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <LinkComponent href="/dashboard" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Scale className="w-5 h-5 text-white" />
              </div>
              <span className="font-semibold text-gray-900">DroitDraft</span>
            </LinkComponent>
            <Separator orientation="vertical" className="h-6" />
            <LinkComponent href="/dashboard" className="text-sm font-medium text-gray-500 hover:text-gray-900 transition-colors">
              Dashboard
            </LinkComponent>
            <Separator orientation="vertical" className="h-6" />
            <div className="flex items-center space-x-2">
              <FileText className="w-4 h-4 text-gray-600" />
              <Input
                value={doc.title}
                onChange={(e) => updateDocument({ title: e.target.value })}
                className="border-none bg-transparent text-sm font-medium focus:bg-white focus:border focus:border-gray-300 min-w-[300px]"
              />
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <Badge
              variant="secondary"
              className={isSaving ? "bg-yellow-100 text-yellow-800" : "bg-green-100 text-green-800"}
            >
              {isSaving ? "Saving..." : lastSaved ? "Auto-saved" : "Unsaved"}
            </Badge>
            <Button variant="outline" size="sm" onClick={() => setIsShareModalOpen(true)}>
              <Share className="w-4 h-4 mr-2" />
              Share
            </Button>
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700" onClick={handleSave} disabled={isSaving || isFetching}>
              <Save className="w-4 h-4 mr-2" />
              {isSaving ? "Saving..." : "Save"}
            </Button>
          </div>
        </div>
      </header>

      {isFetching && (
        <div className="absolute inset-0 bg-white/50 backdrop-blur-sm z-[100] flex items-center justify-center">
          <div className="flex flex-col items-center space-y-4">
            <Scale className="w-12 h-12 text-blue-600 animate-pulse" />
            <p className="text-lg font-medium text-gray-900">Loading document...</p>
          </div>
        </div>
      )}

      {/* Toolbar */}
      <div className="bg-white border-b border-gray-200 px-4 py-2">
        <div className="flex items-center space-x-1 flex-wrap gap-y-2">
          {/* File Operations */}
          <div className="flex items-center space-x-1">
            <Button variant="ghost" size="sm" onClick={() => formatText("undo")}>
              <Undo className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => formatText("redo")}>
              <Redo className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={handlePrint}>
              <Print className="w-4 h-4" />
            </Button>
            <div className="relative group">
              <Button variant="ghost" size="sm" className="flex items-center">
                <Download className="w-4 h-4 mr-1" />
                Export
              </Button>
              <div className="absolute top-full left-0 mt-1 bg-white border rounded shadow-lg z-10 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleExport("pdf")}
                  className="w-full justify-start whitespace-nowrap"
                >
                  Export as PDF
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleExport("docx")}
                  className="w-full justify-start whitespace-nowrap"
                >
                  Export as DOCX
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => handleExport("doc")}
                  className="w-full justify-start whitespace-nowrap"
                >
                  Export as DOC
                </Button>
              </div>
            </div>
          </div>

          <Separator orientation="vertical" className="h-6" />

          {/* Font Controls */}
          <div className="flex items-center space-x-1">
            <Select value={currentFont} onValueChange={(value) => formatText("fontName", value)}>
              <SelectTrigger className="w-40">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {fontFamilies.map((font) => (
                  <SelectItem key={font} value={font} style={{ fontFamily: font }}>
                    {font}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={currentFontSize} onValueChange={(value) => formatText("fontSize", value)}>
              <SelectTrigger className="w-16">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {fontSizes.map((size) => (
                  <SelectItem key={size} value={size}>
                    {size}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            <Select value={currentLineHeight} onValueChange={applyLineHeight}>
              <SelectTrigger className="w-16">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                {lineHeights.map((height) => (
                  <SelectItem key={height} value={height}>
                    {height}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <Separator orientation="vertical" className="h-6" />

          {/* Text Formatting */}
          <div className="flex items-center space-x-1">
            <Button variant="ghost" size="sm" onClick={() => formatText("bold")}>
              <Bold className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => formatText("italic")}>
              <Italic className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => formatText("underline")}>
              <Underline className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => formatText("strikethrough")}>
              <Strikethrough className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => formatText("subscript")}>
              <Subscript className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => formatText("superscript")}>
              <Superscript className="w-4 h-4" />
            </Button>
          </div>

          <Separator orientation="vertical" className="h-6" />

          {/* Colors */}
          <div className="flex items-center space-x-1">
            <input
              type="color"
              onChange={(e) => formatText("foreColor", e.target.value)}
              className="w-8 h-8 border rounded cursor-pointer"
              title="Text Color"
            />
            <input
              type="color"
              onChange={(e) => formatText("hiliteColor", e.target.value)}
              className="w-8 h-8 border rounded cursor-pointer"
              title="Highlight Color"
            />
          </div>

          <Separator orientation="vertical" className="h-6" />

          {/* Alignment */}
          <div className="flex items-center space-x-1">
            <Button variant="ghost" size="sm" onClick={() => formatText("justifyLeft")}>
              <AlignLeft className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => formatText("justifyCenter")}>
              <AlignCenter className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => formatText("justifyRight")}>
              <AlignRight className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => formatText("justifyFull")}>
              <AlignJustify className="w-4 h-4" />
            </Button>
          </div>

          <Separator orientation="vertical" className="h-6" />

          {/* Lists and Indentation */}
          <div className="flex items-center space-x-1">
            <Button variant="ghost" size="sm" onClick={() => formatText("insertUnorderedList")}>
              <List className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => formatText("insertOrderedList")}>
              <ListOrdered className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => formatText("outdent")}>
              <Outdent className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => formatText("indent")}>
              <Indent className="w-4 h-4" />
            </Button>
          </div>

          <Separator orientation="vertical" className="h-6" />

          {/* Insert Options */}
          <div className="flex items-center space-x-1">
            <Button variant="ghost" size="sm" onClick={() => formatText("insertTable")}>
              <Table className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => formatText("insertImage")}>
              <ImageIcon className="w-4 h-4" />
            </Button>
            <Button variant="ghost" size="sm" onClick={() => formatText("createLink")}>
              <Link className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>

      {/* Main Editor Area */}
      <div className="flex-1 flex">
        {/* AI Assistant Sidebar */}
        <div className="w-80 bg-white border-r border-gray-200 flex flex-col">
          <div className="flex border-b">
            <button
              onClick={() => setActiveTab("drafting")}
              className={`flex-1 py-3 text-sm font-medium transition-colors ${activeTab === "drafting"
                ? "text-blue-600 border-b-2 border-blue-600"
                : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                }`}
            >
              Drafting
            </button>
            <button
              onClick={() => setActiveTab("research")}
              className={`flex-1 py-3 text-sm font-medium transition-colors ${activeTab === "research"
                ? "text-blue-600 border-b-2 border-blue-600"
                : "text-gray-500 hover:text-gray-700 hover:bg-gray-50"
                }`}
            >
              Research
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {activeTab === "drafting" ? (
              <>
                <div className="flex items-center space-x-2 mb-4">
                  <Bot className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold text-gray-900">AI Draftsman</h3>
                </div>

                <div className="space-y-3">
                  <div className="relative border rounded-md focus-within:ring-1 focus-within:ring-blue-500 bg-white">
                    <Textarea
                      placeholder="Describe the document or upload evidence..."
                      value={aiPrompt}
                      onChange={(e) => setAiPrompt(e.target.value)}
                      className="min-h-[120px] resize-none border-0 focus-visible:ring-0 pr-10 text-xs"
                    />
                    <div className="absolute bottom-2 right-2 flex items-center space-x-2">
                      <input
                        type="file"
                        id="unified-upload"
                        className="hidden"
                        onChange={handleFileUpload}
                        accept=".pdf,image/*"
                      />
                      <label
                        htmlFor="unified-upload"
                        className="p-1.5 text-gray-400 hover:text-blue-600 cursor-pointer rounded-md hover:bg-gray-100 transition-colors"
                      >
                        <Paperclip className="w-4 h-4" />
                      </label>
                    </div>
                  </div>

                  {uploadedFiles.length > 0 && (
                    <div className="flex flex-wrap gap-2 py-1">
                      {uploadedFiles.map((file) => (
                        <Badge key={file.id} variant="secondary" className="px-2 py-1 flex items-center gap-1.5 bg-blue-50 text-blue-700 border-blue-100">
                          <FileText className="w-3 h-3" />
                          <span className="max-w-[120px] truncate text-[10px]">{file.name}</span>
                          <button onClick={() => removeFile(file.id)} className="hover:text-red-600">
                            <X className="w-3 h-3" />
                          </button>
                        </Badge>
                      ))}
                    </div>
                  )}

                  <Button
                    onClick={handleAiGenerate}
                    className="w-full bg-blue-600 hover:bg-blue-700 h-9"
                    disabled={isGenerating || isUploading || (!!isExtracting) || (!aiPrompt.trim() && uploadedFiles.length === 0)}
                  >
                    {isGenerating || isExtracting ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Sparkles className="w-4 h-4 mr-2" />
                    )}
                    {isGenerating ? "Generating..." : isExtracting ? "Extracting..." : "Draft Document"}
                  </Button>
                </div>

                <Separator />

                <div>
                  <h4 className="text-[10px] font-semibold text-gray-500 uppercase tracking-wider mb-2">Quick Drafts</h4>
                  <div className="space-y-1">
                    {[
                      "Draft a Probate Petition for Maharashtra High Court",
                      "Draft a Legal Notice for recovery of dues",
                    ].map((suggestion, index) => (
                      <Button
                        key={index}
                        variant="ghost"
                        size="sm"
                        className="w-full justify-start text-[11px] h-auto py-1.5 px-2 text-left hover:bg-gray-50"
                        onClick={() => setAiPrompt(suggestion)}
                      >
                        <Type className="w-3 h-3 mr-2 flex-shrink-0 text-gray-400" />
                        <span className="truncate">{suggestion}</span>
                      </Button>
                    ))}
                  </div>
                </div>
              </>
            ) : (
              <>
                <div className="flex items-center space-x-2 mb-4">
                  <Scan className="w-5 h-5 text-blue-600" />
                  <h3 className="font-semibold text-gray-900">Research Sandbox</h3>
                </div>

                <div className="space-y-3">
                  <div className="relative border rounded-md focus-within:ring-1 focus-within:ring-blue-500 bg-white">
                    <Textarea
                      placeholder="Ask a legal question (e.g., Probate rules in Mumbai)..."
                      value={researchQuery}
                      onChange={(e) => setResearchQuery(e.target.value)}
                      className="min-h-[100px] resize-none border-0 focus-visible:ring-0 text-xs"
                    />
                  </div>
                  <Button
                    onClick={handleResearchQuery}
                    className="w-full bg-indigo-600 hover:bg-indigo-700 h-9"
                    disabled={isResearching || !researchQuery.trim()}
                  >
                    {isResearching ? (
                      <Loader2 className="w-4 h-4 animate-spin mr-2" />
                    ) : (
                      <Scale className="w-4 h-4 mr-2" />
                    )}
                    {isResearching ? "Researching..." : "Search Legal Base"}
                  </Button>
                </div>

                {researchResult && (
                  <div className="space-y-4 pt-2">
                    <div className="bg-slate-50 border rounded-p-3 p-3 text-xs leading-relaxed text-gray-700">
                      {renderWithCitations(researchResult.answer, researchResult.sources)}
                    </div>

                    {researchResult.sources.length > 0 && (
                      <div className="space-y-2">
                        <h4 className="text-[10px] font-bold text-gray-500 uppercase">Cited Sources</h4>
                        {researchResult.sources.map((source, i) => (
                          <div key={i} className="bg-white border rounded p-2 text-[10px] hover:border-blue-300 transition-colors">
                            <p className="font-semibold text-gray-900 truncate">{source.title}</p>
                            <p className="text-gray-500">{source.source}</p>
                            <div className="flex items-center space-x-2 mt-2">
                              {source.url && (
                                <a href={source.url} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
                                  View
                                </a>
                              )}
                              <Button
                                variant="ghost"
                                size="sm"
                                className="h-6 px-2 text-[10px] text-indigo-600 hover:text-indigo-700 hover:bg-indigo-50"
                                onClick={() => insertToDraft(`**Source: ${source.title}**\n\n${source.source || ""}`)}
                              >
                                Insert to Draft
                              </Button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}

                <div className="bg-blue-50 p-3 rounded text-[10px] text-blue-700">
                  <p>Ground your drafting in live Maharashtra judgments and LiveLaw top stories.</p>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Editor */}
        <div className="flex-1 p-8 overflow-auto">
          <div className="max-w-4xl mx-auto">
            <div
              ref={editorRef}
              contentEditable
              className="min-h-[800px] bg-white shadow-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 p-16"
              style={{
                fontFamily: currentFont,
                fontSize: `${currentFontSize}pt`,
                lineHeight: currentLineHeight,
                width: "8.5in",
                minHeight: "11in",
              }}
              onInput={updateContentFromEditor}
              onKeyDown={(e) => {
                // Handle Tab for Ghost Typing
                if (e.key === "Tab" && suggestion) {
                  e.preventDefault();
                  acceptSuggestion();
                  return;
                }

                // Handle keyboard shortcuts
                if (e.ctrlKey || e.metaKey) {
                  switch (e.key) {
                    case "b":
                      e.preventDefault()
                      formatText("bold")
                      break
                    case "i":
                      e.preventDefault()
                      formatText("italic")
                      break
                    case "u":
                      e.preventDefault()
                      formatText("underline")
                      break
                    case "s":
                      e.preventDefault()
                      handleSave()
                      break
                  }
                }
              }}
            ></div>
          </div>
        </div>
      </div>

      {/* Status Bar */}
      <div className="bg-white border-t border-gray-200 px-4 py-2 text-xs text-gray-600">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <span>Page 1 of 1</span>
            <span>
              Words:{" "}
              {
                doc.content
                  .replace(/<[^>]*>/g, "")
                  .split(/\s+/)
                  .filter((word) => word.length > 0).length
              }
            </span>
            <span>Characters: {doc.content.replace(/<[^>]*>/g, "").length}</span>
          </div>
          <div className="flex items-center space-x-4">
            <span>{Math.round(100)}%</span>
            <span>English (US)</span>
            <span>
              Font: {currentFont} {currentFontSize}pt
            </span>
          </div>
        </div>
      </div>

      {/* Share Modal */}
      <ShareModal
        isOpen={isShareModalOpen}
        onClose={() => setIsShareModalOpen(false)}
        documentId={doc.id || "temp"}
        documentTitle={doc.title}
      />
    </div >
  )
}

export default function EditorPage() {
  return (
    <Suspense fallback={<div className="flex items-center justify-center min-h-screen">Loading editor...</div>}>
      <EditorContent />
    </Suspense>
  )
}