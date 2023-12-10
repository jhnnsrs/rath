---
sidebar_label: file
title: links.file
---

## FileExtraction Objects

```python
class FileExtraction(ContinuationLink)
```

FileExtraction Link is a link that extracts file-like objects from the variables dict.
It traverses the variables dict, and extracts any (nested) file-like objects to the context.files dict.

These can then be used by the FileUploadLink to upload the files to a remote server.
or used through the multipart/form-data encoding in the terminating link (if supported).

