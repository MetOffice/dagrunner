# (C) Crown Copyright, Met Office. All rights reserved.
#
# This file is part of 'dagrunner' and is released under the BSD 3-Clause license.
# See LICENSE in the root of the repository for full licensing details.
from abc import ABC, abstractmethod


class DocstringParser(ABC):
    def __init__(self, doc):
        self._doc = self.remove_docstring_padding(doc, skip_first=True)
        self._desc = ""
        self._var_lookup = {}

    @classmethod
    @abstractmethod
    def is_style(cls, doc):
        raise NotImplementedError

    @property
    @abstractmethod
    def description(self):
        raise NotImplementedError

    @property
    @abstractmethod
    def variable_mapping(self):
        raise NotImplementedError

    @staticmethod
    def remove_docstring_padding(doc, skip_first=False):
        if isinstance(doc, str):
            doc = doc.split("\n")
        # Determine docstring padding
        if not doc[0].strip():
            doc = doc[1:]  # empty line so remove it
        start_indx = 0
        if skip_first and not doc[0].startswith(" "):
            start_indx = 1
        for dd in doc[start_indx:]:
            if dd.strip() and dd.startswith(" "):
                padding = len(dd) - len(dd.lstrip())
                break
            elif dd.strip() and not dd.startswith(" "):
                padding = 0
                break

        # Remove docstring padding
        for dind in range(len(doc)):
            if not doc[dind][:padding].strip():
                doc[dind] = doc[dind][padding:].rstrip()
            elif not doc[dind].strip():
                doc[dind] = ""
            else:
                doc[dind] = doc[dind].rstrip()
        return doc

    @staticmethod
    def infer_multiline(doc):
        ndoc = ""
        for dd in doc:
            if dd.startswith(" "):
                ndoc += f" {dd.strip()}"
            else:
                ndoc += "\n" + dd if ndoc else dd.strip()
        return ndoc.split("\n")
        # return '\n'.join(doc).replace('\n' + ' '*padding, ' ').split('\n')

    @staticmethod
    def get_index(doc, startswith=None, endswith=None):
        ret = None
        for ind, dd in enumerate(doc):
            if (startswith and dd.startswith(startswith)) or (
                endswith and dd.endswith(endswith)
            ):
                ret = ind
                break
        return ret


class GoogleStyle(DocstringParser):
    @classmethod
    def is_style(cls, doc):
        doc = "\n".join(cls.remove_docstring_padding(doc))
        return "Args:\n    " in doc or "Returns:\n    " in doc

    @property
    def description(self):
        if not self._desc:
            dind = self.get_index(self._doc, endswith=":")
            self._desc = "\n".join(self._doc[:dind]).rstrip()
        return self._desc

    @property
    def variable_mapping(self):
        if not self._var_lookup:
            args = self._doc[self._doc.index("Args:") + 1 :]
            args = args[: args.index("")]
            args = self.remove_docstring_padding(args)
            self._var_lookup = {
                line.split("(")[0].strip(): ":".join(line.split(":")[1:]).strip()
                for line in self.infer_multiline(args)
            }
        return self._var_lookup


class NumpyStyle(DocstringParser):
    @classmethod
    def is_style(cls, doc):
        doc = "\n".join(cls.remove_docstring_padding(doc))
        return "Parameters\n----------\n" in doc or "Returns\n-------\n" in doc

    @property
    def description(self):
        if not self._desc:
            dind = self.get_index(self._doc, startswith="--")
            self._desc = "\n".join(self._doc[: dind - 2]).rstrip()
        return self._desc

    @property
    def variable_mapping(self):
        if not self._var_lookup:
            args = self._doc[self._doc.index("Parameters") + 2 :]
            args = args[: args.index("")]
            args = [
                f"{arg.split(':')[0]}:"
                if not arg.startswith(" ") and ":" in arg
                else arg
                for arg in args
            ]
            self._var_lookup = {
                line.split(":")[0].strip(): ":".join(line.split(":")[1:]).strip()
                for line in self.infer_multiline(args)
            }
        return self._var_lookup


class RSTStyle(DocstringParser):
    @classmethod
    def is_style(cls, doc):
        return ":param " in doc or ":return:" in doc

    @property
    def description(self):
        if not self._desc:
            dind = self.get_index(self._doc, startswith=":")
            self._desc = "\n".join(self._doc[:dind]).rstrip()
        return self._desc

    @property
    def variable_mapping(self):
        if not self._var_lookup:
            name = ":param"
            dind = self.get_index(self._doc, name)
            args = self._doc[dind:]
            args = args[: args.index("")]
            self._var_lookup = {
                line.split(name)[1].split(":")[0].strip(): ":".join(
                    line.split(name)[1].split(":")[1:]
                ).strip()
                for line in self.infer_multiline(args)
                if line.startswith(name)
            }
        return self._var_lookup


class MDStyle(DocstringParser):
    @classmethod
    def is_style(cls, doc):
        doc = "\n".join(cls.remove_docstring_padding(doc))
        return "Args:\n- " in doc or "Returns:\n- " in doc

    @property
    def description(self):
        if not self._desc:
            dind = self.get_index(self._doc, endswith=":")
            self._desc = "\n".join(self._doc[:dind]).rstrip()
        return self._desc

    @property
    def variable_mapping(self):
        if not self._var_lookup:
            args = self._doc[self._doc.index("Args:") + 1 :]
            args = args[: args.index("")]
            self._var_lookup = {
                line.split(":")[0].split(" ")[1].replace("`", ""): ":".join(
                    line.split(":")[1:]
                ).strip()
                for line in self.infer_multiline(args)
            }
        return self._var_lookup
