# An Extreme Lightweight Version of Blowfish, Only 1.5% of Original Size

![Blowfish Logo](https://github.com/nunocoracao/blowfish/blob/main/logo.png?raw=true)

The Hugo theme Blowfish is feature-rich but heavy in size. Since the upstream maintainer prefers to preserve full history, reducing the repository size directly isn't feasible.

This repository provides a minimal replacement for the original Blowfish theme, aimed at faster clone time, which is particularly beneficial for CI. This is also known as the [Blowfish core](https://github.com/nunocoracao/blowfish/issues/980#issuecomment-1743626167).

> Although this repository is built for Blowfish, the workflow and script are generic and can be reused for any Hugo theme that provides GitHub Releases.

## Usage

Simply add this repo as a submodule to your Hugo blog:

```sh
git submodule add -b main https://github.com/ZhenShuo2021/blowfish-core.git themes/blowfish
```

That's it.

## How It Works

This repository is updated by a ~~Python~~ shell script that pulls files from the upstream Blowfish repository. It excludes images, scripts, and commit history, resulting in a clean, minimal version that is only **8.5MB—1.5%** of the original size.

A GitHub Action checks for new Blowfish releases every 8 hours. The update is automatic unless the upstream repository introduces new folders or files that require changes in the .theme_ignore file.

If you are the owner of the target repo, webhook payload object for [repository_dispatch](https://docs.github.com/en/webhooks/webhook-events-and-payloads#repository_dispatch) is a better choice.

## Using This for Other Hugo Themes

This setup can be used with any Hugo theme that publishes releases. To adapt it for another theme, modify a few configuration files in the `.github` folder:

- `.github/workflows/update.yml`: Update any references to `blowfish`, write your own `Check latest theme version`.
- `.github/.theme_version`: Stores the current **release** version of the theme. If the upstream's **release** hasn't changed, the workflow will exit early.
- `.github/update.sh`: The main script.

## Acknowledgement

The demo theme is Blowfish, from Nuno Coração (https://nunocoracao.com), MIT license.
