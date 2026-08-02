# Guia: colocar o SorteLab no ar (GitHub Pages)

Tempo total: ~15 minutos. Tudo gratuito.

## 1. Criar sua conta no GitHub (5 min)

1. Acesse <https://github.com/signup>
2. Use seu e-mail, crie uma senha e escolha um nome de usuário
   (ex.: `valterbaiao` — ele aparece no endereço do site:
   `valterbaiao.github.io/sortelab`)
3. Confirme o código que chega por e-mail. Plano **Free**.

## 2. Criar o repositório (2 min)

1. Logado, clique no **+** (canto superior direito) → **New repository**
2. Repository name: `sortelab`
3. Deixe **Public** marcado (necessário para o site gratuito)
4. NÃO marque "Add a README" (o projeto já tem)
5. Clique **Create repository**

## 3. Enviar o site (3 min)

Abra o terminal na pasta `sortelab` (botão direito → "Abrir no Terminal")
e rode, trocando SEU-USUARIO pelo seu nome de usuário:

    git remote add origin https://github.com/SEU-USUARIO/sortelab.git
    git push -u origin main

O GitHub vai pedir login na primeira vez (abre o navegador — autorize).

## 4. Ligar o site (2 min)

1. No repositório, clique em **Settings** → **Pages** (menu lateral)
2. Em "Build and deployment" → Source: **Deploy from a branch**
3. Branch: **main**, pasta **/ (root)** → **Save**
4. Aguarde ~2 minutos e acesse: `https://SEU-USUARIO.github.io/sortelab`

## 5. Ligar o robô (1 min)

1. No repositório, aba **Actions** → botão verde para habilitar workflows
2. Clique no workflow "Atualizar resultados das loterias" → **Run workflow**
   (teste manual — deve terminar verde ✔)
3. Pronto: ele passa a rodar sozinho todo dia às 21h30 (com repescagens)

## 6. Últimos retoques

- Edite `sitemap.xml` e `robots.txt` trocando `SEU-USUARIO` pelo seu usuário
  (pode pedir para o Claude fazer), commit e push.
- Depois de alguns dias no ar: cadastre o site no
  [Google Search Console](https://search.google.com/search-console) (gratuito)
  para aparecer nas buscas.
- Domínio próprio e AdSense: quando quiser, é outra conversa de 15 minutos.

## Problemas comuns

- **Página 404**: aguarde 2-3 min após ativar o Pages; confira se o
  repositório é público.
- **Robô com erro**: abra a aba Actions e veja o log — se for a API da Caixa
  fora do ar, a próxima rodada resolve sozinha.
- **Site desatualizado no navegador**: Ctrl+F5 força recarregar.
