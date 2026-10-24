# Installed application launching

`openApplication` discovers locally registered Windows applications through
`Get-StartApps`. An omitted application name returns the installed names.
Opening matches a Unicode-normalised case-insensitive exact name, then a unique
whole-word prefix. Ambiguous or missing names return candidates without launching.

Only an AppID obtained from the OS catalogue can be launched through Explorer's
AppsFolder interface. User text is never interpolated into a shell command,
executed as a path or forwarded as arguments. Discovery has a bounded timeout
and a hidden PowerShell window. Other platforms return an unsupported result.
Success means the OS launch request was dispatched, not proof of a visible window.
Tools return raw result data; the reply engine handles the user's language.

`application_aliases` maps user-chosen names to installed display names before
selection. Aliases remain names, never executable paths or arguments. They can
map a familiar product name to a locally installed compatible client.

Catalogue discovery and launch dispatch own temporary `LAUNCHING` activity, except during protected speech or dictation. Completion and failure release that ownership without overwriting newer work.
