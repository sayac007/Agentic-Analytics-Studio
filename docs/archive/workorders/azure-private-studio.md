# Azure private-owner deployment

User-authorized preparation of a PowerShell Cloud Shell deployment for the
existing synthetic Studio, including exact Azure Key Vault secret instructions.
No paid Azure resource is created by this development task.

- Keep local mode, statistical contracts, frozen protocols and archived results.
- Provide an explicit deployment plan and an opt-in creation command.
- Use a single local managed-disk SQLite workspace, HTTPS and owner authentication.
- Retrieve runtime secrets with managed identity; no secrets in source, images,
  command-line arguments, VM custom data or logs.
- Explicitly support a user-created RBAC vault in the existing resource group;
  preserve its secrets, human roles and tags. Keep strict ownership checks for
  every VM and network resource. No Microsoft Graph identity lookup is needed
  to reuse a vault whose secret permissions are already configured.
- Document costs, runtime limitations, actual tests and unverified live steps.
- Submit one focused Draft PR; no automatic merge or production deployment.
