/**
 * Kubernetes Copilot — Executive & Business Advisor Logic
 */

let currentConversationId = null;
let currentMessageCount = 0;
let pendingFeedbackMessageIndex = null;
let currentMode = "business"; // "business" or "technical"

// DOM Elements
const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const sendButton = document.getElementById("send-button");
const loadingIndicator = document.getElementById("loading-indicator");
const thinkingStepText = document.getElementById("thinking-step-text");
const welcomeCard = document.getElementById("welcome-card");
const btnNewChat = document.getElementById("btn-new-chat");
const sidebarToggle = document.getElementById("sidebar-toggle");
const sidebar = document.querySelector(".sidebar");
const activeModeDisplay = document.getElementById("active-mode-display");
const btnModeBusiness = document.getElementById("btn-mode-business");
const btnModeTechnical = document.getElementById("btn-mode-technical");

// Modals
const feedbackModal = document.getElementById("feedback-modal");
const btnCloseModal = document.getElementById("btn-close-modal");
const btnCancelFeedback = document.getElementById("btn-cancel-feedback");
const btnSubmitFeedback = document.getElementById("btn-submit-feedback");
const feedbackComment = document.getElementById("feedback-comment");

const glossaryModal = document.getElementById("glossary-modal");
const btnOpenGlossary = document.getElementById("btn-open-glossary");
const btnCloseGlossary = document.getElementById("btn-close-glossary");
const btnCloseGlossaryFooter = document.getElementById("btn-close-glossary-footer");

const systemStatusText = document.getElementById("system-status-text");
const llmModelBadge = document.getElementById("llm-model-badge");

// Initialize application
document.addEventListener("DOMContentLoaded", async () => {
    initNewConversation();
    fetchSystemHealth();
    setupEventListeners();
    setupTextareaAutoResize();
});

// Setup Event Listeners
function setupEventListeners() {
    chatForm.addEventListener("submit", handleFormSubmit);

    // Textarea Enter key handling (Shift+Enter for newline)
    userInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            chatForm.dispatchEvent(new Event("submit"));
        }
    });

    // New Briefing Button
    btnNewChat.addEventListener("click", () => {
        initNewConversation(true);
    });

    // Mode Selector
    btnModeBusiness.addEventListener("click", () => switchMode("business"));
    btnModeTechnical.addEventListener("click", () => switchMode("technical"));

    // Sidebar toggle for mobile
    if (sidebarToggle) {
        sidebarToggle.addEventListener("click", () => {
            sidebar.classList.toggle("open");
        });
    }

    // Prompt Chips in Sidebar
    document.querySelectorAll(".prompt-chip").forEach((chip) => {
        chip.addEventListener("click", () => {
            const promptText = chip.getAttribute("data-prompt");
            if (promptText) {
                userInput.value = promptText;
                chatForm.dispatchEvent(new Event("submit"));
            }
        });
    });

    // Starter Prompt Buttons on Welcome Card
    document.querySelectorAll(".starter-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const promptText = btn.getAttribute("data-prompt");
            if (promptText) {
                userInput.value = promptText;
                chatForm.dispatchEvent(new Event("submit"));
            }
        });
    });

    // Glossary Modal Triggers
    if (btnOpenGlossary) btnOpenGlossary.addEventListener("click", openGlossaryModal);
    if (btnCloseGlossary) btnCloseGlossary.addEventListener("click", closeGlossaryModal);
    if (btnCloseGlossaryFooter) btnCloseGlossaryFooter.addEventListener("click", closeGlossaryModal);

    // Glossary Card Click -> Auto-Ask
    document.querySelectorAll(".glossary-card").forEach((card) => {
        card.addEventListener("click", () => {
            const term = card.getAttribute("data-term");
            closeGlossaryModal();
            userInput.value = `Can you provide an executive briefing on Kubernetes ${term}? Explain the plain English analogy, how it works, and its business impact.`;
            chatForm.dispatchEvent(new Event("submit"));
        });
    });

    // Feedback Modal actions
    btnCloseModal.addEventListener("click", closeFeedbackModal);
    btnCancelFeedback.addEventListener("click", closeFeedbackModal);
    btnSubmitFeedback.addEventListener("click", submitNegativeFeedback);
}

// Mode Switching (Executive vs Technical)
function switchMode(mode) {
    currentMode = mode;
    if (mode === "business") {
        btnModeBusiness.classList.add("active");
        btnModeTechnical.classList.remove("active");
        document.body.className = "mode-business";
        if (activeModeDisplay) {
            activeModeDisplay.innerHTML = `<i class="fa-solid fa-user-tie"></i> Executive View`;
        }
    } else {
        btnModeTechnical.classList.add("active");
        btnModeBusiness.classList.remove("active");
        document.body.className = "mode-technical";
        if (activeModeDisplay) {
            activeModeDisplay.innerHTML = `<i class="fa-solid fa-code"></i> Technical View`;
        }
    }
}

