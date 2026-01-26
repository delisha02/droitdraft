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
  const [doc, setDoc] = useState<Document>(
    initialDocument || {
      title: "Untitled Document",
      content: "",
      type: "contract",
    }
  );
  const [isSaving, setIsSaving] = useState(false);
  const [isGenerating, setIsGenerating] = useState(false);
  const [isFetching, setIsFetching] = useState(false);
  const [lastSaved, setLastSaved] = useState<string>();

  const fetchDocument = useCallback(async (id: string) => {
    setIsFetching(true);
    const token = localStorage.getItem("accessToken");
    if (!token) {
      setIsFetching(false);
      return;
    }

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/documents/${id}`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setDoc(data);
      } else {
        console.error("Failed to fetch document:", await response.text());
      }
    } catch (error) {
      console.error("Error fetching document:", error);
    } finally {
      setIsFetching(false);
    }
  }, []);

  // Auto-save functionality
  useEffect(() => {
    const autoSave = setTimeout(() => {
      if (doc.content.trim() && !isSaving && !isFetching) {
        handleSave();
      }
    }, 30000); // Auto-save every 30 seconds

    return () => clearTimeout(autoSave);
  }, [doc.content, doc.id]);

  const handleSave = useCallback(async () => {
    if (isSaving) return;
    setIsSaving(true);
    const token = localStorage.getItem("accessToken");
    if (!token) {
      console.error("Authentication token not found.");
      setIsSaving(false);
      return;
    }

    try {
      const url = doc.id
        ? `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/documents/${doc.id}`
        : `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/documents/`;
      const method = doc.id ? "PUT" : "POST";

      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          title: doc.title,
          content: doc.content,
        }),
      });

      if (response.ok) {
        const result = await response.json();
        const updatedDoc = { ...doc, id: result.id };
        setDoc(updatedDoc);
        setLastSaved(new Date().toISOString());
        setIsSaving(false);
        return updatedDoc;
      } else {
        console.error("Save failed:", await response.text());
      }
    } catch (error) {
      console.error("Save failed:", error);
    } finally {
      setIsSaving(false);
    }
  }, [doc, isSaving]);

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
              template_id: parseInt(doc.type, 10),
              case_facts: { prompt },
              title: doc.title,
            }),
          }
        );

        if (response.ok) {
          const result = await response.json();
          setDoc(result);
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
    [doc.type, doc.title]
  );

  const updateDocument = useCallback((updates: Partial<Document>) => {
    setDoc((prev) => ({ ...prev, ...updates }))
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
            content: doc.content,
            title: doc.title,
            format,
          }),
        })

        const result = await response.json()

        if (result.success) {
          // Create a temporary link to download the file
          const link = window.document.createElement("a")
          link.href = result.downloadUrl
          link.download = `${doc.title}.${format}`
          link.click()
        }

        return result
      } catch (error) {
        console.error("Export failed:", error)
        return { success: false, message: "Export failed" }
      }
    },
    [doc],
  )

  return {
    document: doc,
    isSaving,
    isGenerating,
    isFetching,
    lastSaved,
    handleSave,
    fetchDocument,
    handleGenerateAI,
    updateDocument,
    exportDocument,
  }
}