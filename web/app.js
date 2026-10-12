/* Matrix Quest - the browser side.
 * Everything that runs Python goes through the local server (server.py):
 * this file only draws the game and sends your code there. */
"use strict";

const TOKEN = document.querySelector('meta[name="matrix-token"]').content;
const $ = (sel, root = document) => root.querySelector(sel);
const main = $("#main");

const COLORS = {
  "Morpheus": "#7cc8ff", "Trinity": "#d79bff", "Tank": "#a5e26a", "Neo": "var(--accent)",
  "The Oracle": "#ffd166", "The Keymaker": "#ffab70", "The Architect": "#ff6b6b",
  "Mouse": "#9ad1c9", "Cypher": "#ff8a65", "Niobe": "#f48fb1", "The Merovingian": "#ff6b6b",
};

let GAME = null;      // worlds and chapters from the server
let STATE = null;     // progress: xp, fights, forged, projects, rank
const fights = {};    // fight state kept while you browse around
const editors = {};   // forge editor contents not yet saved

/* ------------------------------------------------------------ helpers */

function esc(text) {
  return String(text).replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
}

function h(html) {
  const t = document.createElement("template");
  t.innerHTML = html.trim();
  return t.content.firstElementChild;
}

async function api(path, body = {}) {
  const response = await fetch(path, {
    method: "POST",
    headers: { "Content-Type": "application/json", "X-Matrix-Token": TOKEN },
    body: JSON.stringify(body),
  });
  const data = await response.json().catch(() => ({ error: "bad response" }));
  if (!response.ok) throw new Error(data.error || response.statusText);
  return data;
}

function toast(message) {
  const el = $("#toast");
  el.textContent = message;
  el.classList.add("show");
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => el.classList.remove("show"), 2600);
}

const store = {
  get(key, fallback) {
    try { const v = localStorage.getItem("mq." + key); return v === null ? fallback : JSON.parse(v); }
    catch { return fallback; }
  },
  set(key, value) { try { localStorage.setItem("mq." + key, JSON.stringify(value)); } catch { /* private mode */ } },
};

const KEYWORDS = new Set(("False None True and as assert async await break class continue def del elif else except " +
  "finally for from global if import in is lambda nonlocal not or pass raise return try while with yield").split(" "));
const BUILTINS = new Set(("print len range int str float list dict set tuple input open sum min max round super " +
  "isinstance issubclass type next enumerate sorted self cls staticmethod classmethod").split(" "));

