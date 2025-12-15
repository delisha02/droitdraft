"use client"

import { useState, useCallback, useEffect } from "react";

export interface Document {
  id?: string;
  title: string;
  content: string;
  type: string;
  lastSaved?: string;
}

export function useDocument(initialDocument?: Document) {
  const [document, setDocument] = useState<Document>(
    initialDocument || {
      title: "Untitled Document",
      content: "",
      type: "contract",
    }
  );
  const [isSaving, setIsSaving] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [lastSaved, setLastSaved] = useState<string>();

  // Auto-save functionality
  useEffect(() => {
    const autoSave = setTimeout(() => {
      if (document.content.trim()) {
        handleSave();
      }
    }, 30000); // Auto-save every 30 seconds

    return () => clearTimeout(autoSave);
  }, [document.content]);

  const handleSave = useCallback(async () => {
    setIsSaving(true);
    const token = localStorage.getItem("accessToken");
    if (!token) {
      // Handle case where user is not authenticated
      console.error("Authentication token not found.");
      setIsSaving(false);
      return;
    }

    try {
      const url = document.id
        ? `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/documents/${document.id}`
        : `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/documents/`;
      const method = document.id ? "PUT" : "POST";

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: document.title,
          content: document.content,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        setDocument((prev) => ({ ...prev, id: result.id }));
        setLastSaved(new Date().toISOString());
      } else {
        console.error("Save failed:", await response.text());
      }
    } catch (error) {
      console.error("Save failed:", error);
    } finally {
      setIsSaving(false);
    }
  }, [document]);

  const handleGenerateAI = useCallback(
    async (prompt: string) => {
      setIsGenerating(true);
      const token = localStorage.getItem("accessToken");
      if (!token) {
        console.error("Authentication token not found.");
        setIsGenerating(false);
        return null;
      }

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/documents/generation/generate`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
              template_id: parseInt(document.type, 10),
              case_facts: { prompt },
              title: document.title,
            }),
          }
        );

        if (response.ok) {
          const result = await response.json();
          setDocument(result);
          return result.content;
        } else {
          console.error("AI generation failed:", await response.text());
          return null;
        }
      } catch (error) {
        console.error("AI generation failed:", error);
        return null;
      } finally {
        setIsGenerating(false);
      }
    },
    [document.type, document.title]
  );

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