# History of [_pygls_][pygls] 

This is the story of [_pygls_][pygls]' inception as recounted by its original project creator, [@augb][augb]. 

While working at [Open Law Library][openlaw] as a programmer, we created a VS Code extension originally written in TypeScript called _Codify_. _Codify_ processes legal XML into legal code. Since our codification process was written in Python we were faced with the choice of slower performance to roundtrip from TypeScript to Python and back, or duplicating the logic in TypeScript. Neither option was really good. I had the idea of using the [Language Server Protocol (LSP)][lsp] to communicate with a Python LSP server. Existing Python language servers were focused on Python the language. We needed a generic language server since we were dealing with XML. [David Greisen][dgreisen], agreed with this approach. Thus, [_pygls_][pygls] was born. 

I, [@augb][augb], was the project manager for the project. Daniel Elero ([@danixeee][danixeee]) did the coding. When I left Open Law Library, Daniel took over the project for a time. 

It was open sourced on December 21, 2018. The announcement on Hacker News is [here][announcement]. 

[augb]: https://github.com/augb 
[announcement]: https://news.ycombinator.com/item?id=18735413 
[danixeee]: https://github.com/danixeee 
[dgreisen]: https://github.com/dgreisen 
[lsp]: https://microsoft.github.io/language-server-protocol/specification 
[openlaw]: https://openlawlib.org/ 
[pygls]: https://github.com/openlawlibrary/pygls
