output "api_key_id" {
  description = "Identifier for the created Atlas organization API key."
  value       = mongodbatlas_org_api_key.this.id
}

output "public_key" {
  description = "Public component of the Atlas API key."
  value       = mongodbatlas_org_api_key.this.public_key
  sensitive   = true
}

output "private_key" {
  description = "Private component of the Atlas API key."
  value       = mongodbatlas_org_api_key.this.private_key
  sensitive   = true
}
