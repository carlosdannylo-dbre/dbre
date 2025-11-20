variable "atlas_public_key" {
  description = "Public key for the MongoDB Atlas programmatic API."
  type        = string
  sensitive   = true
}

variable "atlas_private_key" {
  description = "Private key for the MongoDB Atlas programmatic API."
  type        = string
  sensitive   = true
}
