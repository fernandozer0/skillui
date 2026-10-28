# Sales Odontologia — comercial para Reels

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
