# History of Pygls

This is the story of Pygls' inception as recounted by its original author, [@augb](https://github.com/augb).

While working at Open Law Library as a programmer, we created a VS Code extension originally written in TypeScript called Codify. Codify processes legal XML into legal code. Since our codification process was written in Python we were faced with the choice of slower performance to roundtrip from TypeScript to Python and back, or duplicating the logic in TypeScript. Neither option was really good. I had the idea of using the Language Server Protocol to communicate with a Python LSP server. Existing Python language servers were focused on Python the language. We needed a generic language server since we were dealing with XML. The manager of the Codify project, David Greisen, agreed with this approach. Thus, pygls was born.

I, @augb, was the project manager for the project. Daniel Elero ([@danixeee](https://github.com/danixeee)) did the coding. When I left Open Law Library, Daniel took over the project for a time.

It was open sourced on December 21, 2018. The announcement on Hacker News is [here](https://news.ycombinator.com/item?id=18735413).
