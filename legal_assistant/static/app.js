// Ask page: send a question, render the structured answer (FR-08) and send feedback (FR-22).
// All server text is inserted with textContent, never innerHTML, so user or AI text cannot inject markup.
(function () {
  "use strict";

  const csrf = document.querySelector('meta[name="csrf-token"]').content;

  async function postJSON(url, body) {
    const res = await fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", "X-CSRF-Token": csrf },
      body: JSON.stringify(body),
    });
    let data = {};
    try { data = await res.json(); } catch (_) { /* non-JSON error page */ }
    if (!res.ok) throw new Error(data.error || "Something went wrong. Please try again.");
    return data;
  }

  function el(tag, text, className) {
    const node = document.createElement(tag);
    if (text) node.textContent = text;
    if (className) node.className = className;
    return node;
  }

  function paragraphs(container, text) {
    text.split(/\n\s*\n|\n/).filter((p) => p.trim()).forEach((p) => container.appendChild(el("p", p.trim())));
  }

  function renderAnswer(data) {
    const node = document.getElementById("answer-template").content.firstElementChild.cloneNode(true);
    node.querySelector(".answer-question").textContent = data.question;

    if (data.category) {
      const badge = node.querySelector(".category-badge");
      badge.textContent = data.category.name;
      badge.hidden = false;
    }

    if (data.emergency.length) {
      const box = node.querySelector(".emergency");
      data.emergency.forEach((msg) => box.appendChild(el("p", msg)));
      box.hidden = false;
    }

    paragraphs(node.querySelector(".summary"), data.summary);
    node.querySelector(".source").textContent = data.source === "ai"
      ? "Summary written by AI using approved legal information."
      : "Summary from the approved legal knowledge base.";

    if (data.steps.length) {
      const list = node.querySelector(".steps");
      data.steps.forEach((s) => list.appendChild(el("li", s)));
      node.querySelector(".steps-section").hidden = false;
    }

    if (data.professional_help) {
      const reasons = node.querySelector(".lawyer-reasons");
      data.professional_help.reasons.forEach((r) => reasons.appendChild(el("li", r)));
      node.querySelector(".lawyer-advice").textContent = data.professional_help.advice;
      node.querySelector(".lawyer").hidden = false;
    }

    const refs = node.querySelector(".references");
    data.references.forEach((r) => {
      const li = el("li");
      const title = r.url ? el("a", r.title) : el("strong", r.title);
      if (r.url) { title.href = r.url; title.target = "_blank"; title.rel = "noopener"; }
      li.append(title, el("span", ` ${r.kind} · ${r.source}`, "muted small"), el("p", r.description, "small"));
      refs.appendChild(li);
    });
    if (data.no_reference_message) {
      const none = node.querySelector(".no-reference");
      none.textContent = data.no_reference_message;
      none.hidden = false;
    }

    node.querySelector(".disclaimer").textContent = data.disclaimer;
    setupFeedback(node.querySelector(".feedback-form"), data.query_id);
    return node;
  }

  function setupFeedback(form, queryId) {
    const group = form.querySelector(".rating");
    const name = "rating-" + Math.random().toString(36).slice(2);
    // Built 5..1 and shown with row-reverse, so CSS "~" highlights the chosen star and the ones to its left.
    for (let i = 5; i >= 1; i--) {
      const label = el("label", "", "star");
      const input = document.createElement("input");
      input.type = "radio"; input.name = name; input.value = i;
      label.append(input, el("span", "★"));
      label.title = i + " star" + (i > 1 ? "s" : "");
      group.appendChild(label);
    }
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const status = form.querySelector(".feedback-status");
      const checked = form.querySelector(`input[name="${name}"]:checked`);
      if (!checked) { status.textContent = "Please choose a rating."; return; }
      try {
        const res = await postJSON("/api/feedback", {
          rating: Number(checked.value), comment: form.comment.value, query_id: queryId,
        });
        status.textContent = res.message;
        form.querySelector("button").disabled = true;
      } catch (err) {
        status.textContent = err.message;
      }
    });
  }

  function setupAsk() {
    const form = document.getElementById("ask-form");
    if (!form) return;
    const textarea = document.getElementById("question");
    const error = document.getElementById("question-error");
    const count = document.getElementById("char-count");
    const loading = document.getElementById("loading");
    const button = document.getElementById("ask-button");
    const answers = document.getElementById("answers");

    textarea.addEventListener("input", () => { count.textContent = textarea.value.length; error.textContent = ""; });
    document.querySelectorAll("[data-example]").forEach((chip) => chip.addEventListener("click", () => {
      textarea.value = chip.dataset.example;
      count.textContent = textarea.value.length;
      textarea.focus();
    }));
    textarea.addEventListener("keydown", (e) => {
      if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) form.requestSubmit();
    });

    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const question = textarea.value.trim();
      if (question.length < 10) {  // same rule as the server (FR-06)
        error.textContent = "Please describe your problem in a few words.";
        return;
      }
      button.disabled = true;
      loading.hidden = false;
      try {
        const data = await postJSON("/api/query", { question });
        const node = renderAnswer(data);
        answers.prepend(node);
        node.scrollIntoView({ behavior: "smooth", block: "start" });
        textarea.value = "";
        count.textContent = "0";
      } catch (err) {
        error.textContent = err.message;
      } finally {
        button.disabled = false;
        loading.hidden = true;
      }
    });
  }

  setupAsk();
})();
