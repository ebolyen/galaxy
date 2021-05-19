import io
import zipfile
import uuid as _uuid

import yaml

from galaxy.datatypes.binary import CompressedZipArchive
from galaxy.datatypes.metadata import MetadataElement


class QIIME2Result(CompressedZipArchive):
    MetadataElement(name="semantic_type", readonly=True)
    MetadataElement(name="semantic_type_simple", readonly=True, visible=False)
    MetadataElement(name="uuid", readonly=True)
    MetadataElement(name="format", optional=True, no_value='', readonly=True)
    MetadataElement(name="version", readonly=True)

    def set_meta(self, dataset, overwrite=True, **kwd):
        metadata = _get_metadata_from_archive(dataset.file_name)
        for key, value in metadata.items():
            if value:
                setattr(dataset.metadata, key, value)

        try:
            expression_tree = ast.parse(dataset.metadata.semantic_type)
            PredicateRemover().visit(expression_tree)
            reconstructer = ReconstructExpression()
            reconstructer.visit(expression_tree)
            dataset.metadata.semantic_type_simple = reconstructer.expression
        # If anything went wrong just default to using the full type. This
        # punts any potential issues off to the GUI instead of raising back end
        # exceptions
        except:
            dataset.metadata.semantic_type_simple = \
                dataset.metadata.semantic_type

    def set_peek(self, dataset, is_multi_byte=False):
        if dataset.metadata.semantic_type == 'Visualization':
            dataset.blurb = 'QIIME 2 Visualization'
        else:
            dataset.blurb = 'QIIME 2 Artifact'

        dataset.peek = '\n'.join(map(': '.join, self._peek(dataset)))

    def display_peek(self, dataset):
        def make_row(item):
            return '<tr><th>%s</th><td>%s</td></td>' % item

        table = ['<table cellspacing="0" cellpadding="2">']
        table += list(map(make_row, self._peek(dataset, simple=True)))
        table += ['</table>']

        return ''.join(table)

    def _peek(self, dataset, simple=False):
        peek = [
            ('Type', dataset.metadata.semantic_type),
            ('UUID', dataset.metadata.uuid)]
        if not simple:
            if dataset.metadata.format is not None:
                peek.append(('Format', dataset.metadata.format))
            peek.append(('Version', dataset.metadata.version))
        return peek

    def _sniff(self, filename):
        try:
            if not zipfile.is_zipfile(filename):
                raise Exception()
            return _get_metadata_from_archive(filename)
        except Exception:
            return False


class QIIME2Artifact(QIIME2Result):
    file_ext = "qza"

    def sniff(self, filename):
        metadata = self._sniff(filename)
        return metadata and metadata['semantic_type'] != 'Visualization'


class QIIME2Visualization(QIIME2Result):
    file_ext = "qzv"

    def sniff(self, filename):
        metadata = self._sniff(filename)
        return metadata and metadata['semantic_type'] == 'Visualization'


class PredicateRemover(ast.NodeTransformer):
    def visit_BinOp(self, node):
        if isinstance(node.op, ast.Mod):
            return PredicateRemover().visit(node.left)
        return node


class ReconstructExpression(ast.NodeVisitor):
    expression = '%s'
    tuple_count = 0
<<<<<<< HEAD
    in_index = False

=======

>>>>>>> SQUASH: second pass at strip properties
    def visit_Name(self, node):
        if self.tuple_count == 0:
            self.expression = self.expression % node.id
        else:
            self.expression = self.expression % node.id + ' ,%s'
            self.tuple_count -= 1

        self.generic_visit(node)
<<<<<<< HEAD

=======

>>>>>>> SQUASH: second pass at strip properties
    def visit_Index(self, node):
        pre_strip = len(self.expression)
        self.expression = self.expression.rstrip(', %s')
        post_strip = len(self.expression)

        self.expression += '[%s'
        self.generic_visit(node)
<<<<<<< HEAD

=======
        self.expression += ']'

        # If we stripped the space for the next tuple element to accomodate a
        # nested index we now need to add that space back
        if post_strip < pre_strip:
            self.expression += ', %s'

>>>>>>> SQUASH: second pass at strip properties
    def visit_Tuple(self, node):
        self.tuple_count = len(node.elts) - 1
        self.generic_visit(node)


def _get_metadata_from_archive(archive):
    uuid = _get_uuid(archive)
    archive_version, framework_version = _get_versions(archive, uuid)
    metadata_contents = _get_metadata_contents(archive, uuid)

    return {
        'uuid': uuid,
        'version': framework_version,
        'semantic_type': metadata_contents['type'],
        'format': metadata_contents['format'] or ''
    }


def _get_metadata_contents(path, uuid):
    with _open_file_in_archive(path, 'metadata.yaml', uuid) as fh:
        return yaml.safe_load(fh.read())


def _get_uuid(path):
    roots = set()
    for relpath in _iter_zip_root(path):
        if not relpath.startswith('.'):
            roots.add(relpath)

    if len(roots) == 0:
        raise ValueError("Archive does not have a visible root directory.")
    if len(roots) > 1:
        raise ValueError("Archive has multiple root directories: %r"
                         % roots)
    uuid = roots.pop()
    if not _is_uuid4(uuid):
        raise ValueError(
            "Archive root directory name %r is not a valid version 4 "
            "UUID." % uuid)
    return uuid


def _get_versions(path, uuid):
    try:
        with _open_file_in_archive(path, 'VERSION', uuid) as fh:
            header, version_line, framework_version_line, eof = \
                fh.read().split('\n')
        if header.strip() != 'QIIME 2':
            raise Exception()  # GOTO except Exception
        version = version_line.split(':')[1].strip()
        framework_version = framework_version_line.split(':')[1].strip()
        return version, framework_version
    except Exception:
        raise ValueError("Archive does not contain a correctly formatted"
                         " VERSION file.")


def _open_file_in_archive(zip_path, path, uuid):
    relpath = '/'.join([uuid, path])
    with zipfile.ZipFile(zip_path, mode='r') as zf:
        return io.TextIOWrapper(zf.open(relpath))


def _iter_zip_root(path):
    seen = set()
    with zipfile.ZipFile(path, mode='r') as zf:
        for name in zf.namelist():
            parts = name.split('/')  # zip is always / for seperators
            if len(parts) > 0:
                result = parts[0]
                if result not in seen:
                    seen.add(result)
                    yield result


def _is_uuid4(uuid_str):
    # Adapted from https://gist.github.com/ShawnMilo/7777304
    try:
        uuid = _uuid.UUID(hex=uuid_str, version=4)
    except ValueError:
        # The string is not a valid hex code for a UUID.
        return False

    # If uuid_str is a valid hex code, but an invalid uuid4, UUID.__init__
    # will convert it to a valid uuid4.
    return str(uuid) == uuid_str
