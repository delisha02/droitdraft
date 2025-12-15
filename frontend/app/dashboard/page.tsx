"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import {
  FileText,
  Scale,
  Shield,
  Users,
  Home,
  Briefcase,
  Play,
  Mail,
  AlertCircle,
  FileCheck,
  Repeat,
  CheckCircle,
  ArrowRight,
  Building2,
  FileVolume2 as FileDocument,
  Gift,
} from "lucide-react"
import Link from "next/link"
import { AuthModal } from "@/components/auth-modal"
import { DocumentList } from "@/components/document-list";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog"

const icons = [FileText, Shield, Scale, Home, Briefcase, Mail, AlertCircle, FileCheck, Repeat, CheckCircle, ArrowRight, Building2, FileDocument, Gift];
const colors = ["bg-red-500", "bg-green-500", "bg-blue-500", "bg-purple-500", "bg-indigo-500", "bg-amber-500", "bg-cyan-500", "bg-orange-500", "bg-emerald-500", "bg-rose-500", "bg-lime-500", "bg-pink-500", "bg-sky-500", "bg-violet-500", "bg-fuchsia-500", "bg-teal-500"];

export default function DashboardPage() {
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false)
  const [isDemoOpen, setIsDemoOpen] = useState(false)
  const [documentTypes, setDocumentTypes] = useState<any[]>([])
  const router = useRouter()

  useEffect(() => {
    const isAuthenticated = localStorage.getItem("isAuthenticated");
    if (isAuthenticated !== "true") {
      router.push("/auth/signin");
    }
  }, [router]);

  useEffect(() => {
    const fetchDocumentTypes = async () => {
      const token = localStorage.getItem("accessToken");
      if (!token) {
        return;
      }
      try {
        const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE_URL}/api/v1/templates/`, {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });
        if (response.ok) {
          const data = await response.json();
          setDocumentTypes(data.map((template: any, index: number) => ({
            id: template.id,
            title: template.name,
            description: template.description,
            icon: icons[index % icons.length],
            color: colors[index % colors.length],
            features: [template.document_type, template.jurisdiction],
          })));
        }
      } catch (error) {
        console.error("Failed to fetch document types", error);
      }
    };
    fetchDocumentTypes();
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("isAuthenticated");
    localStorage.removeItem("accessToken");
    localStorage.removeItem("userEmail");
    router.push("/auth/signin");
  };

  const handleStartCreating = () => {
    // Scroll to document types section
    document.getElementById("document-list")?.scrollIntoView({
      behavior: "smooth",
    })
  }

  const handleWatchDemo = () => {
    setIsDemoOpen(true)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
                <Scale className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">DroitDraft</h1>
                <p className="text-sm text-gray-600">AI-Powered Legal Document Generation</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                Beta
              </Badge>
              <Button variant="outline" size="sm" onClick={handleLogout}>
                Logout
              </Button>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-16 px-4">
        <div className="container mx-auto text-center max-w-4xl">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 mb-6">
            Generate Legal Documents with <span className="text-blue-600">AI Precision</span>
          </h2>
          <p className="text-xl text-gray-600 mb-8 leading-relaxed">
            Create case-specific legal documents tailored to your unique requirements. Our AI copilot understands
            context and generates professional documents that adapt to each situation.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button size="lg" className="bg-blue-600 hover:bg-blue-700" onClick={handleStartCreating}>
              Start Creating Documents
            </Button>
            <Button size="lg" variant="outline" onClick={handleWatchDemo}>
              <Play className="w-4 h-4 mr-2" />
              Watch Demo
            </Button>
          </div>
        </div>
      </section>

      <DocumentList />

      {/* Document Types Section */}
      <section id="document-types" className="py-16 px-4">
        <div className="container mx-auto max-w-7xl">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">Choose Your Document Type</h3>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Select from our specialized legal document categories, each powered by AI to generate contextually
              relevant and legally sound documents.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {documentTypes.map((docType) => {
              const IconComponent = docType.icon
              return (
                <Card
                  key={docType.id}
                  className="group hover:shadow-lg transition-all duration-300 border-0 shadow-md hover:scale-105"
                >
                  <CardHeader className="pb-4">
                    <div className="flex items-center space-x-3 mb-3">
                      <div
                        className={`w-12 h-12 ${docType.color} rounded-lg flex items-center justify-center group-hover:scale-110 transition-transform`}
                      >
                        <IconComponent className="w-6 h-6 text-white" />
                      </div>
                      <div className="flex-1">
                        <CardTitle className="text-lg font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                          {docType.title}
                        </CardTitle>
                      </div>
                    </div>
                    <CardDescription className="text-gray-600 leading-relaxed">{docType.description}</CardDescription>
                  </CardHeader>
                  <CardContent className="pt-0">
                    <div className="space-y-3">
                      <div className="flex flex-wrap gap-2">
                        {docType.features.map((feature, index) => (
                          <Badge key={index} variant="secondary" className="text-xs bg-gray-100 text-gray-700">
                            {feature}
                          </Badge>
                        ))}
                      </div>
                      <Link href={`/editor?type=${docType.id}`} className="block">
                        <Button className="w-full bg-gray-900 hover:bg-gray-800 text-white">Create Document</Button>
                      </Link>
                    </div>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 px-4 bg-white">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">Why Choose DroitDraft?</h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Users className="w-8 h-8 text-blue-600" />
              </div>
              <h4 className="text-xl font-semibold mb-2">Case-Specific Generation</h4>
              <p className="text-gray-600">
                AI understands your unique case requirements and generates tailored documents.
              </p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Shield className="w-8 h-8 text-green-600" />
              </div>
              <h4 className="text-xl font-semibold mb-2">Legally Compliant</h4>
              <p className="text-gray-600">All documents follow current legal standards and best practices.</p>
            </div>
            <div className="text-center">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText className="w-8 h-8 text-purple-600" />
              </div>
              <h4 className="text-xl font-semibold mb-2">Professional Formatting</h4>
              <p className="text-gray-600">Documents are formatted professionally and ready for immediate use.</p>
            </div>
          </div>
        </div>
      </section>

      <Dialog open={isDemoOpen} onOpenChange={setIsDemoOpen}>
        <DialogContent className="sm:max-w-4xl">
          <DialogHeader>
            <DialogTitle>DroitDraft Demo</DialogTitle>
            <DialogDescription>Watch a quick walkthrough of DroitDraft in action.</DialogDescription>
          </DialogHeader>
          <div className="aspect-video w-full">
            <iframe
              src="https://www.youtube.com/embed/UKMdAccrM1M?start=3"
              title="DroitDraft Demo"
              className="w-full h-full rounded-md"
              frameBorder="0"
              allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
              allowFullScreen
            />
          </div>
        </DialogContent>
      </Dialog>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4">
        <div className="container mx-auto max-w-6xl">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div className="col-span-1 md:col-span-2">
              <div className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
                  <Scale className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold">DroitDraft</span>
              </div>
              <p className="text-gray-400 mb-4">
                Empowering legal professionals with AI-driven document generation that adapts to every case and
                situation.
              </p>
            </div>
            <div>
              <h5 className="font-semibold mb-4">Product</h5>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Features
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Pricing
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    API
                  </a>
                </li>
              </ul>
            </div>
            <div>
              <h5 className="font-semibold mb-4">Support</h5>
              <ul className="space-y-2 text-gray-400">
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Documentation
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Contact
                  </a>
                </li>
                <li>
                  <a href="#" className="hover:text-white transition-colors">
                    Legal
                  </a>
                </li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
            <p>&copy; 2025 DroitDraft. All rights reserved.</p>
          </div>
        </div>
      </footer>

      {/* Auth Modal */}
      <AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />
    </div>
  )
}