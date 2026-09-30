# Prabha community

Connect with students, researchers and developers exploring photonic computing and neural-network inference. Beginners are welcome.

<p><a id="community-join-link" href="https://prabhacommunity5701.flarum.cloud/" target="_blank" rel="noreferrer">Open the Prabha forum</a> · <a id="community-chat-link" href="https://discord.gg/RUdRMHBFp" target="_blank" rel="noreferrer">Join Prabha on Discord</a></p>

Use the forum for detailed questions, reproducible results and ongoing project discussions. Use Discord for quick questions and live conversation. Reading the public forum does not require a forum account; posting requires joining. Forum and Discord accounts are separate from the Studio, which needs no account.

## Find the right place

| Forum tag | What to post |
|---|---|
| Announcements | Maintainer news and release updates |
| Help | Installation, usage and troubleshooting questions |
| Research and validation | Reproducible experiments, model questions and validation results |
| Showcase | Projects and demonstrations built with Prabha |
| Development | Implementation ideas, contributions and roadmap discussions |

For a reproducible software defect, use the [GitHub issue tracker](https://github.com/Abhishek5467/Prabha/issues). Code changes use pull requests; see [contributing](contributing.md).

## Share a useful experiment

Include the Prabha version, engine mode, expected behaviour and observed result. Attach the exported run JSON so other people can reproduce the inputs, converter settings and network coefficients. Add CSV or a screenshot if helpful. Keep the complete run JSON alongside a batch CSV.

State whether a result comes from a simulation, an analytical calculation or a hardware measurement. An output-ordering match in the small ANN is not classification accuracy or an energy benchmark.

Do not post passwords, tokens or confidential datasets. Treat other members respectfully and follow the project's [Code of Conduct](https://github.com/Abhishek5467/Prabha/blob/main/CODE_OF_CONDUCT.md).

## Maintainer: update community links

Edit the public settings in `frontend/studio/public/community.json`:

```json
{
  "url": "https://prabhacommunity5701.flarum.cloud/",
  "chat_url": "https://discord.gg/RUdRMHBFp"
}
```

Only HTTPS addresses without credentials are accepted. The Studio falls back to this documentation page if the forum URL is missing or invalid, and hides the chat link if its URL is missing. Update the fallback links in this page when moving either community. Push your changes, then start a new **Publish web preview** workflow on the updated branch.

The website links to both communities; it does not embed their chats or synchronize memberships.
