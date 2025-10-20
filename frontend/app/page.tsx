"use client"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Scale, Bot, Sparkles, Users, Shield, FileText, ArrowRight, Github, Linkedin, Mail } from "lucide-react"
import Link from "next/link"
import { AnimatedText } from "@/components/animated-text"

const developers = [
  {
    name: "Deep",
    role: "Lead AI Engineer",
    description:
      "Specializes in natural language processing and legal document analysis. Expert in machine learning algorithms for legal text generation.",
    avatar: "/professional-developer-portrait.png",
    github: "#",
    linkedin: "#",
    email: "deep@droitdraft.com",
  },
  {
    name: "Soham",
    role: "Full Stack Developer",
    description:
      "Frontend and backend development specialist. Focuses on creating seamless user experiences and robust system architecture.",
    avatar: "/professional-developer-portrait.png",
    github: "#",
    linkedin: "#",
    email: "soham@droitdraft.com",
  },
  {
    name: "Delisha",
    role: "Legal Tech Specialist",
    description:
      "Legal domain expert ensuring compliance and accuracy. Bridges the gap between legal requirements and technology solutions.",
    avatar: "/professional-developer-portrait.png",
    github: "#",
    linkedin: "#",
    email: "delisha@droitdraft.com",
  },
  {
    name: "Priyal",
    role: "UI/UX Designer",
    description:
      "User experience designer focused on creating intuitive interfaces for legal professionals. Expert in accessibility and user-centered design.",
    avatar: "/professional-developer-portrait.png",
    github: "#",
    linkedin: "#",
    email: "priyal@droitdraft.com",
  },
]

const features = [
  {
    icon: Bot,
    title: "AI-Powered Generation",
    description:
      "Advanced GPT technology specifically trained on legal documents and terminology for accurate, contextual content generation.",
  },
  {
    icon: Shield,
    title: "Legal Compliance",
    description:
      "Ensures all generated documents meet current legal standards and regulatory requirements across multiple jurisdictions.",
  },
  {
    icon: FileText,
    title: "Document Variety",
    description:
      "Supports generation of contracts, notices, wills, plaintiff documents, and other legal instruments with professional formatting.",
  },
  {
    icon: Users,
    title: "Collaborative Workflow",
    description:
      "Built for legal teams with sharing, review, and collaborative editing features to streamline document creation processes.",
  },
]

export default function LandingPage() {
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
                <p className="text-sm text-gray-600">Legal GPT Platform</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <Badge variant="secondary" className="bg-blue-100 text-blue-800">
                Beta v1.0
              </Badge>
              <Link href="/auth/signin">
                <Button variant="outline" size="sm">
                  Sign In
                </Button>
              </Link>
              <Link href="/auth/signup">
                <Button size="sm" className="bg-blue-600 hover:bg-blue-700">
                  Get Started
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="py-20 px-4">
        <div className="container mx-auto text-center max-w-6xl">
          <div className="mb-8">
            <Badge variant="secondary" className="bg-blue-100 text-blue-800 mb-4">
              <Sparkles className="w-4 h-4 mr-2" />
              Powered by Advanced AI
            </Badge>
            <h1 className="text-5xl md:text-7xl font-bold text-gray-900 mb-6">
              Droit<span className="text-blue-600">Draft</span>
            </h1>
            <div className="text-2xl md:text-3xl text-gray-600 mb-8 min-h-[80px] flex items-center justify-center">
              <AnimatedText />
            </div>
            <p className="text-xl text-gray-600 mb-12 leading-relaxed max-w-4xl mx-auto">
              Revolutionary AI-powered legal document generation platform that transforms how legal professionals
              create, review, and manage legal documents. Built by experts, designed for excellence.
            </p>
          </div>

          <div className="flex flex-col sm:flex-row gap-6 justify-center mb-16">
            <Link href="/auth/signup">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-4">
                Start Creating Documents
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
            <Link href="#features">
              <Button size="lg" variant="outline" className="text-lg px-8 py-4 bg-transparent">
                Learn More
              </Button>
            </Link>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-20">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">10K+</div>
              <div className="text-gray-600">Documents Generated</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">500+</div>
              <div className="text-gray-600">Legal Professionals</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">99.9%</div>
              <div className="text-gray-600">Accuracy Rate</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">24/7</div>
              <div className="text-gray-600">AI Availability</div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="py-20 px-4 bg-white">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Why Choose DroitDraft?</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our platform combines cutting-edge AI technology with deep legal expertise to deliver unparalleled
              document generation capabilities.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 mb-20">
            {features.map((feature, index) => {
              const IconComponent = feature.icon
              return (
                <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-all duration-300">
                  <CardHeader>
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                        <IconComponent className="w-6 h-6 text-blue-600" />
                      </div>
                      <CardTitle className="text-xl">{feature.title}</CardTitle>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-gray-600 leading-relaxed">{feature.description}</CardDescription>
                  </CardContent>
                </Card>
              )
            })}
          </div>
        </div>
      </section>

      {/* Developers Section */}
      <section className="py-20 px-4 bg-gradient-to-br from-blue-50 to-indigo-50">
        <div className="container mx-auto max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Meet Our Team</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              A diverse team of experts combining legal knowledge, AI expertise, and exceptional engineering skills to
              revolutionize legal document creation.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {developers.map((dev, index) => (
              <Card key={index} className="border-0 shadow-lg hover:shadow-xl transition-all duration-300 text-center">
                <CardHeader className="pb-4">
                  <div className="w-24 h-24 mx-auto mb-4 rounded-full overflow-hidden bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
                    <span className="text-2xl font-bold text-white">{dev.name[0]}</span>
                  </div>
                  <CardTitle className="text-xl">{dev.name}</CardTitle>
                  <Badge variant="secondary" className="bg-blue-100 text-blue-800 w-fit mx-auto">
                    {dev.role}
                  </Badge>
                </CardHeader>
                <CardContent className="space-y-4">
                  <CardDescription className="text-gray-600 leading-relaxed">{dev.description}</CardDescription>
                  <div className="flex justify-center space-x-3">
                    <Button variant="ghost" size="sm" className="p-2">
                      <Github className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="sm" className="p-2">
                      <Linkedin className="w-4 h-4" />
                    </Button>
                    <Button variant="ghost" size="sm" className="p-2">
                      <Mail className="w-4 h-4" />
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 bg-gray-900 text-white">
        <div className="container mx-auto max-w-4xl text-center">
          <h2 className="text-4xl font-bold mb-6">Ready to Transform Your Legal Practice?</h2>
          <p className="text-xl text-gray-300 mb-8 leading-relaxed">
            Join thousands of legal professionals who trust LegalGPT for their document generation needs. Start creating
            professional legal documents in minutes, not hours.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/auth/signup">
              <Button size="lg" className="bg-blue-600 hover:bg-blue-700 text-lg px-8 py-4">
                Get Started Free
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </Link>
            <Link href="/auth/signin">
              <Button
                size="lg"
                variant="outline"
                className="text-lg px-8 py-4 border-gray-600 text-gray-300 hover:bg-gray-800 bg-transparent"
              >
                Sign In
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4 border-t border-gray-800">
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
    </div>
  )
}