// Auto-expand textarea
function setupTextareaAutoResize() {
    userInput.addEventListener("input", () => {
        userInput.style.height = "auto";
        userInput.style.height = Math.min(userInput.scrollHeight, 140) + "px";
    });
}

// Fetch system health and model info from API
async function fetchSystemHealth() {
    try {
        const response = await fetch("/api/health");
        if (response.ok) {
            const data = await response.json();
            if (systemStatusText) {
                systemStatusText.textContent = "Verified Standards Connected";
            }
            if (data.llm_model && llmModelBadge) {
                const provider = (data.llm_provider || "groq").toUpperCase();
                const modelDisplay = data.llm_model.includes("gpt-oss-120b") ? "GPT-OSS 120B" : data.llm_model;
                const effort = data.reasoning_effort ? ` • ${data.reasoning_effort.charAt(0).toUpperCase() + data.reasoning_effort.slice(1)}` : "";
                llmModelBadge.textContent = `${provider} (${modelDisplay}${effort})`;
            }
        }
    } catch (err) {
        console.warn("Could not fetch system health:", err);
        if (systemStatusText) {
            systemStatusText.textContent = "Offline / Standalone";
        }
    }
}

// Start a fresh conversation session
async function initNewConversation(clearUI = false) {
    try {
        const res = await fetch("/api/conversations", { method: "POST" });
        if (res.ok) {
            const data = await res.json();
            currentConversationId = data.conversation_id;
        } else {
            currentConversationId = `conv-${Date.now()}`;
        }
    } catch (err) {
        currentConversationId = `conv-${Date.now()}`;
    }

    currentMessageCount = 0;

    if (clearUI) {
        chatMessages.innerHTML = "";
        if (welcomeCard) {
            chatMessages.appendChild(welcomeCard);
            welcomeCard.style.display = "flex";
        }
    }
}

// Handle Form Submission
async function handleFormSubmit(e) {
    e.preventDefault();
    let query = userInput.value.trim();
    if (!query) return;

    // In business mode, optionally append framing if not already present
    let apiQuery = query;
    if (currentMode === "business" && !query.toLowerCase().includes("business") && !query.toLowerCase().includes("analogy") && !query.toLowerCase().includes("plain")) {
        apiQuery = `${query}\n(Please include a brief Executive Summary, Real-World Analogy, and Business Impact in plain English.)`;
    }

    // Hide welcome card if visible
    if (welcomeCard && welcomeCard.parentElement === chatMessages) {
        welcomeCard.style.display = "none";
    }

    // Append User Message to Thread
    appendUserMessage(query);
    userInput.value = "";
    userInput.style.height = "auto";
    sendButton.disabled = true;

    // Show Loading Animation
    showLoading();

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                message: apiQuery,
                conversation_id: currentConversationId
            })
        });

        if (!response.ok) {
            throw new Error(`Server returned status ${response.status}`);
        }

        const data = await response.json();
        currentConversationId = data.conversation_id;
        hideLoading();
        appendAssistantMessage(data);
    } catch (err) {
        hideLoading();
        console.error("Chat error:", err);
        appendErrorMessage("I couldn't generate a response right now. Please verify your backend server and try again.");
    } finally {
        sendButton.disabled = false;
        userInput.focus();
    }
}

// Append User Message
function appendUserMessage(text) {
    currentMessageCount++;
    const row = document.createElement("div");
    row.className = "message-row user";
    row.innerHTML = `
        <div class="message-content-wrapper">
            <div class="message-bubble">${escapeHtml(text)}</div>
        </div>
    `;
    chatMessages.appendChild(row);
    scrollToBottom();
}

