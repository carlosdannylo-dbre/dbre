output "project_id" {
  description = "Identifier of the created project."
  value       = mongodbatlas_project.this.id
}

output "federation_mapping_id" {
  description = "Role mapping ID created for the federated group (if enabled)."
  value       = try(mongodbatlas_federated_settings_org_role_mapping.project_mapping[0].id, null)
}
