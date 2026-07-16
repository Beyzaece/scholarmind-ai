
import { useEffect, useState } from "react";
import "./App.css";


function App() {
  const [selectedDocumentId, setSelectedDocumentId] = useState(null);
  const [selectedDocumentName, setSelectedDocumentName] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState([]);
  const [uploadMessage, setUploadMessage] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [documents, setDocuments] = useState([]);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [documentsError, setDocumentsError] = useState("");
  const uploadDocument = async () => {
    if (!selectedFile) {
      return;
    }

    setIsUploading(true);
    setUploadMessage("");
    setErrorMessage("");

    try {
      const formData = new FormData();
      formData.append("file", selectedFile);

      const response = await fetch("http://127.0.0.1:8000/upload", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Doküman yüklenirken bir hata oluştu."
        );
      }

      setUploadMessage(
        `${data.filename} başarıyla işlendi. ${data.chunk_count} chunk oluşturuldu.`
      );
      await fetchDocuments();
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setIsUploading(false);
    }
  };

  const askQuestion = async () => {
    if (!question.trim()) {
      return;
    }

    setIsAsking(true);
    setAnswer("");
    setSources([]);
    setErrorMessage("");

    try {
      const response = await fetch("http://127.0.0.1:8000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          question: question,
          document_id: selectedDocumentId,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(
          data.detail || "Cevap oluşturulurken bir hata oluştu."
        );
      }

      setAnswer(data.answer);
      setSources(data.sources || []);
    } catch (error) {
      setErrorMessage(error.message);
    } finally {
      setIsAsking(false);
    }
  };
  const fetchDocuments = async () => {
  try {
    setDocumentsLoading(true);
    setDocumentsError("");

    const response = await fetch(
      "http://127.0.0.1:8000/documents"
    );

    if (!response.ok) {
      throw new Error("Dokümanlar alınamadı.");
    }

    const data = await response.json();
    setDocuments(data);
  } catch (error) {
    setDocumentsError(error.message);
  } finally {
    setDocumentsLoading(false);
  }
};

const deleteDocument = async (documentId) => {
  const confirmed = window.confirm(
    "Bu dokümanı silmek istediğinize emin misiniz?"
  );

  if (!confirmed) {
    return;
  }

  try {
    const response = await fetch(
      `http://127.0.0.1:8000/documents/${documentId}`,
      {
        method: "DELETE",
      }
    );

    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail || "Doküman silinemedi."
      );
    }

    await fetchDocuments();

  } catch (error) {
    setErrorMessage(error.message);
  }
};

