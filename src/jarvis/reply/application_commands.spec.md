# Configured application commands

`match_application_command` recognises complete literal templates from
`application_command_templates`. Defaults are empty. Each template contains
exactly one `{application}` placeholder; other characters are regex-escaped.
Whitespace, Unicode compatibility forms and case are normalised. Optional leading
configured assistant names and terminal sentence punctuation are accepted.
Longer literal templates take precedence. At most 32 templates, 200 characters
per template, 512 input characters and 160 application-name characters are used.

The parser contains no language-specific verbs or suffix rules. A match supplies
only a name to `openApplication`, which validates against the current OS catalogue.
It supplies no shell command, path or executable arguments. Partial matches and
unconfigured phrasing remain normal model requests. Direct mode executes a match
through the ordinary contextual tool runner, preserving
activity ownership, raw results, failure handling and conversation recording.
Configured `application_command_responses` render the acknowledgement from the
actual raw launch outcome, without reply inference. The success message requires
both tool success and `status=launch_requested`; unknown or malformed results use
the error message. Only the literal `{application}` placeholder is substituted,
using the OS display name on success. Responses describe dispatch rather than
claiming a visible window. Common reply recording retains the interaction and
its raw tool result. Unmatched conversation uses the unified system prompt.
