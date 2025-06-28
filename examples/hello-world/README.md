# Hello World Pygls Language Server

This is the bare-minimum, working example of a Pygls-based Language Server. It is the same as that shown in the main README, it autocompletes `hello.` with the options, "world" and "friend".

You will only need to have installed Pygls on your system. Eg; `pip install pygls`. Normally you will want to formally define `pygls` as a dependency of your Language Server, with something like [venv](https://docs.python.org/3/library/venv.html), [uv](https://docs.astral.sh/uv/getting-started/installation), etc.

# Editor Configurations

<details>
<summary>Neovim Lua (vanilla Neovim without `lspconfig`)</summary>

  Normally, once you have completed your own Language Server, you will want to submit it to the [LSP Config](https://github.com/neovim/nvim-lspconfig) repo, it is the defacto way to support Language Servers in the Neovim ecosystem. But before then you can just use something like this:

  ```lua
  vim.api.nvim_create_autocmd({ "BufEnter" }, {
    -- NB: You must remember to manually put the file extension pattern matchers for each LSP filetype
    pattern = { "*" },
    callback = function()
      vim.lsp.start({
        name = "hello-world-pygls-example",
        cmd = { "python path-to-hello-world-example/main.py" },
        root_dir = vim.fs.dirname(vim.fs.find({ ".git" }, { upward = true })[1])
      })
    end,
  })
  ```
</details>

<details>
<summary>Vim (`vim-lsp`)</summary>

  ```vim
  augroup HelloWorldPythonExample
  au!
  autocmd User lsp_setup call lsp#register_server({
      \ 'name': 'hello-world-pygls-example',
      \ 'cmd': {server_info->['python', 'path-to-hello-world-example/main.py']},
      \ 'allowlist': ['*']
      \ })
  augroup END
  ```
</details>

<details>
<summary>Emacs (`lsp-mode`)</summary>
  Normally, once your Language Server is complete, you'll want to submit it to the [M-x Eglot](https://github.com/joaotavora/eglot) project, which will automatically set your server up. Until then, you can use:

  ```
  (make-lsp-client :new-connection
  (lsp-stdio-connection
    `(,(executable-find "python") "path-to-hello-world-example/main.py"))
    :activation-fn (lsp-activate-on "*")
    :server-id 'hello-world-pygls-example')))
  ```
</details>

<details>
<summary>Sublime</summary>


  ```
  {
      "clients": {
        "pygls-hello-world-example": {
          "command": ["python", "path-to-hello-world-example/main.py"],
          "enabled": true,
          "selector": "source.python"
        }
      }
    }
  ```
</details>

<details>
<summary>VSCode</summary>
  
  VSCode is the most complex of the editors to setup. See the [json-vscode-extension](https://github.com/openlawlibrary/pygls/tree/master/examples/json-vscode-extension) for an idea of how to do it.
</details>
