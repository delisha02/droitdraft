import { type NextRequest, NextResponse } from "next/server"

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const token = request.headers.get("Authorization")



    // Call the FastAPI backend for actual document generation
    const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/documents/export`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token ? { Authorization: token } : {}),
      },
      body: JSON.stringify(body),
    })


    if (!response.ok) {
      const errorText = await response.text()
      console.error("Backend export failed:", errorText)
      return NextResponse.json(
        { success: false, message: `Backend error: ${response.status}` },
        { status: response.status }
      )
    }

    // Get the binary data
    const blob = await response.blob()
    
    // In Next.js API routes, we return the blob with appropriate headers
    return new NextResponse(blob, {
      status: 200,
      headers: {
        "Content-Type": response.headers.get("Content-Type") || "application/octet-stream",
        "Content-Disposition": response.headers.get("Content-Disposition") || `attachment; filename="document.${body.format}"`,
      },
    })
  } catch (error) {
    console.error("Export proxy error:", error)
    return NextResponse.json(
      { success: false, message: "Export proxy failed" },
      { status: 500 }
    )
  }
}

