# requests-seekable

Open HTTP responses as *seekable* file objects. When `seek()` is called, a new request is made with
the [`Range`](https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Range) header set.

This is useful for extracting files from large web-based `.zip` archives.

## Usage

If your existing code looks like this:

```python
import requests

response = requests.get('https://example.com', stream=True)
fileobj = response.raw  # not seekable :(
```

Then replace `response.raw` with `SeekableResponse(response)`:

```python
import requests
import requests_seekable

response = requests.get('https://example.com', stream=True)
fileobj = requests_seekable.SeekableResponse(response)  # seekable :)
```

If the server doesn't support `Range` headers, then `SeekableResponse` initializer raises a
`SeekError` exception. This type of exception (a subclass of `OSError`) is also raised from
`SeekableResponse.seek()` in the following cases:

- If the given *whence* value isn't `SEEK_SET` (0), `SEEK_CUR` (1) or `SEEK_END` (2); or
- If the given *whence* value is `SEEK_END` but the content length isn't known; or
- If the response status isn't 206 "Partial Content" or 416 "Range Not Satisfiable".
