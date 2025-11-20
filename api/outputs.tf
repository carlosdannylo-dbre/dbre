output "public_key" {
  value     = mongodbatlas_api_key.this.public_key
  sensitive = true
}
output "private_key" {
  value     = mongodbatlas_api_key.this.private_key
  sensitive = true
}
output "api_key_id" {
  value     = mongodbatlas_api_key.this.id
  sensitive = true
}