// Append Assistant Message with Executive Formatting
function appendAssistantMessage(data) {
    const messageIndex = currentMessageCount++;
    const row = document.createElement("div");
    row.className = "message-row assistant";

    // Format Answer with Business Markdown Styling
    const formattedAnswer = renderBusinessMarkdown(data.answer);

    // Format Official Sources
    let sourcesHtml = "";
    if (data.sources && data.sources.length > 0) {
        const sourceLinks = data.sources.map(src => {
            return `
                <a href="${escapeHtml(src.url)}" target="_blank" rel="noopener noreferrer" class="source-item-link" title="Open official Kubernetes documentation">
                    <i class="fa-solid fa-arrow-up-right-from-square"></i>
                    <span>${escapeHtml(src.title)}</span>
                </a>
            `;
        }).join("");

        sourcesHtml = `
            <div class="sources-card">
                <div class="sources-header">
                    <i class="fa-solid fa-certificate"></i> Verified Against Official Kubernetes Documentation:
                </div>
                <div class="sources-list">${sourceLinks}</div>
            </div>
        `;
    }

    row.innerHTML = `
        <div class="message-avatar">
            <i class="fa-solid fa-dharmachakra"></i>
        </div>
        <div class="message-content-wrapper">
            <div class="message-bubble">
                <div class="message-body">${formattedAnswer}</div>
                ${sourcesHtml}
            </div>
            <div class="message-actions">
                <div class="feedback-group">
                    <button class="feedback-btn" data-thumb="up" data-index="${messageIndex}" title="Clear & helpful explanation">
                        <i class="fa-regular fa-thumbs-up"></i> Helpful
                    </button>
                    <button class="feedback-btn" data-thumb="down" data-index="${messageIndex}" title="Needs simpler explanation or missing context">
                        <i class="fa-regular fa-thumbs-down"></i> Needs Improvement
                    </button>
                </div>
                <button class="btn-copy-action" title="Copy briefing text">
                    <i class="fa-regular fa-copy"></i> Copy Briefing
                </button>
            </div>
        </div>
    `;

    // Attach feedback click handlers
    const btnUp = row.querySelector('.feedback-btn[data-thumb="up"]');
    const btnDown = row.querySelector('.feedback-btn[data-thumb="down"]');
    const btnCopy = row.querySelector('.btn-copy-action');

    btnUp.addEventListener("click", () => handleThumbUp(btnUp, btnDown, messageIndex));
    btnDown.addEventListener("click", () => openFeedbackModal(btnUp, btnDown, messageIndex));

    btnCopy.addEventListener("click", () => {
        navigator.clipboard.writeText(data.answer);
        btnCopy.innerHTML = `<i class="fa-solid fa-check"></i> Copied!`;
        setTimeout(() => {
            btnCopy.innerHTML = `<i class="fa-regular fa-copy"></i> Copy Briefing`;
        }, 2000);
    });

    chatMessages.appendChild(row);
    scrollToBottom();
}

// Append Error Message
function appendErrorMessage(errorText) {
    const row = document.createElement("div");
    row.className = "message-row assistant";
    row.innerHTML = `
        <div class="message-avatar" style="background: #ef4444;">
            <i class="fa-solid fa-triangle-exclamation"></i>
        </div>
        <div class="message-content-wrapper">
            <div class="message-bubble" style="border-color: rgba(239, 68, 68, 0.4);">
                <p style="color: #fca5a5;">${escapeHtml(errorText)}</p>
            </div>
        </div>
    `;
    chatMessages.appendChild(row);
    scrollToBottom();
}

// Feedback Handlers
async function handleThumbUp(btnUp, btnDown, index) {
    btnUp.classList.add("active", "thumb-up");
    btnDown.classList.remove("active", "thumb-down");

    try {
        await fetch("/api/feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                conversation_id: currentConversationId,
                thumb: "up",
                message_index: index
            })
        });
    } catch (e) {
        console.error("Feedback error:", e);
    }
}

function openFeedbackModal(btnUp, btnDown, index) {
    pendingFeedbackMessageIndex = index;
    feedbackModal.classList.remove("hidden");
}

function closeFeedbackModal() {
    feedbackModal.classList.add("hidden");
    pendingFeedbackMessageIndex = null;
    feedbackComment.value = "";
    const selectedRadio = document.querySelector('input[name="feedback-reason"]:checked');
    if (selectedRadio) selectedRadio.checked = false;
}

async function submitNegativeFeedback() {
    const selectedRadio = document.querySelector('input[name="feedback-reason"]:checked');
    const reason = selectedRadio ? selectedRadio.value : "Other";
    const comment = feedbackComment.value.trim();

    try {
        await fetch("/api/feedback", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                conversation_id: currentConversationId,
                thumb: "down",
                message_index: pendingFeedbackMessageIndex,
                reason: reason,
                comment: comment
            })
        });

        if (pendingFeedbackMessageIndex !== null) {
            const btnDown = document.querySelector(`.feedback-btn[data-thumb="down"][data-index="${pendingFeedbackMessageIndex}"]`);
            const btnUp = document.querySelector(`.feedback-btn[data-thumb="up"][data-index="${pendingFeedbackMessageIndex}"]`);
            if (btnDown) btnDown.classList.add("active", "thumb-down");
            if (btnUp) btnUp.classList.remove("active", "thumb-up");
        }
    } catch (e) {
        console.error("Feedback error:", e);
    } finally {
        closeFeedbackModal();
    }
}

