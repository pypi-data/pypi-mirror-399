# Upload Files

This example demonstrates the efficient way to upload files using the External API SDK's `client.upload_files()` method.

```python
from io import BytesIO
from pathlib import Path

from uncountable.core import AuthDetailsApiKey, Client
from uncountable.core.client import ClientConfig
from uncountable.core.file_upload import DataFileUpload, UploadedFile

client: Client = Client(
    base_url="<BASE_URL>",
    auth_details=AuthDetailsApiKey(
        api_id="<API_ID>", 
        api_secret_key="<API_SECRET_KEY>"
    ),
    config=ClientConfig(allow_insecure_tls=False),
)

filepath = Path("<YOUR_FILE_PATH>")
file_io: BytesIO = BytesIO(filepath.read_bytes())

upload_file_response: list[UploadedFile] = client.upload_files(
    file_uploads=[DataFileUpload(data=file_io, name=filepath.name)]
)

uploaded_file_name = upload_file_response[0].name
uploaded_file_id = upload_file_response[0].file_id
```
