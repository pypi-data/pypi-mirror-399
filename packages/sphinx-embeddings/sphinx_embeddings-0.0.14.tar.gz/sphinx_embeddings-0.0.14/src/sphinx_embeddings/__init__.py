import glob
import hashlib
import json
from pathlib import Path

from docutils.nodes import section
from sphinx.errors import ExtensionError


def _find_first_match(matches: list[str], src_suffixes: list[str]) -> str | None:
    for match in matches:
        for src_suffix in src_suffixes:
            if match.endswith(src_suffix):
                return match
    return None
 

def _read_src(srcdir: str, docname: str, src_suffixes: list[str]) -> str | None:
    pattern = f'{srcdir}/{docname}.*'
    matches = glob.glob(pattern)
    match len(matches):
        case 0:
            return None
        case 1:
            return Path(matches[0]).read_text()
        case _:
            match = _find_first_match(matches, src_suffixes)
            return Path(match).read_text()


def _read_data(srcdir: str, docname: str) -> dict | None:
    path = Path(srcdir) / Path(f'{docname}.embeddings.json')
    if path.exists():
        return json.loads(path.read_text())
    return None


def _find_embedding(md5, provider, model, task_type, previous):
    if previous is None:
        return None
    sections = [section for section in previous['sections'] if section['md5'] == md5]
    if len(sections) == 0:
        return None
    if len(sections) > 1:
        raise ExtensionError(f'[sphinx-embeddings] Section discrepancy detected: {md5}')
    embeddings = sections[0]['embeddings']
    for e in embeddings:
        if e['provider'] == provider and e['model'] == model and e['type'] == task_type:
            return e
    return None


def _gemini_api(md5, title, text, models, previous):
    # TODO: Run this only once during extension initialization
    try:
        from google import genai
    except ImportError:
        raise ExtensionError(f'[sphinx-embeddings] Gemini API import failed')
    gemini = genai.Client()
    embeddings = []
    for name in models:
        model = models[name]
        for task_type in model['task-types']:
            embedding = _find_embedding(md5, 'gemini-api', name, task_type, previous)
            if embedding is not None:
                embeddings.append(embedding)
                continue
            # https://googleapis.github.io/python-genai/genai.html#genai.types.EmbedContentConfig
            config = genai.types.EmbedContentConfig(task_type=task_type)
            if task_type == 'RETRIEVAL_DOCUMENT':
                config.title = title
            response = gemini.models.embed_content(model=name, contents=text, config=config)
            data = response.embeddings[0].values
            embeddings.append({
                'data': data,
                'provider': 'gemini-api',
                'model': name,
                'type': task_type
            })
    return embeddings


def _process_section(node, providers, previous):
    text = node.astext()
    md5 = hashlib.md5(text.encode('utf-8')).hexdigest()
    ids = node['ids']
    title = node[0].astext()  # Title is usually (always?) first child
    data = {'md5': md5, 'ids': ids, 'title': title, 'embeddings': []}
    for provider in providers:
        match provider:
            case 'gemini-api':
                models = providers['gemini-api']['models']
                data['embeddings'] += _gemini_api(md5, title, text, models, previous)
    return data


def embed(app, doctree) -> None:
    docname = app.env.docname
    srcdir = str(app.srcdir)
    src_suffixes = app.config.source_suffix
    src = _read_src(srcdir, docname, src_suffixes)
    md5 = hashlib.md5(src.encode('utf-8')).hexdigest()
    previous = _read_data(srcdir, docname)
    data = {'md5': md5, 'docname': docname, 'sections': []}
    providers = app.config.sphinx_embeddings['providers']
    for node in doctree.traverse(section):
        data['sections'].append(_process_section(node, providers, previous))
    srcpath = Path(srcdir) / Path(f'{docname}.embeddings.json')
    srcpath.write_text(json.dumps(data))
    outdir = str(app.outdir)
    outpath = Path(outdir) / Path(f'{docname}.embeddings.json')
    if not outpath.parent.exists():
        outpath.parent.mkdir(parents=True, exist_ok=False)
    outpath.write_text(json.dumps(data))


def relate(app, doctree, docname):
    pass


def write(app, exception):
    if app.builder.format != 'html' or exception:
        return
    index = []
    outdir = str(app.outdir)
    base = app.config.html_baseurl
    for path in Path(outdir).glob(f'**/*.embeddings.json'):
        abspath = str(path).replace(outdir, "")
        url = f"{base}{abspath}"
        index.append(url)
    index_path = Path(outdir) / Path('.well-known') / Path('embeddings.json')
    if not index_path.parent.exists():
        index_path.parent.mkdir(parents=False, exist_ok=False)
    index_path.write_text(json.dumps(index))


def _check_config(config):
    doc = 'https://www.sphinx-doc.org/en/master/usage/configuration.html'
    if config.html_baseurl == '':
        url = f'{doc}#confval-html_baseurl'
        raise ExtensionError(f'[sphinx-embeddings] html_baseurl is required: {url}')


def _add_static_path(html_static_path):
    static = Path(__file__).parent / Path('static')
    html_static_path.append(str(static))


def setup(app):
    app.diffs = {}  # DBG
    _check_config(app.config)
    config = {
        'providers': {
            'gemini-api': {
                'models': {
                    'gemini-embedding-001': {
                        'task-types': [
                            'CLUSTERING',
                            'RETRIEVAL_DOCUMENT'
                        ]
                    }
                }
            }
        }
    }
    app.add_config_value('sphinx_embeddings', config, 'env')
    _add_static_path(app.config.html_static_path)
    # app.add_js_file('sphinx-embeddings.js')
    app.connect('doctree-read', embed)
    app.connect('doctree-resolved', relate)
    app.connect('build-finished', write)
    return {
        'version': '0.0.14',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }

# find . -name "*.embeddings.json" -type f -delete
