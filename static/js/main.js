/* ResiRate shared helpers, exposed as window.ResiRate. */
(function () {
  "use strict";

  function getCsrfToken() {
    var input = document.querySelector("input[name=csrfmiddlewaretoken]");
    if (input) {
      return input.value;
    }
    var match = document.cookie.match(/(?:^|;\s*)csrftoken=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : "";
  }

  function postJson(url, data) {
    return fetch(url, {
      method: "POST",
      credentials: "same-origin",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCsrfToken(),
        "Accept": "application/json"
      },
      body: JSON.stringify(data)
    });
  }

  function debounce(fn, wait) {
    var timer;
    return function () {
      var args = arguments;
      var self = this;
      clearTimeout(timer);
      timer = setTimeout(function () { fn.apply(self, args); }, wait);
    };
  }

  /* Django renders form widgets without Bootstrap classes; add them here. */
  function styleForms() {
    document.querySelectorAll(".rr-form .rr-field").forEach(function (wrapper) {
      wrapper.querySelectorAll("input, select, textarea").forEach(function (el) {
        var type = (el.getAttribute("type") || "").toLowerCase();
        if (type === "hidden") {
          return;
        }
        if (type === "checkbox" || type === "radio") {
          el.classList.add("form-check-input");
        } else if (el.tagName === "SELECT") {
          el.classList.add("form-select");
        } else {
          el.classList.add("form-control");
        }
        if (wrapper.classList.contains("has-error")) {
          el.classList.add("is-invalid");
          el.setAttribute("aria-invalid", "true");
        }
      });
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", styleForms);
  } else {
    styleForms();
  }

  window.ResiRate = {
    getCsrfToken: getCsrfToken,
    postJson: postJson,
    debounce: debounce
  };
})();