useEffect(() => {
  fetchDocuments();
}, []);



  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <div className="brand">
            <div className="brand-icon">S</div>

            <div>
              <h1>ScholarMind AI</h1>
              <span>Research Intelligence Platform</span>
            </div>
          </div>

          <div className="sidebar-section">
            <p className="section-label">WORKSPACE</p>

            <button className="nav-item active">
              <span>01</span>
              Research Assistant
            </button>

            <button className="nav-item">
              <span>02</span>
              Document Library
            </button>

            <button className="nav-item">
              <span>03</span>
              Research History
            </button>
          </div>
        </div>

        <div className="sidebar-footer">
          <div className="status-dot"></div>

          <div>
            <strong>System Online</strong>
            <span>RAG pipeline is ready</span>
          </div>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="eyebrow">AI RESEARCH ASSISTANT</p>

            <h2>Ask your documents anything.</h2>

            <p className="subtitle">
              Upload an academic PDF and receive context-aware answers with
              source references.
            </p>
          </div>

          <div className="system-badge">
            <span></span>
            Connected
          </div>
        </header>

        {errorMessage && (
          <div className="message-box error-message">
            {errorMessage}
          </div>
        )}

        {uploadMessage && (
          <div className="message-box success-message">
            {uploadMessage}
          </div>
        )}

        <section className="workspace-grid">
          <div className="panel upload-panel">
            <div className="panel-header">
              <div>
                <p className="step-label">STEP 01</p>
                <h3>Upload document</h3>
              </div>

              <span className="panel-tag">PDF only</span>
            </div>

            <label className="upload-zone">
              <div className="upload-icon">↑</div>

              <strong>
                {selectedFile
                  ? selectedFile.name
                  : "Choose a research paper"}
              </strong>

              <span>
                {selectedFile
                  ? "Document is ready to upload."
                  : "Browse from your computer and select a PDF file."}
              </span>

              <input
                type="file"
                accept="application/pdf"
                onChange={(event) =>
                  setSelectedFile(event.target.files?.[0] ?? null)
                }
              />
            </label>

            <button
              className="primary-button"
              disabled={!selectedFile || isUploading}
              onClick={uploadDocument}
            >
              {isUploading ? "Processing..." : "Process Document"}
            </button>
          </div>

          <div className="panel query-panel">
            <div className="panel-header">
              <div>
                <p className="step-label">STEP 02</p>
                <h3>Ask a research question</h3>
              </div>

              <span className="panel-tag">RAG enabled</span>
            </div>

            {selectedDocumentId && (
                <div className="selected-document">
                  <div>
                    📄 Searching only in:
                    <strong> {selectedDocumentName}</strong>
                  </div>

                  <button
                    className="secondary-button"
                    onClick={() => {
                      setSelectedDocumentId(null);
                      setSelectedDocumentName("");
                    }}
                  >
                    Search All Documents
                  </button>
                </div>
              )}

            <textarea
              placeholder="Example: What are the main findings of this study?"
              value={question}
              onChange={(event) => setQuestion(event.target.value)}
            />

            <div className="query-footer">
              <span>{question.length} characters</span>

              <button
                className="primary-button compact"
                disabled={!question.trim() || isAsking}
                onClick={askQuestion}
              >
                {isAsking ? "Generating..." : "Generate Answer"}
              </button>
            </div>
          </div>
        </section>

        <section className="documents-section">
  <div className="documents-header">
    <div>
      <p className="step-label">LIBRARY</p>
      <h3>My Documents</h3>
    </div>

    <button
      type="button"
      className="secondary-button"
      onClick={fetchDocuments}
      disabled={documentsLoading}
    >
      {documentsLoading ? "Loading..." : "Refresh"}
    </button>
  </div>

  {documentsError && (
    <div className="message-box error-message">
      {documentsError}
    </div>
  )}

  {!documentsLoading &&
    !documentsError &&
    documents.length === 0 && (
      <div className="documents-empty">
        Henüz yüklenmiş bir doküman yok.
      </div>
    )}

  <div className="documents-list">
    {documents.map((document) => (
      <article
        className="document-card"
        key={document.document_id}
      >
        <div className="document-main">
          <div className="document-icon">📄</div>

          <div>
            <h4>{document.filename}</h4>

            <div className="document-meta">
              <span>
                {document.page_count} sayfa
              </span>

              <span>
                {new Date(
                  document.uploaded_at
                ).toLocaleDateString("tr-TR")}
              </span>
            </div>
          </div>
        </div>

        <div className="document-actions">
          <button
            type="button"
            className="secondary-button"
            onClick={() => {
              setSelectedDocumentId(document.document_id);
              setSelectedDocumentName(document.filename);
            }}
          >
            🔍 Bu dokümanda ara
          </button>

          <button
            type="button"
            className="danger-button"
            onClick={() =>
              deleteDocument(document.document_id)
            }
          >
            🗑 Sil
          </button>
        </div>
      </article>
    ))}
  </div>
</section>

        <section className="answer-panel">
          <div className="answer-header">
            <div>
              <p className="step-label">RESPONSE</p>
              <h3>Research answer</h3>
            </div>

            <span className="answer-status">
              {answer ? "Generated" : "Waiting for question"}
            </span>
          </div>

          {answer ? (
            <>
              <div className="answer-content">
                <p>{answer}</p>
              </div>

              {sources.length > 0 && (
                <div className="sources-section">
                  <h4>Sources</h4>

                  <div className="sources-list">
                    {sources.map((source, index) => (
                      <div className="source-card"
    key={`${source.filename}-${source.page_number}-${index}`}>
  <strong>{source.filename}</strong>
  <p>Sayfa {source.page_number}</p>
</div>
                    ))}
                  </div>
                </div>
              )}
            </>
          ) : (
            <div className="empty-state">
              <div className="empty-icon">✦</div>

              <strong>Your answer will appear here</strong>

              <span>
                Upload a document and ask a question to start the RAG pipeline.
              </span>
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

export default App;