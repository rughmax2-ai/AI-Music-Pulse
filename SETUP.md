# Setup: Publishing to GitHub

Three steps to go live. Total time: about 2 minutes.

## 1. Create the repository on GitHub

Create a new **public** repo (public repos get unlimited free Actions
minutes) named e.g. `ai-music-pulse`. Do **not** initialize it with a
README — this folder already has one.

## 2. Push this folder

```bash
cd ai-music-pulse
git remote add origin git@github.com:YOUR_USERNAME/ai-music-pulse.git
git push -u origin main
```

(Or use HTTPS: `https://github.com/YOUR_USERNAME/ai-music-pulse.git`)

## 3. Enable workflow write access & run it once

1. On GitHub: **Settings → Actions → General → Workflow permissions** →
   select **"Read and write permissions"** → Save.
   (The workflow also declares `permissions: contents: write`, but some
   org/account defaults require this toggle.)
2. Go to the **Actions** tab → **Daily AI Music Update** → **Run
   workflow** to trigger the first run manually.
3. Confirm a commit appears with `data/daily/<today>.json` and an
   updated README digest.

From then on it runs automatically every day at **06:15 UTC**.

## Notes & maintenance

- **Schedule**: edit the cron line in
  `.github/workflows/daily-update.yml`. GitHub cron uses UTC and may
  delay runs by a few minutes under load.
- **60-day inactivity rule**: GitHub disables scheduled workflows in
  repos with no activity for 60 days. Since this workflow commits daily,
  it keeps itself alive automatically; if it ever fails for 60 straight
  days, re-enable it from the Actions tab.
- **Rate limiting**: GitHub Actions runners occasionally get 429s from
  Reddit's JSON API. The fetcher automatically retries and falls back to
  RSS feeds, and the run only fails if *every* source fails.
- **Adding sources**: append subreddits to `sources.json`. For Discord
  later: add a `scripts/fetch_discord.py` writing the same schema and a
  step in the workflow, with the bot token stored in
  **Settings → Secrets and variables → Actions**.
