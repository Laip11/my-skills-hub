/* Research Visual Report interactions. No framework dependency. */
function initPage() {
  "use strict";

  var configNode = document.getElementById("rvr-config");
  var config = {};
  try { config = JSON.parse(configNode ? configNode.textContent : "{}"); } catch (_error) {}
  var cardRoot = document.querySelector("[data-card-section]");
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (window.renderMathInElement) {
    try {
      renderMathInElement(document.body, {
        delimiters: [
          { left: "$$", right: "$$", display: true },
          { left: "$", right: "$", display: false },
          { left: "\\(", right: "\\)", display: false },
          { left: "\\[", right: "\\]", display: true }
        ],
        throwOnError: false
      });
    } catch (_error) {}
  }

  var themeButton = document.querySelector("[data-theme-toggle]");
  var savedTheme = null;
  try { savedTheme = window.localStorage.getItem("rvr-theme"); } catch (_error) {}
  var currentTheme = savedTheme || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  function applyTheme(theme) {
    currentTheme = theme;
    document.documentElement.setAttribute("data-theme", theme);
    if (themeButton) {
      themeButton.textContent = theme === "dark" ? "☀" : "◐";
      themeButton.setAttribute("aria-label", theme === "dark" ? "切换到浅色主题" : "切换到深色主题");
    }
  }
  applyTheme(currentTheme);
  if (themeButton) {
    themeButton.addEventListener("click", function () {
      var next = currentTheme === "dark" ? "light" : "dark";
      applyTheme(next);
      try { window.localStorage.setItem("rvr-theme", next); } catch (_error) {}
    });
  }

  var bar = document.querySelector(".progress");
  var toTop = document.querySelector(".to-top");
  function onScroll() {
    var page = document.documentElement;
    var max = page.scrollHeight - page.clientHeight;
    if (bar) bar.style.width = (max > 0 ? (page.scrollTop / max) * 100 : 0) + "%";
    if (toTop) toTop.classList.toggle("show", page.scrollTop > 700);
  }
  document.addEventListener("scroll", onScroll, { passive: true });
  onScroll();

  var spyLinks = Array.prototype.slice.call(document.querySelectorAll(".toc a"));
  var targets = spyLinks.map(function (link) {
    return document.getElementById(link.getAttribute("href").slice(1));
  }).filter(Boolean);
  function spy() {
    var y = window.scrollY + 120;
    var current = null;
    targets.forEach(function (target) { if (target.offsetTop <= y) current = target.id; });
    spyLinks.forEach(function (link) {
      link.classList.toggle("active", Boolean(current) && link.getAttribute("href") === "#" + current);
    });
  }
  document.addEventListener("scroll", spy, { passive: true });
  spy();

  var revealEls = document.querySelectorAll(".reveal");
  if (!reduced && "IntersectionObserver" in window) {
    var observer = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("in");
          observer.unobserve(entry.target);
        }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.02 });
    revealEls.forEach(function (element) { observer.observe(element); });
  } else {
    revealEls.forEach(function (element) { element.classList.add("in"); });
  }

  if (cardRoot) {
    function setCardClosed(card, closed) {
      card.classList.toggle("closed", closed);
      var toggle = card.querySelector(".card-toggle");
      if (toggle) toggle.setAttribute("aria-expanded", String(!closed));
    }

    cardRoot.querySelectorAll(".card-toggle").forEach(function (toggle) {
      toggle.addEventListener("click", function () {
        var card = toggle.closest(".card");
        setCardClosed(card, !card.classList.contains("closed"));
      });
    });

    var allButton = cardRoot.querySelector('[data-act="toggle-all"]');
    if (allButton) {
      allButton.addEventListener("click", function () {
        var cards = Array.prototype.slice.call(cardRoot.querySelectorAll(".card"));
        var anyOpen = cards.some(function (card) { return !card.classList.contains("closed"); });
        cards.forEach(function (card) { setCardClosed(card, anyOpen); });
        allButton.textContent = anyOpen ? config.expandButton : config.collapseButton;
      });
    }

    var sortButton = cardRoot.querySelector('[data-act="sort-date"]');
    var newestFirst = false;
    if (sortButton) {
      sortButton.addEventListener("click", function () {
        newestFirst = !newestFirst;
        sortButton.textContent = newestFirst ? config.sortButtonAlt : config.sortButton;
        sortButton.classList.toggle("on", newestFirst);
        cardRoot.querySelectorAll(".fam-group").forEach(function (group) {
          var cards = Array.prototype.slice.call(group.querySelectorAll(":scope > .card"));
          cards.sort(function (a, b) {
            var aDate = a.getAttribute("data-date") || "";
            var bDate = b.getAttribute("data-date") || "";
            return newestFirst ? bDate.localeCompare(aDate) : aDate.localeCompare(bDate);
          });
          cards.forEach(function (card) { group.appendChild(card); });
        });
      });
    }

    var familyRow = cardRoot.querySelector(".fam-row");
    if (familyRow) {
      var updateOverflow = function () {
        familyRow.classList.toggle("scrollable", familyRow.scrollWidth > familyRow.clientWidth + 1);
      };
      updateOverflow();
      window.addEventListener("resize", updateOverflow);
    }

    var chips = Array.prototype.slice.call(cardRoot.querySelectorAll(".chip[data-fam]"));
    var searchInput = cardRoot.querySelector("#card-search");
    var count = cardRoot.querySelector(".toolbar .count");
    var activeFamily = "all";
    function applyFilter() {
      var query = (searchInput && searchInput.value || "").trim().toLowerCase();
      var visible = 0;
      var total = 0;
      cardRoot.querySelectorAll(".card").forEach(function (card) {
        total += 1;
        var familyMatch = activeFamily === "all" || card.getAttribute("data-fam") === activeFamily;
        var textMatch = !query || (card.getAttribute("data-search") || "").toLowerCase().indexOf(query) !== -1;
        var show = familyMatch && textMatch;
        card.hidden = !show;
        if (show) visible += 1;
      });
      cardRoot.querySelectorAll(".fam-group").forEach(function (group) {
        var hasVisibleCard = Array.prototype.some.call(group.querySelectorAll(".card"), function (card) {
          return !card.hidden;
        });
        group.hidden = !hasVisibleCard;
      });
      if (count) {
        count.textContent = (config.countTemplate || "{visible} / {total}")
          .replace("{visible}", visible).replace("{total}", total);
      }
    }

    chips.forEach(function (chip) {
      chip.setAttribute("aria-pressed", String(chip.classList.contains("on")));
      chip.addEventListener("click", function () {
        activeFamily = chip.getAttribute("data-fam");
        chips.forEach(function (item) {
          var selected = item === chip;
          item.classList.toggle("on", selected);
          item.setAttribute("aria-pressed", String(selected));
          item.style.background = selected && item.getAttribute("data-fam") !== "all"
            ? item.getAttribute("data-color") : "";
        });
        applyFilter();
      });
    });
    if (searchInput) {
      searchInput.addEventListener("input", applyFilter);
      searchInput.addEventListener("keydown", function (event) {
        if (event.key === "Escape") { searchInput.value = ""; applyFilter(); }
      });
    }
    applyFilter();
  }

  if (toTop) {
    toTop.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: reduced ? "auto" : "smooth" });
    });
  }
}

document.addEventListener("DOMContentLoaded", initPage);
