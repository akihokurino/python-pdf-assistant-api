
## 証明書周り

1. gcloud certificate-manager dns-authorizations create test-dns-auth --domain="akiho.app"
2. gcloud certificate-manager dns-authorizations describe test-dns-auth の結果をCNAMEで追加
3. gcloud certificate-manager certificates create test-cert --domains="akiho.app" --dns-authorization=test-dns-auth

## Api Gatewayのデフォルトホストの確認

gcloud api-gateway gateways describe api-gateway --location=asia-northeast1 --project=pdf-assistant-445201