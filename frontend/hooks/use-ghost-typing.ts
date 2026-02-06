"use client"

import { useState, useCallback, useRef } from "react"

interface GhostTypingProps {
    caseFacts: any;
    docType?: string | null;
}

export function useGhostTyping({ caseFacts, docType }: GhostTypingProps) {
    const [suggestion, setSuggestion] = useState<string>("")
    const [isFetching, setIsFetching] = useState(false)
    const lastRequestRef = useRef<number>(0)

    const fetchSuggestion = useCallback(async (content: string) => {
        if (!content || content.length < 20) {
            setSuggestion("")
            return
        }

        const now = Date.now()
        if (now - lastRequestRef.current < 2000) return // Rate limit 2s

        setIsFetching(true)
        const token = localStorage.getItem("accessToken")
        try {
            lastRequestRef.current = now
            const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/documents/generation/ghost-suggest`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify({
                    current_content: content,
                    case_facts: caseFacts,
                    doc_type: docType
                })
            })

            if (response.ok) {
                const data = await response.json()
                if (data.suggestion && data.suggestion.trim()) {
                    setSuggestion(data.suggestion)
                } else {
                    setSuggestion("")
                }
            }
        } catch (error) {
            console.error("Ghost typing fetch error:", error)
        } finally {
            setIsFetching(false)
        }
    }, [caseFacts, docType])

    const clearSuggestion = useCallback(() => {
        setSuggestion("")
    }, [])

    return {
        suggestion,
        isFetching,
        fetchSuggestion,
        clearSuggestion
    }
}
