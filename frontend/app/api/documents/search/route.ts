import { type NextRequest, NextResponse } from "next/server"

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const query = searchParams.get("q")
  const documentType = searchParams.get("type")

  // Simulate search functionality
  await new Promise((resolve) => setTimeout(resolve, 500))

  const mockResults = [
    { text: "confidentiality clause", position: 245, context: "regarding confidential information" },
    { text: "payment terms", position: 1024, context: "net 30 days payment terms" },
    { text: "termination", position: 1856, context: "agreement termination conditions" },
  ]

  const filteredResults = query
    ? mockResults.filter(
        (result) =>
          result.text.toLowerCase().includes(query.toLowerCase()) ||
          result.context.toLowerCase().includes(query.toLowerCase()),
      )
    : []

  return NextResponse.json({
    success: true,
    results: filteredResults,
    query,
    count: filteredResults.length,
  })
}
