.PHONY: init validate plan apply show drift detect reconcile destroy clean

init:
	terraform init

validate:
	terraform validate

plan:
	terraform plan

apply:
	terraform apply -auto-approve

show:
	@echo "--- finapp.txt ---"
	@cat finapp.txt
	@echo
	@echo "--- terraform state list ---"
	@terraform state list
	@echo
	@echo "--- terraform state show ---"
	@terraform state show local_file.finapp

drift:
	@sed -i.bak 's/Production/Development/' finapp.txt
	@rm -f finapp.txt.bak
	@echo "Manual drift created:"
	@cat finapp.txt

detect:
	@terraform plan -detailed-exitcode; rc=$$?; echo "Terraform exit code: $$rc"; exit 0

reconcile:
	terraform apply -auto-approve
	@echo "Reconciled file:"
	@cat finapp.txt

destroy:
	terraform destroy -auto-approve

clean:
	rm -rf .terraform terraform.tfstate terraform.tfstate.* finapp.txt
