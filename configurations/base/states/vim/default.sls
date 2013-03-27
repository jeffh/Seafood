# makes this the default editor of choice!
include:
    - vim

tools.editor:
    environment.set:
        - variables:
            EDITOR: vim
        - require:
            - package: vim
