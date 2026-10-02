// Year in footer
document.querySelectorAll("[data-year]").forEach((el) => (el.textContent = new Date().getFullYear()));

// Nav background on scroll
const nav = document.querySelector(".nav");
const onScroll = () => nav && nav.classList.toggle("scrolled", window.scrollY > 20);
onScroll();
window.addEventListener("scroll", onScroll, { passive: true });

// Reveal on scroll
const io = new IntersectionObserver((entries) => {
  entries.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
  });
}, { threshold: 0.12 });
document.querySelectorAll(".reveal").forEach((el) => io.observe(el));

// Sliders: drag with mouse, swipe on touch, arrows, progress
document.querySelectorAll(".slider-wrap").forEach((wrap) => {
  const track = wrap.querySelector(".slider");
  const prev = wrap.querySelector("[data-prev]");
  const next = wrap.querySelector("[data-next]");
  const bar = wrap.querySelector(".progress i");
  const count = wrap.querySelector(".count");

  const visible = () => [...track.querySelectorAll(".project")].filter((p) => !p.classList.contains("hide"));
  const step = () => {
    const first = visible()[0];
    return first ? first.getBoundingClientRect().width + parseFloat(getComputedStyle(track).gap || 0) : 300;
  };

  const update = () => {
    const max = track.scrollWidth - track.clientWidth;
    const ratio = max > 0 ? track.scrollLeft / max : 0;
    const items = visible();
    const shown = Math.max(1, Math.round(track.clientWidth / step()));
    const width = Math.min(100, (shown / Math.max(items.length, 1)) * 100);
    if (bar) { bar.style.width = width + "%"; bar.style.left = ratio * (100 - width) + "%"; }
    if (count) {
      const idx = Math.min(items.length, Math.round(track.scrollLeft / step()) + 1);
      count.textContent = String(idx).padStart(2, "0") + " / " + String(items.length).padStart(2, "0");
    }
    if (prev) prev.disabled = track.scrollLeft <= 2;
    if (next) next.disabled = track.scrollLeft >= max - 2;
  };

  prev && prev.addEventListener("click", () => track.scrollBy({ left: -step(), behavior: "smooth" }));
  next && next.addEventListener("click", () => track.scrollBy({ left: step(), behavior: "smooth" }));
  track.addEventListener("scroll", update, { passive: true });
  window.addEventListener("resize", update);

  // Mouse drag (touch already scrolls natively)
  let down = false, startX = 0, startLeft = 0, moved = 0;
  track.addEventListener("pointerdown", (e) => {
    if (e.pointerType !== "mouse") return;
    down = true; moved = 0; startX = e.clientX; startLeft = track.scrollLeft;
  });
  window.addEventListener("pointermove", (e) => {
    if (!down) return;
    const dx = e.clientX - startX;
    moved = Math.max(moved, Math.abs(dx));
    if (moved > 4) track.classList.add("dragging");
    track.scrollLeft = startLeft - dx;
  });
  window.addEventListener("pointerup", () => {
    if (!down) return;
    down = false;
    if (track.classList.contains("dragging")) {
      track.classList.remove("dragging");
      // snap to nearest card after dragging
      const target = Math.round(track.scrollLeft / step()) * step();
      track.scrollTo({ left: target, behavior: "smooth" });
    }
  });
  track.addEventListener("click", (e) => { if (moved > 4) e.preventDefault(); }, true);

  // Filters (portfolio page)
  const buttons = document.querySelectorAll(".filters button");
  buttons.forEach((btn) => btn.addEventListener("click", () => {
    buttons.forEach((b) => b.classList.toggle("on", b === btn));
    const f = btn.dataset.f;
    track.querySelectorAll(".project").forEach((p) => {
      p.classList.toggle("hide", !(f === "todos" || p.dataset.cat.split(" ").includes(f)));
      p.classList.add("in");
    });
    track.scrollTo({ left: 0 });
    update();
  }));

  update();
});
