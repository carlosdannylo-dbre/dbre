# MongoDB Atlas Terraform building blocks

Este repositório traz três módulos do Terraform para provisionamento completo do MongoDB Atlas seguindo boas práticas de organização, segurança e automação:

- **modules/atlas-api**: cria chaves de API em nível de organização e concede acesso a projetos específicos com listas de controle de origem.
- **modules/atlas-cluster**: entrega um cluster avançado (replica set) em AWS ou Azure com endpoints privados aprovados.
- **modules/atlas-project**: cria projetos e mapeia grupos de federation (SSO) para funções específicas dentro de cada projeto.

Um exemplo de uso combinando os módulos está disponível em [`examples/complete`](examples/complete), incluindo variáveis para apontar regiões, endpoints privados e grupos federados.

## Requisitos
- Terraform >= 1.5
- Provider `mongodb/mongodbatlas` >= 1.17
- Chaves de API do Atlas exportadas como variáveis de ambiente ou via `terraform.tfvars` (`atlas_public_key`, `atlas_private_key`).

## Como começar
1. Copie `examples/complete` e preencha suas variáveis (organização, regiões, endpoints privados de AWS/Azure, ID do federation settings e grupos SSO).
2. Preencha um `terraform.tfvars` (exemplo em `examples/complete/terraform.tfvars.example`) **ou** exporte as variáveis sensíveis como `TF_VAR_atlas_public_key` e `TF_VAR_atlas_private_key`.
3. Execute `terraform init` para baixar o provider.
4. Use `terraform plan`/`apply` para validar e criar os recursos.

### Exemplo rápido de `terraform.tfvars`
```hcl
atlas_public_key  = "public-xxxx"
atlas_private_key = "private-xxxx"

org_id                 = "<org_id>"
federation_settings_id = "<federation_id>"
project_owner_id       = "<owner_user_id>"
environment            = "dev"
aws_region             = "us-east-1"
azure_region           = "eastus"
```

### Usando em um pipeline do GitHub
```yaml
name: terraform-atlas

on:
  workflow_dispatch:

jobs:
  plan:
    runs-on: ubuntu-latest
    env:
      TF_IN_AUTOMATION: "true"
      TF_VAR_atlas_public_key: ${{ secrets.ATLAS_PUBLIC_KEY }}
      TF_VAR_atlas_private_key: ${{ secrets.ATLAS_PRIVATE_KEY }}
    steps:
      - uses: actions/checkout@v4
      - uses: hashicorp/setup-terraform@v3
        with:
          terraform_version: 1.6.6
      - run: |
          cd examples/complete
          terraform init
          terraform plan -out=tfplan
      - name: Publicar plano
        uses: actions/upload-artifact@v4
        with:
          name: tfplan
          path: examples/complete/tfplan
```

Cada módulo foi desenhado para ser composable e protegido contra deleções acidentais (termination protection habilitada por padrão nos clusters).
