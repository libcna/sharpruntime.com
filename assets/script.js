/* Sharp Runtime — shared progressive enhancement */
(function () {
  'use strict';

  var THEME_KEY = 'sharp-runtime-theme';

  function savedTheme() {
    try { return localStorage.getItem(THEME_KEY); } catch (_) { return null; }
  }

  function effectiveTheme() {
    return savedTheme() || (window.matchMedia && window.matchMedia('(prefers-color-scheme: light)').matches ? 'light' : 'dark');
  }

  function labelThemeButtons() {
    var next = effectiveTheme() === 'light' ? 'dark' : 'light';
    document.querySelectorAll('.theme-toggle').forEach(function (button) {
      button.setAttribute('aria-label', 'Switch to ' + next + ' theme');
      button.setAttribute('title', 'Switch to ' + next + ' theme');
    });
  }

  document.querySelectorAll('.theme-toggle').forEach(function (button) {
    button.addEventListener('click', function () {
      var next = effectiveTheme() === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', next);
      try { localStorage.setItem(THEME_KEY, next); } catch (_) { /* storage may be unavailable */ }
      labelThemeButtons();
    });
  });
  labelThemeButtons();

  if (window.matchMedia) {
    var preference = window.matchMedia('(prefers-color-scheme: light)');
    var onPreference = function () { if (!savedTheme()) labelThemeButtons(); };
    if (preference.addEventListener) preference.addEventListener('change', onPreference);
    else if (preference.addListener) preference.addListener(onPreference);
  }

  var navToggle = document.querySelector('.nav-toggle');
  var navLinks = document.querySelector('.nav-links');
  function closeNav() {
    if (!navToggle || !navLinks) return;
    navLinks.classList.remove('open');
    navToggle.setAttribute('aria-expanded', 'false');
    navToggle.setAttribute('aria-label', 'Open navigation');
    document.body.classList.remove('menu-open');
  }
  if (navToggle && navLinks) {
    navToggle.addEventListener('click', function () {
      var open = navLinks.classList.toggle('open');
      navToggle.setAttribute('aria-expanded', String(open));
      navToggle.setAttribute('aria-label', open ? 'Close navigation' : 'Open navigation');
      document.body.classList.toggle('menu-open', open && window.innerWidth <= 620);
    });
    document.addEventListener('click', function (event) {
      if (!navToggle.contains(event.target) && !navLinks.contains(event.target)) closeNav();
    });
  }

  var docsToggle = document.querySelector('.docs-toggle');
  var docsSidebar = document.querySelector('.docs-sidebar');
  if (docsToggle && docsSidebar) {
    docsToggle.addEventListener('click', function () {
      var open = docsSidebar.classList.toggle('open');
      docsToggle.setAttribute('aria-expanded', String(open));
      docsToggle.textContent = open ? 'Hide documentation' : 'Browse documentation';
    });
  }

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape') {
      closeNav();
      if (docsSidebar) docsSidebar.classList.remove('open');
      if (docsToggle) {
        docsToggle.setAttribute('aria-expanded', 'false');
        docsToggle.textContent = 'Browse documentation';
      }
      return;
    }
    if (event.key === '/' && !event.ctrlKey && !event.metaKey && !event.altKey) {
      var tag = document.activeElement && document.activeElement.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
      event.preventDefault();
      var searchInput = document.getElementById('search-input');
      if (searchInput) searchInput.focus();
      else window.location.href = document.documentElement.getAttribute('data-search-url') || 'search.html';
    }
  });

  document.querySelectorAll('.docs-content h2[id], .docs-content h3[id]').forEach(function (heading) {
    if (heading.querySelector('.heading-anchor')) return;
    var anchor = document.createElement('a');
    anchor.className = 'heading-anchor';
    anchor.href = '#' + heading.id;
    anchor.textContent = '#';
    anchor.setAttribute('aria-label', 'Link to ' + heading.textContent);
    heading.appendChild(anchor);
  });

  function highlightCode(code) {
    var match = code.className.match(/language-([\w-]+)/);
    if (!match) return;
    var language = match[1].toLowerCase();
    var keywords = {
      cpp: new Set(['alignas','auto','bool','break','case','catch','char','class','const','constexpr','continue','default','delete','do','double','else','enum','explicit','false','final','float','for','if','include','int','long','namespace','new','noexcept','nullptr','override','private','protected','public','return','short','signed','sizeof','static','struct','template','this','throw','true','try','typedef','typename','using','virtual','void','while']),
      cmake: new Set(['add_executable','add_library','add_subdirectory','cmake_minimum_required','find_package','project','set','target_compile_features','target_include_directories','target_link_libraries']),
      bash: new Set(['case','cd','cmake','do','done','echo','elif','else','esac','fi','for','function','git','if','in','then','while']),
      json: new Set(['true','false','null']),
      xml: new Set([])
    };
    var source = code.textContent;
    var pattern = /\/\/[^\n]*|\/\*[\s\S]*?\*\/|#[^\n]*|"(?:\\.|[^"\\])*"|'(?:\\.|[^'\\])*'|\b(?:0x[\da-fA-F]+|\d+(?:\.\d+)?)\b|[A-Za-z_][\w:.]*|\s+|./g;
    var fragment = document.createDocumentFragment();
    var token;
    while ((token = pattern.exec(source)) !== null) {
      var value = token[0];
      var className = '';
      if (/^(\/\/|\/\*)/.test(value) || (value[0] === '#' && language !== 'cpp')) className = 'tok-comment';
      else if (value[0] === '#' && language === 'cpp') className = 'tok-preprocessor';
      else if (/^["']/.test(value)) className = 'tok-string';
      else if (/^(?:0x[\da-f]+|\d)/i.test(value)) className = 'tok-number';
      else if (keywords[language] && keywords[language].has(value)) className = 'tok-keyword';
      if (className) {
        var span = document.createElement('span');
        span.className = className;
        span.textContent = value;
        fragment.appendChild(span);
      } else fragment.appendChild(document.createTextNode(value));
    }
    code.textContent = '';
    code.appendChild(fragment);
    var label = document.createElement('span');
    label.className = 'code-language';
    label.textContent = language === 'cpp' ? 'C++' : language;
    code.parentElement.insertBefore(label, code);
  }
  document.querySelectorAll('pre code[class*="language-"]').forEach(highlightCode);

  document.querySelectorAll('pre').forEach(function (pre) {
    var code = pre.querySelector('code');
    if (!code || pre.querySelector('.copy-button')) return;
    var button = document.createElement('button');
    button.type = 'button';
    button.className = 'copy-button';
    button.textContent = 'Copy';
    button.setAttribute('aria-label', 'Copy code');
    button.addEventListener('click', function () {
      if (!navigator.clipboard) return;
      navigator.clipboard.writeText(code.textContent).then(function () {
        button.textContent = 'Copied';
        window.setTimeout(function () { button.textContent = 'Copy'; }, 1600);
      });
    });
    pre.appendChild(button);
  });
})();
