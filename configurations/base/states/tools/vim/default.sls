# makes this the default editor of choice!
include:
    - tools.vim

tools.editor:
    environment.set:
        - variables:
            EDITOR: vim
        - require:
            - package: vim