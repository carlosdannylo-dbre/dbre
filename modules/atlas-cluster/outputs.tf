output "cluster_id" {
  description = "ID of the created advanced cluster."
  value       = mongodbatlas_advanced_cluster.this.id
}

output "srv_address" {
  description = "Private SRV connection string for applications."
  value       = mongodbatlas_advanced_cluster.this.connection_strings[0].private_srv
}

output "private_endpoint_ids" {
  description = "Map of created private endpoint identifiers keyed by provider."
  value = {
    aws   = try(mongodbatlas_private_endpoint.aws[0].id, null)
    azure = try(mongodbatlas_private_endpoint.azure[0].id, null)
  }
}
