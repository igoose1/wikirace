
def file_holder(cls):
    prev_init = cls.__init__

    def _add_file(self, f):
        self._opened_files.append(f)
        return f

    def _close(self):
        for f in self._opened_files:
            if f is not None:
                f.close()

    def _init(self, *args, **kwargs):
        self._opened_files = []
        try:
            prev_init(self, *args, **kwargs)
        except:
            self.close()
            raise

    def _open_file(self, *args):
        return self._add_file(open(*args))

    cls.close = _close
    cls._add_file = _add_file
    cls._open_file = _open_file
    cls.__init__ = _init
    return cls
