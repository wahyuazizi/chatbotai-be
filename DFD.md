# DFD (Data Flow Diagram) - Level 0

Diagram ini menggambarkan alur data utama pada aplikasi chatbot.

- **Persegi Panjang**: Entitas Eksternal (sumber atau tujuan data).
- **Lingkaran/Oval**: Proses yang mentransformasi data.
- **Garis Terbuka**: Penyimpanan Data (Data Store).

```mermaid
graph TD
    subgraph "User Interaction"
        U[User]
        P2(2.0 Chat Service)
        P1(1.0 Authentication Service)
    end

    subgraph "Data Management"
        DA[Data Admin/Source]
        P3(3.0 Ingestion Service)
    end

    subgraph "Data Stores"
        D1[(D1 User Database)]
        D2[(D2 Knowledge Base <br> Azure AI Search)]
        D3[(D3 Chat History)]
    end

    subgraph "External Services"
        LLM[LLM Service]
    end

    %% Authentication Flow
    U -- "1. User Credentials" --> P1
    P1 -- "2. Validate/Create User" --> D1
    D1 -- "3. User Info" --> P1
    P1 -- "4. Auth Token" --> U

    %% Chat Flow
    U -- "5. Prompt (with Token)" --> P2
    P2 -- "6. Verify Token" --> P1
    P2 -- "7. Create Search Query" --> D2
    D2 -- "8. Relevant Documents" --> P2
    P2 -- "9. Augmented Prompt" --> LLM
    LLM -- "10. Generated Answer" --> P2
    P2 -- "11. Store Conversation" --> D3
    P2 -- "12. Final Response" --> U

    %% Ingestion Flow
    DA -- "A. Source Documents" --> P3
    P3 -- "B. Process & Create Embeddings" --> D2
```
> **Penjelasan Alur:**
> 1.  **Authentication**: Pengguna mengirim kredensial ke *Authentication Service*, yang memvalidasinya dengan *User Database* dan mengembalikan token.
> 2.  **Ingestion**: Admin menyediakan dokumen ke *Ingestion Service*, yang memprosesnya dan menyimpannya ke dalam *Knowledge Base* (Azure AI Search).
> 3.  **Chat**: Pengguna mengirim prompt (beserta token) ke *Chat Service*. Layanan ini mengambil dokumen relevan dari *Knowledge Base*, mengirimkannya bersama prompt ke *LLM Service*, menerima jawaban, menyimpan histori, dan mengirimkan respons akhir ke pengguna.
