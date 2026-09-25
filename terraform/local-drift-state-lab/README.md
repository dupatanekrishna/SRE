# Terraform Local Drift & State Lab

This is the small **no-AWS Terraform experiment** I used to practice Terraform safely.

The purpose is simple:

- learn `terraform init`, `validate`, `plan`, and `apply`
- inspect Terraform state
- create drift manually
- detect drift using `terraform plan -detailed-exitcode`
- reconcile the real file back to the declared Terraform configuration
- repeat the experiment without creating any AWS resources or cloud cost

The lab uses the HashiCorp **local provider** and creates only a local text file.

---

## Architecture

```text
main.tf
   |
   | terraform apply
   v
Terraform state
   |
   v
finapp.txt
```

Then we intentionally modify `finapp.txt` outside Terraform:

```text
Terraform code says: Production
Actual file says:      Development
```

Terraform detects the mismatch on the next plan.

---

## Folder

```text
terraform/local-drift-state-lab/
├── README.md
├── main.tf
├── .gitignore
└── Makefile
```

---

# 1. Prerequisites

Check Terraform:

```bash
terraform version
```

This experiment was originally performed with Terraform running locally on macOS.

---

# 2. Initialize

```bash
terraform init
```

Expected result:

- local provider is downloaded
- `.terraform/` is created
- `.terraform.lock.hcl` is generated

---

# 3. Validate

```bash
terraform validate
```

Expected:

```text
Success! The configuration is valid.
```

---

# 4. Plan

```bash
terraform plan
```

Terraform should propose creating:

```text
local_file.finapp
```

No AWS account is required.

---

# 5. Apply

```bash
terraform apply
```

Approve with:

```text
yes
```

The local file is created:

```text
finapp.txt
```

Check it:

```bash
cat finapp.txt
```

Expected content:

```text
Environment: Production
Application: FinApp
Managed-By: Terraform
```

---

# 6. Inspect Terraform state

List managed resources:

```bash
terraform state list
```

Expected:

```text
local_file.finapp
```

Inspect the resource:

```bash
terraform state show local_file.finapp
```

This demonstrates the relationship:

```text
Terraform configuration
        ↓
Terraform state
        ↓
Actual resource
```

For this lab, the actual resource is just a local file.

---

# 7. Create drift manually

Now modify the managed file **outside Terraform**.

On macOS:

```bash
sed -i '' 's/Production/Development/' finapp.txt
```

Check:

```bash
cat finapp.txt
```

You should now see:

```text
Environment: Development
Application: FinApp
Managed-By: Terraform
```

But `main.tf` still declares:

```text
Environment: Production
```

This is drift.

---

# 8. Detect drift

Run:

```bash
terraform plan -detailed-exitcode
echo $?
```

Terraform should detect that the real resource no longer matches the declared configuration.

Exit-code meaning:

```text
0 = no changes
1 = error
2 = changes detected
```

For this experiment, drift should result in:

```text
2
```

This is useful in CI/CD because a scheduled job can detect drift without automatically changing infrastructure.

---

# 9. Reconcile drift

Because the manual change was intentional only for the experiment, Terraform remains the source of truth.

Run:

```bash
terraform apply
```

Then:

```bash
cat finapp.txt
```

The file should return to:

```text
Environment: Production
Application: FinApp
Managed-By: Terraform
```

Mental model:

```text
Wrong manual change
      ↓
terraform plan
      ↓
drift detected
      ↓
terraform apply
      ↓
declared configuration restored
```

If the manual change had been a legitimate business change, the correct workflow would instead be:

```text
Update Terraform code
        ↓
terraform plan
        ↓
review
        ↓
terraform apply
```

The goal is:

```text
Configuration = State = Actual Resource
```

---

# 10. State experiment

Check the state file:

```bash
ls -la terraform.tfstate
```

Inspect through Terraform rather than editing it manually:

```bash
terraform state list
terraform state show local_file.finapp
```

Important SRE/IaC rule:

> Do not manually edit Terraform state unless you have a very specific recovery reason and understand the impact.

For real infrastructure, state should normally be stored remotely with controls such as encryption, versioning, locking and restricted IAM access.

This lab deliberately keeps state local because the purpose is learning.

---

# 11. Destroy and repeat

Destroy only the local managed file:

```bash
terraform destroy
```

Then repeat:

```bash
terraform plan
terraform apply
```

This makes the lab safe to practice repeatedly.

---

# Fast experiment

Using the included Makefile:

```bash
make init
make apply
make show
make drift
make detect
make reconcile
make destroy
```

---

# What this taught me

## Drift

```text
Declared configuration != actual resource
```

## State

State is Terraform's record connecting configuration to managed resources.

## Recovery thinking

If state is ever lost in a real environment:

```text
Check remote backend
   ↓
check previous/versioned state
   ↓
restore known-good state when possible
   ↓
otherwise inventory/import/reconstruct carefully
   ↓
review plan before apply
```

Never blindly run `terraform apply` after losing state.

---

# Interview summary

> I created a local Terraform lab using the local provider so I could safely experiment with state and drift without creating cloud resources. I applied a local file, inspected it through `terraform state list` and `terraform state show`, changed the file manually to create out-of-band drift, and used `terraform plan -detailed-exitcode` to detect it. I then reconciled the resource through Terraform. The experiment helped reinforce that the target state is configuration = state = actual infrastructure.

