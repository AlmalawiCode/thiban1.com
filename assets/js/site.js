/* Thiban Tech Solutions — minimal vanilla JS.
   Handles the Arabic/English switch (persisted) and the mobile nav.
   The initial language is applied by a tiny inline script in <head>
   (see the generated pages) so there is no flash of the wrong language. */
(function () {
  "use strict";

  var STORAGE_KEY = "thiban-lang";

  function apply(lang) {
    var html = document.documentElement;
    html.setAttribute("data-lang", lang);
    html.setAttribute("lang", lang);
    html.setAttribute("dir", lang === "ar" ? "rtl" : "ltr");
    // Update every language button label to show the *other* language.
    var btns = document.querySelectorAll("[data-lang-toggle]");
    for (var i = 0; i < btns.length; i++) {
      btns[i].textContent = lang === "ar" ? "English" : "العربية";
      btns[i].setAttribute(
        "aria-label",
        lang === "ar" ? "Switch to English" : "التبديل إلى العربية"
      );
    }
  }

  function current() {
    return document.documentElement.getAttribute("data-lang") || "en";
  }

  function setLang(lang) {
    try { localStorage.setItem(STORAGE_KEY, lang); } catch (e) {}
    apply(lang);
  }

  document.addEventListener("DOMContentLoaded", function () {
    // Sync button labels with whatever the head script already applied.
    apply(current());

    document.addEventListener("click", function (e) {
      var toggle = e.target.closest && e.target.closest("[data-lang-toggle]");
      if (toggle) {
        e.preventDefault();
        setLang(current() === "ar" ? "en" : "ar");
        return;
      }
      var navToggle = e.target.closest && e.target.closest("[data-nav-toggle]");
      if (navToggle) {
        var links = document.getElementById("nav-links");
        if (links) {
          var open = links.classList.toggle("open");
          navToggle.setAttribute("aria-expanded", open ? "true" : "false");
        }
      }
    });
  });
})();
