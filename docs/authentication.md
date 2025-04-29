# API Authentication  
Visla's OpenAPI uses API Key + Secret with HMAC-SHA256 signature authentication for security.  

## Example Request  
```bash
curl -X GET "https://openapi.visla.us/openapi/v1/user/info" -H "accept: */*" -H "key: your_api_key" -H "nonce: whatever" -H "ts: 1742459291139" -H "sign: 90bbc7d829bd54a74e77d80731ac3f772c54bcac4a5b106f63754ceccf185cb5"
```
