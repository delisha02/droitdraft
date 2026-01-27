"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { FileText, Plus, Trash2, Loader2 } from "lucide-react";
import Link from "next/link";

interface Document {
  id: number;
  title: string;
  content: string;
  owner_id: number;
}

export function DocumentList() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");
  const [isDeleting, setIsDeleting] = useState<number | null>(null);
  const router = useRouter();

  useEffect(() => {
    const fetchDocuments = async () => {
      const token = localStorage.getItem("accessToken");
      if (!token) {
        router.push("/auth/signin");
        return;
      }

      try {
        const response = await fetch(
          `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/documents/`,
          {
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }
        );

        if (response.ok) {
          const data = await response.json();
          setDocuments(data);
        } else {
          setError("Failed to fetch documents.");
        }
      } catch (error) {
        setError("An unexpected error occurred.");
      } finally {
        setIsLoading(false);
      }
    };

    fetchDocuments();
  }, [router]);

  const handleDelete = async (id: number) => {
    if (!confirm("Are you sure you want to delete this document?")) return;

    setIsDeleting(id);
    const token = localStorage.getItem("accessToken");
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/documents/${id}`,
        {
          method: "DELETE",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }
      );

      if (response.ok) {
        setDocuments((prev) => prev.filter((doc) => doc.id !== id));
      } else {
        alert("Failed to delete document.");
      }
    } catch (error) {
      alert("An error occurred while deleting.");
    } finally {
      setIsDeleting(null);
    }
  };

  if (isLoading) {
    return <div>Loading documents...</div>;
  }

  if (error) {
    return <div className="text-red-500">{error}</div>;
  }

  return (
    <section className="py-16 px-4 bg-white">
      <div className="container mx-auto max-w-7xl">
        <div className="flex justify-between items-center mb-12">
          <h3 className="text-3xl font-bold text-gray-900">Your Documents</h3>
          <Button asChild>
            <Link href="/editor">
              <Plus className="w-4 h-4 mr-2" />
              New Document
            </Link>
          </Button>
        </div>

        {documents.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {documents.map((doc) => (
              <Card key={doc.id} className="hover:shadow-lg transition-shadow">
                <CardHeader>
                  <CardTitle className="flex items-center justify-between">
                    <div className="flex items-center space-x-2 truncate">
                      <FileText className="w-5 h-5 text-blue-600 flex-shrink-0" />
                      <span className="truncate">{doc.title}</span>
                    </div>
                    <Button
                      variant="ghost"
                      size="sm"
                      className="text-gray-400 hover:text-red-600 transition-colors"
                      onClick={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        handleDelete(doc.id);
                      }}
                      disabled={isDeleting === doc.id}
                    >
                      {isDeleting === doc.id ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <Trash2 className="w-4 h-4" />
                      )}
                    </Button>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div
                    className="text-sm text-gray-600 line-clamp-3"
                    dangerouslySetInnerHTML={{ __html: doc.content }}
                  />
                  <Button asChild variant="link" className="px-0 mt-4">
                    <Link href={`/editor?id=${doc.id}`}>Open Document</Link>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        ) : (
          <div className="text-center py-12 border-2 border-dashed rounded-lg">
            <p className="text-gray-500">You haven't created any documents yet.</p>
            <Button asChild className="mt-4">
              <Link href="/editor">Create Your First Document</Link>
            </Button>
          </div>
        )}
      </div>
    </section>
  );
}
