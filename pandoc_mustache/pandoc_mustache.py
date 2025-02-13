"""
Pandoc filter to apply mustache templates on regular text.
"""
from panflute import *
import chevron, yaml

def prepare(doc):
    """ Parse metadata to obtain list of mustache templates,
        then load those templates.
    """
    doc.mustache_files = doc.get_metadata('mustache')
    if isinstance(doc.mustache_files, str):  # process single YAML value stored as string
        if not doc.mustache_files:
            doc.mustache_files = None  # switch empty string back to None
        else:
            doc.mustache_files = [ doc.mustache_files ]  # put non-empty string in list
    # with open('debug.txt', 'a') as the_file:
    #     the_file.write(str(doc.mustache_files))
    #     the_file.write('\n')
    if doc.mustache_files is not None:
        doc.mustache_hashes = [yaml.load(open(file, 'r').read(), Loader=yaml.SafeLoader) for file in doc.mustache_files]
        doc.mhash = { k: v for mdict in doc.mustache_hashes for k, v in mdict.items() }  # combine list of dicts into a single dict
    else:
        doc.mhash = {}
    if len(doc.metadata.content) > 0:
        # Local variables in markdown file wins over any contained in mustache_files
        # doc.mhash.update({ k: doc.get_metadata(k) for k in doc.metadata.content })
        # doc.mrenderer = pystache.Renderer(escape=lambda u: u, missing_tags='strict')
        # Local variables in markdown file wins over any contained in mustache_files
        doc.mhash.update({ k: doc.get_metadata(k) for k in doc.metadata.content })
        # No need for the renderer here anymore as chevron handles it directly
    else:
        doc.mhash = None

def action(elem, doc):
    """ Apply combined mustache template to all strings in document.
    """
    if type(elem) in (Str, CodeBlock, Code, RawBlock) and doc.mhash is not None:
        # elem.text = doc.mrenderer.render(elem.text, doc.mhash)
        elem.text = chevron.render(elem.text, doc.mhash)
        return elem

def main(doc=None):
    return run_filter(action, prepare=prepare, doc=doc)

if __name__ == '__main__':
    main()
