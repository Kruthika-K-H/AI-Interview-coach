import { useState, useRef, useEffect } from "react";
import axios from "axios";
import "./App.css";

const API_BASE = "http://127.0.0.1:8000";

const categoryLabels = {
  coding: "💻 Coding",
  aptitude: "🧮 Aptitude",
  hr_behavioral: "🗣️ HR/Behavioral",
  company_specific: "🏢 Company-Specific"
};

function App() {
  const [messages, setMessages] = useState([
    { sender: "bot", text: "Hi! Upload your resume to get started (PDF or DOCX)." }
  ]);
  const [stage, setStage] = useState("awaiting_resume");
  const [resumeText, setResumeText] = useState("");
  const [sessionId, setSessionId] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [textInput, setTextInput] = useState("");
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const addMessage = (sender, text) => {
    setMessages((prev) => [...prev, { sender, text }]);
  };

  const handleFileUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    addMessage("user", `📄 Uploaded: ${file.name}`);
    setLoading(true);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await axios.post(`${API_BASE}/upload-resume`, formData);
      setResumeText(res.data.extracted_text);

      const sessionRes = await axios.post(`${API_BASE}/create-session`);
      setSessionId(sessionRes.data.session_id);

      const weaknessRes = await axios.get(`${API_BASE}/weakness-history`);
      if (weaknessRes.data.top_weaknesses.length > 0) {
        const topTags = weaknessRes.data.top_weaknesses
          .map((w) => w.tag.replace("_", " "))
          .join(", ");
        addMessage(
          "bot",
          `📈 Heads up — across your past sessions, you've been marked down most on: ${topTags}. Let's focus on improving these today.`
        );
      }

      addMessage("bot", "Now paste the job description you're targeting.");
      setStage("awaiting_jd");
    } catch (err) {
      addMessage("bot", "Something went wrong parsing your resume. Try again.");
    }
    setLoading(false);
  };

  const handleTextSubmit = async () => {
    if (!textInput.trim()) return;

    if (stage === "awaiting_jd") {
      addMessage("user", textInput);
      setLoading(true);
      try {
        const [analyzeRes, atsRes, prepRes] = await Promise.all([
          axios.post(`${API_BASE}/analyze`, { resume_text: resumeText, jd_text: textInput }),
          axios.post(`${API_BASE}/ats-score`, { resume_text: resumeText, jd_text: textInput }),
          axios.post(`${API_BASE}/prep-guide`, { resume_text: resumeText, jd_text: textInput })
        ]);

        addMessage(
          "bot",
          `📊 ATS Score: ${atsRes.data.ats_score}/100\n${atsRes.data.formatting_notes}`
        );

        const { matched_skills, missing_skills } = analyzeRes.data;
        addMessage(
          "bot",
          `✅ Matched Skills: ${matched_skills.join(", ")}\n⚠️ Missing Skills: ${missing_skills.join(", ")}`
        );

        const { prep_guide, questions: categorizedQuestions } = prepRes.data;
        addMessage(
          "bot",
          `📚 Topics to study: ${prep_guide.topics_to_study.join(", ")}\n📖 Resources: ${prep_guide.resources.join(", ")}`
        );

        const flatQuestions = [
          ...categorizedQuestions.coding.map((q) => ({ ...q, category: "coding" })),
          ...categorizedQuestions.aptitude.map((q) => ({ ...q, category: "aptitude" })),
          ...categorizedQuestions.hr_behavioral.map((q) => ({ ...q, category: "hr_behavioral" })),
          ...categorizedQuestions.company_specific.map((q) => ({ ...q, category: "company_specific" }))
        ];

        setQuestions(flatQuestions);
        setCurrentQIndex(0);

        addMessage("bot", `${categoryLabels[flatQuestions[0].category]} Question:\n${flatQuestions[0].text}`);
        setStage("awaiting_answer");
      } catch (err) {
        addMessage("bot", "Something went wrong analyzing. Try again.");
      }
      setLoading(false);
    } else if (stage === "awaiting_answer") {
      addMessage("user", textInput);
      setLoading(true);
      try {
        const isCoding = questions[currentQIndex].category === "coding";
        const endpoint = isCoding ? "/answer-coding" : "/answer";

        const res = await axios.post(`${API_BASE}${endpoint}`, {
          question: questions[currentQIndex].text,
          answer: textInput,
          session_id: sessionId
        });

        let feedbackMsg;
        if (isCoding) {
          const { score, correctness, bugs_or_issues, complexity_analysis, improvements, feedback_summary } = res.data;
          feedbackMsg = `Score: ${score}/10 (${correctness})\n🐛 Issues: ${bugs_or_issues?.join(", ") || "None"}\n⏱️ ${complexity_analysis}\n💡 ${improvements?.join(", ")}\n\n${feedback_summary}`;
        } else {
          const { score, strengths, improvements, feedback_summary } = res.data;
          feedbackMsg = `Score: ${score}/10\n✔ ${strengths.join("\n✔ ")}\n✘ ${improvements.join("\n✘ ")}\n\n${feedback_summary}`;
        }
        addMessage("bot", feedbackMsg);

        const nextIndex = currentQIndex + 1;
        if (nextIndex < questions.length) {
          setCurrentQIndex(nextIndex);
          addMessage("bot", `${categoryLabels[questions[nextIndex].category]} Question:\n${questions[nextIndex].text}`);
        } else {
          addMessage("bot", "That's all the questions! Great session. 🎉");
          setStage("done");
        }
      } catch (err) {
        addMessage("bot", "Something went wrong scoring your answer. Try again.");
      }
      setLoading(false);
    }

    setTextInput("");
  };

  const handleRestart = () => {
    setMessages([{ sender: "bot", text: "Hi! Upload your resume to get started (PDF or DOCX)." }]);
    setStage("awaiting_resume");
    setResumeText("");
    setSessionId(null);
    setQuestions([]);
    setCurrentQIndex(0);
    setTextInput("");
  };

  return (
    <div className="chat-container">
      <h2>AI Interview Coach</h2>
      <div className="chat-window">
        {messages.map((m, i) => (
          <div key={i} className={`message-row ${m.sender}`}>
            <div className={`avatar ${m.sender}`}>{m.sender === "bot" ? "🤖" : "🙂"}</div>
            <div className={`message ${m.sender}`}>
              {m.text.split("\n").map((line, j) => (
                <div key={j}>{line}</div>
              ))}
            </div>
          </div>
        ))}
        {loading && (
          <div className="message-row bot">
            <div className="avatar bot">🤖</div>
            <div className="message bot typing-indicator">
              <span></span><span></span><span></span>
            </div>
          </div>
        )}
        <div ref={chatEndRef} />
      </div>

      <div className="input-area">
        {stage === "awaiting_resume" ? (
          <input type="file" accept=".pdf,.docx" onChange={handleFileUpload} />
        ) : stage === "done" ? (
          <button onClick={handleRestart}>Start New Session</button>
        ) : (
          <>
            <textarea
              value={textInput}
              onChange={(e) => setTextInput(e.target.value)}
              placeholder={
                stage === "awaiting_jd" ? "Paste job description..." : "Type your answer..."
              }
              rows={3}
            />
            <button onClick={handleTextSubmit} disabled={loading}>
              Send
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default App;