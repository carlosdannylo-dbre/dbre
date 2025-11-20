resource "mongodbatlas_project" "this" {
  name      = var.name
  org_id    = var.org_id
  project_owner_id = var.project_owner_id

  with_default_alerts_settings = true

  dynamic "teams" {
    for_each = var.teams
    content {
      team_id = teams.value.team_id
      roles   = teams.value.roles
    }
  }
}

resource "mongodbatlas_federated_settings_org_role_mapping" "project_mapping" {
  count = var.federation_settings_id != null && var.external_group_name != null ? 1 : 0

  federation_settings_id = var.federation_settings_id
  org_id                 = var.org_id
  external_group_name    = var.external_group_name

  role_assignments = [for role in var.federated_project_roles : {
    role       = role
    project_id = mongodbatlas_project.this.id
  }]
}
