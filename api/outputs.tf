output "api_key_id" {
  description = "ID interno da API key"
  value       = mongodbatlas_api_key.this.api_key_id
}

output "public_key" {
  description = "Public key gerada pela API key"
  value       = mongodbatlas_api_key.this.public_key
}

output "private_key" {
  description = "Private key gerada pela API key"
  value       = mongodbatlas_api_key.this.private_key
}