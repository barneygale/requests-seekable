from os import SEEK_SET, SEEK_CUR, SEEK_END
from io import BufferedIOBase, BytesIO

from requests.adapters import BaseAdapter
from requests import PreparedRequest, Response


__version__ = '0.1.0'


class SeekError(OSError):
    pass


class SeekableResponse:
    _adapter: BaseAdapter
    _request: PreparedRequest
    _reader: BufferedIOBase
    _length: int = -1
    _offset: int = 0

    def __init__(self, response: Response):
        self._adapter = response.connection
        self._request = response.request
        self._reader = response.raw
        content_length = response.headers.get('content-length')
        if content_length:
            self._length = int(content_length)
        accept_ranges = response.headers.get('accept-ranges')
        if accept_ranges != 'bytes':
            raise SeekError('server does not accept range headers')

    def __getattr__(self, name):
        return getattr(self._reader, name)

    def seekable(self):
        return True

    def seek(self, offset, whence=SEEK_SET):
        if whence == SEEK_END:
            if self._length == -1:
                raise SeekError('seek failed: unknown content length')
            offset += self._length
        elif whence == SEEK_CUR:
            offset += self.tell()
        elif whence != SEEK_SET:
            raise SeekError(f'seek failed: invalid argument {whence=}')

        if offset != self.tell():
            request = self._request.copy()
            request.headers['range'] = f'bytes={offset}-'
            response = self._adapter.send(request, stream=True)
            if response.status_code == 206:  # partial content
                self._reader.close()
                self._reader = response.raw
                self._offset = offset
            elif response.status_code == 416:  # range not satisfiable
                self._reader.close()
                self._reader = BytesIO()
                self._offset = offset
            else:
                raise SeekError(f'seek failed: invalid status {response=}')

    def tell(self):
        return self._offset + self._reader.tell()