// Glossary Modal Handlers
function openGlossaryModal() {
    glossaryModal.classList.remove("hidden");
}

function closeGlossaryModal() {
    glossaryModal.classList.add("hidden");
}

// Loading Indicator helpers
let thinkingTimer = null;
function showLoading() {
    loadingIndicator.classList.remove("hidden");
    const steps = [
        "Consulting official Kubernetes standards...",
        "Formulating plain English explanation...",
        "Structuring business impact & analogy...",
        "Finalizing executive briefing..."
    ];
    let stepIndex = 0;
    thinkingStepText.textContent = steps[0];
    thinkingTimer = setInterval(() => {
        stepIndex = (stepIndex + 1) % steps.length;
        thinkingStepText.textContent = steps[stepIndex];
    }, 1100);

    scrollToBottom();
}

function hideLoading() {
    if (thinkingTimer) clearInterval(thinkingTimer);
    loadingIndicator.classList.add("hidden");
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function escapeHtml(str) {
    if (!str) return "";
    return str
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

// Markdown Parser with Executive Callout Styling
function renderBusinessMarkdown(md) {
    if (!md) return "";

    let html = md;

    // Fenced Code Blocks (```bash ... ```)
    html = html.replace(/```([a-zA-Z0-9_\-]*)\n([\s\S]*?)```/g, (match, lang, code) => {
        return `<pre><code class="language-${lang || 'text'}">${escapeHtml(code.trim())}</code></pre>`;
    });

    // Inline Code (`code`)
    html = html.replace(/`([^`]+)`/g, (match, code) => {
        return `<code>${escapeHtml(code)}</code>`;
    });

    // Headers
    html = html.replace(/^### (.*$)/gim, '<h3>$1</h3>');
    html = html.replace(/^## (.*$)/gim, '<h2>$1</h2>');
    html = html.replace(/^# (.*$)/gim, '<h1>$1</h1>');

    // Bold (**text**)
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');

    // Bullet Lists (* item or - item)
    html = html.replace(/^\s*[-*]\s+(.*$)/gim, '<li>$1</li>');
    html = html.replace(/(<li>[\s\S]*?<\/li>)/gim, '<ul>$1</ul>');
    html = html.replace(/<\/ul>\s*<ul>/g, '');

    // Convert Markdown Tables
    html = html.replace(/\|(.+)\|/g, (match) => {
        const cells = match.split('|').filter(c => c.trim() !== '');
        if (cells.every(c => c.trim().match(/^-+$/))) {
            return ''; // separator row
        }
        const cellHtml = cells.map(c => `<td>${c.trim()}</td>`).join('');
        return `<tr>${cellHtml}</tr>`;
    });
    html = html.replace(/(<tr>[\s\S]*?<\/tr>)/gim, '<table>$1</table>');
    html = html.replace(/<\/table>\s*<table>/g, '');

    // Horizontal Rule
    html = html.replace(/^---+$/gim, '<hr class="section-divider">');

    // Paragraphs
    const blocks = html.split(/\n\n+/);
    html = blocks.map(block => {
        block = block.trim();
        if (!block) return "";
        if (block.startsWith("<pre>") || block.startsWith("<h1>") || block.startsWith("<h2>") || 
            block.startsWith("<h3>") || block.startsWith("<ul>") || block.startsWith("<table>") ||
            block.startsWith("<hr")) {
            return block;
        }

        // Highlight Executive Summary block
        if (block.includes("Executive Summary") || block.includes("📌")) {
            const cleanContent = block
                .replace(/<strong>\s*(?:📌)?\s*Executive Summary\s*<\/strong>:?/gi, '')
                .replace(/📌|Executive Summary:?/gi, '')
                .trim();
            return `<div class="executive-summary-box"><div class="executive-summary-title"><i class="fa-solid fa-bullseye"></i> Executive Summary</div><p>${cleanContent}</p></div>`;
        }

        // Highlight Analogy block
        if (block.includes("Real‑World Analogy") || block.includes("Real-World Analogy") || block.includes("Analogy") || block.includes("💡")) {
            const cleanContent = block
                .replace(/<strong>\s*(?:💡)?\s*Real[‑\-\s]*World Analogy\s*<\/strong>:?/gi, '')
                .replace(/💡|Real[‑\-\s]*World Analogy:?/gi, '')
                .trim();
            return `<div class="analogy-callout"><div class="analogy-title"><i class="fa-solid fa-lightbulb"></i> Real-World Analogy</div><p>${cleanContent}</p></div>`;
        }

        return `<p>${block.replace(/\n/g, '<br>')}</p>`;
    }).join("");

    return html;
}
