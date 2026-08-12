(function () {
  'use strict';
  var input = document.getElementById('search-input');
  var results = document.getElementById('search-results');
  if (!input || !results) return;
  var index = [];

  function escapeHtml(value) {
    return String(value).replace(/[&<>"']/g, function (character) {
      return {'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#039;'}[character];
    });
  }
  function score(page, terms) {
    var title = page.title.toLowerCase();
    var tags = page.tags.join(' ').toLowerCase();
    var description = page.description.toLowerCase();
    var headings = (page.headings || []).join(' ').toLowerCase();
    var content = (page.content || '').toLowerCase();
    var total = 0;
    for (var i = 0; i < terms.length; i += 1) {
      if (title.indexOf(terms[i]) !== -1) total += 8;
      if (tags.indexOf(terms[i]) !== -1) total += 4;
      if (description.indexOf(terms[i]) !== -1) total += 2;
      if (headings.indexOf(terms[i]) !== -1) total += 3;
      if (content.indexOf(terms[i]) !== -1) total += 1;
      if (!title.includes(terms[i]) && !tags.includes(terms[i]) && !description.includes(terms[i]) && !headings.includes(terms[i]) && !content.includes(terms[i])) return -1;
    }
    return total;
  }
  function run() {
    var query = input.value.trim().toLowerCase();
    var params = new URLSearchParams(window.location.search);
    if (query) { params.set('q', query); history.replaceState(null, '', '?' + params.toString()); }
    else { history.replaceState(null, '', window.location.pathname); }
    if (query.length < 2) { results.innerHTML = '<p>Type at least two characters to search.</p>'; return; }
    var terms = query.split(/\s+/).filter(Boolean);
    var matches = index.map(function (page) { return {page: page, score: score(page, terms)}; })
      .filter(function (item) { return item.score >= 0; })
      .sort(function (a, b) { return b.score - a.score || a.page.title.localeCompare(b.page.title); });
    if (!matches.length) {
      results.innerHTML = '<p>No results for <strong>' + escapeHtml(query) + '</strong>. Try a component name or a broader concept.</p>';
      return;
    }
    results.innerHTML = '<p class="search-count">' + matches.length + ' result' + (matches.length === 1 ? '' : 's') + '</p>' + matches.map(function (item) {
      var page = item.page;
      return '<a class="search-result" href="' + encodeURI(page.url) + '"><h2>' + escapeHtml(page.title) + '</h2><p>' + escapeHtml(page.description) + '</p><span class="search-result-meta">' + escapeHtml(page.category) + ' · ' + escapeHtml(page.url) + '</span></a>';
    }).join('');
  }
  fetch('search-index.json').then(function (response) { if (!response.ok) throw new Error('index'); return response.json(); })
    .then(function (data) { index = data; run(); })
    .catch(function () { results.innerHTML = '<p>Search index is unavailable. Use the documentation navigation above.</p>'; });
  input.addEventListener('input', run);
  var initial = new URLSearchParams(window.location.search).get('q') || '';
  input.value = initial;
  if (initial) input.focus();
})();
