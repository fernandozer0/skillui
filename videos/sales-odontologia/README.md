# Sales Odontologia — comerciais para Reels

## v1 — premium escuro (`reel.html`, `music.py`)

- `sales-odontologia-reels.mp4` — vídeo final (1080×1920, 30 fps, 23 s, com trilha)
- `capa.jpg` — sugestão de capa

## Roteiro
| Tempo | Cena |
|---|---|
| 0–3 s | Gancho: "Você esconde seu sorriso nas fotos?" 😬 |
| 3–5 s | Virada: "Isso acaba hoje." |
| 5–7 s | Revelação da marca (logo Sales Odontologia) |
| 7–13 s | Tratamentos: Implantes, Facetas, Ortodontia, Prótese |
| 13–15 s | "Todas as especialidades em um só lugar" |
| 15–17,5 s | "Atendimento humanizado" |
| 17,5–23 s | CTA: Agende sua avaliação — WhatsApp (41) 98414-4299 |

## Como regenerar
```sh
python3 music.py music.wav            # trilha (numpy + scipy)
node render.js reel_silent.mp4        # quadros via Playwright -> ffmpeg
ffmpeg -i reel_silent.mp4 -i music.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart sales-odontologia-reels.mp4
```
Textos, cores e tempos ficam em `reel.html` (função `render(t)`).

## v2 — editorial claro + funk 130 BPM (`reel2.html`, `music2.py`)

- `sales-odontologia-reels-v2.mp4` — vídeo final (1080×1920, 30 fps, ~23 s, com trilha)
- `capa-v2.jpg` — sugestão de capa

| Batidas | Cena |
|---|---|
| 0–6 | Gancho com carimbos: "Pare de esconder seu sorriso" 🤭🚫 |
| 6–16 | Antes/depois com slider (ilustração) — "pode ser você ✨" |
| 16–28 | "Por que a Sales?" — 3 motivos em cards coloridos com faixa animada |
| 28–36 | Estrobo: um tratamento por batida |
| 36–48 | Celular simulando o agendamento pelo WhatsApp + número |

```sh
python3 music2.py music2.wav
PAGE=reel2.html node render.js reel2_silent.mp4
ffmpeg -i reel2_silent.mp4 -i music2.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart sales-odontologia-reels-v2.mp4
```

## v3 — "vida no iPhone" + emojis da Apple (`reel3.html`, `music3.py`)

- `sales-odontologia-reels-v3.mp4` — vídeo final (1080×1920, 30 fps, ~23,6 s, com trilha)
- `capa-v3.jpg` — sugestão de capa
- `emoji/` — emojis no estilo iPhone (Apple), usados no lugar dos emojis do sistema

| Batidas (100 BPM) | Cena |
|---|---|
| 0–6 | Tela de bloqueio: notificações ("32 fotos… e você não sorri em nenhuma") → "Isso acontece com você? 🫣" |
| 6–16 | App Notas: lista "Metas 💫"; marcar "Avaliação na Sales" resolve o resto |
| 16–24 | Tela inicial com "apps" dos tratamentos (balançando como no iOS) → zoom no 🦷 |
| 24–30 | Busca Spotlight "dentista em curitiba" → card da Sales Odontologia |
| 30–38 | Lembrete do Calendário + CTA WhatsApp com chuva de emojis |

```sh
python3 music3.py music3.wav
PAGE=reel3.html node render.js reel3_silent.mp4
ffmpeg -i reel3_silent.mp4 -i music3.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart sales-odontologia-reels-v3.mp4
```

## v4 — "Mito ou Verdade?" (`reel4.html`, `music4.py`)

Quiz com 4 perguntas: cada uma tem contagem 3-2-1, revelação com carimbo MITO/VERDADE e explicação.
Trilha 120 BPM estilo game show (tique-taque na contagem, buzina no mito, sino na verdade).

## v5 — "5 sinais de que você precisa ir ao dentista" (`reel5.html`, `music5.py`)

Contagem regressiva 5→1 (gengiva sangrando, sensibilidade, mau hálito, dor ao mastigar, +6 meses sem consulta),
cada sinal com cor própria e emoji grande. Trilha 128 BPM com sirene, giro de números e despertador.

`lib/anim.js` e `lib/synth.py` são os utilitários compartilhados a partir da v4.

```sh
python3 music4.py music4.wav && PAGE=reel4.html node render.js reel4_silent.mp4
python3 music5.py music5.wav && PAGE=reel5.html node render.js reel5_silent.mp4
ffmpeg -i reelN_silent.mp4 -i musicN.wav -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart sales-odontologia-reels-vN.mp4
```

## v6 — "Como funciona o implante em 3 passos" (`reel6.html`, `music6.py`)
Estilo planta técnica (azul-marinho com grade): ilustração em corte mostra avaliação 🩻, instalação do pino 🔩 e coroa 👑.

## v7 — "Vai colocar aparelho? Saiba disso antes" (`reel7.html`, `music7.py`)
Formato carrossel: slides deslizando com pontos de página e 👉 indicando o arraste. 4 dicas + CTA.

## v8 — "Você escova os dentes errado?" (`reel8.html`, `music8.py`)
4 erros comuns: cada um aparece com ❌ (fundo rosado, emoji tremendo) e vira ✅ com a forma certa.

## v9 — "Perguntas que a gente mais recebe" (`reel9.html`, `music9.py`)
Caixinha de perguntas que gira na tela, pergunta sendo digitada e resposta em destaque.

`lib/common.css` reúne os estilos do selo, do botão de WhatsApp e da marca usados a partir da v6.
`render_all.sh 6 7 8 9` renderiza e junta o áudio de vários vídeos de uma vez.
