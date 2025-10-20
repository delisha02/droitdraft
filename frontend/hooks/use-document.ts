"use client"

import { useState, useCallback, useEffect } from "react"
import { saveDocument, generateAIContent } from "@/lib/actions"

export interface Document {
  id?: string
  title: string
  content: string
  type: string
  lastSaved?: string
}

export function useDocument(initialDocument?: Document) {
  const [document, setDocument] = useState<Document>(
    initialDocument || {
      title: "Untitled Document",
      content: "",
      type: "contract",
    },
  )
  const [isSaving, setIsSaving] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)
  const [lastSaved, setLastSaved] = useState<string>()

  // Auto-save functionality
  useEffect(() => {
    const autoSave = setTimeout(() => {
      if (document.content.trim()) {
        handleSave()
      }
    }, 30000) // Auto-save every 30 seconds

    return () => clearTimeout(autoSave)
  }, [document.content])

  const handleSave = useCallback(async () => {
    setIsSaving(true)
    try {
      const result = await saveDocument(document)
      if (result.success) {
        setDocument((prev) => ({ ...prev, id: result.documentId }))
        setLastSaved(result.timestamp)
      }
    } catch (error) {
      console.error("Save failed:", error)
    } finally {
      setIsSaving(false)
    }
  }, [document])

  const handleGenerateAI = useCallback(
    async (prompt: string) => {
      setIsGenerating(true)
      try {
        const result = await generateAIContent(prompt, document.type)
        if (result.success) {
          return result.content
        }
      } catch (error) {
        console.error("AI generation failed:", error)
      } finally {
        setIsGenerating(false)
      }
      return null
    },
    [document.type],
  )

  const updateDocument = useCallback((updates: Partial<Document>) => {
    setDocument((prev) => ({ ...prev, ...updates }))
  }, [])

  const exportDocument = useCallback(
    async (format: "pdf" | "docx") => {
      try {
        const response = await fetch("/api/documents/export", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            content: document.content,
            title: document.title,
            format,
          }),
        })

        const result = await response.json()

        if (result.success) {
          // Create a temporary link to download the file
          const link = document.createElement("a")
          link.href = result.downloadUrl
          link.download = `${document.title}.${format}`
          link.click()
        }

        return result
      } catch (error) {
        console.error("Export failed:", error)
        return { success: false, message: "Export failed" }
      }
    },
    [document],
  )

  return {
    document,
    isSaving,
    isGenerating,
    lastSaved,
    handleSave,
    handleGenerateAI,
    updateDocument,
    exportDocument,
  }
}
