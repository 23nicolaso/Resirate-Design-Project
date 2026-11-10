/*
 * Address autocomplete for components/search_bar.html.
 * GET  {suggest-url}?q=...           -> {"suggestions": [{label, ..., selection_token}]}
 * POST {resolve-url} {selection_token} -> {"building_id", "created", "url"}
 */
(function () {
  "use strict";

  var MIN_CHARS = 3;
  var GENERIC_ERROR = "Something went wrong. Please try again.";

  function setStatus(el, message) {
    if (!el) { return; }
    el.textContent = message || "";
    el.classList.toggle("d-none", !message);
  }

  function resolveAndGo(form, token, statusEl) {
    setStatus(statusEl, "");
    return window.ResiRate.postJson(form.dataset.resolveUrl, { selection_token: token })
      .then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok || !data.url) {
            throw new Error(data.error || GENERIC_ERROR);
          }
          window.location.assign(data.url);
        });
      })
      .catch(function (err) {
        setStatus(statusEl, err.message || GENERIC_ERROR);
      });
  }

  function fetchSuggestions(form, query) {
    var url = form.dataset.suggestUrl + "?q=" + encodeURIComponent(query);
    return fetch(url, { headers: { "Accept": "application/json" }, credentials: "same-origin" })
      .then(function (response) {
        return response.json().then(function (data) {
          if (!response.ok) {
            throw new Error(data.error || GENERIC_ERROR);
          }
          return data.suggestions || [];
        });
      });
  }

  function initSearch(form) {
    var input = form.querySelector("input[name=q]");
    var list = form.querySelector(".address-suggestions");
    var statusEl = form.querySelector("[data-address-status]");
    var items = [];
    var activeIndex = -1;
    var latestQuery = "";

    function close() {
      list.classList.add("d-none");
      list.innerHTML = "";
      input.setAttribute("aria-expanded", "false");
      input.removeAttribute("aria-activedescendant");
      items = [];
      activeIndex = -1;
    }

    function setActive(index) {
      var options = list.querySelectorAll("[role=option]");
      options.forEach(function (opt, i) {
        var on = i === index;
        opt.classList.toggle("active", on);
        opt.setAttribute("aria-selected", on ? "true" : "false");
      });
      activeIndex = index;
      if (index >= 0 && options[index]) {
        input.setAttribute("aria-activedescendant", options[index].id);
        options[index].scrollIntoView({ block: "nearest" });
      } else {
        input.removeAttribute("aria-activedescendant");
      }
    }

    function choose(index) {
      var item = items[index];
      if (!item) { return; }
      input.value = item.label;
      close();
      resolveAndGo(form, item.selection_token, statusEl);
    }

    function render(suggestions) {
      items = suggestions;
      list.innerHTML = "";
      if (!suggestions.length) {
        var empty = document.createElement("li");
        empty.className = "list-group-item text-body-secondary small";
        empty.textContent = "No NYC addresses found. Try including the borough.";
        list.appendChild(empty);
      }
      suggestions.forEach(function (s, i) {
        var li = document.createElement("li");
        li.id = "address-option-" + i;
        li.className = "list-group-item list-group-item-action";
        li.setAttribute("role", "option");
        li.setAttribute("aria-selected", "false");
        li.textContent = s.label;
        li.addEventListener("mousedown", function (e) {
          e.preventDefault(); /* keep focus in the input */
          choose(i);
        });
        list.appendChild(li);
      });
      list.classList.remove("d-none");
      input.setAttribute("aria-expanded", "true");
      activeIndex = -1;
    }

    var lookup = window.ResiRate.debounce(function () {
      var query = input.value.trim();
      latestQuery = query;
      if (query.length < MIN_CHARS) {
        close();
        return;
      }
      fetchSuggestions(form, query)
        .then(function (suggestions) {
          if (query !== latestQuery) { return; } /* a newer request is pending */
          setStatus(statusEl, "");
          render(suggestions);
        })
        .catch(function (err) {
          if (query !== latestQuery) { return; }
          close();
          setStatus(statusEl, err.message || GENERIC_ERROR);
        });
    }, 250);

    input.addEventListener("input", lookup);

    input.addEventListener("keydown", function (e) {
      var open = !list.classList.contains("d-none") && items.length;
      if (e.key === "ArrowDown" && open) {
        e.preventDefault();
        setActive((activeIndex + 1) % items.length);
      } else if (e.key === "ArrowUp" && open) {
        e.preventDefault();
        setActive(activeIndex <= 0 ? items.length - 1 : activeIndex - 1);
      } else if (e.key === "Enter" && open && activeIndex >= 0) {
        e.preventDefault();
        choose(activeIndex);
      } else if (e.key === "Escape") {
        close();
      }
    });

    input.addEventListener("blur", function () {
      setTimeout(close, 150);
    });
  }

  /*
   * "View building" buttons on the server-rendered result list carry only the
   * address label, so look the label up again to get a signed selection token.
   */
  function initResultButtons() {
    var form = document.querySelector("[data-address-search]");
    if (!form) { return; }
    var statusEl = document.querySelector("[data-results-status]");
    document.querySelectorAll("[data-open-address]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var label = btn.dataset.openAddress;
        btn.disabled = true;
        setStatus(statusEl, "");
        fetchSuggestions(form, label)
          .then(function (suggestions) {
            var match = suggestions.filter(function (s) { return s.label === label; })[0] || suggestions[0];
            if (!match) {
              throw new Error("We couldn't open this address. Please pick it from the search box instead.");
            }
            return resolveAndGo(form, match.selection_token, statusEl);
          })
          .catch(function (err) {
            setStatus(statusEl, err.message || GENERIC_ERROR);
          })
          .then(function () { btn.disabled = false; });
      });
    });
  }

  function init() {
    document.querySelectorAll("[data-address-search]").forEach(initSearch);
    initResultButtons();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
