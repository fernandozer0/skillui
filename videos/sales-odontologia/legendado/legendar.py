"""Burns two-colour captions into the "Mitos e verdades sobre implante" interview.

Questions (asked off-camera, which is exactly when the footage is blurred) are yellow;
the doctor's answers are white. Text was transcribed with faster-whisper (word
timestamps, saved in transcript.json) and then proof-read; each line below keeps the
transcript's timing and only fixes the wording.

Usage: python3 legendar.py <input.mov> <transcript.json> <out.mp4>
"""
import json
import subprocess
import sys

YELLOW, WHITE = "&H0000D4FF", "&H00FFFFFF"   # ASS colours are &HAABBGGRR

# (speaker, corrected text) in the same order as the transcript segments
LINES = [
    ("Q", "Doutor, vamos para os mitos e verdades sobre implante?"),
    ("A", "Claro!"),
    ("Q", "Primeiro: implante é só para idoso?"),
    ("A", "Mito! Na verdade, implante pode ser em qualquer idade."),
    ("A", "Se a gente já fez o crescimento ósseo e você perder um dente ali, ou mais de um dente,"),
    ("A", "você pode fazer implante."),
    ("Q", "Implante dói muito, doutor?"),
    ("A", "Mito! O implante muitas vezes dói menos que uma extração,"),
    ("A", "porque já foi relatado por muitos pacientes."),
    ("Q", "O osso pode diminuir se eu demorar para fazer?"),
    ("A", "Verdade! Se você demora muito para fazer o implante, você pode ter uma perda óssea."),
    ("A", "Mas isso pode ser resolvido com um procedimento chamado enxerto ósseo,"),
    ("A", "que em muitos casos é necessário."),
    ("Q", "Implante dá cárie?"),
    ("A", "Mito! Na verdade, o implante não dá cárie."),
    ("A", "Ele pode ter uma doença que se chama peri-implantite,"),
    ("A", "mas tendo acompanhamento com limpezas de 6 em 6 meses, você não tem esse problema."),
    ("Q", "Como a pessoa que está assistindo esse vídeo consegue falar com você?"),
    ("A", "É só acionar o link na bio e a gente dá uma avaliação."),
]

MAX_WORDS, MAX_CHARS = 4, 22


def chunks(words):
    """Split a line into short caption chunks, preferring breaks after punctuation."""
    out, cur = [], []
    for w in words:
        cur.append(w)
        text = " ".join(cur)
        if len(cur) >= MAX_WORDS or len(text) >= MAX_CHARS or w[-1] in ",.?!:":
            out.append(cur)
            cur = []
    if cur:
        out.append(cur)
    # don't leave a single dangling word on its own if it fits with the previous chunk
    merged = []
    for c in out:
        if merged and len(c) == 1 and len(" ".join(merged[-1] + c)) <= MAX_CHARS + 8:
            merged[-1] = merged[-1] + c
        else:
            merged.append(c)
    return merged


def ts(t):
    h, rem = divmod(max(t, 0), 3600)
    m, s = divmod(rem, 60)
    return f"{int(h)}:{int(m):02d}:{s:05.2f}"


def build_ass(segments):
    assert len(segments) == len(LINES), (len(segments), len(LINES))
    events = []
    for seg, (who, text) in zip(segments, LINES):
        asr = seg["words"]
        words = text.split()
        n = len(words)
        # map each corrected word onto the ASR word timeline proportionally
        pos = 0
        for c in chunks(words):
            a = pos / n
            b = (pos + len(c)) / n
            ia = min(int(a * len(asr)), len(asr) - 1)
            ib = max(min(int(round(b * len(asr))) - 1, len(asr) - 1), ia)
            events.append([asr[ia]["s"], asr[ib]["e"], who, " ".join(c)])
            pos += len(c)
    # hold each chunk until the next one starts (bridging small gaps), never overlapping
    for k, e in enumerate(events):
        nxt = events[k + 1][0] if k + 1 < len(events) else e[1] + 0.6
        if nxt - e[1] <= 0.6:
            e[1] = nxt
        else:
            e[1] = min(max(e[1] + 0.25, e[0] + 0.35), nxt)
    head = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Black,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,0,0,0,0,100,100,0,0,1,7,3,2,70,70,560,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    lines = []
    for s, e, who, txt in events:
        col = YELLOW if who == "Q" else WHITE
        pop = r"{\fscx82\fscy82\t(0,90,\fscx100\fscy100)}"
        lines.append(f"Dialogue: 0,{ts(s)},{ts(e)},Cap,,0,0,0,,{{\\c{col}}}{pop}{txt}")
    return head + "\n".join(lines) + "\n", events


if __name__ == "__main__":
    src, tr, out = sys.argv[1:4]
    ass, events = build_ass(json.load(open(tr)))
    open("legendas.ass", "w").write(ass)
    for s, e, who, txt in events:
        print(f"{s:6.2f}-{e:6.2f} {'AMARELO' if who == 'Q' else 'branco '} {txt}")
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-i", src,
                    "-vf", "scale=1080:1920:flags=lanczos,ass=legendas.ass",
                    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
                    "-c:a", "copy", "-movflags", "+faststart", out], check=True)
    print("wrote", out)
