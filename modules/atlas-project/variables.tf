variable "org_id" {
  description = "MongoDB Atlas organization identifier."
  type        = string
}

variable "name" {
  description = "Project name."
  type        = string
}

variable "project_owner_id" {
  description = "Optional user ID to set as project owner."
  type        = string
  default     = null
}

variable "teams" {
  description = "Optional map of team configurations keyed by name."
  type = map(object({
    team_id = string
    roles   = list(string)
  }))
  default = {}
}

variable "federation_settings_id" {
  description = "Federation settings ID to use when mapping SSO groups."
  type        = string
  default     = null
}

variable "external_group_name" {
  description = "Name of the external identity provider group to map."
  type        = string
  default     = null
}

variable "federated_project_roles" {
  description = "Roles to grant to the federated group within this project."
  type        = list(string)
  default     = ["GROUP_OWNER"]
}
