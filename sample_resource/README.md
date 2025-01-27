# ファイルのアップロード

```shell
curl -X PUT -H "Content-Type: application/pdf" --upload-file sample.pdf "upload_url"
curl -X PUT -H "Content-Type: text/csv" --upload-file sample.csv "upload_url"
```