# Publicação

Somente os arquivos listados em PUBLIC_FILES.txt podem ser versionados.
Execute `python3 tools/publicar_pacote.py --check` antes de publicar e
`python3 tools/publicar_pacote.py` para gerar o ZIP apenas com os fontes.
ROMs, dependências binárias, tradução, artes, saves e capturas permanecem na
pasta privada, fora deste checkout. Não inicialize Git na raiz da instalação.
