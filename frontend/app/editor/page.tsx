"use client"

import { useState, useRef, useEffect } from "react"
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
} from "lucide-react"
import LinkComponent from "next/link"
import { useSearchParams } from "next/navigation"
import { useDocument } from "@/hooks/use-document"
import { ShareModal } from "@/components/share-modal"

const documentTemplates = {
  notices: "Legal Notice Template",
  will: "Last Will & Testament Template",
  plaintiff: "Plaintiff Document Template",
  "preceding-drafts": "Preceding Draft Template",
  contracts: "Contract Agreement Template",
  probate: "Probate Document Template",
  "letters-of-administration": "Letters of Administration Template",
  caveat: "Caveat Template",
  "sale-deed": "Sale Deed Template",
  "deed-of-exchange": "Deed of Exchange Template",
  "release-deed": "Release Deed Template",
  "deed-of-transfer": "Deed of Transfer Template",
  "development-agreement": "Development Agreement Template",
  conveyance: "Conveyance Template",
  "gift-deed": "Gift Deed Template",
  "permanent-alternate-accommodation": "Permanent Alternate Accommodation Template",
}

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

export default function EditorPage() {
  const searchParams = useSearchParams()
  const docType = searchParams.get("type") || "contracts"
  const [isShareModalOpen, setIsShareModalOpen] = useState(false)
  const [currentFont, setCurrentFont] = useState("Times New Roman")
  const [currentFontSize, setCurrentFontSize] = useState("12")
  const [currentLineHeight, setCurrentLineHeight] = useState("1.5")
  const [aiPrompt, setAiPrompt] = useState("")
  const editorRef = useRef<HTMLDivElement>(null)

  const {
    document: doc,
    isSaving,
    lastSaved,
    handleSave,
    updateDocument,
    handleGenerateAI: handleAiGenerateFromHook,
    isGenerating,
  } = useDocument({
    title: `Untitled ${documentTemplates[docType as keyof typeof documentTemplates] || "Document"}`,
    content: "",
    type: docType,
  })

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
      updateDocument({ content: editorRef.current.innerHTML })
    }
  }

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
    if (!aiPrompt.trim()) return;

    const generatedContent = await handleAiGenerateFromHook(aiPrompt);

    if (generatedContent && editorRef.current) {
      // Append the generated content to the editor
      const selection = window.getSelection();
      if (selection && selection.rangeCount > 0) {
        const range = selection.getRangeAt(0);
        const div = window.document.createElement("div");
        div.innerHTML = generatedContent;
        range.deleteContents();
        range.insertNode(div);
      } else {
        editorRef.current.innerHTML += generatedContent;
      }
      updateContentFromEditor();
      setAiPrompt("");
    }
  }

  useEffect(() => {
    if (editorRef.current && !doc.content) {
      const initialContent = `
        <div style="font-family: ${currentFont}; font-size: ${currentFontSize}pt; line-height: ${currentLineHeight};">
          <div style="text-align: center; margin-bottom: 2em;">
            <h1 style="font-size: 18pt; font-weight: bold; margin-bottom: 0.5em;">${documentTemplates[docType as keyof typeof documentTemplates] || "Legal Document"}</h1>
            <p style="color: #666; font-size: 12pt;">Generated by DroitDraft</p>
          </div>
          <div style="margin-bottom: 2em;">
            <p><strong>Date:</strong> ${new Date().toLocaleDateString()}</p>
            <p><strong>Document Type:</strong> ${documentTemplates[docType as keyof typeof documentTemplates] || "Legal Document"}</p>
          </div>
          <div>
            <p>Click here to start writing your document or use the AI Assistant to generate content...</p>
          </div>
        </div>
      `
      editorRef.current.innerHTML = initialContent
      updateDocument({ content: initialContent })
    }
  }, [docType, currentFont, currentFontSize, currentLineHeight])

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 px-4 py-2">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <LinkComponent href="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                <Scale className="w-5 h-5 text-white" />
              </div>
              <span className="font-semibold text-gray-900">DroitDraft</span>
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
            <Button size="sm" className="bg-blue-600 hover:bg-blue-700" onClick={handleSave} disabled={isSaving}>
              <Save className="w-4 h-4 mr-2" />
              {isSaving ? "Saving..." : "Save"}
            </Button>
          </div>
        </div>
      </header>

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
            </BinnerText>
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
        <div className="w-80 bg-white border-r border-gray-200 p-4">
          <div className="space-y-4">
            <div className="flex items-center space-x-2 mb-4">
              <Bot className="w-5 h-5 text-blue-600" />
              <h3 className="font-semibold text-gray-900">AI Assistant</h3>
              <Sparkles className="w-4 h-4 text-yellow-500" />
            </div>

            <div className="space-y-3">
              <Textarea
                placeholder="Describe what you want to generate (e.g., 'Create a confidentiality clause for software development')"
                value={aiPrompt}
                onChange={(e) => setAiPrompt(e.target.value)}
                className="min-h-[100px] resize-none"
              />

              <Button
                onClick={handleAiGenerate}
                className="w-full bg-blue-600 hover:bg-blue-700"
                disabled={isGenerating || !aiPrompt.trim()}
              >
                {isGenerating ? (
                  <>
                    <Bot className="w-4 h-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Sparkles className="w-4 h-4 mr-2" />
                    Generate Content
                  </>
                )}
              </Button>
            </div>

            <Separator />

            <div>
              <h4 className="font-medium text-gray-900 mb-3">Quick Suggestions</h4>
              <div className="space-y-2">
                {[
                  "Add a confidentiality clause",
                  "Generate payment terms",
                  "Create liability limitations",
                  "Add termination conditions",
                  "Include dispute resolution",
                  "Add force majeure clause",
                ].map((suggestion, index) => (
                  <Button
                    key={index}
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start text-xs h-auto py-2 px-3 text-left"
                    onClick={() => setAiPrompt(suggestion)}
                  >
                    <Type className="w-3 h-3 mr-2 flex-shrink-0" />
                    {suggestion}
                  </Button>
                ))}
              </div>
            </div>

            <Separator />

            <div>
              <h4 className="font-medium text-gray-900 mb-3">Document Templates</h4>
              <div className="space-y-2">
                {[
                  "Standard Contract Header",
                  "Party Information Section",
                  "Terms and Conditions",
                  "Signature Block",
                ].map((template, index) => (
                  <Button
                    key={index}
                    variant="ghost"
                    size="sm"
                    className="w-full justify-start text-xs h-auto py-2 px-3 text-left"
                    onClick={() => setAiPrompt(`Generate ${template.toLowerCase()}`)}
                  >
                    <FileText className="w-3 h-3 mr-2 flex-shrink-0" />
                    {template}
                  </Button>
                ))}
              </div>
            </div>

            <div className="mt-6 p-3 bg-blue-50 rounded-lg">
              <p className="text-xs text-blue-700">
                <Bot className="w-4 h-4 inline mr-1" />
                AI integration will be enhanced with advanced legal document generation capabilities.
              </p>
            </div>
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
            />
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
    </div>
  )
}