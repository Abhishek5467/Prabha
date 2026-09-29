# Restore the Prabha documentation folder

Your terminal log shows that GitHub push of commit aea533c succeeded and the local frontend server starts. The asset build fails because docs/site is missing from the local project. The full source ZIP contains that folder; this smaller repair package restores it separately.

1. Stop the running Python server with Ctrl+C.
2. Extract this ZIP outside your project.
3. Copy the extracted docs folder and mkdocs.yml into your existing Prabha root, merging folders. Review any local documentation changes before replacing files. Do not put docs inside frontend.
4. The result must contain Prabha/docs/site/index.md and Prabha/docs/site/assets/community.js.
5. From your Prabha root in the Windows terminal, run these commands in order. Stop if any command fails:

```bat
dir docs\site\index.md
.\.venv\Scripts\python.exe scripts/build_web_assets.py
npm.cmd run build --prefix frontend/studio
.\.venv\Scripts\python.exe frontend/web/server.py
```

Open http://127.0.0.1:8000 and http://127.0.0.1:8000/docs/ . The failed earlier asset build also stopped before creating the downloadable source ZIP; the successful rebuild restores that download.

To publish the restored source, use another terminal from the repository root:

```bat
git status
git add docs mkdocs.yml
git diff --cached --stat
git commit -m "Restore Prabha documentation source"
git push origin main
```

Then rerun the GitHub validation/Pages workflow when ready. The log's LF/CRLF notices are line-ending warnings, not the documentation failure. The obsolete credential-manager-core warning did not prevent the recorded push.

## Community platform

This repair removes the hardcoded Discourse choice from the restored public documentation. The existing community.json accepts any valid HTTPS URL. It is left unchanged by this package so your chosen address is preserved. No forum or chat account is created.

- Hosted forum: https://freeflarum.com/ . Donation funded; subject to fair-use, inactivity and non-commercial-use terms: https://docs.freeflarum.com/en/legal/terms/ . It is suitable for trying an early community, not for relying on business-critical support availability.
- Project discussions: enable GitHub Discussions in the repository settings: https://docs.github.com/en/discussions/quickstart .
- Live chat: https://discord.com/ . A hosted forum and a chat service may use separate accounts.

Keep release files, scientific evidence and documentation in the GitHub repository. A forum/chat discussion does not replace those records.
