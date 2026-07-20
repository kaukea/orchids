---
name: write-to-s3
description: Upload evidence or captured data to S3 in a secure, tamper-evident, custody-preserving way — client-side encryption (key held by the operator, plaintext never leaves the host), immutable Object-Lock (WORM) + versioning, in-transit sha256, from a clean AWS account (MFA, not tied to any compromised identity), with every S3 operation logged. Invoke to offload images/manifests to the cloud without exposing plaintext or breaking chain of custody. Assumes an active identity-layer adversary — treat the AWS account as attackable.
roles: [security/forensics]
---

# Write to S3 (secure, immutable, custody-preserving)

Cloud turns the storage wall into a staging problem, but the data is your whole machine — encrypt
before it leaves, make it immutable, and log every operation. Upload from the **clean host** (Pi);
the compromised laptop never touches the network.

## 0. Preflight — the account is the weak point
- **Fresh AWS account**, MFA on a **clean device**, **NOT** linked to any compromised email/domain
  (the adversary owns the iCloud + squatted the domain — keep the bucket unreachable through them).
- Bucket created with **Object Lock enabled at creation** (can't be added later) + **Versioning**.
- Least-privilege IAM: an upload-only key; no delete; deny `s3:BypassGovernanceRetention`.
```bash
aws s3api create-bucket --bucket <bkt> --object-lock-enabled-for-bucket --region <r> \
  --create-bucket-configuration LocationConstraint=<r>
aws s3api put-object-lock-configuration --bucket <bkt> \
  --object-lock-configuration 'ObjectLockEnabled=Enabled,Rule={DefaultRetention={Mode=COMPLIANCE,Days=3650}}'
```
`COMPLIANCE` mode = **no one**, not even root, can delete/alter before retention expires. That is the
property you want for evidence.

## 1. Capture-then-upload (safer than stream-during-capture)
Stage one image locally, verify it complete, THEN upload — a network hiccup mid-`dd`-to-S3 corrupts
the object. Record the plaintext hash before encrypting:
```bash
sha256sum image.dd | tee image.dd.sha256          # forensic hash of the plaintext image
```

## 2. Client-side encrypt (plaintext never leaves the host)
```bash
# symmetric, key you hold — store the passphrase in KeePass, NOT with the data:
gpg --symmetric --cipher-algo AES256 --output image.dd.gpg image.dd
# (or: age -r <recipient> -o image.dd.age image.dd)
sha256sum image.dd.gpg | tee image.dd.gpg.sha256  # hash of the ciphertext actually uploaded
```

## 3. Upload immutable, with retention + integrity
```bash
aws s3api put-object --bucket <bkt> --key <case>/image.dd.gpg --body image.dd.gpg \
  --checksum-algorithm SHA256 \
  --object-lock-mode COMPLIANCE \
  --object-lock-retain-until-date "$(date -u -d '+10 years' +%FT%TZ)" \
  --metadata "plain-sha256=$(cut -d' ' -f1 image.dd.sha256),operator=S.Lambla"
```
Record the returned **VersionId**, **ETag**, and **ChecksumSHA256** — those go in the custody log.
For big files use `aws s3 cp` (auto-multipart) with `--checksum-algorithm SHA256`; for streaming from
a pipe: `... | gpg -c | aws s3 cp - s3://<bkt>/<key>` (only after you accept the no-local-verify risk).

## 4. Cost/retrieval note
Cold evidence → **Glacier Deep Archive** storage class (far cheaper); keep only actively-analysed
objects in Standard. Object Lock works across storage classes.

## 5. Verify + log (chain of custody)
```bash
aws s3api head-object --bucket <bkt> --key <case>/image.dd.gpg   # confirm ChecksumSHA256 + retention
```
Log, per object: bucket, key, **VersionId**, ETag, ChecksumSHA256, plaintext-sha256, retention-until,
upload UTC time. Sign the manifest of all objects+hashes with `digital-signature`. Only after the object is
confirmed present, checksum-verified, and the manifest signed may the local staging copy be wiped and
reused for the next capture.

## 6. Traceability / audit trail — who touched it, and proving it never changed
- **Turn on the access audit BEFORE the first upload:** **S3 server access logging** + **CloudTrail
  data events** on the bucket, delivered to a SEPARATE Object-Locked log bucket. Records every
  GET/PUT/DELETE-attempt with identity, time, and source IP — the "who accessed it" trail.
- **Pin each object's identity** in the custody log at upload: bucket, key, **VersionId**, ETag,
  **ChecksumSHA256**, retention-until, UTC time. VersionId + checksum uniquely fix the exact bytes.
- **On every retrieval (itself a custody event):** `get-object` → recompute SHA-256 → compare to the
  recorded/signed hash, confirm the VersionId matches, log the access. That closes the loop:
  *what it is* (hash) + *who/when* (CloudTrail + signed manifest) + *unchanged* (Object Lock + checksum)
  + *every touch since* (access logs).

## Rules
- Plaintext never leaves the host — encrypt client-side, key held separately.
- Object Lock COMPLIANCE + versioning = immutable evidence.
- Laptop stays air-gapped; upload only from the clean host.
- Every S3 API call is a custody event — log it (bucket/key/version/checksum/time).
