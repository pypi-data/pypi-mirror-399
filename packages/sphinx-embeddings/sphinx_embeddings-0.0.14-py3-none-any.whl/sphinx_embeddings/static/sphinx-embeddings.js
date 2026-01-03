Search.query = async (query) => {
  const [q, terms, excluded, highlights, objects] = Search._parseQuery(query);
  const results = await Search._performSearch(q, terms, excluded, highlights, objects);
  _displayNextItem(results, results.length, terms, highlights);
};

const dot = (a, b) => {
  if (a.length !== b.length) { throw new Error('a.length !== b.length'); }
  return a.reduce((sum, val, i) => sum + val * b[i], 0);
};

// TODO: Load all the data in parallel.
const fetchEmbeddings = async () => {
  const root = document.documentElement.dataset.content_root;
  const embeddingsIndexUrl = `${root}/.well-known/embeddings.json`;
  const response = await fetch(embeddingsIndexUrl);
  const index = await response.json();
  let embeddings = []
  for (let i = 0; i < index.length; i++) {
    const url = index[i];
    const embeddingResponse = await fetch(url);
    const data = await embeddingResponse.json();
    const docname = data.docname;
    data.sections.forEach(section => {
      const ids = section.ids;
      const title = section.title;
      section.embeddings.forEach(e => {
        if (e.provider === 'gemini-api' && e.model === 'gemini-embedding-001' && e.type === 'RETRIEVAL_DOCUMENT') {
          embeddings.push({'data': e.data, 'docname': docname, 'ids': ids, 'title': title});
        }
      });
    });
  }
  return embeddings;
};

const preload = async () => {
  const root = document.documentElement.dataset.content_root;
  const embeddingsIndexUrl = `${root}/.well-known/embeddings.json`;
  const response = await fetch(embeddingsIndexUrl);
  const index = await response.json();
  const requests = index.map(url => fetch(url));
  await Promise.all(requests);
};

// TODO: Handle the situation where sphinx-embeddings.js loads before
// searchtools.js.
Search._performSearch = async (query, terms, excluded, highlights, objects) => {
  const filenames = Search._index.filenames;
  const docnames = Search._index.docnames;
  const titles = Search._index.titles;

  // Update search UI.
  _removeChildren(document.getElementById("search-progress"));

  // TODO: Support custom Scorer

  const embeddings = await fetchEmbeddings();

  // Generate an embedding for the query.
  // TODO: Fetch on each keyup event.
  // TODO: Need to set task type
  const url = "https://script.google.com/macros/s/AKfycbz_7Y_VxVysKFUKZYDsQjlCpFPa33oTpRQQoFBSPY2reyWc9FM6_58ZSyN9r8Sg7SmB1w/exec";
  const response = await fetch(url, {
    method: "POST",
    redirect: "follow",
    headers: {"Content-Type": "text/plain;charset=utf-8"},
    body: JSON.stringify({query})
  });
  const json = await response.json();
  const queryEmbedding = json.embedding;

  let results = [];
  embeddings.forEach(e => {
    const score = dot(queryEmbedding, e.data);
    const index = docnames.indexOf(e.docname);
    results.push([
      e.docname,
      e.title,  // TODO: Display section title instead
      `#${e.ids[0]}`,  // TODO: Determine correct section ID (may have multiple)
      null,  // TODO: Can we use this? Believe it's "description"
      score,
      filenames[index],
      SearchResultKind.text
    ]);
  });
  results.sort((a, b) => a[4] - b[4]);
  results = results.filter(result => result[4] > 0.65);

  // TODO: Return real data.
  return results;
};

const removeSearchDescription = () => {
  document.querySelectorAll('p').forEach(p => {
    if (!p.textContent.includes('Searching for multiple words only shows')) {
      return;
    }
    p.remove();
  });
};

preload();
removeSearchDescription();
