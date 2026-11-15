# Wangan 6R no ROG Ally — 0.1.0

Adaptador para jogar uma cópia própria de **Wangan Midnight Maximum Tune 6R
(Japan, 2020)** no ROG Ally com Bazzite. Inicialização pela Steam, comandos do
portátil, jogo livre e pausa. Validado em corrida no Ally X.

**Traga sua própria cópia.** Este repositório contém somente código próprio e
documentação. Não inclui jogo, executáveis, DLLs, tradução, capas ou saves.

## Instalação

Requer Python 3.12 ou superior, Steam, gamescope e drivers Vulkan já disponíveis
no Bazzite. Não altera pacotes do sistema. Em uma pasta com o código deste projeto:

```sh
python3 tools/instalar.py --game-zip "/caminho/Wangan6R.zip" --download-runtime
```

O runtime externo é baixado da publicação original, conferido por SHA-256 e
extraído somente na pasta privada do jogo. Também é possível passar
`--runtime-archive arquivo.tar.gz` para usar um arquivo já baixado.
Os componentes destinados aos jogos MT3 e 6RR não são instalados.

Adicione `~/Games/Wangan6R/jogar.sh` como jogo não-Steam. Não force outro modo de
compatibilidade: o inicializador já utiliza seu Wine privado.

## Controles

| Controle | Função |
|---|---|
| Analógico esquerdo | Direção, zona morta de 12% |
| RT / LT | Acelerar / frear |
| A / B | Confirmar-acelerar / voltar-frear |
| RB / LB | Subir / reduzir marcha no câmbio manual |
| Y | Câmera |
| X | Alternar aceitação de disputa |
| Start | Pausar / retomar |
| A durante a pausa | Retomar |

A pausa congela a última imagem; não abre um menu próprio. Use apenas no modo
local. A retomada foi verificada durante uma corrida, sem avanço do cronômetro
pelo tempo pausado. Ao sair, o inicializador encerra seu próprio ambiente Wine.

## Idioma e imagem

A edição original é japonesa. Foi testada uma tradução inglesa de Tattoohanz,
indicada no [guia do projeto Bayshore](https://github.com/kritbualad/Bayshore_WMMT6/wiki/Setup-Guide).
Ela não é distribuída aqui. Para aplicar o arquivo compatível, coloque-o em
`dependencias/english-patch.zip` dentro da instalação, feche o jogo e execute:

```sh
python3 tools/aplicar_ingles.py "$HOME/Games/Wangan6R"
```

O instalador verifica o hash e cria `backup-japones/`. Os menus, o HUD e as
legendas vistos no teste ficaram em inglês; não se afirma tradução completa de
todos os modos. A dublagem permanece a original.

Apresentação em tela cheia de 1920×1080 no Ally. O jogo tem base de renderização
1360×768; a apresentação utiliza o compositor já aberto pela Steam. Distâncias
e velocidade são exibidas em metros, quilômetros e km/h.

As artes podem ser aplicadas separadamente com `tools/instalar_artes.py`, usando
arquivos próprios em `artes/`: portrait.png, hero.png, landscape.png, logo.png
e icon.png. As imagens não fazem parte desta licença nem do repositório.

## Estado e limites

Modo local com jogo livre, sem fichas. Validado como **GUEST**: não há servidor
de cartões/perfil ou progresso online configurado. Não se promete salvar
progressão de campanha entre partidas. As configurações locais ficam em
`userdata/`; preserve essa pasta nas atualizações.

O executável aceito tem SHA-256
`bf9fded65f5d029deaed5c3b5d06e8035dae70eee2e03c51e3adc2b1444ae2be`.
Outras versões são recusadas pelo instalador.

## Dependências e créditos

O [Wangan Midnight launcher](https://github.com/akitaonrails/rea-teknoparrot-wangan-series)
de akitaonrails (GPL-3.0-or-later) fornece o ambiente Wine/DXVK, o OpenParrot
com suas correções e a placa de entrada WIO1. São projetos externos, baixados
separadamente, com licenças e fontes disponibilizadas pelos respectivos autores.
Este adaptador comunica-se com o formato WIO1 documentado pelo launcher.
Nenhum binário dessas dependências é redistribuído neste repositório.

O código próprio é MIT. As marcas e o conteúdo do jogo pertencem aos respectivos
titulares. Projeto não oficial, sem afiliação com a fabricante.
