variable "org_id" {
  description = "MongoDB Atlas organization identifier where the API key will be created."
  type        = string
}

variable "description" {
  description = "Human friendly description for the API key."
  type        = string
  default     = "Managed by Terraform"
}

variable "org_roles" {
  description = "Roles to assign at the organization scope."
  type        = list(string)
  default     = ["ORG_MEMBER"]
}

variable "project_ids" {
  description = "Optional list of project IDs where the API key should be granted roles."
  type        = list(string)
  default     = []
}

variable "project_roles" {
  description = "Roles to assign to the API key within each project."
  type        = list(string)
  default     = ["GROUP_DATA_ACCESS_READ_WRITE"]
}

variable "access_list" {
  description = "Optional map of API access list entries keyed by a descriptive name."
  type = map(object({
    cidr_block = optional(string)
    ip_address = optional(string)
    comment    = optional(string, "Managed by Terraform")
  }))
  default = {}
}
