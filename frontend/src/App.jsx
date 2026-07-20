
import { useEffect, useState } from "react";
import "./App.css";


function App() {
  const [selectedDocumentId, setSelectedDocumentId] = useState(null);
  const [selectedDocumentName, setSelectedDocumentName] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [question, setQuestion] = useState("");
  const [uploadMessage, setUploadMessage] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");
  const [documents, setDocuments] = useState([]);
  const [documentsLoading, setDocumentsLoading] = useState(false);
  const [documentsError, setDocumentsError] = useState("");
  const [messages, setMessages] = useState([]);
  const [conversationTitle, setConversationTitle] = useState("");
  const [conversationId, setConversationId] = useState(null);
  const [conversations, setConversations] = useState([]);
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
  const trimmedQuestion = question.trim();

  if (!trimmedQuestion) {
    return;
  }

  const userMessage = {
    role: "user",
    content: trimmedQuestion,
  };
  if (!conversationTitle) {
  setConversationTitle(trimmedQuestion);
}

  setMessages((currentMessages) => [
    ...currentMessages,
    userMessage,
  ]);

  setQuestion("");
  setIsAsking(true);
  setErrorMessage("");

  try {
  let activeConversationId = conversationId;

  if (!activeConversationId) {
    activeConversationId = await createConversation(
      trimmedQuestion
    );
  }

  const response = await fetch(
    "http://127.0.0.1:8000/search",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        question: trimmedQuestion,
        document_id: selectedDocumentId || null,
        conversation_id: activeConversationId,
      }),
    }
  );


    const data = await response.json();

    if (!response.ok) {
      throw new Error(
        data.detail ||
          "Cevap oluşturulurken bir hata oluştu."
      );
    }

    const assistantMessage = {
      role: "assistant",
      content: data.answer,
      sources: data.sources || [],
    };

    setMessages((currentMessages) => [
      ...currentMessages,
      assistantMessage,
    ]);
  } catch (error) {
    setErrorMessage(error.message);

    const errorMessage = {
      role: "assistant",
      content:
        "Üzgünüm, cevap oluşturulurken bir hata meydana geldi.",
      sources: [],
      isError: true,
    };

    setMessages((currentMessages) => [
      ...currentMessages,
      errorMessage,
    ]);
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
    if (selectedDocumentId === documentId) {
      setSelectedDocumentId(null);
      setSelectedDocumentName("");
      }

    await fetchDocuments();

  } catch (error) {
    setErrorMessage(error.message);
  }
};
const createConversation = async (title) => {
  const response = await fetch("http://127.0.0.1:8000/conversations", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      title: title,
      document_id: selectedDocumentId || null,
    }),
  });

  if (!response.ok) {
    throw new Error("Conversation oluşturulamadı.");
  }

  const data = await response.json();

  setConversationId(data.conversation_id);
  await loadConversations();

  return data.conversation_id;
};
const startNewConversation = () => {
  setMessages([]);
  setQuestion("");
  setErrorMessage("");
  setConversationTitle("");
  setConversationId(null);
};
const loadConversations = async () => {
  const response = await fetch(
    "http://127.0.0.1:8000/conversations"
  );

  if (!response.ok) {
    throw new Error("Conversations yüklenemedi.");
  }

  const data = await response.json();

  setConversations(data);
};
const loadConversationMessages = async (conversationId) => {
  console.log("Tıklanan conversation:", conversationId);

  const response = await fetch(
    `http://127.0.0.1:8000/conversations/${conversationId}/messages`
  );

  console.log("Response status:", response.status);

  if (!response.ok) {
    throw new Error("Conversation yüklenemedi.");
  }

  const data = await response.json();

  console.log("Backend'den gelen mesajlar:", data);

  setConversationId(conversationId);

  setMessages(
    data.map((message) => ({
      role: message.role,
      content: message.content
    }))
  );
};
useEffect(() => {
  loadConversations();
}, []);
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
          <div className="conversation-list">
            <h3>Research History</h3>

            <div className="conversation-items">
              {conversations.map((conversation) => (
                <button
                  key={conversation.conversation_id}
                  className={`conversation-item ${
                      conversationId === conversation.conversation_id
                          ? "active"
                          : ""
                  }`}
                  onClick={() =>
                      loadConversationMessages(
                          conversation.conversation_id
                      )
                  }
              >
                                <span className="conversation-icon">✦</span>

                  <span className="conversation-title">
                    {conversation.title}
                  </span>
                </button>
              ))}
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

       <section className="answer-panel chat-panel">
        <div className="answer-header">
          <div>
            <p className="step-label">CONVERSATION</p>
            <h3>
              {conversationTitle || "Research chat"}
              </h3>
          </div>

          <div className="conversation-actions">
            <span className="answer-status">
              {messages.length > 0
                ? `${messages.length} messages`
                : "Waiting for question"}
            </span>

            <button
              type="button"
              className="secondary-button"
              onClick={startNewConversation}
              disabled={messages.length === 0 || isAsking}
            >
              New Chat
            </button>
          </div>
        </div>

        {messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">✦</div>

            <strong>Your conversation will appear here</strong>

            <span>
              Upload or select a document and ask your first question.
            </span>
          </div>
        ) : (
          <div className="chat-messages">
            {messages.map((message, index) => (
              <div
                className={`chat-message ${message.role}`}
                key={`${message.role}-${index}`}
              >
                <div className="message-role">
                  {message.role === "user"
                    ? "You"
                    : "ScholarMind AI"}
                </div>

                <div
                  className={`message-bubble ${
                    message.isError ? "message-error" : ""
                  }`}
                >
                  <p>{message.content}</p>

                  {message.sources?.length > 0 && (
                    <div className="message-sources">
                      <strong>Sources</strong>

                      {message.sources.map(
                        (source, sourceIndex) => (
                          <div
                            className="message-source"
                            key={`${source.filename}-${source.page_number}-${sourceIndex}`}
                          >
                            <span>{source.filename}</span>
                            <span>
                              Sayfa {source.page_number}
                            </span>
                          </div>
                        )
                      )}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {isAsking && (
              <div className="chat-message assistant">
                <div className="message-role">
                  ScholarMind AI
                </div>

                <div className="message-bubble typing-message">
                  Cevap hazırlanıyor...
                </div>
              </div>
            )}
          </div>
        )}
      </section>
      </main>
    </div>
  );
}

export default App;