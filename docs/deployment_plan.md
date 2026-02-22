# Deployment Plan: DroitDraft Deployment Strategy

This plan details the resource requirements and storage footprint for different deployment options.

## 📊 Resource Footprint Comparison

| Strategy | **Local Disk Usage** | **Cloud Disk Usage** | **Complexity** |
| :--- | :--- | :--- | :--- |
| **Local Dev (Now)** | High (Containers + Data) | None | Zero (Existing) |
| **Path A: VPS (Oracle)**| Low (Repo only) | ~200GB (Free OCI Disk) | Low (Docker Compose) |
| **Path B: Hybrid** | Lowest (No Local Data) | 5.5GB+ (Supabase/Pinecone) | High (Code changes) |

---

## 🏗️ Path A: "Zero Refactor" (Recommended)
**Provider:** [Oracle Cloud (OCI) Always Free](https://www.oracle.com/cloud/free/)

**Does this use more local space?**
**No.** In fact, it saves you space.
- The 200GB storage belongs to the **Oracle server**, not your computer.
- Once deployed, you can stop running the local databases and free up several gigabytes on your machine.
- Your local machine only needs to store the **source code** (~100MB).

**Reasoning:** You ship your "Heavy" components (Postgres, MinIO, ChromaDB) to the Oracle cloud. They run inside their own virtual environment there.

---

## 🌩️ Path B: "Serverless Hybrid"
**Provider:** Vercel + Supabase + Pinecone

**Does this use more local space?**
**No.** This is the "lightest" possible option.
- Your data exists entirely as "API services" in the cloud.
- You don't run any heavy containers (Postgres/Chroma) even during production.
- **Trade-off:** Requires rewriting the legal research and storage logic to use these external APIs.

---

## 🚀 The Deployment Flow (Path A)

1.  **OCI VM**: Oracle provides a full Virtual Machine with 200GB of storage for free.
2.  **Docker Compose**: Use the [docker-compose.yml](file:///d:/droitdraft/docker-compose.yml) I created to launch the stack on that VM.
3.  **Data Persistence**: The data stays on the OCI disk. Your local laptop is only used for editing code and pushing to Git.

### Final Recommendation
**Path A (Oracle Cloud)** remains the best choice. It gives you massive server-side space (200GB) while significantly **reducing** the load on your local machine.
