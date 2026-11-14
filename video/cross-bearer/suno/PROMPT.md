# Suno용 프롬프트 — '십자가의 전달자' 오프닝 60초 연주곡

합성한 현재 음악 대신 실제 악단 같은 소리를 원할 때 쓴다. Suno 생성은 본인 계정으로 직접 해야 한다.
`bitwize-music` 플러그인의 `suno-engineer` 지침(연주곡: Instrumental 켜기, 스타일 상자에 장르·악기·분위기·템포, 가사 상자에는 구조 태그만, 태그마다 연주 지시 한두 단어)에 맞춰 작성했다.

## 설정

- Advanced Mode, **Instrumental: On**, **Variety: Off** (켜면 Suno가 스타일 상자를 고쳐 쓴다)
- 길이는 1분 안팎으로 나오게 여러 번 생성해 고른다. 정확히 60초로는 안 나오므로 받은 뒤 맞춘다.

## Style Box

```
Epic cinematic orchestral film score, instrumental, D minor resolving to D major, 60 BPM, slow and solemn. Solo piano and low cello drone open in darkness; strings join; timpani and low brass for a storm; a hushed wordless choir; a complete silence before the climax; solo cello over an accelerating timpani roll; then full orchestra, French horns, choir and cymbals in a triumphant major key. Reverent, sacred, goosebump-inducing, wide concert hall reverb, huge dynamic range.
```

## Exclude Styles

```
vocals, lyrics, singing words, drums kit, electric guitar, synth, EDM, trap, pop beat, lo-fi
```

## Lyrics Box (구조 태그만)

```
[Intro - dark, solitary piano]

[Theme - four-note motif, low strings]

[Build - hopeful, rolling strings]

[Storm - timpani, low brass, urgent]

[Interlude - hushed wordless choir]

[Break - total silence]

[Bridge - solo cello, timpani roll rising]

[Climax - full orchestra, major key, triumphant]

[Outro - horns carry the theme, final chord]

[End]
```

## 영상 큐 (받은 음원을 맞출 기준)

| 시간 | 영상 | 음악 |
|---|---|---|
| 0–6초 | 다메섹 길 | 어둡고 고요하게 |
| 6초 | 하늘의 빛 | 첫 충격음 |
| 14–20초 | 금빛 새벽 항해 | 밝아짐 |
| 20–25초 | 파선 | 가장 거친 구간 |
| 25–42초 | 감옥, 작별, 로마 | 잦아듦 |
| 42–44초 | 암전 | **완전한 침묵** |
| 44–48초 | 갈보리를 오름 | 첼로와 팀파니가 밀어 올림 |
| **48초** | 빛이 터짐 | **정점, 장조로 전환** |
| 50–56초 | 캠퍼스 | 주제를 크게 |
| 56–60초 | 제목 | 마지막 화음, 끝 1초는 잔향 |

음원을 `video/cross-bearer/suno/`에 올려 주면 정점을 48초에 맞춰 자르고, 플러그인으로 마스터링해 영상에 입힌다. '십자가의 전달자' 원곡 선율은 프롬프트에 넣지 않았다.
