# 🌸 Heloisa Cunha — 3D Isometric Portfolio & Interactive Studio ✨

> Um portfólio tridimensional interativo e acolhedor (*cozy kawaii aesthetic*), construído com **Three.js**, **Web Audio API** e **Python**. Apresenta minha trajetória profissional multidisciplinar em **Design Gráfico Editorial**, **Desenvolvimento Front-end / UX** e **Operações Digitais & Idiomas**.

---

## 🌟 Funcionalidades Principais

- **Cenografia Isométrica 3D**:
  - Modelagem paramétrica em Three.js com projeção isométrica personalizada.
  - Paleta pastel fofa: **Verde Menta**, **Rosa Pastel** e **Lilás / Roxo**.
  - Sombras suaves (`PCFSoftShadowMap`), tone mapping `ACESFilmic` e partículas dinâmicas de poeira e vapor de café.
- **Interatividade & Raycasting**:
  - Clique no **Monitor** para ver projetos de *Desenvolvimento & UX/UI*.
  - Clique nos **Livros / Revista** para ver trabalhos de *Design Editorial, Diagramação e Branding*.
  - Clique no **Caderno** para ver histórico em *Operações Corporativas, CRM (Zendesk, Zoho, Manychat) e Tradução*.
  - Clique no **Abajur** para ligar/desligar a iluminação da mesa.
  - Clique na **Gatinha Mimi 🐾** na prateleira para ouvir um miado fofo e interagir!
- **Modo Dia ☀️ & Noite 🌙**:
  - Alternador de atmosfera entre noite acolhedora com estrelas e LED neon coração, e manhã iluminada com luz solar dourada.
- **Motor Bilíngue Instantâneo (`PT` ⇄ `EN`)**:
  - Tradução em tempo real de toda a interface, gaveta de projetos, marcadores 3D e currículo clássico completo.
  - Redesenho dinâmico do monitor do computador via Canvas 2D em Three.js.
- **Visualizador Editorial (*Lightbox Gallery*)**:
  - Amostras de alta resolução com especificações técnicas (InDesign, grid tipográfico, fechamento gráfico CMYK / EPUB).
- **Áudio Sintetizado & SFX Táteis**:
  - Chuva suave / som Lo-Fi e cliques mecânicos de teclado pastel sintetizados nativamente via Web Audio API (sem dependências externas).
- **Backend Integrado (`server.py`)**:
  - Servidor em Python 3 nativo com endpoint `POST /api/contact` que valida e armazena os contatos em `messages.json`.
  - Fallback automático para WhatsApp e E-mail (`mailto:`) caso executado como site estático.

---

## 🚀 Como Executar Localmente

### Com o servidor Python do projeto:
```bash
python3 server.py 14726
```
Abra seu navegador em: `http://localhost:14726`

### Ou como site estático (qualquer servidor web):
```bash
python3 -m http.server 3000
```
Abra em: `http://localhost:3000`

---

## 🛠️ Tecnologias Utilizadas

- **Front-end 3D**: Three.js (r160), WebGL, HTML5 Canvas, CSS3 Moderno, JavaScript ES6+
- **Áudio**: Web Audio API (sintetizadores de ruído rosa, osciladores de clique e modulação senoidal)
- **Design & Tipografia**: Space Grotesk, Space Mono, Plus Jakarta Sans
- **Back-end**: Python 3 Standard Library (`http.server`, `urllib`, `json`)

---

## 📬 Contato

- **E-mail**: heloisaoliveira@zohomail.com
- **LinkedIn**: [linkedin.com/in/lisscunha](https://linkedin.com/in/lisscunha)
- **WhatsApp**: +55 (27) 99768-2682
