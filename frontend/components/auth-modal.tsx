"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { signIn } from "@/lib/actions"
import { X } from "lucide-react"

interface AuthModalProps {
  isOpen: boolean
  onClose: () => void
}

export function AuthModal({ isOpen, onClose }: AuthModalProps) {
  const [isLoading, setIsLoading] = useState(false)
  const [message, setMessage] = useState("")

  if (!isOpen) return null

  const handleSubmit = async (formData: FormData) => {
    setIsLoading(true)
    setMessage("")

    try {
      const result = await signIn(formData)
      setMessage(result.message)

      if (result.success) {
        setTimeout(() => {
          onClose()
          window.location.reload()
        }, 1000)
      }
    } catch (error) {
      setMessage("An error occurred. Please try again.")
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <Card className="w-full max-w-md mx-4">
        <CardHeader className="relative">
          <Button variant="ghost" size="sm" onClick={onClose} className="absolute right-2 top-2">
            <X className="w-4 h-4" />
          </Button>
          <CardTitle>Sign In to DroitDraft</CardTitle>
          <CardDescription>Access your documents and AI-powered legal tools</CardDescription>
        </CardHeader>
        <CardContent>
          <form action={handleSubmit} className="space-y-4">
            <div>
              <Input name="email" type="email" placeholder="Email address" required disabled={isLoading} />
            </div>
            <div>
              <Input name="password" type="password" placeholder="Password" required disabled={isLoading} />
            </div>
            <Button type="submit" className="w-full" disabled={isLoading}>
              {isLoading ? "Signing in..." : "Sign In"}
            </Button>
            {message && (
              <p className={`text-sm text-center ${message.includes("success") ? "text-green-600" : "text-red-600"}`}>
                {message}
              </p>
            )}
          </form>
        </CardContent>
      </Card>
    </div>
  )
}