function highlight(code) {
  const re = /(#[^\n]*)|("""[\s\S]*?"""|'''[\s\S]*?'''|f?"(?:\\.|[^"\\\n])*"|f?'(?:\\.|[^'\\\n])*')|(\b\d+(?:\.\d+)?\b)|(@\w+)|([A-Za-z_]\w*)/g;
  let out = "", last = 0, m;
  while ((m = re.exec(code))) {
    out += esc(code.slice(last, m.index));
    const [tok, com, str, num, deco, word] = m;
    if (com) out += `<span class="c">${esc(tok)}</span>`;
    else if (str) out += `<span class="s">${esc(tok)}</span>`;
    else if (num) out += `<span class="n">${esc(tok)}</span>`;
    else if (deco) out += `<span class="f">${esc(tok)}</span>`;
    else if (KEYWORDS.has(word)) out += `<span class="k">${esc(tok)}</span>`;
    else if (BUILTINS.has(word)) out += `<span class="f">${esc(tok)}</span>`;
    else out += esc(tok);
    last = re.lastIndex;
  }
  return out + esc(code.slice(last));
}

function codeBlock(code, tryIt = true) {
  if (!code) return "";
  const button = tryIt ? `<button class="btn small ghost" data-try title="Open in the Construct">▶ Try it</button>` : "";
  return `<div class="code-wrap"><pre class="code" data-code="${esc(code)}">${highlight(code)}</pre>${button}</div>`;
}

function wireTry(root) {
  root.querySelectorAll("[data-try]").forEach(btn => btn.addEventListener("click", () => {
    store.set("sandbox", { code: btn.previousElementSibling.dataset.code, args: "", stdin: "" });
    location.hash = "#/construct";
  }));
}

function avatar(who) {
  const initials = who.replace(/^The /, "").split(/\s+/).map(w => w[0]).join("").slice(0, 2).toUpperCase();
  return initials;
}

function lineHtml(line) {
  const c = COLORS[line.who] || "var(--info)";
  const neo = line.who === "Neo" ? " neo" : "";
  return `<div class="line${neo}" style="--c:${c}"><div class="avatar">${esc(avatar(line.who))}</div>
    <div class="bubble"><span class="who">${esc(line.who)}</span><span class="say"></span></div></div>`;
}

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function typeInto(el, text) {
  if (!settings.typing || matchMedia("(prefers-reduced-motion: reduce)").matches) { el.textContent = text; return; }
  el.textContent = "";
  for (let i = 0; i < text.length; i += 2) {
    if (el.dataset.skip) break;
    el.textContent = text.slice(0, i + 2);
    await sleep(14);
  }
  el.textContent = text;
}

/* Show dialogue lines one by one. Resolves when all are shown. */
function playDialogue(container, lines, done) {
  container.innerHTML = "";
  let i = 0;
  const next = h(`<button class="btn primary">Continue ▸</button>`);
  const skip = h(`<button class="btn ghost">Show all</button>`);
  const bar = h(`<div class="row" style="margin-top:1em"></div>`);
  bar.append(next, skip);
  const box = h(`<div class="dialogue"></div>`);
  container.append(box, bar);
  let typing = null, finished = false;
  const finish = () => {
    if (finished) return;
    finished = true; bar.remove(); container.onkey = null; done && done();
  };
  async function step() {
    if (typing) { typing.dataset.skip = "1"; return; }
    if (i >= lines.length) return;
    const el = h(lineHtml(lines[i++]));
    box.append(el);
    typing = $(".say", el);
    await typeInto(typing, lines[i - 1].text);
    typing = null;
    if (i >= lines.length) finish();
  }
  next.addEventListener("click", step);
  skip.addEventListener("click", () => {
    if (typing) typing.dataset.skip = "1";
    box.innerHTML = lines.map(lineHtml).join("");
    box.querySelectorAll(".say").forEach((el, k) => { el.textContent = lines[k].text; });
    i = lines.length;
    finish();
  });
  container.onkey = e => { if (e.key === "Enter" && document.activeElement.tagName !== "BUTTON") step(); };
  step();
  next.focus();
}

/* ------------------------------------------------------------ settings */

const settings = Object.assign({ size: "m", theme: "matrix", rain: true, typing: true },
  store.get("settings", {}));

function applySettings() {
  document.documentElement.dataset.size = settings.size;
  document.documentElement.dataset.theme = settings.theme;
  document.querySelectorAll(".seg").forEach(seg => {
    seg.querySelectorAll("button").forEach(b => b.classList.toggle("on", b.dataset.value === settings[seg.dataset.setting]));
  });
  document.querySelectorAll('input[type="checkbox"][data-setting]').forEach(cb => { cb.checked = !!settings[cb.dataset.setting]; });
  rain.toggle(settings.rain);
  store.set("settings", settings);
  Object.values(editorInstances).forEach(cm => cm && cm.refresh && cm.refresh());
}

function setupSettings() {
  const dialog = $("#settings");
  $("#settingsBtn").addEventListener("click", () => dialog.showModal());
  dialog.querySelectorAll(".seg button").forEach(b => b.addEventListener("click", () => {
    settings[b.parentElement.dataset.setting] = b.dataset.value; applySettings();
  }));
  dialog.querySelectorAll('input[type="checkbox"][data-setting]').forEach(cb => cb.addEventListener("change", () => {
    settings[cb.dataset.setting] = cb.checked; applySettings();
  }));
  $("#replayIntro").addEventListener("click", () => { dialog.close(); boot(true); });
  $("#resetProgress").addEventListener("click", async () => {
    if (!confirm("Erase all your progress (XP, fights, forges)? Your code files in workshop/ are kept.")) return;
    STATE = await api("/api/reset");
    Object.keys(fights).forEach(k => delete fights[k]);
    dialog.close(); renderChrome(); route(); toast("Progress reset. Welcome back, Neo.");
  });
}

/* ------------------------------------------------------------ digital rain */

const rain = (() => {
  const canvas = $("#rain");
  const ctx = canvas.getContext("2d");
  const glyphs = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓﾔﾕﾖﾗﾘﾙﾚﾛﾜﾝ0123456789<>=+*:".split("");
  let drops = [], size = 18, on = false, timer = null;
  function resize() {
    canvas.width = innerWidth; canvas.height = innerHeight;
    drops = Array.from({ length: Math.ceil(canvas.width / size) }, () => Math.random() * -50);
  }
  function frame() {
    const color = getComputedStyle(document.documentElement).getPropertyValue("--rain").trim() || "#2f6";
    const bg = getComputedStyle(document.documentElement).getPropertyValue("--bg").trim() || "#000";
    ctx.globalAlpha = 0.12; ctx.fillStyle = bg; ctx.fillRect(0, 0, canvas.width, canvas.height);
    ctx.globalAlpha = 1; ctx.fillStyle = color; ctx.font = `${size}px monospace`;
    drops.forEach((y, i) => {
      ctx.fillText(glyphs[(Math.random() * glyphs.length) | 0], i * size, y * size);
      drops[i] = y * size > canvas.height && Math.random() > 0.975 ? 0 : y + 1;
    });
  }
  addEventListener("resize", resize);
  document.addEventListener("visibilitychange", () => toggle(on));
  function toggle(want) {
    on = want && !matchMedia("(prefers-reduced-motion: reduce)").matches;
    clearInterval(timer); timer = null;
    canvas.hidden = !on;
    if (on && !document.hidden) { if (!drops.length) resize(); timer = setInterval(frame, 55); }
  }
  resize();
  return { toggle, boost(v) { canvas.style.opacity = v; } };
})();

/* ------------------------------------------------------------ boot sequence */

async function boot(force = false) {
  const el = $("#boot");
  if (!force && store.get("booted", false)) { el.hidden = true; $("#app").hidden = false; return; }
  $("#app").hidden = true;
  el.hidden = false;
  rain.toggle(true); rain.boost(0.5);
  el.innerHTML = `<div><div class="term" id="term"></div><div id="choice"></div></div>
    <button class="btn ghost skip" id="skipBoot">Skip intro</button>`;
  let skipped = false;
  const finish = () => {
    skipped = true; store.set("booted", true);
    el.hidden = true; $("#app").hidden = false; rain.boost(""); rain.toggle(settings.rain);
    location.hash = "#/home"; route();
  };
  $("#skipBoot").addEventListener("click", finish);
  const term = $("#term");
  const say = async (text, pause = 900) => {
    if (skipped) return;
    term.innerHTML = "";
    for (let i = 1; i <= text.length && !skipped; i++) {
      term.innerHTML = esc(text.slice(0, i)) + '<span class="cursor"></span>';
      await sleep(55);
    }
    await sleep(pause);
  };
  await say("Wake up, Neo...", 1200);
  await say("The Matrix has you...", 1200);
  await say("Follow the white rabbit.", 1000);
  await say("Knock, knock, Neo.", 900);
  if (skipped) return;
  term.innerHTML = `<p style="color:#cfe">Morpheus: <em>This is your last chance. After this, there is no turning back.</em></p>
    <p style="color:#cfe">You take the <b style="color:#6af">blue pill</b> - the story ends, you wake up in your bed and believe whatever you want to believe.</p>
    <p style="color:#cfe">You take the <b style="color:#f66">red pill</b> - you learn Python, and I show you how deep the rabbit hole goes.</p>`;
  $("#choice").innerHTML = `<div class="pills"><button class="pill blue" id="blue">Blue pill</button><button class="pill red" id="red">Red pill</button></div>`;
  $("#red").focus();
  $("#red").addEventListener("click", finish);
  $("#blue").addEventListener("click", () => {
    term.innerHTML = `<p style="color:#cfe">You wake up in your bed. Your Python projects are still due on Friday.</p>
      <p style="color:#cfe">Something feels... wrong.</p>`;
    $("#choice").innerHTML = `<div class="pills"><button class="pill red" id="red2">...fine. Red pill.</button></div>`;
    $("#red2").focus();
    $("#red2").addEventListener("click", finish);
  });
}

/* ------------------------------------------------------------ chrome */

function chapterNumber(chapter) {
  return Number(chapter.id.split("c")[1]) + 1;
}

function findChapter(id) {
  for (const world of GAME.worlds) {
    const i = world.chapters.findIndex(c => c.id === id);
    if (i >= 0) return { world, chapter: world.chapters[i], index: i };
  }
  return null;
}

function nextStep() {
  for (const world of GAME.worlds) {
    for (const chapter of world.chapters) {
      if (!STATE.forged.includes(chapter.id)) {
        const step = STATE.fights.includes(chapter.id) ? "forge" : "story";
        return { href: `#/${chapter.id}/${step}`, label: `${world.title} · ${chapter.title}` };
      }
    }
    if (!STATE.projects.includes(world.id)) return { href: `#/${world.id}/final`, label: `${world.title} · Final test` };
  }
  return null;
}

function renderChrome() {
  const pct = Math.round(100 * STATE.forged.length / STATE.total);
  $("#status").innerHTML = `<span class="rank" title="Your rank">${esc(STATE.rank)}</span>
    <div class="meter" title="${STATE.forged.length} of ${STATE.total} forge trials done">
      <div class="meter-bar"><div style="width:${pct}%"></div></div>
      <div class="meter-label">${STATE.forged.length}/${STATE.total} trials · ${STATE.xp} XP</div></div>`;
  const current = location.hash.split("/")[1] || "";
  $("#sidebar").innerHTML = GAME.worlds.map(world => {
    const items = world.chapters.map(c => {
      const fought = STATE.fights.includes(c.id), forged = STATE.forged.includes(c.id);
      return `<a class="nav-item${current === c.id ? " active" : ""}" href="#/${c.id}/story">
        <span class="num">${chapterNumber(c)}</span><span>${esc(c.title)}</span>
        <span class="ticks" title="fight · forge"><span class="${fought ? "tick-on" : ""}">⚔</span> <span class="${forged ? "tick-on" : ""}">⚒</span></span></a>`;
    }).join("");
    const done = STATE.projects.includes(world.id);
    return `<div class="world-nav"><h3><a href="#/${world.id}">${esc(world.title)}</a></h3>
      <span class="proj">${esc(world.project)} · ${esc(world.subtitle)}</span>${items}
      <a class="nav-item${current === world.id ? " active" : ""}" href="#/${world.id}/final"><span class="num">★</span>
      <span>Final test: your real project</span><span class="ticks"><span class="${done ? "tick-on" : ""}">${done ? "✓" : "○"}</span></span></a></div>`;
  }).join("");
}

/* ------------------------------------------------------------ views */

function view(html, narrow = false) {
  main.innerHTML = "";
  const el = h(`<div class="view${narrow ? " narrow" : ""}">${html}</div>`);
  main.append(el);
  main.scrollTop = 0;
  wireTry(el);
  return el;
}

function renderHome() {
  const next = nextStep();
  const cards = GAME.worlds.map((w, i) => {
    const done = w.chapters.filter(c => STATE.forged.includes(c.id)).length;
    const pct = Math.round(100 * done / w.chapters.length);
    return `<a class="panel world-card" href="#/${w.id}"><span class="kicker">PROJECT ${i + 1} · ${esc(w.project)}</span>
      <h2>${esc(w.title)}</h2><span class="muted">${esc(w.subtitle)} · with ${esc(w.mentor)}</span>
      <div class="meter"><div class="meter-bar"><div style="width:${pct}%"></div></div>
      <div class="meter-label">${done}/${w.chapters.length} chapters${STATE.projects.includes(w.id) ? " · project ✓" : ""}</div></div></a>`;
  }).join("");
  const el = view(`<div class="hero"><div class="panel"><h1>Welcome back, Neo.</h1>
    <p>Four programs stand between you and the Source - one for each of your Python projects. Every chapter is one exercise:
    you meet the crew, <b>train</b> with short lessons, <b>fight</b> code riddles that real Python verifies, then
    <b>forge</b> the code yourself. At the end of each world, the game checks <b>your real project</b>.</p>
    <div class="row">${next ? `<a class="btn primary" href="${next.href}">▸ Continue: ${esc(next.label)}</a>` :
      `<span class="tag">Everything complete. You are the One.</span>`}
      <a class="btn ghost" href="#/construct">⌨ Open the Construct (free coding)</a></div></div>
    <div class="worlds">${cards}</div>
    <p class="keys-help">Tips: <kbd>Enter</kbd> continues dialogue · <kbd>1</kbd>-<kbd>4</kbd> answer riddles ·
    <kbd>Ctrl</kbd>+<kbd>S</kbd> saves and <kbd>Ctrl</kbd>+<kbd>Enter</kbd> tests in the forge · ⚙ Settings changes text size and theme.</p></div>`);
  return el;
}

function renderWorld(world) {
  const list = world.chapters.map(c => `<li><a href="#/${c.id}/story">${chapterNumber(c)}. ${esc(c.title)}</a>
    <span class="tag">${esc(c.exercise)}</span> <span class="muted small">${esc(c.concept)}</span></li>`).join("");
  const el = view(`<div class="crumbs"><a href="#/home">Home</a> › ${esc(world.title)}</div>
    <div class="panel"><h1>${esc(world.title)}</h1><p class="muted">Project: <b>${esc(world.project)}</b> · ${esc(world.subtitle)}</p>
    <div id="dlg"></div></div>
    <div class="panel"><h2>Chapters</h2><ol style="padding-left:1.2em;display:grid;gap:.5em">${list}</ol>
    <a class="btn" href="#/${world.id}/final">★ Final test: defend your real project</a></div>`, true);
  playDialogue($("#dlg", el), world.intro, () => {
    $("#dlg", el).append(h(`<a class="btn primary" href="#/${world.chapters[0].id}/story">▸ Start chapter 1</a>`));
  });
  return el;
}

function chapterHeader(world, chapter, step) {
  const steps = [["story", "Briefing"], ["train", "Training"], ["fight", "Fight"], ["forge", "Forge"]];
  const done = { story: true, train: true, fight: STATE.fights.includes(chapter.id), forge: STATE.forged.includes(chapter.id) };
  const tabs = steps.map(([key, label], i) => `<a class="step${key === step ? " active" : ""}${done[key] && (key === "fight" || key === "forge") ? " done" : ""}"
    href="#/${chapter.id}/${key}"><span class="n">${done[key] && (key === "fight" || key === "forge") ? "✓" : i + 1}</span>${label}</a>`).join("");
  return `<div class="crumbs"><a href="#/home">Home</a> › <a href="#/${world.id}">${esc(world.title)}</a> › Chapter ${chapterNumber(chapter)}</div>
    <h1>${esc(chapter.title)}</h1>
    <div class="row"><span class="tag">${esc(world.project)} · ${esc(chapter.exercise)}</span><span class="muted small">${esc(chapter.concept)}</span></div>
    <nav class="steps">${tabs}</nav>`;
}

function renderStory(world, chapter) {
  const el = view(`${chapterHeader(world, chapter, "story")}<div class="panel"><div id="dlg"></div></div>`, true);
  playDialogue($("#dlg", el), chapter.story, () => {
    $("#dlg", el).append(h(`<a class="btn primary" style="margin-top:1em" href="#/${chapter.id}/train">▸ Start training</a>`));
    $("#dlg a.btn.primary", el).focus();
  });
  return el;
}

function renderTraining(world, chapter, pageIndex = 0) {
  const pages = chapter.pages;
  const page = pages[pageIndex];
  const last = pageIndex === pages.length - 1;
  const el = view(`${chapterHeader(world, chapter, "train")}
    <div class="panel"><div class="muted small">Training program ${pageIndex + 1} / ${pages.length}</div>
    <h2>${esc(page.title)}</h2><div class="page-text">${page.text.map(p => `<p>${esc(p)}</p>`).join("")}</div>
    ${codeBlock(page.code)}
    <div class="pager"><button class="btn ghost" id="prev" ${pageIndex === 0 ? "disabled" : ""}>◂ Back</button>
    <div class="dots">${pages.map((_, i) => `<button class="dot${i === pageIndex ? " on" : ""}" data-i="${i}" aria-label="Page ${i + 1}"></button>`).join("")}</div>
    ${last ? `<a class="btn primary" href="#/${chapter.id}/fight" id="next">▸ To the fight</a>` : `<button class="btn primary" id="next">Next ▸</button>`}</div></div>`, true);
  const go = i => renderTraining(world, chapter, i);
  $("#prev", el).addEventListener("click", () => go(pageIndex - 1));
  if (!last) $("#next", el).addEventListener("click", () => go(pageIndex + 1));
  el.querySelectorAll(".dot").forEach(d => d.addEventListener("click", () => go(Number(d.dataset.i))));
  el.onkey = e => {
    if (e.key === "ArrowRight" && !last) go(pageIndex + 1);
    if (e.key === "ArrowLeft" && pageIndex > 0) go(pageIndex - 1);
  };
  $("#next", el).focus();
  return el;
}

/* ------------------------------------------------------------ fights */

function newFight(count) {
  return { queue: [...Array(count).keys()], hp: count, max: count, hearts: 5, current: null, answered: false };
}

function renderFight(opts) {
  // opts: { fightId, riddles, enemy, header, onWin }
  const f = fights[opts.fightId] ||= newFight(opts.riddles.length);
  const el = view(`${opts.header}<div class="arena">
    <div class="panel enemy"><pre>${esc(opts.enemy.art.replace(/^\n/, ""))}</pre>
      <div class="name">${esc(opts.enemy.name)}</div><p class="taunt">"${esc(opts.enemy.taunt)}"</p>
      <div class="bars"><div class="hp"><span>${esc(opts.enemy.name)}</span><span id="ehp"></span></div>
      <div class="hp-bar enemy-hp"><div id="ebar"></div></div>
      <div class="hp"><span>Neo</span><span class="hearts" id="hearts"></span></div></div></div>
    <div class="panel" id="riddle" aria-live="polite"></div></div>`);
  const riddleBox = $("#riddle", el);

  function bars() {
    $("#ehp", el).textContent = `${f.hp} / ${f.max}`;
    $("#ebar", el).style.width = `${100 * f.hp / f.max}%`;
    $("#hearts", el).innerHTML = "♥".repeat(f.hearts) + `<span class="lost">${"♥".repeat(5 - f.hearts)}</span>`;
  }

  function show() {
    bars();
    if (f.hp <= 0) return victory();
    if (f.hearts <= 0) return fainted();
    if (f.current === null) f.current = f.queue.shift();
    f.answered = false;
    const r = opts.riddles[f.current];
    riddleBox.innerHTML = `<div class="muted small">Riddle ${f.max - f.hp + 1} of ${f.max}${f.queue.length ? "" : " · last one!"}</div>
      <div class="question">${esc(r.question)}</div>${codeBlock(r.code, false)}
      ${r.kind === "choice"
        ? `<div class="options">${r.options.map((o, i) => `<button class="option" data-i="${i}"><span class="key">${i + 1}</span><span>${esc(o)}</span></button>`).join("")}</div>`
        : `<form class="blank"><input type="text" autocomplete="off" spellcheck="false" placeholder="type the missing word" aria-label="Your answer"><button class="btn primary">Answer</button></form>`}
      <div id="fb"></div>`;
    if (r.kind === "choice") {
      riddleBox.querySelectorAll(".option").forEach(b => b.addEventListener("click", () => submit(Number(b.dataset.i))));
      riddleBox.querySelector(".option").focus();
    } else {
      const form = $("form", riddleBox);
      form.addEventListener("submit", e => { e.preventDefault(); submit($("input", form).value); });
      $("input", form).focus();
    }
  }

  async function submit(answer) {
    if (f.answered) return;
    f.answered = true;
    const r = opts.riddles[f.current];
    riddleBox.querySelectorAll("button, input").forEach(b => { b.disabled = true; });
    let res;
    try { res = await api("/api/answer", { fight: opts.fightId, index: f.current, answer }); }
    catch (e) { toast("Connection to the Matrix lost: " + e.message); f.answered = false; show(); return; }
    if (r.kind === "choice") {
      riddleBox.querySelectorAll(".option").forEach(b => {
        const i = Number(b.dataset.i);
        if (i === res.answer) b.classList.add("right");
        else if (i === answer) b.classList.add("wrong");
      });
    }
    if (res.correct) { f.hp -= 1; STATE.xp += 5; }
    else { f.hearts -= 1; f.queue.push(f.current); riddleBox.classList.add("shake"); setTimeout(() => riddleBox.classList.remove("shake"), 400); }
    f.current = null;
    const expected = r.kind === "blank" && !res.correct ? `<p>The answer: <code>${esc(res.answer[0])}</code></p>` : "";
    const output = res.output !== undefined ? `<div class="console-title">Tank's console · what real Python printed</div><pre class="console">${esc(res.output || "(no output)")}</pre>` : "";
    $("#fb", riddleBox).innerHTML = `<div class="feedback ${res.correct ? "good" : "bad"}">
      <h3>${res.correct ? "✓ Hit! " + esc(opts.enemy.name) + " staggers." : "✗ " + esc(opts.enemy.name) + " strikes back. This riddle will return."}</h3>
      ${expected}<p>${esc(res.explain)}</p>${output}
      <button class="btn primary" id="cont">Continue ▸</button></div>`;
    bars(); renderChrome();
    $("#cont", riddleBox).addEventListener("click", show);
    $("#cont", riddleBox).focus();
  }

  function fainted() {
    riddleBox.innerHTML = `<div class="overlay"><h2 style="color:var(--danger)">You died in the Matrix.</h2>
      <p>Tank: "Hold on, Neo... I'm pulling you out. Reloading."</p>
      <p class="muted">The riddles you missed come back. Re-read the training if you need to - there's no shame in it.</p>
      <div class="row" style="justify-content:center">${opts.trainHref ? `<a class="btn ghost" href="${opts.trainHref}">Back to training</a>` : ""}
      <button class="btn primary" id="again">Jack back in</button></div></div>`;
    $("#again", riddleBox).addEventListener("click", () => { fights[opts.fightId] = newFight(opts.riddles.length); renderFight(opts); });
    $("#again", riddleBox).focus();
  }

  async function victory() {
    try { STATE = await api("/api/fight_won", { fight: opts.fightId }); } catch (e) { toast(e.message); }
    renderChrome();
    riddleBox.innerHTML = `<div class="overlay"><h2 style="color:var(--accent)">Victory</h2><p>${esc(opts.enemy.defeat)}</p>
      <div class="row" style="justify-content:center"><button class="btn ghost" id="replay">Fight again</button>${opts.winButton}</div></div>`;
    $("#replay", riddleBox).addEventListener("click", () => { fights[opts.fightId] = newFight(opts.riddles.length); renderFight(opts); });
    const btn = riddleBox.querySelector(".btn.primary");
    if (btn) btn.focus();
    opts.onWin && opts.onWin(riddleBox);
  }

  el.onkey = e => {
    const n = Number(e.key);
    if (!f.answered && n >= 1 && n <= 9 && document.activeElement.tagName !== "INPUT") {
      const b = riddleBox.querySelector(`.option[data-i="${n - 1}"]`);
      if (b && !b.disabled) b.click();
    }
  };
  show();
  return el;
}

function renderChapterFight(world, chapter) {
  return renderFight({
    fightId: chapter.id, riddles: chapter.riddles, enemy: chapter.enemy,
    header: chapterHeader(world, chapter, "fight"), trainHref: `#/${chapter.id}/train`,
    winButton: `<a class="btn primary" href="#/${chapter.id}/forge">▸ To the forge</a>`,
  });
}

/* ------------------------------------------------------------ editors */

const editorInstances = {};

function makeEditor(host, value, onSave, onRun) {
  let get, set, focus;
  if (window.CodeMirror) {
    const cm = CodeMirror(host, {
      value, mode: "python", lineNumbers: true, indentUnit: 4, tabSize: 4, matchBrackets: true,
      indentWithTabs: false, lineWrapping: false,
      extraKeys: {
        Tab: c => c.somethingSelected() ? c.indentSelection("add") : c.replaceSelection("    "),
        "Shift-Tab": c => c.indentSelection("subtract"),
        "Ctrl-S": () => onSave(), "Cmd-S": () => onSave(),
        "Ctrl-Enter": () => onRun(), "Cmd-Enter": () => onRun(),
      },
    });
    get = () => cm.getValue(); set = v => cm.setValue(v); focus = () => cm.focus();
    setTimeout(() => cm.refresh(), 30);
    editorInstances.current = cm;
  } else {
    const ta = h(`<textarea class="plain" spellcheck="false"></textarea>`);
    ta.value = value;
    ta.addEventListener("keydown", e => {
      if (e.key === "Tab") {
        e.preventDefault();
        const s = ta.selectionStart;
        ta.setRangeText("    ", s, ta.selectionEnd, "end");
      }
      if ((e.ctrlKey || e.metaKey) && e.key === "s") { e.preventDefault(); onSave(); }
      if ((e.ctrlKey || e.metaKey) && e.key === "Enter") { e.preventDefault(); onRun(); }
    });
    host.append(ta);
    get = () => ta.value; set = v => { ta.value = v; }; focus = () => ta.focus();
  }
  return { get, set, focus };
}

function outputHtml(out) {
  if (out.error) return `<span class="err">${esc(out.error)}</span>`;
  let html = esc(out.stdout || "");
  if (out.stderr) html += `<span class="err">${esc(out.stderr)}</span>`;
  if (!out.stdout && !out.stderr) html = `<span class="dim">(the program printed nothing)</span>`;
  html += `\n<span class="dim">── exit code ${out.code}${out.timeout ? " (stopped)" : ""}</span>`;
  return html;
}

/* ------------------------------------------------------------ forge */

async function renderForge(world, chapter) {
  const trial = chapter.trial;
  const el = view(`${chapterHeader(world, chapter, "forge")}
    <div class="panel briefing">
      <div><h3>Mission</h3><pre class="mission">${esc(trial.mission.join("\n"))}</pre></div>
      <div><h3>Trials your code must pass</h3><ul class="checks" id="checks">
          ${trial.checks.map(name => `<li><span class="todo">○</span><span>${esc(name)}</span></li>`).join("")}</ul>
        <div class="row" style="margin-top:1.2em"><h3 style="margin:0">Hints</h3><span class="spacer"></span>
          <button class="btn small" id="hintBtn">Show a hint (0/${trial.hints.length})</button></div><div id="hints"></div>
      </div>
    </div>
    <div>
        <div class="panel tight">
          <div class="editor-bar"><span class="filename">workshop/${esc(trial.filename)}</span><span class="spacer"></span>
            <button class="btn small ghost" id="reload" title="Load the file again (if you edited it in VS Code)">↻ Reload file</button>
            <button class="btn small ghost" id="reset" title="Go back to the starting code">Reset</button>
            <button class="btn small" id="save">Save <kbd>Ctrl S</kbd></button></div>
          <div class="editor" id="editor"></div>
          <div class="run-inputs">
            <label class="field">Command-line arguments (for Run)<input type="text" id="args" spellcheck="false" placeholder="e.g. hello world 42"></label>
            <label class="field">Input typed by the user (stdin, for Run)<textarea class="input" id="stdin" spellcheck="false" placeholder="one answer per line"></textarea></label>
          </div>
          <div class="row"><button class="btn" id="run">▶ Run</button><button class="btn primary" id="test">✔ Test my code <kbd>Ctrl ↵</kbd></button>
            <span class="muted small" id="where"></span></div>
          <div class="tabs"><button class="tab on" data-tab="out">Output</button><button class="tab" data-tab="lint">flake8 / mypy</button></div>
          <pre class="console" id="out"><span class="dim">Run your program or test it. Results appear here.</span></pre>
          <pre class="console" id="lint" hidden><span class="dim">Linters run when all trials pass.</span></pre>
          <div id="result"></div>
        </div>
    </div>`);
  let data;
  try { data = await api(`/api/forge/${chapter.id}/open`); }
  catch (e) { $("#out", el).innerHTML = `<span class="err">${esc(e.message)}</span>`; return el; }
  $("#where", el).textContent = `Also editable in your own editor: ${data.path}`;
  $("#args", el).value = trial.run_args; $("#stdin", el).value = trial.run_stdin;

  const save = async (quiet = false) => {
    editors[chapter.id] = undefined;
    try { await api(`/api/forge/${chapter.id}/save`, { code: editor.get() }); if (!quiet) toast("Saved to workshop/" + trial.filename); }
    catch (e) { toast("Save failed: " + e.message); }
  };
  const tab = name => {
    el.querySelectorAll(".tab").forEach(t => t.classList.toggle("on", t.dataset.tab === name));
    $("#out", el).hidden = name !== "out"; $("#lint", el).hidden = name !== "lint";
  };
  el.querySelectorAll(".tab").forEach(t => t.addEventListener("click", () => tab(t.dataset.tab)));

  const run = async () => {
    tab("out");
    $("#out", el).innerHTML = `<span class="dim">Running...</span>`;
    try {
      const out = await api(`/api/forge/${chapter.id}/run`, { code: editor.get(), args: $("#args", el).value, stdin: $("#stdin", el).value });
      $("#out", el).innerHTML = `<span class="dim">$ python3 ${esc(trial.filename)} ${esc($("#args", el).value)}</span>\n` + outputHtml(out);
    } catch (e) { $("#out", el).innerHTML = `<span class="err">${esc(e.message)}</span>`; }
  };

  const test = async () => {
    tab("out");
    $("#test", el).disabled = true;
    $("#out", el).innerHTML = `<span class="dim">The forge is testing your code with real Python...</span>`;
    let rep;
    try { rep = await api(`/api/forge/${chapter.id}/test`, { code: editor.get() }); }
    catch (e) { $("#out", el).innerHTML = `<span class="err">${esc(e.message)}</span>`; $("#test", el).disabled = false; return; }
    $("#test", el).disabled = false;
    editors[chapter.id] = undefined;
    const list = $("#checks", el);
    if (rep.load_error) {
      list.innerHTML = trial.checks.map(name => `<li><span class="todo">○</span><span>${esc(name)}</span></li>`).join("");
      $("#out", el).innerHTML = `<span class="err">✗ ${esc(rep.load_error)}</span>`;
    } else {
      list.innerHTML = rep.results.map(r => `<li><span class="${r.ok ? "ok" : "ko"}">${r.ok ? "✓" : "✗"}</span><span>${esc(r.name)}</span>
        ${r.ok ? "" : `<span class="why">→ ${esc(r.message)}</span>`}</li>`).join("");
      const passed = rep.results.filter(r => r.ok).length;
      $("#out", el).innerHTML = rep.results.map(r => `<span class="${r.ok ? "" : "err"}">${r.ok ? "✓" : "✗"} ${esc(r.name)}${r.ok ? "" : "\n    → " + esc(r.message)}</span>`).join("\n")
        + `\n\n<span class="dim">${passed}/${rep.results.length} trials passed</span>`;
    }
    if (rep.lint.length) {
      $("#lint", el).innerHTML = rep.lint.map(l => `<span class="${l.ok === false ? "err" : ""}">${l.ok === null ? "•" : l.ok ? "✓" : "✗"} ${esc(l.tool)}</span>${l.output ? "\n" + esc(l.output) : ""}`).join("\n\n");
    }
    STATE = rep.state; renderChrome();
    const result = $("#result", el);
    if (rep.passed) {
      const lintBad = rep.lint.some(l => l.ok === false);
      const nextIdx = world.chapters.indexOf(chapter) + 1;
      const nextHref = nextIdx < world.chapters.length ? `#/${world.chapters[nextIdx].id}/story` : `#/${world.id}/final`;
      const nextLabel = nextIdx < world.chapters.length ? `▸ Next: ${esc(world.chapters[nextIdx].title)}` : "▸ Final test of this world";
      result.innerHTML = `<div class="banner"><h3>⚒ Forged! All trials pass.</h3>
        ${lintBad ? `<p>⚠ flake8 or mypy have remarks (see the tab above). The subject requires both to be clean - worth fixing.</p>` : ""}
        <div id="vic"></div><div class="row" style="margin-top:.8em"><a class="btn primary" href="${nextHref}">${nextLabel}</a></div></div>`;
      playDialogue($("#vic", result), chapter.victory, () => {});
    } else {
      result.innerHTML = `<div class="banner bad">Not yet. Read the ✗ messages, fix your code, and test again. Stuck? Take a hint - or ask a peer.</div>`;
    }
  };

  const editor = makeEditor($("#editor", el), editors[chapter.id] ?? data.code, () => save(), test);
  editor.focus();
  if (window.CodeMirror && editorInstances.current) editorInstances.current.on("change", () => { editors[chapter.id] = editor.get(); });
  $("#save", el).addEventListener("click", () => save());
  $("#run", el).addEventListener("click", run);
  $("#test", el).addEventListener("click", test);
  $("#reload", el).addEventListener("click", async () => {
    const fresh = await api(`/api/forge/${chapter.id}/open`); editor.set(fresh.code); editors[chapter.id] = undefined; toast("Reloaded from disk");
  });
  $("#reset", el).addEventListener("click", async () => {
    if (!confirm("Replace your code with the starting skeleton?")) return;
    const fresh = await api(`/api/forge/${chapter.id}/reset`); editor.set(fresh.code); editors[chapter.id] = undefined;
  });
  let shown = 0;
  $("#hintBtn", el).addEventListener("click", () => {
    if (shown >= trial.hints.length) return;
    $("#hints", el).append(h(`<div class="hint">💡 ${esc(trial.hints[shown++])}</div>`));
    $("#hintBtn", el).textContent = shown >= trial.hints.length ? "No more hints - ask a peer!" : `Show a hint (${shown}/${trial.hints.length})`;
  });
  return el;
}

/* ------------------------------------------------------------ world final */

function renderFinal(world) {
  const header = `<div class="crumbs"><a href="#/home">Home</a> › <a href="#/${world.id}">${esc(world.title)}</a> › Final test</div>
    <h1>Final test: ${esc(world.project)}</h1>
    <p class="muted">First the evaluators' questions, then the game checks the project <b>you</b> wrote.</p>`;
  if (!STATE.fights.includes(world.id)) {
    return renderFight({
      fightId: world.id, riddles: world.defense, enemy: world.boss, header,
      winButton: `<button class="btn primary" id="toCheck">▸ Check my real project</button>`,
      onWin: box => $("#toCheck", box).addEventListener("click", () => renderProjectCheck(world, header)),
    });
  }
  return renderProjectCheck(world, header);
}

function renderProjectCheck(world, header) {
  const saved = store.get("path." + world.id, GAME.project_root);
  const briefs = world.exercises.map(e => `<div class="brief"><code>${esc(e.folder)}/${esc(e.file)}</code><span>${esc(e.brief.join(" "))}</span></div>`).join("");
  const el = view(`${header}<div class="panel"><h2>Your project</h2>
    <p>Write these files yourself, in your project repository. Your forge files in <code>workshop/</code> are a good reference - but the
    names, the plants and the details are different, so you'll really have to think. Then point the checker at your folder.</p>
    <div class="briefs">${briefs}</div>
    <label class="field">Folder that contains ex0/, ex1/, ...<input type="text" id="path" value="${esc(saved)}" spellcheck="false"></label>
    <div class="row" style="margin-top:.8em"><button class="btn primary" id="check">⚖ Check my project</button>
    <span class="muted small">Same check in a terminal: <code>python3 play.py --check ${esc(world.id)} &lt;folder&gt;</code></span></div>
    <div id="reports"></div></div>`, true);
  $("#check", el).addEventListener("click", async () => {
    const path = $("#path", el).value.trim();
    store.set("path." + world.id, path);
    $("#reports", el).innerHTML = `<p class="muted">Running your programs...</p>`;
    let res;
    try { res = await api("/api/check", { world: world.id, path }); }
    catch (e) { $("#reports", el).innerHTML = `<div class="banner bad">${esc(e.message)}</div>`; return; }
    STATE = res.state; renderChrome();
    $("#reports", el).innerHTML = res.reports.map(r => `<div class="report${r.ok ? " ok" : ""}"><h3>${r.ok ? "✓" : "✗"} ${esc(r.folder)}/${esc(r.file)}</h3><ul>
      ${r.failed.map(x => `<li class="f">${esc(x)}</li>`).join("")}${r.passed.map(x => `<li class="p">${esc(x)}</li>`).join("")}
      ${r.notes.map(x => `<li class="n">${esc(x)}</li>`).join("")}</ul></div>`).join("")
      + (res.ok ? `<div class="banner"><h3>All exercises pass the checks.</h3><div id="outro"></div>
        <p>Now make sure you can explain every line to a peer. That's the real test.</p></div>`
        : `<div class="banner bad">Some exercises still need work. Fix them and check again.</div>`);
    if (res.ok) playDialogue($("#outro", el), world.outro, () => {});
  });
  return el;
}

/* ------------------------------------------------------------ construct */

function renderConstruct() {
  const saved = store.get("sandbox", null) || { code: 'print("Hello from the Construct.")\n\nfor pill in ["red", "blue"]:\n    print(pill)\n', args: "", stdin: "" };
  const el = view(`<div class="crumbs"><a href="#/home">Home</a> › The Construct</div>
    <h1>The Construct</h1><p class="muted">"This is the Construct. It's our loading program." Run any Python here, with real Python.
    Files <code>keys.txt</code> and <code>ancient_fragment.txt</code> are available to open().</p>
    <div class="panel tight"><div class="editor" id="editor"></div>
    <div class="run-inputs"><label class="field">Command-line arguments<input type="text" id="args" spellcheck="false"></label>
    <label class="field">Input (stdin)<textarea class="input" id="stdin" spellcheck="false"></textarea></label></div>
    <div class="row"><button class="btn primary" id="run">▶ Run <kbd>Ctrl ↵</kbd></button></div>
    <div class="console-title">Output</div><pre class="console" id="out"><span class="dim">Nothing yet.</span></pre></div>`);
  $("#args", el).value = saved.args || ""; $("#stdin", el).value = saved.stdin || "";
  const run = async () => {
    const body = { code: editor.get(), args: $("#args", el).value, stdin: $("#stdin", el).value };
    store.set("sandbox", body);
    $("#out", el).innerHTML = `<span class="dim">Running...</span>`;
    try { $("#out", el).innerHTML = outputHtml(await api("/api/sandbox", body)); }
    catch (e) { $("#out", el).innerHTML = `<span class="err">${esc(e.message)}</span>`; }
  };
  const editor = makeEditor($("#editor", el), saved.code, () => { store.set("sandbox", { code: editor.get(), args: $("#args", el).value, stdin: $("#stdin", el).value }); toast("Kept in this browser"); }, run);
  $("#run", el).addEventListener("click", run);
  if (store.get("sandbox", null)) run();
  return el;
}

/* ------------------------------------------------------------ router */

let currentView = null;

function route() {
  if (!GAME) return;
  $("#sidebar").classList.remove("open");
  const [, a = "home", b = ""] = location.hash.split("/");
  renderChrome();
  const world = GAME.worlds.find(w => w.id === a);
  const found = findChapter(a);
  if (a === "construct") currentView = renderConstruct();
  else if (world && b === "final") currentView = renderFinal(world);
  else if (world) currentView = renderWorld(world);
  else if (found) {
    const { world: w, chapter } = found;
    if (b === "train") currentView = renderTraining(w, chapter);
    else if (b === "fight") currentView = renderChapterFight(w, chapter);
    else if (b === "forge") renderForge(w, chapter).then(v => { currentView = v; });
    else currentView = renderStory(w, chapter);
  } else currentView = renderHome();
  main.focus({ preventScroll: true });
}

document.addEventListener("keydown", e => {
  if (e.target.closest && e.target.closest(".CodeMirror, textarea, input")) return;
  const v = main.firstElementChild;
  if (!v) return;
  if (v.onkey) v.onkey(e);
  const dlg = v.querySelector("#dlg, #vic, #outro");
  if (dlg && dlg.onkey) dlg.onkey(e);
});

async function start() {
  setupSettings();
  applySettings();
  $("#menuBtn").addEventListener("click", () => $("#sidebar").classList.toggle("open"));
  try {
    GAME = await api("/api/game");
  } catch (e) {
    document.body.innerHTML = `<div class="panel" style="margin:3em auto;max-width:600px;position:relative;z-index:2">
      <h2>No connection to the Matrix</h2><p>The game server isn't answering. Start it with <code>python3 play.py</code> and reload this page.</p>
      <p class="muted">${esc(e.message)}</p></div>`;
    return;
  }
  STATE = GAME.state;
  addEventListener("hashchange", route);
  await boot();
  if (!$("#app").hidden) route();
}

start();
