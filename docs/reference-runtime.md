# Reference model and runtime

The public benchmark uses `Qwen/Qwen3-8B` at revision
`b968826d9c46dd6066d109eabc6255188de91218` with thinking disabled, temperature
zero, and a local vLLM OpenAI-compatible endpoint.

The model is a reference implementation, not a package requirement. Any local model
server that accepts OpenAI-compatible chat-completion requests can be evaluated with
the same glossary, prompt, and benchmark runner. Model weights are not redistributed.

The Qwen model and this project's code are Apache-2.0. Public datasets retain their
own licenses. In particular, WMT25 evaluation material is CC BY-NC 4.0 and is not
bundled in release artifacts.
