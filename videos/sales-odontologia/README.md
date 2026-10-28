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
