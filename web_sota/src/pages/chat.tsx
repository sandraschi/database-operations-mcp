import { clsx } from "clsx";
import {
  Bot,
  Command,
  Mic,
  Paperclip,
  Send,
  Sparkles,
  User,
} from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { API_BASE } from "../lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

export function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      role: "assistant",
      content:
        "Hello! I'm your Database Operations assistant. I can help you analyze schemas, build queries, manage connections, or analyze database activity. How can I help you today?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [provider, setProvider] = useState<string | null>(null);
  const [checking, setChecking] = useState(true);
  const [activeModel, setActiveModel] = useState<string | null>(null);
  const [refining, setRefining] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const savedP = localStorage.getItem("llm_provider") || "ollama";
    const savedM = localStorage.getItem("llm_model") || "";
    if (savedM) {
      setActiveModel(savedM);
    }

    fetch(`${API_BASE}/api/v1/settings/llm`)
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => {
        if (d?.provider) {
          const mapping: Record<string, string> = {
            ollama: "Ollama",
            lm_studio: "LM Studio",
            openai: "OpenAI Compatible",
            deepseek: "DeepSeek",
            anthropic: "Anthropic Claude",
            gemini: "Google Gemini",
          };
          const provName = mapping[savedP] || d.provider;
          const modelName = savedM
            ? ` (${savedM})`
            : d.model
              ? ` (${d.model})`
              : "";
          setProvider(`${provName}${modelName}`);
        } else {
          setProvider(null);
        }
      })
      .catch(() => setProvider(null))
      .finally(() => setChecking(false));
  }, []);

  const handleRefine = async () => {
    if (!input.trim() || refining) return;
    setRefining(true);
    try {
      const res = await fetch(`${API_BASE}/api/v1/chat/refine`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: input,
          model: activeModel || undefined,
        }),
      });
      if (res.ok) {
        const data = await res.json();
        if (data.refined) {
          setInput(data.refined);
        }
      }
    } catch (error) {
      console.error("Refine error:", error);
    } finally {
      setRefining(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      role: "user",
      content: input,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    const currentInput = input;
    setInput("");

    try {
      const res = await fetch(`${API_BASE}/api/v1/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: currentInput,
          history: messages.map((m) => ({ role: m.role, content: m.content })),
          model: activeModel || undefined,
        }),
      });
      const data = await res.json();

      const assistantMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content: data.reply || "I'm sorry, I couldn't process that.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (error) {
      console.error("Chat error:", error);
      const errorMsg: Message = {
        id: (Date.now() + 1).toString(),
        role: "assistant",
        content:
          "I'm having trouble connecting to my intelligence core. Is the backend running?",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMsg]);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-8rem)] max-w-5xl mx-auto border border-slate-800 bg-slate-950/40 backdrop-blur-xl rounded-2xl overflow-hidden shadow-2xl shadow-black/50">
      {/* Chat Header */}
      <div className="p-4 border-b border-slate-800 bg-white/5 flex items-center justify-between shrink-0">
        <div className="flex items-center gap-4">
          <div className="p-2.5 bg-blue-600/10 rounded-xl border border-blue-600/20">
            <Sparkles className="w-5 h-5 text-blue-400" />
          </div>
          <div>
            <h3 className="font-bold text-white text-base leading-tight">
              Database Fleet Intelligence
            </h3>
            <p className="text-[10px] text-slate-400 flex items-center gap-1.5 mt-1 font-medium uppercase tracking-wider">
              <span
                className={`w-1.5 h-1.5 rounded-full ${provider ? "bg-emerald-500" : "bg-red-500"}`}
              />
              {checking
                ? "Scanning..."
                : provider
                  ? provider
                  : "No LLM available"}
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            title="Open Command Center"
            aria-label="Commands"
            className="p-2 hover:bg-white/5 rounded-lg text-slate-400 transition-colors"
          >
            <Command className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar bg-slate-950/20">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-4 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
          >
            <div
              className={`w-9 h-9 rounded-xl flex items-center justify-center border shadow-sm shrink-0 ${
                msg.role === "assistant"
                  ? "bg-blue-600/10 border-blue-600/20 text-blue-400"
                  : "bg-slate-800 border-slate-700 text-slate-200"
              }`}
            >
              {msg.role === "assistant" ? (
                <Bot className="w-4.5 h-4.5" />
              ) : (
                <User className="w-4.5 h-4.5" />
              )}
            </div>
            <div
              className={`max-w-[80%] p-4 rounded-2xl text-sm leading-relaxed ${
                msg.role === "assistant"
                  ? "bg-slate-900/50 border border-slate-800 text-slate-200 rounded-tl-none"
                  : "bg-blue-600 text-white rounded-tr-none"
              }`}
            >
              <div className="whitespace-pre-line">{msg.content}</div>
              <div
                className={`text-[10px] mt-2 opacity-50 font-medium ${msg.role === "user" ? "text-right" : ""}`}
              >
                {msg.timestamp.toLocaleTimeString([], {
                  hour: "2-digit",
                  minute: "2-digit",
                })}
              </div>
            </div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-slate-800 bg-slate-900/30 shrink-0">
        <div className="relative group">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) =>
              e.key === "Enter" &&
              !e.shiftKey &&
              (e.preventDefault(), handleSend())
            }
            placeholder="Ask anything about your databases..."
            className="w-full bg-slate-950/60 border border-white/5 rounded-2xl p-4 pr-32 min-h-[90px] max-h-[160px] resize-none text-slate-100 placeholder-slate-500 text-sm focus:ring-1 focus:ring-blue-500 outline-none transition-all duration-300 group-hover:border-white/10"
          />
          <div className="absolute right-3 bottom-3 flex items-center gap-2">
            <button
              type="button"
              onClick={handleRefine}
              disabled={refining || !input.trim()}
              title="Refine Prompt (AI Optimization)"
              aria-label="Refine"
              className={clsx(
                "p-2 rounded-lg text-slate-400 transition-colors hover:bg-white/5 hover:text-blue-400",
                refining ? "animate-pulse text-blue-400" : "",
                !input.trim() || refining
                  ? "opacity-40 cursor-not-allowed"
                  : "",
              )}
            >
              <Sparkles className="w-4 h-4" />
            </button>
            <button
              type="button"
              title="Attach File"
              aria-label="Attach"
              className="p-2 hover:bg-white/5 rounded-lg text-slate-400 transition-colors"
            >
              <Paperclip className="w-4 h-4" />
            </button>
            <button
              type="button"
              title="Voice Input"
              aria-label="Mic"
              className="p-2 hover:bg-white/5 rounded-lg text-slate-400 transition-colors"
            >
              <Mic className="w-4 h-4" />
            </button>
            <button
              type="button"
              onClick={handleSend}
              title="Send Message"
              aria-label="Send"
              className="p-2 bg-blue-600 text-white rounded-xl hover:bg-blue-500 transition-all shadow-lg shadow-blue-600/20"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
        <div className="mt-2.5 flex items-center justify-between px-2 text-[10px] text-slate-500 font-semibold uppercase tracking-widest">
          <span>Shift + Enter for newline</span>
          <span className="flex items-center gap-1">
            <Command className="w-3 h-3" /> J to open tools
          </span>
        </div>
      </div>
    </div>
  );
}
