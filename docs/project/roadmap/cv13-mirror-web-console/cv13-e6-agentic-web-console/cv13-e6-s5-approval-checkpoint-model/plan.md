[< Story](index.md)

# Plan — CV13.E6.S5 Approval checkpoint model

Represent approval as durable run state before mutation. For the first slice, conversation journey repair with `dryRun: false` creates an `approval_required` run instead of applying immediately. The user approves the run through a guarded endpoint, and only then does the existing operation worker execute.
