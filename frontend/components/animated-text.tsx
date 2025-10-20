"use client"

import { useState, useEffect } from "react"

const texts = [
  "Generate Legal Documents with AI Precision",
  "Transform Legal Practice with Smart Technology",
  "Create Professional Contracts in Minutes",
  "Streamline Legal Workflows with Automation",
  "Empower Legal Teams with Intelligent Tools",
]

export function AnimatedText() {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [displayText, setDisplayText] = useState("")
  const [isDeleting, setIsDeleting] = useState(false)

  useEffect(() => {
    const currentText = texts[currentIndex]

    const timeout = setTimeout(
      () => {
        if (!isDeleting) {
          // Typing
          if (displayText.length < currentText.length) {
            setDisplayText(currentText.slice(0, displayText.length + 1))
          } else {
            // Pause before deleting
            setTimeout(() => setIsDeleting(true), 2000)
          }
        } else {
          // Deleting
          if (displayText.length > 0) {
            setDisplayText(displayText.slice(0, -1))
          } else {
            setIsDeleting(false)
            setCurrentIndex((prev) => (prev + 1) % texts.length)
          }
        }
      },
      isDeleting ? 50 : 100,
    )

    return () => clearTimeout(timeout)
  }, [displayText, isDeleting, currentIndex])

  return (
    <span className="text-blue-600 font-semibold">
      {displayText}
      <span className="animate-pulse">|</span>
    </span>
  )
}
