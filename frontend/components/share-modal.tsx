"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { shareDocument } from "@/lib/actions"
import { X, Copy, Check } from "lucide-react"

interface ShareModalProps {
  isOpen: boolean
  onClose: () => void
  documentId: string
  documentTitle: string
}

export function ShareModal({ isOpen, onClose, documentId, documentTitle }: ShareModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState("")
  const [shareLink, setShareLink] = useState("")
  const [copied, setCopied] = useState(false)

  if (!isOpen) return null

  const handleShare = async (formData: FormData) => {
    setIsLoading(true)
    setMessage("")

    try {
      const email = formData.get("email") as string
      const result = await shareDocument(documentId, email)

      setMessage(result.message)
      setShareLink(result.shareLink)
    } catch (error) {
      setMessage("Failed to share document. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  const copyToClipboard = async () => {
    try {
      await navigator.clipboard.writeText(shareLink)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch (error) {
      console.error("Failed to copy to clipboard")
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md mx-4">
        <CardHeader className="relative">
          <Button variant="ghost" size="sm" onClick={onClose} className="absolute right-2 top-2">
            <X className="w-4 h-4" />
          </Button>
          <CardTitle>Share Document</CardTitle>
          <CardDescription>Share "{documentTitle}" with others</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <form action={handleShare} className="space-y-4">
            <div>
              <Input name="email" type="email" placeholder="Enter email address" required disabled={isLoading} />
            </div>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Sharing..." : "Share Document"}
            </Button>
          </form>

          {shareLink && (
            <div className="space-y-2">
              <p className="text-sm font-medium">Share Link:</p>
              <div className="flex items-center space-x-2">
                <Input value={shareLink} readOnly className="text-xs" />
                <Button variant="outline" size="sm" onClick={copyToClipboard}>
                  {copied ? <Check className="w-4 h-4" /> : <Copy className="w-4 h-4" />}
                </Button>
              </div>
            </div>
          )}

          {message && (
            <p
              className={`text-sm text-center ${
                message.includes("success") || message.includes("shared") ? "text-green-600" : "text-red-600"
              }`}
            >
              {message}
            </p>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
