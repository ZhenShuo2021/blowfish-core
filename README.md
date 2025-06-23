# Auto-Sync Repo Core POC

The Hugo theme [Blowfish](https://github.com/nunocoracao/blowfish) is feature-rich but [heavy in size](https://github.com/nunocoracao/blowfish/issues/980). This POC automatically syncs Blowfish's core via GitHub workflow.

The workflow uses cron schedule to check for new releases, update files, create pull requests, build preview sites, and create a new tag. Everything is automatic.

## Adaptation

To use with another theme, modify these `.github` files:

- `.github/workflows/update.yml`: Replace `blowfish` references and customize `Check latest theme version`
- `.github/.theme_version`: Stores current release version for early exit if unchanged
- `.github/update.sh`: Main script

## Preview Deployment

This POC uses Cloudflare Pages (free) with [direct upload](https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/). Add these GitHub Secrets:

- [CLOUDFLARE_ACCOUNT_ID](https://developers.cloudflare.com/fundamentals/setup/find-account-and-zone-ids/)
- [CLOUDFLARE_API_TOKEN](https://developers.cloudflare.com/pages/how-to/use-direct-upload-with-continuous-integration/)

Required GitHub Actions permissions:

- Read and write access
- Create and approve pull requests

## Acknowledgement

Demo theme: Blowfish by Nuno Coração (https://nunocoracao.com), MIT license.
