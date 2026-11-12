# Visualizador 3D das camisetas: publicar e usar

O visualizador é formado por **dois arquivos**, `index.html` e `dados.js`. Ele não depende de servidor, de
internet nem de nenhuma conta paga: o Three.js, os modelos e as artes estão todos dentro desses arquivos.
Por isso, publicado no **GitHub Pages**, ele continua no ar enquanto o repositório existir.

---

## Parte 1: Publicar no GitHub Pages (uma vez)

### Por que um repositório separado?

No plano gratuito do GitHub, o Pages só funciona em repositório **público**. O repositório `polisat-org/DESIGN`
tem o Design Package, a fonte ND Logos (licença só para uso pessoal) e os arquivos de produção, e não deve ficar
público. A solução é criar um repositório público pequeno, só com os dois arquivos do visualizador.

### Passo a passo (pelo site, sem terminal)

1. Entre em <https://github.com> com uma conta que seja **membro da organização `polisat-org`** e tenha permissão
   para criar repositórios.
2. Clique em **+** (canto superior direito) → **New repository**.
3. Preencha:
   - **Owner:** `polisat-org`
   - **Repository name:** `camisetas-3d` (esse nome vai fazer parte do endereço do site)
   - **Visibility:** **Public**
   - Marque **Add a README file**
   - Clique em **Create repository**.
4. No repositório novo, clique em **Add file** → **Upload files**.
5. Arraste **os dois arquivos** desta pasta (`camisetas/visualizador_3d/`):
   - `index.html`
   - `dados.js`
6. Em *Commit changes* escreva algo como `Visualizador 3D das camisetas` e clique em **Commit changes**.
   O upload pode levar alguns segundos, porque os arquivos têm cerca de 6 MB.
7. Vá em **Settings** → **Pages** (no menu da esquerda).
8. Em **Build and deployment**:
   - **Source:** `Deploy from a branch`
   - **Branch:** `main` e pasta `/ (root)` → **Save**.
9. Espere de 1 a 3 minutos e recarregue a página de Settings → Pages. Vai aparecer:
   **"Your site is live at `https://polisat-org.github.io/camisetas-3d/`"**.
10. Abra o link e confira se a camiseta aparece e gira. Depois é só mandar o link para a equipe.

> Se aparecer erro 404 logo depois de publicar, espere mais alguns minutos: a primeira publicação demora.
> Confira também se o arquivo se chama exatamente `index.html` (minúsculo) e está na raiz do repositório.

### Alternativa pelo terminal

```bash
# a partir da pasta DESIGN
mkdir /tmp/camisetas-3d && cp camisetas/visualizador_3d/index.html camisetas/visualizador_3d/dados.js /tmp/camisetas-3d/
cd /tmp/camisetas-3d
git init -b main && git add . && git commit -m "Visualizador 3D das camisetas"
gh repo create polisat-org/camisetas-3d --public --source . --push
gh api -X POST repos/polisat-org/camisetas-3d/pages -f "source[branch]=main" -f "source[path]=/"
```

---

## Parte 2: Atualizar o site depois de mudar um design

1. Edite os designs em `camisetas/_fonte/` e gere de novo: `python3 build.py` (veja `camisetas/README.md`).
2. No repositório `camisetas-3d`, clique em **Add file** → **Upload files** e envie de novo `index.html` e
   `dados.js`. Os arquivos antigos são substituídos.
3. Clique em **Commit changes**. Em 1 ou 2 minutos o site está atualizado. Se ainda aparecer a versão antiga,
   use **Ctrl + F5**.

---

## Parte 3: Como usar o visualizador

Abra `https://polisat-org.github.io/camisetas-3d/` no computador ou no celular. Localmente, dê dois cliques em
`index.html`.

| Ação | Como fazer |
|---|---|
| **Trocar de modelo** | Clique num modelo na lista da esquerda (Polo, Algodão ou Dry-fit). No celular, a lista fica no topo. |
| **Girar** | Arraste com o mouse (ou com o dedo). |
| **Zoom** | Roda do mouse, ou pinça com dois dedos. |
| **Mover a câmera** | Botão direito do mouse + arrastar, ou dois dedos arrastando. |
| **Vistas prontas** | Botões **Frente**, **Lado** e **Costas** na barra de baixo. |
| **Rotação automática** | Botão **Girar** (liga e desliga). |
| **Tema claro / escuro** | Botão **Tema**. |
| **Testar um nome** (dry-fit) | Digite no campo **Nome (costas)**: o nome aparece nas costas na hora. Nomes longos diminuem para caber na área reservada. |

**Dicas**

- O site lembra o último modelo aberto.
- Para mandar o link de um modelo específico, acrescente `?model=ID` ao endereço, por exemplo
  `https://polisat-org.github.io/camisetas-3d/?model=D2`.
  IDs: `P1`, `P2`, `P3`, `A1`, `A2`, `A3`, `D1`, `D2`, `D3`.
- Para abrir já numa vista, use `&view=front`, `&view=back` ou `&view=side`, por exemplo `?model=A1&view=back`.
- Funciona nos navegadores atuais (Chrome, Edge, Firefox, Safari). Em celulares mais antigos, o primeiro
  carregamento pode levar alguns segundos.
- O 3D serve para **visualizar e aprovar**. Medidas, cores e arquivos de produção estão nas fichas técnicas
  (`modelos/<modelo>/ficha_tecnica_XX.pdf`).
