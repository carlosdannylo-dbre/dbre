output "public_key" {
  value     = mongodbatlas_api_key.this.public_key
  sensitive = true
}