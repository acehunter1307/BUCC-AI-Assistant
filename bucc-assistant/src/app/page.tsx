"use client";

import { useState, useEffect, useRef, useCallback } from "react";

// ── Types ────────────────────────────────────────────────────────────────
type Role = "user" | "bot";

interface Message {
  id: string;
  role: Role;
  text: string;
  time: string;
  error?: boolean;
}

interface UserProfile {
  program: string;
  level: string;
}

// ── Onboarding state machine ─────────────────────────────────────────────
type OnboardStep = "ask_program" | "ask_level" | "done";

// ── Helpers ──────────────────────────────────────────────────────────────
const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

function nowTime() {
  return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function uid() {
  return Math.random().toString(36).slice(2);
}

const SUGGESTIONS = [
  "What classes do I have today?",
  "What's my next class?",
  "Any events today?",
  "Events this week?",
];

// ── Component ────────────────────────────────────────────────────────────
export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [onboardStep, setOnboardStep] = useState<OnboardStep>("ask_program");
  const [tempProgram, setTempProgram] = useState("");

  const bottomRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Load profile from localStorage on mount
  useEffect(() => {
    const saved = localStorage.getItem("bucc_profile");
    if (saved) {
      const p: UserProfile = JSON.parse(saved);
      setProfile(p);
      setOnboardStep("done");
      pushBot(
        `Welcome back! 👋 I remember you — ${p.program}, Level ${p.level}.\n\nWhat can I help you with today?`
      );
    } else {
      pushBot(
        "Hey there! 👋 Welcome to the BUCC AI Assistant.\n\nI can tell you about your classes, upcoming events, and more.\n\nFirst, what's your program? (e.g. Computer Science)"
      );
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  function pushBot(text: string, error = false) {
    setMessages((prev) => [
      ...prev,
      { id: uid(), role: "bot", text, time: nowTime(), error },
    ]);
  }

  function pushUser(text: string) {
    setMessages((prev) => [
      ...prev,
      { id: uid(), role: "user", text, time: nowTime() },
    ]);
  }

  // ── Onboarding handler ─────────────────────────────────────────────────
  function handleOnboard(text: string) {
    if (onboardStep === "ask_program") {
      setTempProgram(text);
      setOnboardStep("ask_level");
      pushBot(`Got it — ${text}! 📚\n\nNow what's your level? (e.g. 300)`);
      return;
    }

    if (onboardStep === "ask_level") {
      const levelMatch = text.match(/\d{3}/);
      const level = levelMatch ? levelMatch[0] : text.trim();
      const newProfile: UserProfile = { program: tempProgram, level };

      setProfile(newProfile);
      setOnboardStep("done");
      localStorage.setItem("bucc_profile", JSON.stringify(newProfile));

      pushBot(
        `Perfect! I've saved your profile:\n📖 Program: ${newProfile.program}\n🎓 Level: ${newProfile.level}\n\nYou can now ask me about your classes or events!`
      );
      return;
    }
  }

  // ── Query FastAPI ──────────────────────────────────────────────────────
  async function queryBackend(text: string, p: UserProfile) {
    setLoading(true);
    try {
      const params = new URLSearchParams({
        q: text,
        program: p.program,
        level: p.level,
      });

      const res = await fetch(`${API}/ask?${params}`);

      if (!res.ok) {
        throw new Error(`Server error: ${res.status}`);
      }

      const data = await res.json();

      // The /ask endpoint returns { intent, text, data } or { intent, message }
      const reply =
        data.text ||
        data.message ||
        "Sorry, I couldn't find an answer to that.";

      pushBot(reply);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Unknown error";
      pushBot(
        `Couldn't reach the server. Make sure your FastAPI backend is running.\n\n(${msg})`,
        true
      );
    } finally {
      setLoading(false);
    }
  }

  // ── Send message ──────────────────────────────────────────────────────
  const send = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || loading) return;

      pushUser(trimmed);
      setInput("");

      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = "auto";
      }

      if (onboardStep !== "done") {
        handleOnboard(trimmed);
        return;
      }

      await queryBackend(trimmed, profile!);
    },
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [loading, onboardStep, profile, tempProgram]
  );

  function handleKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      send(input);
    }
  }

  function handleTextareaChange(e: React.ChangeEvent<HTMLTextAreaElement>) {
    setInput(e.target.value);
    // Auto-grow
    e.target.style.height = "auto";
    e.target.style.height = `${Math.min(e.target.scrollHeight, 120)}px`;
  }

  function resetProfile() {
    localStorage.removeItem("bucc_profile");
    setProfile(null);
    setOnboardStep("ask_program");
    setTempProgram("");
    setMessages([]);
    setTimeout(() => {
      pushBot(
        "Profile cleared! Let's start fresh.\n\nWhat's your program? (e.g. Computer Science)"
      );
    }, 50);
  }

  const canSend = input.trim().length > 0 && !loading;

  return (
    <div className="chat-root">
      {/* Header */}
      <header className="header">
        <div className="header-logo">🎓</div>
        <div className="header-info">
          <h1>BUCC Assistant</h1>
          <p>Babcock University CS Department</p>
        </div>

        {profile ? (
          <div className="user-badge">
            <span className="badge-pill">
              {profile.program.split(" ").map((w) => w[0]).join("")} {profile.level}
            </span>
            <button className="reset-btn" onClick={resetProfile}>
              Switch
            </button>
          </div>
        ) : (
          <div className="header-status">
            <span className="status-dot" />
            Online
          </div>
        )}
      </header>

      {/* Messages */}
      <div className="messages">
        {messages.length === 0 && !loading && (
          <div className="welcome">
            <div className="welcome-icon">🎓</div>
            <h2>BUCC AI Assistant</h2>
            <p>
              Your smart academic companion for classes, events, and schedules at
              Babcock University.
            </p>
            {profile && (
              <div className="suggestion-chips">
                {SUGGESTIONS.map((s) => (
                  <button key={s} className="chip" onClick={() => send(s)}>
                    {s}
                  </button>
                ))}
              </div>
            )}
          </div>
        )}

        {messages.map((msg) => (
          <div key={msg.id}>
            <div className={`msg-row ${msg.role}`}>
              <div className={`bubble ${msg.error ? "error" : ""}`}>
                {msg.text}
              </div>
            </div>
            <div className={`msg-time ${msg.role === "user" ? "msg-row user" : "msg-row bot"}`}>
              {msg.time}
            </div>
          </div>
        ))}

        {loading && (
          <div className="typing-row">
            <div className="typing-bubble">
              <span className="typing-dot" />
              <span className="typing-dot" />
              <span className="typing-dot" />
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Suggestion chips (shown after onboarding) */}
      {profile && messages.length > 0 && !loading && (
        <div style={{ padding: "0 16px 8px", display: "flex", gap: 8, flexWrap: "wrap" }}>
          {SUGGESTIONS.map((s) => (
            <button key={s} className="chip" onClick={() => send(s)}>
              {s}
            </button>
          ))}
        </div>
      )}

      {/* Input */}
      <div className="input-area">
        <div className="input-wrap">
          <textarea
            ref={textareaRef}
            rows={1}
            value={input}
            onChange={handleTextareaChange}
            onKeyDown={handleKeyDown}
            placeholder={
              onboardStep === "ask_program"
                ? "Type your program..."
                : onboardStep === "ask_level"
                ? "Type your level (e.g. 300)..."
                : "Ask about classes or events..."
            }
            disabled={loading}
          />
        </div>
        <button
          className="send-btn"
          onClick={() => send(input)}
          disabled={!canSend}
          aria-label="Send"
        >
          ↑
        </button>
      </div>
    </div>
  );
}
